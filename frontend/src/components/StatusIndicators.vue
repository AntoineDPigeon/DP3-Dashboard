<script setup lang="ts">
import { computed } from 'vue'
import type { DeviceState } from '@/types/device'

const props = defineProps<{ state: Partial<DeviceState> }>()

interface Indicator {
  label: string
  key: string
  activeColor: string
}

const indicators = computed<Indicator[]>(() => [
  { label: 'AC Input', key: 'status.ac_in_connected', activeColor: 'var(--accent-green)' },
  { label: 'Solar Input', key: 'status.solar_in_connected', activeColor: 'var(--accent-green)' },
  { label: 'DC Input', key: 'status.dc_in_connected', activeColor: 'var(--accent-green)' },
  { label: 'Charging', key: 'status.is_charging', activeColor: 'var(--accent-green)' },
  { label: 'Discharging', key: 'status.is_discharging', activeColor: 'var(--accent-blue)' },
  { label: 'AC Output', key: 'status.ac_out_enabled', activeColor: 'var(--accent-blue)' },
  { label: 'DC Output', key: 'status.dc_out_enabled', activeColor: 'var(--accent-blue)' },
  { label: '12V DC Out', key: 'status.dc_12v_out_enabled', activeColor: 'var(--accent-blue)' },
  { label: 'Battery Low', key: 'status.battery_low', activeColor: 'var(--accent-red)' },
  { label: 'Battery Full', key: 'status.battery_full', activeColor: 'var(--accent-green)' },
  { label: 'Over Temp', key: 'status.over_temperature', activeColor: 'var(--accent-red)' },
  { label: 'X-Boost', key: 'status.xboost_enabled', activeColor: 'var(--accent-purple)' },
  { label: 'Beeper', key: 'status.beeper_enabled', activeColor: 'var(--accent-purple)' },
])

function isActive(key: string): boolean {
  return !!props.state[key]
}
</script>

<template>
  <div class="card">
    <h3>Status</h3>
    <div class="indicators">
      <div
        v-for="ind in indicators"
        :key="ind.key"
        class="indicator"
        :class="{ active: isActive(ind.key) }"
      >
        <span
          class="led"
          :style="{ background: isActive(ind.key) ? ind.activeColor : 'var(--border-color)' }"
        ></span>
        <span class="ind-label">{{ ind.label }}</span>
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

.indicators {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 8px;
}

.indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  border-radius: 6px;
  background: var(--bg-primary);
  font-size: 0.8rem;
  transition: opacity 0.2s;
}

.indicator:not(.active) {
  opacity: 0.5;
}

.led {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.ind-label {
  color: var(--text-primary);
}
</style>
