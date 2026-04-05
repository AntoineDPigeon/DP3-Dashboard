<script setup lang="ts">
import DashboardLayout from './components/DashboardLayout.vue'
</script>

<template>
  <DashboardLayout />
</template>

<style>
:root {
  --bg-primary: #0f1419;
  --bg-card: #1a1f2e;
  --bg-card-hover: #222838;
  --text-primary: #e4e6eb;
  --text-secondary: #8b949e;
  --accent-green: #3fb950;
  --accent-blue: #58a6ff;
  --accent-orange: #d29922;
  --accent-red: #f85149;
  --accent-purple: #bc8cff;
  --border-color: #30363d;
  --radius: 12px;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  min-height: 100vh;
}

#app {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}
</style>
