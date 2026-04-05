<script setup lang="ts">
import { computed } from 'vue'
import type { DeviceState } from '@/types/device'

const props = defineProps<{ state: Partial<DeviceState> }>()

const soc = computed(() => props.state['battery.soc'] ?? 0)
const soh = computed(() => props.state['battery.soh'] ?? 100)
const cycles = computed(() => props.state['battery.cycles'] ?? 0)
const fullCap = computed(() => props.state['battery.full_cap'])
const remainCap = computed(() => props.state['battery.remain_cap'])
const temp = computed(() => props.state['battery.temp'])
const voltage = computed(() => props.state['battery.voltage'])

const socColor = computed(() => {
  const v = soc.value as number
  if (v > 60) return 'var(--accent-green)'
  if (v > 20) return 'var(--accent-orange)'
  return 'var(--accent-red)'
})

const gaugeOffset = computed(() => {
  const circumference = 2 * Math.PI * 45
  return circumference - (circumference * (soc.value as number)) / 100
})
</script>

<template>
  <div class="card">
    <h3>Battery</h3>
    <div class="battery-main">
      <div class="gauge-container">
        <svg viewBox="0 0 100 100" class="gauge">
          <circle cx="50" cy="50" r="45" fill="none" stroke="var(--border-color)" stroke-width="6" />
          <circle
            cx="50" cy="50" r="45" fill="none"
            :stroke="socColor"
            stroke-width="6"
            stroke-linecap="round"
            :stroke-dasharray="2 * Math.PI * 45"
            :stroke-dashoffset="gaugeOffset"
            transform="rotate(-90 50 50)"
            class="gauge-fill"
          />
        </svg>
        <div class="gauge-text">
          <span class="soc-value">{{ Math.round(soc as number) }}</span>
          <span class="soc-unit">%</span>
        </div>
      </div>
      <div class="battery-stats">
        <div class="stat">
          <span class="stat-label">Health</span>
          <span class="stat-value">{{ soh != null ? `${Math.round(soh as number)}%` : '--' }}</span>
        </div>
        <div class="stat">
          <span class="stat-label">Cycles</span>
          <span class="stat-value">{{ cycles ?? '--' }}</span>
        </div>
        <div class="stat">
          <span class="stat-label">Capacity</span>
          <span class="stat-value">{{ remainCap != null && fullCap != null ? `${Math.round(remainCap as number)} / ${Math.round(fullCap as number)} Wh` : '--' }}</span>
        </div>
        <div class="stat">
          <span class="stat-label">Voltage</span>
          <span class="stat-value">{{ voltage != null ? `${(voltage as number).toFixed(1)} V` : '--' }}</span>
        </div>
        <div class="stat">
          <span class="stat-label">Temp</span>
          <span class="stat-value">{{ temp != null ? `${(temp as number).toFixed(1)} C` : '--' }}</span>
        </div>
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

.battery-main {
  display: flex;
  gap: 24px;
  align-items: center;
}

.gauge-container {
  position: relative;
  width: 120px;
  height: 120px;
  flex-shrink: 0;
}

.gauge { width: 100%; height: 100%; }

.gauge-fill {
  transition: stroke-dashoffset 0.5s ease;
}

.gauge-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.soc-value {
  font-size: 2rem;
  font-weight: 700;
}

.soc-unit {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.battery-stats {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat {
  display: flex;
  justify-content: space-between;
}

.stat-label {
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.stat-value {
  font-weight: 500;
  font-size: 0.85rem;
}
</style>
