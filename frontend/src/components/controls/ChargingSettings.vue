<script setup lang="ts">
import { ref, watch } from 'vue'
import type { DeviceState } from '@/types/device'
import { useDeviceControl } from '@/composables/useDeviceControl'

const props = defineProps<{ state: Partial<DeviceState> }>()
const { setAcChargePower, setMaxChargeSoc, setMinDischargeSoc, loading } = useDeviceControl()

const chargePower = ref(1800)
const maxSoc = ref(100)
const minSoc = ref(0)

// Sync from device state
watch(() => props.state['settings.ac_charge_watts'], (v) => { if (v != null) chargePower.value = v as number })
watch(() => props.state['settings.max_charge_soc'], (v) => { if (v != null) maxSoc.value = v as number })
watch(() => props.state['settings.min_discharge_soc'], (v) => { if (v != null) minSoc.value = v as number })

let debounceTimer: ReturnType<typeof setTimeout> | null = null

function debounceApply(fn: () => void) {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(fn, 500)
}
</script>

<template>
  <div class="card">
    <h3>Charging Settings</h3>
    <div class="settings">
      <div class="setting">
        <div class="setting-header">
          <span>AC Charge Power</span>
          <span class="setting-value">{{ chargePower }} W</span>
        </div>
        <input
          type="range"
          :min="400"
          :max="2900"
          :step="100"
          v-model.number="chargePower"
          :disabled="loading"
          @change="debounceApply(() => setAcChargePower(chargePower))"
        />
      </div>

      <div class="setting">
        <div class="setting-header">
          <span>Max Charge Level</span>
          <span class="setting-value">{{ maxSoc }}%</span>
        </div>
        <input
          type="range"
          :min="50"
          :max="100"
          :step="5"
          v-model.number="maxSoc"
          :disabled="loading"
          @change="debounceApply(() => setMaxChargeSoc(maxSoc))"
        />
      </div>

      <div class="setting">
        <div class="setting-header">
          <span>Min Discharge Level</span>
          <span class="setting-value">{{ minSoc }}%</span>
        </div>
        <input
          type="range"
          :min="0"
          :max="30"
          :step="5"
          v-model.number="minSoc"
          :disabled="loading"
          @change="debounceApply(() => setMinDischargeSoc(minSoc))"
        />
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

.settings {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.setting-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 0.85rem;
}

.setting-value {
  font-weight: 600;
  color: var(--accent-blue);
}

input[type="range"] {
  width: 100%;
  height: 6px;
  -webkit-appearance: none;
  appearance: none;
  background: var(--border-color);
  border-radius: 3px;
  outline: none;
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--accent-blue);
  cursor: pointer;
}

input[type="range"]:disabled {
  opacity: 0.5;
}
</style>
