from pydantic import BaseModel
from typing import Any


class DeviceCommand(BaseModel):
    """Command to send to a Delta Pro 3 via MQTT /set topic."""

    id: int
    version: str = "1.0"
    module_type: int = 1
    operate_type: str = ""
    params: dict[str, Any] = {}

    def to_mqtt_payload(self) -> dict:
        return {
            "id": self.id,
            "version": self.version,
            "moduleType": self.module_type,
            "operateType": self.operate_type,
            "params": self.params,
        }


class DeltaPro3Command(BaseModel):
    """Convenience model for Delta Pro 3 specific commands.

    Commands use cmdId=17, cmdFunc=254, dest=2 for most operations.
    """

    cmd_id: int = 17
    cmd_func: int = 254
    dest: int = 2
    config_params: dict[str, Any]

    def to_params(self) -> dict[str, Any]:
        return {
            "cmdId": self.cmd_id,
            "cmdFunc": self.cmd_func,
            "dest": self.dest,
            **self.config_params,
        }


# Predefined command builders for common operations
def ac_output_command(enable: bool) -> dict[str, Any]:
    return {"cmdId": 17, "cmdFunc": 254, "dest": 2, "cfgHvAcOutOpen": int(enable)}


def dc_output_command(enable: bool) -> dict[str, Any]:
    return {"cmdId": 17, "cmdFunc": 254, "dest": 2, "cfgDcOutOpen": int(enable)}


def dc_12v_output_command(enable: bool) -> dict[str, Any]:
    return {"cmdId": 17, "cmdFunc": 254, "dest": 2, "cfg12VDcOutOpen": int(enable)}


def beeper_command(enable: bool) -> dict[str, Any]:
    return {"cmdId": 17, "cmdFunc": 254, "dest": 2, "cfgBeepSwitch": int(enable)}


def xboost_command(enable: bool) -> dict[str, Any]:
    return {"cmdId": 17, "cmdFunc": 254, "dest": 2, "cfgXboost": int(enable)}


def ac_charge_power_command(watts: int) -> dict[str, Any]:
    """Set AC charging power. Range: 400-2900W."""
    return {"cmdId": 17, "cmdFunc": 254, "dest": 2, "cfgChgWatts": max(400, min(2900, watts))}


def max_charge_level_command(soc: int) -> dict[str, Any]:
    """Set maximum charge level. Range: 50-100%."""
    return {"cmdId": 17, "cmdFunc": 254, "dest": 2, "cfgChgPctMax": max(50, min(100, soc))}


def min_discharge_level_command(soc: int) -> dict[str, Any]:
    """Set minimum discharge level. Range: 0-30%."""
    return {"cmdId": 17, "cmdFunc": 254, "dest": 2, "cfgDsgPctMin": max(0, min(30, soc))}
