# DP3-Dashboard

Real-time monitoring and control dashboard for the EcoFlow Delta Pro 3 portable power station.

## Architecture

**Hybrid REST + MQTT** approach using the EcoFlow public Developer API:

- **MQTT** for real-time sensor updates (subscribes to `/open/{user}/{sn}/quota`)
- **MQTT** for device commands (publishes to `/open/{user}/{sn}/set`, listens on `/set_reply`)
- **REST** for initial state loading, MQTT credential certification, and fallback polling

### Stack
- **Backend**: Python FastAPI + paho-mqtt + httpx
- **Frontend**: Vue 3 + TypeScript + Vite + Chart.js

### Data Flow
```
EcoFlow Cloud MQTT ──> Backend (paho-mqtt) ──> asyncio.Queue ──> DeviceStore ──> WebSocket ──> Vue Frontend
EcoFlow Cloud REST <── Backend (httpx)      (fallback polling + initial load + certification)
Vue Frontend ──> REST POST /api/device/command ──> Backend ──> MQTT publish /set ──> EcoFlow Cloud
```

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- EcoFlow Developer API credentials from https://developer.ecoflow.com

### 1. Configure environment
```bash
cp .env.example .env
# Edit .env with your ACCESS_KEY, SECRET_KEY, DEVICE_SN, REGION, MQTT_CLIENT_ID
```

### 2. Production (single process)

Build the frontend and let FastAPI serve everything:

```bash
cd frontend
npm install
npm run build

cd ../backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000

### 3. Development (two processes, hot-reload)
```bash
# Terminal 1 — backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend (proxies API/WS to backend)
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Features

### Monitoring (40+ sensors)
- Battery: SOC, SOH, cycles, capacity, voltage, current, temperature
- Power Input: AC, Solar (HV/LV), DC — total and per-source watts
- Power Output: AC, DC, USB-C, QC USB, 12V DC — per-port watts
- Time estimates: charge/discharge remaining
- Status indicators: 13 binary sensors (connections, charging state, alerts)
- Extra battery support (up to 2 packs)

### Controls
- Toggle: AC output, DC output, 12V DC, beeper, X-Boost
- Adjust: AC charge power (400-2900W), max charge SOC (50-100%), min discharge SOC (0-30%)

### Dashboard
- Real-time updates via WebSocket (backed by MQTT)
- Connection status indicator (MQTT Live / Reconnecting / REST Fallback)
- Rolling 30-minute power chart (input vs output)
- Dark theme UI
