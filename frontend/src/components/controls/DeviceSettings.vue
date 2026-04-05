<script setup lang="ts">
import type { DeviceState } from '@/types/device'
import { useDeviceControl } from '@/composables/useDeviceControl'

const props = defineProps<{ state: Partial<DeviceState> }>()
const { toggleBeeper, toggleXboost, loading } = useDeviceControl()

interface Toggle {
  label: string
  key: string
  action: (v: boolean) => Promise<unknown>
}

const toggles: Toggle[] = [
  { label: 'X-Boost', key: 'status.xboost_enabled', action: toggleXboost },
  { label: 'Beeper', key: 'status.beeper_enabled', action: toggleBeeper },
]

function isOn(key: string): boolean {
  return !!props.state[key]
}

function toggle(t: Toggle) {
  t.action(!isOn(t.key))
}
</script>

<template>
  <div class="card">
    <h3>Device Settings</h3>
    <div class="toggles">
      <div v-for="t in toggles" :key="t.key" class="toggle-row">
        <span class="toggle-label">{{ t.label }}</span>
        <button
          class="toggle-btn"
          :class="{ on: isOn(t.key) }"
          :disabled="loading"
          @click="toggle(t)"
        >
          <span class="toggle-thumb"></span>
        </button>
      </div>
    </div>

    <div class="info-grid">
      <div class="info-item">
        <span class="info-label">Screen Brightness</span>
        <span class="info-value">{{ props.state['settings.screen_brightness'] ?? '--' }}</span>
      </div>
      <div class="info-item">
        <span class="info-label">Standby Timeout</span>
        <span class="info-value">{{ props.state['settings.standby_timeout'] != null ? `${props.state['settings.standby_timeout']} min` : '--' }}</span>
      </div>
      <div class="info-item">
        <span class="info-label">AC Standby</span>
        <span class="info-value">{{ props.state['settings.ac_standby_timeout'] != null ? `${props.state['settings.ac_standby_timeout']} min` : '--' }}</span>
      </div>
      <div class="info-item">
        <span class="info-label">DC Standby</span>
        <span class="info-value">{{ props.state['settings.dc_standby_timeout'] != null ? `${props.state['settings.dc_standby_timeout']} min` : '--' }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 20px;
}

.card h3 {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 16px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.toggles {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.toggle-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toggle-label { font-size: 0.9rem; }

.toggle-btn {
  width: 48px;
  height: 26px;
  border-radius: 13px;
  border: none;
  background: var(--border-color);
  cursor: pointer;
  position: relative;
  transition: background 0.2s;
}

.toggle-btn.on { background: var(--accent-green); }
.toggle-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.toggle-thumb {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: white;
  transition: transform 0.2s;
}

.toggle-btn.on .toggle-thumb { transform: translateX(22px); }

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.info-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.info-value {
  font-size: 0.85rem;
  font-weight: 500;
}
</style>
