import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings

# Path to the built frontend (frontend/dist after `npm run build`)
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
from .routers import device as device_router
from .routers import ws as ws_router
from .services.device_store import DeviceStore, queue_consumer
from .services.ecoflow_mqtt import EcoFlowMqttClient
from .services.ecoflow_rest import EcoFlowRestClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Shared state
rest_client: EcoFlowRestClient | None = None
mqtt_client_instance: EcoFlowMqttClient | None = None
store: DeviceStore | None = None
_polling_task: asyncio.Task | None = None
_consumer_task: asyncio.Task | None = None


async def _rest_polling_fallback(
    rest: EcoFlowRestClient,
    device_store: DeviceStore,
    mqtt: EcoFlowMqttClient,
) -> None:
    """Poll EcoFlow REST API when MQTT is down."""
    while True:
        await asyncio.sleep(30)
        if not mqtt.connected:
            device_store.connection_status = "rest_fallback"
            try:
                raw = await rest.get_all_quotas()
                if raw:
                    device_store.merge_quotas(raw)
                    await device_store.broadcast_state()
                    logger.info("REST fallback: updated device state")
            except Exception as e:
                logger.error("REST fallback polling failed: %s", e)

            # Try to re-certify and reconnect MQTT
            try:
                creds = await rest.get_certification()
                mqtt.reconnect_with_new_creds(creds)
                logger.info("Attempting MQTT reconnection with fresh credentials")
            except Exception as e:
                logger.debug("MQTT re-certification failed: %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle.

    Startup sequence:
    1. Create REST client
    2. Fetch MQTT credentials via /certification
    3. Fetch initial device state via /device/quota/all
    4. Connect MQTT client
    5. Start async consumer task
    6. Start REST polling fallback task
    """
    global rest_client, mqtt_client_instance, store, _polling_task, _consumer_task

    logger.info("Starting DP3 Dashboard backend...")
    logger.info("Region: %s | Device SN: %s", settings.region, settings.device_sn)

    # 1. Create services
    rest_client = EcoFlowRestClient()
    store = DeviceStore()
    message_queue: asyncio.Queue = asyncio.Queue()
    loop = asyncio.get_event_loop()
    mqtt_client_instance = EcoFlowMqttClient(message_queue, loop)

    # Inject dependencies into routers
    device_router.init(store, mqtt_client_instance)
    ws_router.init(store)

    creds = None

    if settings.is_configured:
        # 2. Fetch MQTT credentials
        try:
            creds = await rest_client.get_certification()
            logger.info("MQTT credentials obtained (broker: %s:%s)", creds.url, creds.port_int)
        except Exception as e:
            logger.error("Failed to get MQTT credentials: %s", e)
            logger.warning("Starting in REST-only mode")

        # 3. Fetch initial device state
        try:
            raw_quotas = await rest_client.get_all_quotas()
            if raw_quotas:
                store.merge_quotas(raw_quotas)
                logger.info("Initial device state loaded (%d keys)", len(raw_quotas))
            else:
                logger.warning("No initial quota data (device may be offline)")
        except Exception as e:
            logger.error("Failed to fetch initial quotas: %s", e)

        # 4. Connect MQTT
        if creds:
            try:
                mqtt_client_instance.connect(creds)
            except Exception as e:
                logger.error("MQTT connection failed: %s", e)
    else:
        logger.warning(
            "EcoFlow credentials not configured. "
            "Set ACCESS_KEY, SECRET_KEY, and DEVICE_SN in .env to connect."
        )
        store.connection_status = "disconnected"

    # 5. Start consumer task
    _consumer_task = asyncio.create_task(
        queue_consumer(message_queue, store, mqtt_client_instance)
    )

    # 6. Start REST fallback polling (only if configured)
    if settings.is_configured:
        _polling_task = asyncio.create_task(
            _rest_polling_fallback(rest_client, store, mqtt_client_instance)
        )

    logger.info("Backend startup complete")
    yield

    # Shutdown
    logger.info("Shutting down...")
    if _consumer_task:
        _consumer_task.cancel()
    if _polling_task:
        _polling_task.cancel()
    if mqtt_client_instance:
        mqtt_client_instance.disconnect()
    if rest_client:
        await rest_client.close()
    logger.info("Shutdown complete")


app = FastAPI(
    title="DP3 Dashboard API",
    description="Delta Pro 3 monitoring and control dashboard",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(device_router.router)
app.include_router(ws_router.router)

# Serve the built Vue frontend as static files.
# API and WebSocket routes are registered first, so they take priority.
# The fallback html=True serves index.html for any unmatched route (SPA support).
if FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
    logger.info("Serving frontend from %s", FRONTEND_DIST)
else:
    logger.warning(
        "Frontend dist not found at %s — run 'npm run build' in frontend/ first",
        FRONTEND_DIST,
    )
