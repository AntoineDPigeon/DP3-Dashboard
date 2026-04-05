import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..services.device_store import DeviceStore

logger = logging.getLogger(__name__)

router = APIRouter()

# Injected at startup
store: DeviceStore | None = None


def init(device_store: DeviceStore) -> None:
    global store
    store = device_store


@router.websocket("/ws/device")
async def device_websocket(ws: WebSocket) -> None:
    """WebSocket endpoint for real-time device updates.

    On connect: sends full state snapshot.
    Then pushes incremental updates as they arrive from MQTT.
    """
    assert store is not None
    await ws.accept()
    store.add_ws_client(ws)
    logger.info("WebSocket client connected (total: %d)", len(store._ws_clients))

    try:
        # Send initial snapshot
        snapshot = store.get_snapshot()
        await ws.send_json({"type": "state", "data": snapshot})

        # Keep alive — the store broadcasts will push data
        while True:
            # Wait for client messages (ping/pong or close)
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.warning("WebSocket error: %s", e)
    finally:
        store.remove_ws_client(ws)
        logger.info("WebSocket client disconnected (total: %d)", len(store._ws_clients))
