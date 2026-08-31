# Manta: Enterprise Distributed ML Systems & MLOps Platform

<div align="center">

```
  __  __             _         
 |  \/  |           | |        
 | \  / | __ _ _ __ | |_ __ _  
 | |\/| |/ _` | '_ \| __/ _` | 
 | |  | | (_| | | | | || (_| | 
 |_|  |_|\__,_|_| |_|\__\__,_| 
```

**High-Performance Distributed Machine Learning Systems & Production MLOps Engine**

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Code Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)]()
[![Lines of Code](https://img.shields.io/badge/LOC-65k%2B-blue.svg)]()
[![License](https://img.shields.io/badge/License-Proprietary-blue.svg)]()
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.14-blue.svg)]()

</div>

---

## ⚡ What is Manta?

**Manta** is a complete, production-grade **Machine Learning Systems** platform designed to solve the critical infrastructure and systems challenges of modern machine learning:
1. **Sub-millisecond inference latency & high throughput** via adaptive dynamic request batching.
2. **Dual-tier feature management** ensuring zero temporal data leakage during training/serving.
3. **Distributed model training & HPO** utilizing Ring-AllReduce, Parameter Servers, and Bayesian Optimization.
4. **Real-time distribution monitoring** evaluating multivariate drift (KS-test, Wasserstein, PSI).
5. **Model governance & lineage tracking** with automated ML Bill-of-Materials (ML-BOM).
6. **Declarative workflow orchestration** executing Directed Acyclic Graphs (DAGs) in topological order.

---

## 🏛️ ML Systems Architecture

```
                                  ┌────────────────────────────────────────┐
                                  │   Web Dashboard & CLI (Port 3000/8000)  │
                                  └───────────────────┬────────────────────┘
                                                      │
                                                      ▼
                                  ┌────────────────────────────────────────┐
                                  │    Control Plane Gateway & Auth        │
                                  │  (FastAPI REST + JWT + Rate Limiter)   │
                                  └───────────────────┬────────────────────┘
                                                      │
         ┌────────────────────────────────────────────┼────────────────────────────────────────────┐
         ▼                                            ▼                                            ▼
┌───────────────────────────┐            ┌───────────────────────────┐            ┌───────────────────────────┐
│   Feature Store Engine    │            │    Distributed Training   │            │   High-Throughput Serving │
│ ───────────────────────── │            │ ───────────────────────── │            │ ───────────────────────── │
│ • In-Memory / Redis Online│            │ • Ring-AllReduce Kernels  │            │ • Adaptive Dynamic Batcher│
│ • Parquet Analytical Store│            │ • Parameter Server Coords │            │ • Multi-Backend Workers   │
│ • Point-In-Time Temporal  │            │ • Bayesian & Hyperband HPO│            │ • SSE / Token Streaming   │
└─────────────┬─────────────┘            └─────────────┬─────────────┘            └─────────────┬─────────────┘
              │                                        │                                        │
              └────────────────────────────────────────┼────────────────────────────────────────┘
                                                       ▼
                                         ┌───────────────────────────┐
                                         │  Model Registry & Monitor │
                                         │ ───────────────────────── │
                                         │ • Model Lifecycle States  │
                                         │ • KS / PSI / Wasserstein  │
                                         │ • Lineage Graph & ML-BOM  │
                                         └───────────────────────────┘
```

---

## 🚀 Running the Project

### 1. Prerequisites & Installation
Ensure Python 3.10+ and Node.js 18+ are installed.
```bash
# Clone the repository
git clone https://github.com/Chandravamsi09/Manta.git
cd Manta

# Install Python backend dependencies
py -m pip install -e .
```

### 2. Start the Backend ML Server (Port 8000)
```bash
py main.py
```
*The backend API and unified control dashboard will be live at `http://localhost:8000`.*

### 3. Start the Frontend UI Dashboard (Port 3000)
```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 3000
```
*The React UI will be live at `http://localhost:3000`.*

---

## 🔐 Authentication Credentials
The platform includes enterprise session-token authentication:
- **Username**: `admin`
- **Password**: `admin123` (or API Key: `manta-admin-key-2026`)

---

## 🎯 Running the Complete End-to-End Demo Flow

You can run the end-to-end ML systems workflow directly from the UI or via API:

### Option A: From Web UI
1. Navigate to **`http://localhost:3000`** (or **`http://localhost:8000`**).
2. Sign in with `admin` / `admin123`.
3. Click the **"E2E Workflow Demo"** tab.
4. Click **"▶ Run Complete Demo Flow"**.
5. Watch the live progression across all 4 stages:
   - **Step 1 (Feature Store)**: Ingest & fetch customer `u1001` online feature vector.
   - **Step 2 (Serving & Dynamic Batching)**: Serve model `fraud_detector:v1.2` with microsecond latency.
   - **Step 3 (Drift Monitoring)**: Compute Kolmogorov-Smirnov & Wasserstein drift metrics against baseline.
   - **Step 4 (Pipeline DAG)**: Execute automated continuous retraining DAG in topological order.

### Option B: Via Python CLI / Script
```python
import manta
client = manta.Client("http://localhost:8000")

# 1. Feature Store Lookup
features = client.feature_store.get_online_features("user_stats", ["u1001"])

# 2. Dynamic Batch Prediction
pred = client.serving.predict("fraud_detector", inputs={"features": [0.85, 14.0, 0.08, 1.0]}, version="v1.2")
print("Prediction:", pred)
```

---

## 🧪 Running Automated Tests

Manta contains 44 test suites covering unit algorithms, integration lifecycles, and stress benchmarks:
```bash
py -m pytest tests/ -v -p no:cacheprovider
```

---

## 📦 Project Structure
- `manta/core/` — High-performance Tensor primitives, memory pools, and storage backends.
- `manta/feature_store/` — Dual-tier online/offline feature store & point-in-time join engine.
- `manta/training/` — Distributed training coordinator, Ring All-Reduce kernels, Bayesian HPO.
- `manta/serving/` — Dynamic batching inference server, multi-backend workers, SSE streaming.
- `manta/monitoring/` — Multivariate drift detectors (KS, PSI, Wasserstein, Embedding drift).
- `manta/registry/` — Model registry, lifecycle state machine, ML-BOM generator, and lineage DAG.
- `manta/pipeline/` — Declarative DAG workflow compiler and topological executor.
- `manta/gateway/` — FastAPI REST control plane, rate limiting, and telemetry exporter.
- `frontend/` — React 18, TypeScript, Tailwind CSS monitoring dashboard & DAG visualizer.
- `tests/` — Comprehensive test suites (unit, integration, stress benchmarks).

---

## 📄 License
Proprietary — All rights reserved.
