.PHONY: install install-backend install-frontend build dev prod clean help

# Default target
help:
	@echo "DP3 Dashboard"
	@echo ""
	@echo "  make install    Install all dependencies (backend + frontend)"
	@echo "  make build      Build frontend for production"
	@echo "  make prod       Build frontend + start backend (single process)"
	@echo "  make dev        Start backend + frontend dev server (hot-reload)"
	@echo "  make clean      Remove build artifacts and caches"
	@echo ""

# ── Install ──────────────────────────────────────────────────────────

install: install-backend install-frontend

install-backend:
	cd backend && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

# ── Build ────────────────────────────────────────────────────────────

build: install-frontend
	cd frontend && npm run build

# ── Run ──────────────────────────────────────────────────────────────

prod: build
	cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000

dev:
	@echo "Starting backend and frontend..."
	@trap 'kill 0' EXIT; \
	cd backend && uvicorn app.main:app --reload --port 8000 & \
	cd frontend && npm run dev & \
	wait

# ── Clean ────────────────────────────────────────────────────────────

clean:
	rm -rf frontend/dist frontend/node_modules/.vite
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
