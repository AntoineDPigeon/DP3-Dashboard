from pydantic import BaseModel
from typing import Any


class BatteryStatus(BaseModel):
    """Battery Management System status."""

    soc: float | None = None  # State of charge (%)
    soh: float | None = None  # State of health (%)
    cycles: int | None = None  # Charge cycle count
    full_cap: float | None = None  # Full capacity (Wh)
    remain_cap: float | None = None  # Remaining capacity (Wh)
    design_cap: float | None = None  # Design capacity (Wh)
    voltage: float | None = None  # Battery voltage (V)
    current: float | None = None  # Battery current (A)
    temp: float | None = None  # Battery temperature (C)
    max_cell_temp: float | None = None
    min_cell_temp: float | None = None
    max_cell_vol: float | None = None
    min_cell_vol: float | None = None
    max_mos_temp: float | None = None
    min_mos_temp: float | None = None


class PowerInput(BaseModel):
    """Input power readings."""

    watts_in_sum: float | None = None  # Total input (W)
    ac_in_watts: float | None = None  # AC input (W)
    ac_in_voltage: float | None = None  # AC input voltage (V)
    ac_in_freq: float | None = None  # AC input frequency (Hz)
    solar_in_watts: float | None = None  # Total solar input (W)
    solar_hv_watts: float | None = None  # HV solar input (W)
    solar_lv_watts: float | None = None  # LV solar input (W)
    dc_in_watts: float | None = None  # DC input (W)


class PowerOutput(BaseModel):
    """Output power readings."""

    watts_out_sum: float | None = None  # Total output (W)
    ac_out_watts: float | None = None  # AC output (W)
    ac_out_voltage: float | None = None  # AC output voltage (V)
    ac_out_freq: float | None = None  # AC output frequency (Hz)
    dc_out_watts: float | None = None  # DC output (W)
    usbc_watts_1: float | None = None  # USB-C port 1 (W)
    usbc_watts_2: float | None = None  # USB-C port 2 (W)
    qc_usb_watts_1: float | None = None  # QC USB port 1 (W)
    qc_usb_watts_2: float | None = None  # QC USB port 2 (W)
    dc_12v_watts: float | None = None  # 12V DC output (W)


class TimeEstimates(BaseModel):
    """Charge/discharge time estimates."""

    chg_remain_time: int | None = None  # Charge remaining (minutes)
    dsg_remain_time: int | None = None  # Discharge remaining (minutes)


class DeviceStatus(BaseModel):
    """Binary status indicators."""

    ac_in_connected: bool | None = None
    solar_in_connected: bool | None = None
    dc_in_connected: bool | None = None
    is_charging: bool | None = None
    is_discharging: bool | None = None
    ac_out_enabled: bool | None = None
    dc_out_enabled: bool | None = None
    dc_12v_out_enabled: bool | None = None
    battery_low: bool | None = None
    battery_full: bool | None = None
    over_temperature: bool | None = None
    xboost_enabled: bool | None = None
    beeper_enabled: bool | None = None


class DeviceSettings(BaseModel):
    """Configurable device settings."""

    ac_charge_watts: int | None = None  # AC charging power (400-2900W)
    max_charge_soc: int | None = None  # Max charge level (50-100%)
    min_discharge_soc: int | None = None  # Min discharge level (0-30%)
    screen_brightness: int | None = None
    standby_timeout: int | None = None  # minutes
    ac_standby_timeout: int | None = None  # minutes
    dc_standby_timeout: int | None = None  # minutes


class ExtraBattery(BaseModel):
    """Extra battery pack status (up to 2 additional packs)."""

    connected: bool = False
    soc: float | None = None
    soh: float | None = None
    cycles: int | None = None
    full_cap: float | None = None
    remain_cap: float | None = None
    temp: float | None = None
    voltage: float | None = None
    current: float | None = None


class DeviceData(BaseModel):
    """Complete Delta Pro 3 device state."""

    battery: BatteryStatus = BatteryStatus()
    power_input: PowerInput = PowerInput()
    power_output: PowerOutput = PowerOutput()
    time_estimates: TimeEstimates = TimeEstimates()
    status: DeviceStatus = DeviceStatus()
    settings: DeviceSettings = DeviceSettings()
    extra_battery_1: ExtraBattery = ExtraBattery()
    extra_battery_2: ExtraBattery = ExtraBattery()
    online: bool = False
    last_updated: float | None = None  # Unix timestamp

    def merge_raw_quotas(self, raw: dict[str, Any]) -> None:
        """Merge a raw EcoFlow API quota response into typed fields.

        The EcoFlow API returns flat key-value pairs. This method maps them
        to the structured models. Unknown keys are silently ignored so the
        dashboard works even if EcoFlow adds new parameters.
        """
        mapping = _build_mapping(self)
        for key, value in raw.items():
            if key in mapping:
                obj, attr = mapping[key]
                setattr(obj, attr, value)

    def to_flat_dict(self) -> dict[str, Any]:
        """Return all data as a flat dict for WebSocket broadcast."""
        result: dict[str, Any] = {"online": self.online, "last_updated": self.last_updated}
        for section_name in [
            "battery", "power_input", "power_output",
            "time_estimates", "status", "settings",
            "extra_battery_1", "extra_battery_2",
        ]:
            section = getattr(self, section_name)
            for field_name in section.model_fields:
                val = getattr(section, field_name)
                if val is not None:
                    result[f"{section_name}.{field_name}"] = val
        return result


def _build_mapping(device: DeviceData) -> dict[str, tuple[BaseModel, str]]:
    """Map known EcoFlow quota keys to (model_instance, attribute_name)."""
    return {
        # Battery (BMS)
        "soc": (device.battery, "soc"),
        "bms_bmsStatus.f32ShowSoc": (device.battery, "soc"),
        "bms_bmsStatus.soh": (device.battery, "soh"),
        "bms_bmsStatus.cycles": (device.battery, "cycles"),
        "bms_bmsStatus.fullCap": (device.battery, "full_cap"),
        "bms_bmsStatus.remainCap": (device.battery, "remain_cap"),
        "bms_bmsStatus.designCap": (device.battery, "design_cap"),
        "bms_bmsStatus.vol": (device.battery, "voltage"),
        "bms_bmsStatus.amp": (device.battery, "current"),
        "bms_bmsStatus.temp": (device.battery, "temp"),
        "bms_bmsStatus.maxCellTemp": (device.battery, "max_cell_temp"),
        "bms_bmsStatus.minCellTemp": (device.battery, "min_cell_temp"),
        "bms_bmsStatus.maxCellVol": (device.battery, "max_cell_vol"),
        "bms_bmsStatus.minCellVol": (device.battery, "min_cell_vol"),
        "bms_bmsStatus.maxMosTemp": (device.battery, "max_mos_temp"),
        "bms_bmsStatus.minMosTemp": (device.battery, "min_mos_temp"),
        "bms_bmsInfo.soh": (device.battery, "soh"),
        "bms_bmsStatus.cycSoh": (device.battery, "soh"),
        # Power input
        "wattsInSum": (device.power_input, "watts_in_sum"),
        "inv.inputWatts": (device.power_input, "ac_in_watts"),
        "inv.acInVol": (device.power_input, "ac_in_voltage"),
        "inv.acInFreq": (device.power_input, "ac_in_freq"),
        "mppt.inWatts": (device.power_input, "solar_in_watts"),
        "mppt.hvInWatts": (device.power_input, "solar_hv_watts"),
        "mppt.lvInWatts": (device.power_input, "solar_lv_watts"),
        "mppt.dcInWatts": (device.power_input, "dc_in_watts"),
        # Power output
        "wattsOutSum": (device.power_output, "watts_out_sum"),
        "inv.outputWatts": (device.power_output, "ac_out_watts"),
        "inv.acOutVol": (device.power_output, "ac_out_voltage"),
        "inv.acOutFreq": (device.power_output, "ac_out_freq"),
        "pd.dcOutWatts": (device.power_output, "dc_out_watts"),
        "pd.typecWatts1": (device.power_output, "usbc_watts_1"),
        "pd.typecWatts2": (device.power_output, "usbc_watts_2"),
        "pd.qcUsb1Watts": (device.power_output, "qc_usb_watts_1"),
        "pd.qcUsb2Watts": (device.power_output, "qc_usb_watts_2"),
        "pd.dc12vWatts": (device.power_output, "dc_12v_watts"),
        # Time estimates
        "bms_emsStatus.chgRemainTime": (device.time_estimates, "chg_remain_time"),
        "bms_emsStatus.dsgRemainTime": (device.time_estimates, "dsg_remain_time"),
        # Device status booleans
        "pd.acInConnected": (device.status, "ac_in_connected"),
        "mppt.solarInConnected": (device.status, "solar_in_connected"),
        "pd.dcInConnected": (device.status, "dc_in_connected"),
        "pd.chgDsgState": (device.status, "is_charging"),
        "inv.acOutEnabled": (device.status, "ac_out_enabled"),
        "pd.dcOutEnabled": (device.status, "dc_out_enabled"),
        "pd.dc12vOutEnabled": (device.status, "dc_12v_out_enabled"),
        "pd.batteryLow": (device.status, "battery_low"),
        "pd.batteryFull": (device.status, "battery_full"),
        "pd.overTemp": (device.status, "over_temperature"),
        "inv.cfgXboost": (device.status, "xboost_enabled"),
        "pd.cfgBeepSwitch": (device.status, "beeper_enabled"),
        # Settings
        "inv.SlowChgWatts": (device.settings, "ac_charge_watts"),
        "inv.cfgChgWatts": (device.settings, "ac_charge_watts"),
        "bms_emsStatus.chgUpLimit": (device.settings, "max_charge_soc"),
        "bms_emsStatus.dsgDownLimit": (device.settings, "min_discharge_soc"),
        "pd.brightness": (device.settings, "screen_brightness"),
        "pd.standbyMin": (device.settings, "standby_timeout"),
        "inv.acStandbyMin": (device.settings, "ac_standby_timeout"),
        "pd.dcStandbyMin": (device.settings, "dc_standby_timeout"),
        # Extra battery 1
        "bms_slave.f32ShowSoc": (device.extra_battery_1, "soc"),
        "bms_slave.soh": (device.extra_battery_1, "soh"),
        "bms_slave.cycles": (device.extra_battery_1, "cycles"),
        "bms_slave.fullCap": (device.extra_battery_1, "full_cap"),
        "bms_slave.remainCap": (device.extra_battery_1, "remain_cap"),
        "bms_slave.temp": (device.extra_battery_1, "temp"),
        "bms_slave.vol": (device.extra_battery_1, "voltage"),
        "bms_slave.amp": (device.extra_battery_1, "current"),
    }
