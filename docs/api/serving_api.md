# Manta Serving Engine API Specification

## Endpoints

### 1. `POST /v1/models/predict`

Executes synchronous, dynamically-batched model inference.

#### Request Body
```json
{
  "model_name": "fraud_detector",
  "version": "v1.2.0",
  "inputs": {
    "features": [0.85, 12.4, 1.02, 33.0]
  }
}
```

#### Response (200 OK)
```json
{
  "request_id": "req_ab4839f",
  "model_name": "fraud_detector",
  "model_version": "v1.2.0",
  "latency_ms": 1.24,
  "outputs": {
    "prediction": [0.942],
    "class": 1
  },
  "status_code": 200
}
```
