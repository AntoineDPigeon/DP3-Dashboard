<script setup lang="ts">
import { computed } from 'vue'
import type { DeviceState } from '@/types/device'

const props = defineProps<{ state: Partial<DeviceState> }>()

function formatTime(minutes: number | null | undefined): string {
  if (minutes == null || minutes <= 0) return '--'
  const h = Math.floor(minutes as number / 60)
  const m = Math.round((minutes as number) % 60)
  if (h === 0) return `${m}m`
  return `${h}h ${m}m`
}

const chgTime = computed(() => formatTime(props.state['time_estimates.chg_remain_time']))
const dsgTime = computed(() => formatTime(props.state['time_estimates.dsg_remain_time']))
const isCharging = computed(() => props.state['status.is_charging'])
</script>

<template>
  <div class="card">
    <h3>Time Remaining</h3>
    <div class="time-grid">
      <div class="time-block" :class="{ active: isCharging }">
        <span class="time-label">Charge</span>
        <span class="time-value">{{ chgTime }}</span>
      </div>
      <div class="time-block" :class="{ active: !isCharging }">
        <span class="time-label">Discharge</span>
        <span class="time-value">{{ dsgTime }}</span>
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

.time-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.time-block {
  text-align: center;
  padding: 16px;
  border-radius: 8px;
  background: var(--bg-primary);
}

.time-block.active {
  border: 1px solid var(--accent-green);
}

.time-label {
  display: block;
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-bottom: 8px;
  text-transform: uppercase;
}

.time-value {
  font-size: 1.5rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}
</style>
