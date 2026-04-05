import logging
from typing import Any

import httpx

from ..config import settings
from ..models.mqtt_credentials import MqttCertification
from .ecoflow_auth import sign_request

logger = logging.getLogger(__name__)


class EcoFlowRestClient:
    """REST client for the EcoFlow public Developer API.

    Handles only: certification, device list, and quota polling.
    Commands go via MQTT, not REST.
    """

    def __init__(self) -> None:
        self.base_url = settings.api_base_url
        self.access_key = settings.access_key
        self.secret_key = settings.secret_key
        self._client = httpx.AsyncClient(timeout=15.0)

    async def close(self) -> None:
        await self._client.aclose()

    def _signed_headers(self, params: dict | None = None) -> dict[str, str]:
        return sign_request(self.access_key, self.secret_key, params)

    async def get_certification(self) -> MqttCertification:
        """Fetch MQTT broker credentials from /iot-open/sign/certification."""
        url = f"{self.base_url}/iot-open/sign/certification"
        headers = self._signed_headers()
        logger.info("GET %s", url)
        resp = await self._client.get(url, headers=headers)
        logger.info("GET %s -> %d", url, resp.status_code)
        resp.raise_for_status()
        data = resp.json()
        logger.debug("Certification response body: %s", data)
        payload = data.get("data", {})
        creds = MqttCertification(
            url=payload.get("url", ""),
            port=payload.get("port", 8883),
            certificate_account=payload.get("certificateAccount", ""),
            certificate_password=payload.get("certificatePassword", ""),
            protocol=payload.get("protocol", "mqtts"),
        )
        logger.info("MQTT credentials obtained (broker: %s:%s, account: %s)", creds.url, creds.port_int, creds.certificate_account)
        return creds

    async def get_device_list(self) -> list[dict[str, Any]]:
        """Fetch list of devices bound to this account."""
        url = f"{self.base_url}/iot-open/sign/device/list"
        headers = self._signed_headers()
        logger.info("GET %s", url)
        resp = await self._client.get(url, headers=headers)
        logger.info("GET %s -> %d", url, resp.status_code)
        resp.raise_for_status()
        data = resp.json()
        devices = data.get("data", [])
        logger.info("Device list returned %d device(s)", len(devices))
        logger.debug("Device list response body: %s", data)
        return devices

    async def get_all_quotas(self, sn: str | None = None) -> dict[str, Any]:
        """Fetch all current device parameters via REST polling."""
        device_sn = sn or settings.device_sn
        params = {"sn": device_sn}
        url = f"{self.base_url}/iot-open/sign/device/quota/all"
        headers = self._signed_headers(params)
        logger.info("GET %s (sn=%s)", url, device_sn)
        resp = await self._client.get(url, headers=headers, params=params)
        logger.info("GET %s -> %d", url, resp.status_code)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != "0" and data.get("code") != 0:
            logger.warning("Quota response error: code=%s message=%s", data.get("code"), data.get("message", "unknown"))
            return {}
        quotas = data.get("data", {})
        logger.info("Quota response: %d parameters received", len(quotas))
        logger.debug("Quota response body: %s", quotas)
        return quotas
