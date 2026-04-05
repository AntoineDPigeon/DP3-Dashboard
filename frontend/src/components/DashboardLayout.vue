<script setup lang="ts">
import { useDeviceData } from '@/composables/useDeviceData'
import ConnectionStatus from './ConnectionStatus.vue'
import BatteryCard from './BatteryCard.vue'
import PowerFlowCard from './PowerFlowCard.vue'
import TimeCard from './TimeCard.vue'
import StatusIndicators from './StatusIndicators.vue'
import OutputControls from './controls/OutputControls.vue'
import ChargingSettings from './controls/ChargingSettings.vue'
import DeviceSettings from './controls/DeviceSettings.vue'
import PowerChart from './PowerChart.vue'

const { state, recentData, fetchRecentData } = useDeviceData()
</script>

<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <h1>Delta Pro 3 Dashboard</h1>
      <ConnectionStatus :state="state" />
    </header>

    <div class="grid">
      <BatteryCard :state="state" />
      <PowerFlowCard :state="state" />
      <TimeCard :state="state" />
      <StatusIndicators :state="state" />
    </div>

    <h2 class="section-title">Controls</h2>
    <div class="grid grid-3">
      <OutputControls :state="state" />
      <ChargingSettings :state="state" />
      <DeviceSettings :state="state" />
    </div>

    <h2 class="section-title">Power History (last 30 min)</h2>
    <PowerChart :data="recentData" @refresh="fetchRecentData" />
  </div>
</template>

<style scoped>
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.dashboard-header h1 {
  font-size: 1.5rem;
  font-weight: 600;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.grid-3 {
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

.section-title {
  font-size: 1.1rem;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 12px;
}
</style>
