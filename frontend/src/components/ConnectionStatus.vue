<script setup lang="ts">
import { computed } from 'vue'
import type { DeviceState } from '@/types/device'

const props = defineProps<{ state: Partial<DeviceState> }>()

const statusLabel = computed(() => {
  switch (props.state.connection_status) {
    case 'connected': return 'MQTT Live'
    case 'reconnecting': return 'Reconnecting...'
    case 'rest_fallback': return 'REST Fallback'
    default: return 'Disconnected'
  }
})

const statusClass = computed(() => props.state.connection_status ?? 'disconnected')

const lastUpdated = computed(() => {
  const ts = props.state.last_updated
  if (!ts) return 'No data yet'
  const d = new Date(ts * 1000)
  return d.toLocaleTimeString()
})
</script>

<template>
  <div class="connection-status">
    <span class="dot" :class="statusClass"></span>
    <span class="label">{{ statusLabel }}</span>
    <span class="separator">|</span>
    <span class="updated">Updated: {{ lastUpdated }}</span>
    <span v-if="state.online === false" class="offline-badge">Device Offline</span>
  </div>
</template>

<style scoped>
.connection-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-secondary);
}

.dot.connected { background: var(--accent-green); }
.dot.reconnecting { background: var(--accent-orange); animation: pulse 1s infinite; }
.dot.rest_fallback { background: var(--accent-orange); }
.dot.disconnected { background: var(--accent-red); }

.separator { color: var(--border-color); }

.offline-badge {
  background: var(--accent-red);
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}
</style>
