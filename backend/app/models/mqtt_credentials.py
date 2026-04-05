from pydantic import BaseModel


class MqttCertification(BaseModel):
    """Response from /iot-open/sign/certification endpoint."""

    url: str
    port: int | str
    certificate_account: str
    certificate_password: str
    protocol: str = "mqtts"

    @property
    def port_int(self) -> int:
        return int(self.port)
