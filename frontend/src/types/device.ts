export interface DeviceState {
  // Battery
  'battery.soc': number | null
  'battery.soh': number | null
  'battery.cycles': number | null
  'battery.full_cap': number | null
  'battery.remain_cap': number | null
  'battery.design_cap': number | null
  'battery.voltage': number | null
  'battery.current': number | null
  'battery.temp': number | null
  'battery.max_cell_temp': number | null
  'battery.min_cell_temp': number | null
  'battery.max_cell_vol': number | null
  'battery.min_cell_vol': number | null
  'battery.max_mos_temp': number | null
  'battery.min_mos_temp': number | null

  // Power Input
  'power_input.watts_in_sum': number | null
  'power_input.ac_in_watts': number | null
  'power_input.ac_in_voltage': number | null
  'power_input.ac_in_freq': number | null
  'power_input.solar_in_watts': number | null
  'power_input.solar_hv_watts': number | null
  'power_input.solar_lv_watts': number | null
  'power_input.dc_in_watts': number | null

  // Power Output
  'power_output.watts_out_sum': number | null
  'power_output.ac_out_watts': number | null
  'power_output.ac_out_voltage': number | null
  'power_output.ac_out_freq': number | null
  'power_output.dc_out_watts': number | null
  'power_output.usbc_watts_1': number | null
  'power_output.usbc_watts_2': number | null
  'power_output.qc_usb_watts_1': number | null
  'power_output.qc_usb_watts_2': number | null
  'power_output.dc_12v_watts': number | null

  // Time Estimates
  'time_estimates.chg_remain_time': number | null
  'time_estimates.dsg_remain_time': number | null

  // Status
  'status.ac_in_connected': boolean | null
  'status.solar_in_connected': boolean | null
  'status.dc_in_connected': boolean | null
  'status.is_charging': boolean | null
  'status.is_discharging': boolean | null
  'status.ac_out_enabled': boolean | null
  'status.dc_out_enabled': boolean | null
  'status.dc_12v_out_enabled': boolean | null
  'status.battery_low': boolean | null
  'status.battery_full': boolean | null
  'status.over_temperature': boolean | null
  'status.xboost_enabled': boolean | null
  'status.beeper_enabled': boolean | null

  // Settings
  'settings.ac_charge_watts': number | null
  'settings.max_charge_soc': number | null
  'settings.min_discharge_soc': number | null
  'settings.screen_brightness': number | null
  'settings.standby_timeout': number | null
  'settings.ac_standby_timeout': number | null
  'settings.dc_standby_timeout': number | null

  // Extra Battery 1
  'extra_battery_1.connected': boolean
  'extra_battery_1.soc': number | null
  'extra_battery_1.soh': number | null

  // Extra Battery 2
  'extra_battery_2.connected': boolean
  'extra_battery_2.soc': number | null
  'extra_battery_2.soh': number | null

  // Meta
  online: boolean
  last_updated: number | null
  connection_status: 'connected' | 'reconnecting' | 'rest_fallback' | 'disconnected'

  // Allow additional unknown keys from the API
  [key: string]: number | boolean | string | null | undefined
}

export interface RecentDataPoint {
  timestamp: number
  watts_in: number | null
  watts_out: number | null
  soc: number | null
}

export interface CommandRequest {
  params: Record<string, number | string | boolean>
  module_type?: number
  operate_type?: string
}

export interface CommandResponse {
  success: boolean
  data?: Record<string, unknown>
  error?: string
}

export interface WsMessage {
  type: 'state' | 'set_reply' | 'status' | 'connection'
  data: Record<string, unknown>
}
