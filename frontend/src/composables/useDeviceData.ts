import { ref, onMounted, onUnmounted } from 'vue'
import type { DeviceState, RecentDataPoint, WsMessage } from '@/types/device'

const state = ref<Partial<DeviceState>>({
  connection_status: 'disconnected',
  online: false,
  last_updated: null,
})

const recentData = ref<RecentDataPoint[]>([])
let ws: WebSocket | null = null
let reconnectTimer: ReturnType<typeof setTimeout> | null = null
let reconnectDelay = 1000
const MAX_RECONNECT_DELAY = 30000

function getWsUrl(): string {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${protocol}//${window.location.host}/ws/device`
}

function connect() {
  if (ws && (ws.readyState === WebSocket.CONNECTING || ws.readyState === WebSocket.OPEN)) {
    return
  }

  ws = new WebSocket(getWsUrl())

  ws.onopen = () => {
    console.log('WebSocket connected')
    reconnectDelay = 1000
  }

  ws.onmessage = (event) => {
    try {
      const msg: WsMessage = JSON.parse(event.data)
      if (msg.type === 'state') {
        state.value = { ...state.value, ...msg.data } as Partial<DeviceState>
      } else if (msg.type === 'connection') {
        state.value.connection_status = msg.data.status as DeviceState['connection_status']
      } else if (msg.type === 'status') {
        state.value.online = msg.data.online as boolean
      }
    } catch (e) {
      console.error('Failed to parse WS message:', e)
    }
  }

  ws.onclose = () => {
    console.log('WebSocket disconnected, reconnecting...')
    scheduleReconnect()
  }

  ws.onerror = (err) => {
    console.error('WebSocket error:', err)
    ws?.close()
  }
}

function scheduleReconnect() {
  if (reconnectTimer) return
  reconnectTimer = setTimeout(() => {
    reconnectTimer = null
    reconnectDelay = Math.min(reconnectDelay * 2, MAX_RECONNECT_DELAY)
    connect()
    // Also fetch snapshot on reconnect
    fetchSnapshot()
  }, reconnectDelay)
}

async function fetchSnapshot() {
  try {
    const resp = await fetch('/api/device/status')
    if (resp.ok) {
      const data = await resp.json()
      state.value = { ...state.value, ...data } as Partial<DeviceState>
    }
  } catch {
    // Will retry on next reconnect
  }
}

async function fetchRecentData() {
  try {
    const resp = await fetch('/api/device/recent')
    if (resp.ok) {
      recentData.value = await resp.json()
    }
  } catch {
    // Non-critical
  }
}

export function useDeviceData() {
  onMounted(() => {
    connect()
    fetchRecentData()
  })

  onUnmounted(() => {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
  })

  return {
    state,
    recentData,
    fetchRecentData,
  }
}
