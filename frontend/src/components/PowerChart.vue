<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import type { RecentDataPoint } from '@/types/device'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const props = defineProps<{ data: RecentDataPoint[] }>()
const emit = defineEmits<{ refresh: [] }>()

let refreshInterval: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  refreshInterval = setInterval(() => emit('refresh'), 10000)
})

onUnmounted(() => {
  if (refreshInterval) clearInterval(refreshInterval)
})

const chartData = computed(() => {
  const labels = props.data.map((d) => {
    const date = new Date(d.timestamp * 1000)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  })

  return {
    labels,
    datasets: [
      {
        label: 'Input (W)',
        data: props.data.map((d) => d.watts_in ?? 0),
        borderColor: '#3fb950',
        backgroundColor: 'rgba(63, 185, 80, 0.1)',
        fill: true,
        tension: 0.3,
        pointRadius: 0,
        borderWidth: 2,
      },
      {
        label: 'Output (W)',
        data: props.data.map((d) => d.watts_out ?? 0),
        borderColor: '#58a6ff',
        backgroundColor: 'rgba(88, 166, 255, 0.1)',
        fill: true,
        tension: 0.3,
        pointRadius: 0,
        borderWidth: 2,
      },
    ],
  }
})

const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index' as const,
    intersect: false,
  },
  plugins: {
    legend: {
      labels: { color: '#8b949e' },
    },
  },
  scales: {
    x: {
      ticks: { color: '#8b949e', maxTicksLimit: 10 },
      grid: { color: 'rgba(48, 54, 61, 0.5)' },
    },
    y: {
      ticks: { color: '#8b949e' },
      grid: { color: 'rgba(48, 54, 61, 0.5)' },
      beginAtZero: true,
    },
  },
})
</script>

<template>
  <div class="chart-card">
    <div class="chart-container">
      <Line
        v-if="data.length > 0"
        :data="chartData"
        :options="chartOptions"
      />
      <div v-else class="no-data">
        No power data yet. Data will appear as the device reports.
      </div>
    </div>
  </div>
</template>

<style scoped>
.chart-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 20px;
}

.chart-container {
  height: 300px;
}

.no-data {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-secondary);
  font-size: 0.9rem;
}
</style>
