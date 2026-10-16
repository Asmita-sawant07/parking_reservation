# DevOps Pipeline for a Parking Reservation System
## Phase 1: Application & Containerization

A lightweight, beginner-friendly Flask REST API for managing parking slots, reservations, and monitoring metrics, designed as the foundation for an automated CI/CD DevOps pipeline.

---

## 📋 Overview & Features

- **Health Check (`GET /`)**: Service liveness and metadata verification.
- **Parking Slots (`GET /slots`)**: View all parking slots with total, available, and occupied counters. Supports status filtering (`?status=available` or `?status=occupied`).
- **Reservations (`GET /reservations` & `POST /reservations`)**: List active reservations or book an available slot with payload validation and conflict protection.
- **Metrics (`GET /metrics`)**: Exposes Prometheus-compatible metrics (`parking_api_http_requests_total`, `parking_available_slots`, etc.) ready for future Prometheus/Grafana monitoring.
- **Automated Testing**: 100% test coverage of all core endpoints using `pytest`.
- **Docker Ready**: Production-grade, lightweight container configuration running Python on port 5000 with debug mode disabled.

---

## 📁 Project Structure

```text
parking_reservation/
├── .dockerignore          # Excludes unnecessary files from Docker build context
├── .gitignore             # Excludes cache, venv, and OS metadata from Git
├── Dockerfile             # Container blueprint for Python 3.11-slim
├── README.md              # Project documentation and command guide
├── app.py                 # Core Flask REST API application
├── requirements.txt       # Project dependencies (Flask, pytest)
└── tests/
    ├── __init__.py        # Test package marker
    └── test_app.py        # Automated test suite for endpoints and validation
```

---

## 🛠️ Prerequisites (macOS Apple Silicon)

- **macOS** with Apple Silicon (M1/M2/M3/M4)
- **Python 3.11+** (or Python 3.14)
- **Docker Desktop for Mac** (running)
- Terminal (zsh) or VS Code Integrated Terminal

---

## 🚀 Local Setup & Testing Commands (macOS)

### 1. Activate the Virtual Environment

From the root project directory:
```bash
source .venv/bin/activate
```
*(Your terminal prompt should now show `(.venv)`).*

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Automated Tests

Execute the automated test suite with verbose output:
```bash
pytest -v
```

Expected output:
```text
tests/test_app.py::test_health_check_endpoint PASSED
tests/test_app.py::test_get_slots_default PASSED
tests/test_app.py::test_filter_slots_available PASSED
tests/test_app.py::test_filter_slots_occupied PASSED
tests/test_app.py::test_get_reservations PASSED
tests/test_app.py::test_create_reservation_success PASSED
tests/test_app.py::test_create_reservation_already_occupied PASSED
tests/test_app.py::test_create_reservation_missing_fields PASSED
tests/test_app.py::test_create_reservation_slot_not_found PASSED
tests/test_app.py::test_metrics_prometheus_format PASSED
tests/test_app.py::test_metrics_json_format PASSED
tests/test_app.py::test_not_found_handler PASSED
```

### 4. Start the Application Locally

```bash
python app.py
```
The server will start listening on `http://0.0.0.0:5000`.

### 5. Test API Endpoints (in a new Terminal tab)

```bash
# 1. Health check
curl http://127.0.0.1:5000/

# 2. View all parking slots
curl http://127.0.0.1:5000/slots

# 3. Filter available slots only
curl "http://127.0.0.1:5000/slots?status=available"

# 4. View existing reservations
curl http://127.0.0.1:5000/reservations

# 5. Book an available parking slot (Slot ID 1)
curl -X POST http://127.0.0.1:5000/reservations \
  -H "Content-Type: application/json" \
  -d '{"slot_id": 1, "vehicle_number": "KA-05-MN-9999", "driver_name": "Rohan Mehra"}'

# 6. View Prometheus metrics
curl http://127.0.0.1:5000/metrics

# 7. View metrics in JSON format
curl "http://127.0.0.1:5000/metrics?format=json"
```

To stop the local server, press `Ctrl + C` in the running terminal.

---

## 🐳 Docker Build & Run Guide

Make sure Docker Desktop is open and running on your Mac.

### 1. Build the Docker Image
```bash
docker build -t parking-reservation-app:v1 .
```

### 2. Run the Container
```bash
docker run -d --name parking-app -p 5000:5000 parking-reservation-app:v1
```

### 3. Check Container Status and Logs
```bash
# Check if container is running
docker ps

# View application logs
docker logs parking-app
```

### 4. Verify Endpoints on the Running Container
```bash
curl http://127.0.0.1:5000/
curl http://127.0.0.1:5000/slots
curl http://127.0.0.1:5000/metrics
```

### 5. Stop and Clean Up Container
```bash
# Stop the container
docker stop parking-app

# Remove the container
docker rm parking-app
```

---

## 📡 API Reference

| Method | Endpoint | Description | Sample Query / Body |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | API Health and service info | None |
| `GET` | `/slots` | List parking slots & counts | `?status=available` or `?status=occupied` |
| `GET` | `/reservations` | List all active reservations | None |
| `POST` | `/reservations` | Create a new reservation | `{"slot_id": 1, "vehicle_number": "...", "driver_name": "..."}` |
| `GET` | `/metrics` | Prometheus metrics scrape | `?format=json` (optional) |

---

## 💡 macOS Troubleshooting

- **Port 5000 In Use Error (macOS AirPlay)**:
  On some macOS versions (Monterey, Ventura, Sonoma, Sequoia), the system AirPlay Receiver might bind to port 5000.
  - *Fix A*: Open **System Settings** > **General** > **AirDrop & AirPlay** and toggle **AirPlay Receiver** off.
  - *Fix B*: Run the app on another port:
    ```bash
    PORT=5001 python app.py
    ```
    Or with Docker:
    ```bash
    docker run -d --name parking-app -p 5001:5000 parking-reservation-app:v1
    ```
- **Permission issues**:
  Ensure Docker Desktop has permission to access your local workspace.
