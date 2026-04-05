import asyncio
import json
import logging
import time
from typing import Any, Callable

import paho.mqtt.client as mqtt

from ..config import settings
from ..models.mqtt_credentials import MqttCertification

logger = logging.getLogger(__name__)


class EcoFlowMqttClient:
    """MQTT client for the EcoFlow public Developer API.

    Subscribes to:
      /open/{certificateAccount}/{sn}/quota       — real-time device data
      /open/{certificateAccount}/{sn}/set_reply    — command responses
      /open/{certificateAccount}/{sn}/status       — online/offline

    Publishes to:
      /open/{certificateAccount}/{sn}/set          — device commands
    """

    def __init__(self, message_queue: asyncio.Queue, loop: asyncio.AbstractEventLoop) -> None:
        self._queue = message_queue
        self._loop = loop
        self._client: mqtt.Client | None = None
        self._creds: MqttCertification | None = None
        self._username: str = ""
        self._sn = settings.device_sn
        self._connected = False
        self._command_futures: dict[int, asyncio.Future] = {}

    @property
    def connected(self) -> bool:
        return self._connected

    def _topic(self, suffix: str) -> str:
        return f"/open/{self._username}/{self._sn}/{suffix}"

    def connect(self, creds: MqttCertification) -> None:
        """Connect to the EcoFlow MQTT broker with provided credentials."""
        self._creds = creds
        self._username = creds.certificate_account

        self._client = mqtt.Client(
            client_id=settings.mqtt_client_id,
            protocol=mqtt.MQTTv311,
        )
        self._client.username_pw_set(creds.certificate_account, creds.certificate_password)
        self._client.tls_set()

        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message

        self._client.reconnect_delay_set(min_delay=1, max_delay=60)

        logger.info("Connecting to MQTT broker %s:%s", creds.url, creds.port_int)
        self._client.connect_async(creds.url, creds.port_int, keepalive=15)
        self._client.loop_start()

    def disconnect(self) -> None:
        if self._client:
            self._client.loop_stop()
            self._client.disconnect()
            self._connected = False

    def reconnect_with_new_creds(self, creds: MqttCertification) -> None:
        """Reconnect with fresh credentials (handles credential expiry)."""
        self.disconnect()
        self.connect(creds)

    def _on_connect(self, client: mqtt.Client, userdata: Any, flags: Any, rc: int) -> None:
        if rc == 0:
            logger.info("MQTT connected successfully")
            self._connected = True
            client.subscribe(self._topic("quota"))
            client.subscribe(self._topic("set_reply"))
            client.subscribe(self._topic("status"))
            logger.info("Subscribed to topics for device %s", self._sn)
            self._loop.call_soon_threadsafe(
                self._queue.put_nowait,
                {"type": "connection", "status": "connected"},
            )
        else:
            logger.error("MQTT connection failed with rc=%d", rc)
            self._connected = False

    def _on_disconnect(self, client: mqtt.Client, userdata: Any, rc: int) -> None:
        logger.warning("MQTT disconnected (rc=%d)", rc)
        self._connected = False
        self._loop.call_soon_threadsafe(
            self._queue.put_nowait,
            {"type": "connection", "status": "disconnected"},
        )

    def _on_message(self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage) -> None:
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            logger.warning("Failed to decode MQTT message on %s", msg.topic)
            return

        topic = msg.topic
        if topic.endswith("/quota"):
            self._loop.call_soon_threadsafe(
                self._queue.put_nowait,
                {"type": "quota", "data": payload, "timestamp": time.time()},
            )
        elif topic.endswith("/set_reply"):
            request_id = payload.get("id")
            self._loop.call_soon_threadsafe(
                self._queue.put_nowait,
                {"type": "set_reply", "data": payload, "id": request_id},
            )
        elif topic.endswith("/status"):
            self._loop.call_soon_threadsafe(
                self._queue.put_nowait,
                {"type": "status", "data": payload},
            )

    def publish_command(self, command_payload: dict) -> None:
        """Publish a command to the MQTT /set topic."""
        if not self._client or not self._connected:
            raise ConnectionError("MQTT not connected")
        topic = self._topic("set")
        self._client.publish(topic, json.dumps(command_payload))
        logger.info("Published command to %s: id=%s", topic, command_payload.get("id"))

    def register_command_future(self, request_id: int, future: asyncio.Future) -> None:
        self._command_futures[request_id] = future

    def resolve_command_future(self, request_id: int, result: dict) -> None:
        future = self._command_futures.pop(request_id, None)
        if future and not future.done():
            self._loop.call_soon_threadsafe(future.set_result, result)
