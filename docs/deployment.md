# ModelOps Deployment & Infrastructure Guide

This guide covers deploying the ModelOps platform with Docker Compose and managing infrastructure services in production.

---

## 1. Prerequisites

- **Docker**: Version 24.0+ (Docker Desktop or Linux Docker Engine)
- **Docker Compose**: Version v2.20+
- **Host Ports**:
  - `8000`: ModelOps FastAPI Inference Service
  - `3000`: React Dashboard Frontend
  - `3001`: Grafana Observability Dashboard
  - `5000`: MLflow Tracking Server
  - `5432`: PostgreSQL Database
  - `9090`: Prometheus Metrics Server

---

## 2. Quickstart with Docker Compose

1. **Clone the repository and prepare environment variables**:
   ```bash
   cp .env.example .env
   ```

2. **Build and launch all services**:
   ```bash
   docker compose up --build -d
   ```

3. **Verify running containers**:
   ```bash
   docker compose ps
   ```

4. **Verify backend readiness**:
   ```bash
   curl -f http://localhost:8000/api/v1/ready
   ```

5. **Access Service UIs**:
   - Web Dashboard: `http://localhost:3000`
   - API Interactive Docs: `http://localhost:8000/docs`
   - MLflow Tracking: `http://localhost:5000`
   - Grafana Dashboard: `http://localhost:3001` (Credentials: `admin` / `admin`)
   - Prometheus UI: `http://localhost:9090`

---

## 3. Persistent Volumes

Docker Compose creates isolated, persistent named volumes:
- `postgres_data`: Stores PostgreSQL database records (experiments, runs, versions, logs).
- `mlflow_data`: Stores MLflow metadata and configurations.
- `modelops_artifacts`: Stores trained scikit-learn pipeline `.joblib` files, JSON metadata, and Evidently HTML reports.
- `prometheus_data`: Stores scraped time-series metric samples.
- `grafana_data`: Stores dashboard configurations and state.

To reset the database and clean all volumes:
```bash
docker compose down -v
```

---

## 4. Production Security Hardening Checklist

When deploying to public cloud infrastructure (AWS ECS/EKS, GCP Cloud Run/GKE, Azure):
1. **Change Default Credentials**: Set secure database passwords and API keys in `.env`.
2. **TLS / SSL Termination**: Place an Nginx reverse proxy, AWS ALB, or Cloudflare in front of ports 8000, 3000, and 3001.
3. **Internal Subnets**: Keep PostgreSQL (5432) and MLflow (5000) within private VPC subnets.
4. **CORS Restrictions**: Update `CORS_ORIGINS` in `.env` to restrict cross-origin access strictly to your verified frontend domain.
