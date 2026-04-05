import { ref } from 'vue'
import type { CommandRequest, CommandResponse } from '@/types/device'

const loading = ref(false)
const lastError = ref<string | null>(null)

async function sendCommand(params: Record<string, number | string | boolean>): Promise<CommandResponse> {
  loading.value = true
  lastError.value = null

  const body: CommandRequest = { params }

  try {
    const resp = await fetch('/api/device/command', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })

    if (!resp.ok) {
      const detail = resp.status === 503 ? 'MQTT not connected' : `HTTP ${resp.status}`
      lastError.value = detail
      return { success: false, error: detail }
    }

    const result: CommandResponse = await resp.json()
    if (!result.success) {
      lastError.value = result.error ?? 'Command failed'
    }
    return result
  } catch (e) {
    const msg = e instanceof Error ? e.message : 'Network error'
    lastError.value = msg
    return { success: false, error: msg }
  } finally {
    loading.value = false
  }
}

// Predefined command helpers
function toggleAcOutput(enable: boolean) {
  return sendCommand({ cmdId: 17, cmdFunc: 254, dest: 2, cfgHvAcOutOpen: enable ? 1 : 0 })
}

function toggleDcOutput(enable: boolean) {
  return sendCommand({ cmdId: 17, cmdFunc: 254, dest: 2, cfgDcOutOpen: enable ? 1 : 0 })
}

function toggleDc12vOutput(enable: boolean) {
  return sendCommand({ cmdId: 17, cmdFunc: 254, dest: 2, cfg12VDcOutOpen: enable ? 1 : 0 })
}

function toggleBeeper(enable: boolean) {
  return sendCommand({ cmdId: 17, cmdFunc: 254, dest: 2, cfgBeepSwitch: enable ? 1 : 0 })
}

function toggleXboost(enable: boolean) {
  return sendCommand({ cmdId: 17, cmdFunc: 254, dest: 2, cfgXboost: enable ? 1 : 0 })
}

function setAcChargePower(watts: number) {
  return sendCommand({ cmdId: 17, cmdFunc: 254, dest: 2, cfgChgWatts: Math.max(400, Math.min(2900, watts)) })
}

function setMaxChargeSoc(soc: number) {
  return sendCommand({ cmdId: 17, cmdFunc: 254, dest: 2, cfgChgPctMax: Math.max(50, Math.min(100, soc)) })
}

function setMinDischargeSoc(soc: number) {
  return sendCommand({ cmdId: 17, cmdFunc: 254, dest: 2, cfgDsgPctMin: Math.max(0, Math.min(30, soc)) })
}

export function useDeviceControl() {
  return {
    loading,
    lastError,
    sendCommand,
    toggleAcOutput,
    toggleDcOutput,
    toggleDc12vOutput,
    toggleBeeper,
    toggleXboost,
    setAcChargePower,
    setMaxChargeSoc,
    setMinDischargeSoc,
  }
}
