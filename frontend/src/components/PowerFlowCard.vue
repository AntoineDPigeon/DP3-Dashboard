<script setup lang="ts">
import { computed } from 'vue'
import type { DeviceState } from '@/types/device'

const props = defineProps<{ state: Partial<DeviceState> }>()

const fmt = (v: number | null | undefined) => v != null ? `${Math.round(v as number)} W` : '-- W'

const inputs = computed(() => [
  { label: 'Total In', value: fmt(props.state['power_input.watts_in_sum']), icon: '>>>' },
  { label: 'AC In', value: fmt(props.state['power_input.ac_in_watts']), icon: 'AC' },
  { label: 'Solar', value: fmt(props.state['power_input.solar_in_watts']), icon: 'PV' },
  { label: 'Solar HV', value: fmt(props.state['power_input.solar_hv_watts']), icon: 'HV' },
  { label: 'Solar LV', value: fmt(props.state['power_input.solar_lv_watts']), icon: 'LV' },
  { label: 'DC In', value: fmt(props.state['power_input.dc_in_watts']), icon: 'DC' },
])

const outputs = computed(() => [
  { label: 'Total Out', value: fmt(props.state['power_output.watts_out_sum']), icon: '<<<' },
  { label: 'AC Out', value: fmt(props.state['power_output.ac_out_watts']), icon: 'AC' },
  { label: 'DC Out', value: fmt(props.state['power_output.dc_out_watts']), icon: 'DC' },
  { label: 'USB-C 1', value: fmt(props.state['power_output.usbc_watts_1']), icon: 'C1' },
  { label: 'USB-C 2', value: fmt(props.state['power_output.usbc_watts_2']), icon: 'C2' },
  { label: 'QC USB 1', value: fmt(props.state['power_output.qc_usb_watts_1']), icon: 'Q1' },
  { label: 'QC USB 2', value: fmt(props.state['power_output.qc_usb_watts_2']), icon: 'Q2' },
  { label: '12V DC', value: fmt(props.state['power_output.dc_12v_watts']), icon: '12' },
])
</script>

<template>
  <div class="card">
    <h3>Power Flow</h3>
    <div class="flow-grid">
      <div class="flow-column input">
        <h4>Input</h4>
        <div v-for="item in inputs" :key="item.label" class="flow-item">
          <span class="flow-icon">{{ item.icon }}</span>
          <span class="flow-label">{{ item.label }}</span>
          <span class="flow-value">{{ item.value }}</span>
        </div>
      </div>
      <div class="flow-column output">
        <h4>Output</h4>
        <div v-for="item in outputs" :key="item.label" class="flow-item">
          <span class="flow-icon">{{ item.icon }}</span>
          <span class="flow-label">{{ item.label }}</span>
          <span class="flow-value">{{ item.value }}</span>
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

.flow-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.flow-column h4 {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-bottom: 8px;
  text-transform: uppercase;
}

.input h4 { color: var(--accent-green); }
.output h4 { color: var(--accent-blue); }

.flow-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  font-size: 0.85rem;
}

.flow-icon {
  width: 24px;
  text-align: center;
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--text-secondary);
  background: var(--bg-primary);
  padding: 2px 4px;
  border-radius: 4px;
}

.flow-label {
  flex: 1;
  color: var(--text-secondary);
}

.flow-value {
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}
</style>
