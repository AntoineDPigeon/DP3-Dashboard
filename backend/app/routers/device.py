import asyncio
import logging
import random
import time
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services.device_store import DeviceStore
from ..services.ecoflow_mqtt import EcoFlowMqttClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/device")

# Injected at startup
store: DeviceStore | None = None
mqtt_client: EcoFlowMqttClient | None = None


def init(device_store: DeviceStore, mqtt: EcoFlowMqttClient) -> None:
    global store, mqtt_client
    store = device_store
    mqtt_client = mqtt


@router.get("/status")
async def get_device_status() -> dict[str, Any]:
    """Return current device state from the in-memory store."""
    assert store is not None
    logger.info("GET /api/device/status")
    snapshot = store.get_snapshot()
    logger.debug("GET /api/device/status -> %d keys", len(snapshot))
    return snapshot


@router.get("/recent")
async def get_recent_data() -> list[dict[str, Any]]:
    """Return recent power data for charts (last ~30 min from in-memory deque)."""
    assert store is not None
    recent = store.get_recent()
    logger.info("GET /api/device/recent -> %d data points", len(recent))
    return recent


@router.get("/health")
async def health() -> dict[str, str]:
    """Readiness check — returns connection status."""
    assert store is not None
    result = {
        "status": "ok",
        "mqtt": store.connection_status,
        "has_data": str(store.device.last_updated is not None),
    }
    logger.info("GET /api/device/health -> mqtt=%s has_data=%s", result["mqtt"], result["has_data"])
    return result


class CommandRequest(BaseModel):
    params: dict[str, Any]
    module_type: int = 1
    operate_type: str = ""


@router.post("/command")
async def send_command(req: CommandRequest) -> dict[str, Any]:
    """Send a command to the device via MQTT /set topic.

    The command is published to MQTT, then we wait for the set_reply
    with a matching request ID (timeout: 10s).
    """
    assert mqtt_client is not None

    if not mqtt_client.connected:
        raise HTTPException(status_code=503, detail="MQTT not connected")

    request_id = random.randint(100000, 999999)
    payload = {
        "id": request_id,
        "version": "1.0",
        "moduleType": req.module_type,
        "operateType": req.operate_type,
        "params": req.params,
    }

    # Create a future to await the set_reply
    loop = asyncio.get_event_loop()
    future: asyncio.Future = loop.create_future()
    mqtt_client.register_command_future(request_id, future)

    try:
        logger.info("POST /api/device/command -> publishing MQTT command id=%d params=%s", request_id, req.params)
        mqtt_client.publish_command(payload)
        result = await asyncio.wait_for(future, timeout=10.0)
        logger.info("POST /api/device/command -> success (id=%d)", request_id)
        return {"success": True, "data": result}
    except asyncio.TimeoutError:
        logger.warning("POST /api/device/command -> timeout (id=%d)", request_id)
        return {"success": False, "error": "Command timed out (10s)"}
    except ConnectionError as e:
        logger.error("POST /api/device/command -> connection error: %s", e)
        raise HTTPException(status_code=503, detail=str(e))
