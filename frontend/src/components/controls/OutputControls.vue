<script setup lang="ts">
import type { DeviceState } from '@/types/device'
import { useDeviceControl } from '@/composables/useDeviceControl'

const props = defineProps<{ state: Partial<DeviceState> }>()
const { toggleAcOutput, toggleDcOutput, toggleDc12vOutput, loading } = useDeviceControl()

interface Toggle {
  label: string
  key: string
  action: (v: boolean) => Promise<unknown>
}

const toggles: Toggle[] = [
  { label: 'AC Output', key: 'status.ac_out_enabled', action: toggleAcOutput },
  { label: 'DC Output', key: 'status.dc_out_enabled', action: toggleDcOutput },
  { label: '12V DC Output', key: 'status.dc_12v_out_enabled', action: toggleDc12vOutput },
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
    <h3>Output Controls</h3>
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
}

.toggle-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toggle-label {
  font-size: 0.9rem;
}

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

.toggle-btn.on {
  background: var(--accent-green);
}

.toggle-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

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

.toggle-btn.on .toggle-thumb {
  transform: translateX(22px);
}
</style>
