import asyncio
import logging
import time
from collections import deque
from typing import Any

from fastapi import WebSocket

from ..models.device import DeviceData

logger = logging.getLogger(__name__)


class DeviceStore:
    """Thread-safe device state store.

    MQTT callback thread puts messages into an asyncio.Queue.
    The async consumer task reads them, merges into device state,
    and broadcasts updates to connected WebSocket clients.
    """

    def __init__(self) -> None:
        self.device = DeviceData()
        self.recent_data: deque[dict[str, Any]] = deque(maxlen=1800)  # ~30 min at 1/sec
        self._ws_clients: set[WebSocket] = set()
        self._connection_status: str = "disconnected"  # connected | reconnecting | rest_fallback

    @property
    def connection_status(self) -> str:
        return self._connection_status

    @connection_status.setter
    def connection_status(self, value: str) -> None:
        self._connection_status = value

    def add_ws_client(self, ws: WebSocket) -> None:
        self._ws_clients.add(ws)

    def remove_ws_client(self, ws: WebSocket) -> None:
        self._ws_clients.discard(ws)

    def merge_quotas(self, raw: dict[str, Any]) -> None:
        """Merge partial or full quota data into device state."""
        # Handle nested MQTT messages with moduleType + params
        if "params" in raw and isinstance(raw["params"], dict):
            self.device.merge_raw_quotas(raw["params"])
        else:
            self.device.merge_raw_quotas(raw)

        self.device.last_updated = time.time()

        # Record snapshot for chart
        self.recent_data.append({
            "timestamp": self.device.last_updated,
            "watts_in": self.device.power_input.watts_in_sum,
            "watts_out": self.device.power_output.watts_out_sum,
            "soc": self.device.battery.soc,
        })

    async def broadcast(self, data: dict[str, Any]) -> None:
        """Send data to all connected WebSocket clients, cleaning up dead ones."""
        dead: list[WebSocket] = []
        for ws in self._ws_clients:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._ws_clients.discard(ws)

    async def broadcast_state(self) -> None:
        """Broadcast current full device state to all WS clients."""
        data = self.device.to_flat_dict()
        data["connection_status"] = self._connection_status
        await self.broadcast({"type": "state", "data": data})

    def get_snapshot(self) -> dict[str, Any]:
        """Return current state as a dict (for REST endpoint)."""
        data = self.device.to_flat_dict()
        data["connection_status"] = self._connection_status
        return data

    def get_recent(self) -> list[dict[str, Any]]:
        """Return recent power data for chart."""
        return list(self.recent_data)


async def queue_consumer(
    queue: asyncio.Queue,
    store: DeviceStore,
    mqtt_client: Any,
) -> None:
    """Async task that consumes messages from the MQTT thread queue.

    Runs on the main async event loop, keeping all state mutations
    single-threaded.
    """
    while True:
        msg = await queue.get()
        msg_type = msg.get("type")

        if msg_type == "quota":
            store.merge_quotas(msg["data"])
            await store.broadcast_state()

        elif msg_type == "set_reply":
            request_id = msg.get("id")
            if request_id is not None:
                mqtt_client.resolve_command_future(request_id, msg["data"])
            await store.broadcast({"type": "set_reply", "data": msg["data"]})

        elif msg_type == "status":
            status_data = msg.get("data", {})
            online = status_data.get("online", False)
            store.device.online = bool(online)
            await store.broadcast({"type": "status", "data": {"online": store.device.online}})

        elif msg_type == "connection":
            status = msg.get("status", "disconnected")
            if status == "connected":
                store.connection_status = "connected"
            else:
                store.connection_status = "reconnecting"
            await store.broadcast({"type": "connection", "data": {"status": store.connection_status}})
