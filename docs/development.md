# ModelOps Local Development Guide

This guide details setting up a local development environment without requiring Docker.

---

## 1. Local Environment Requirements

- **Python**: 3.11.x (CPython 64-bit)
- **Node.js**: v20+ or v22+
- **Package Managers**: `uv` (recommended) or standard `pip`, and `npm`

---

## 2. Setting Up Python Backend

1. **Create virtual environment**:
   ```bash
   uv venv --python 3.11 .venv
   ```

2. **Activate the environment**:
   - Windows (PowerShell):
     ```powershell
     .\.venv\Scripts\activate
     ```
   - Linux / macOS:
     ```bash
     source .venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   uv pip install --python .\.venv\Scripts\python.exe -r backend/requirements.txt
   ```

4. **Initialize database schema**:
   ```bash
   alembic upgrade head
   ```

5. **Start local backend server**:
   ```bash
   uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

---

## 3. Setting Up Frontend Dashboard

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install node dependencies**:
   ```bash
   npm install
   ```

3. **Start Vite development server**:
   ```bash
   npm run dev
   ```
   Open `http://localhost:3000` in your browser. API requests are automatically proxied to `http://localhost:8000`.

---

## 4. Running the Automated Test Suite

Run all unit, integration, and contract tests:
```bash
pytest -v tests/
```

Run tests with coverage:
```bash
pytest -v --cov=backend/app tests/
```
