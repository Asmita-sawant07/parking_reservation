"""
Automated unit and integration tests for Parking Reservation System API.
"""

import pytest
from app import app, reset_state


@pytest.fixture
def client():
    """Create a test client with isolated state for each test run."""
    app.config["TESTING"] = True
    reset_state()
    with app.test_client() as client:
        yield client
    reset_state()


def test_health_check_endpoint(client):
    """Verify GET / returns 200 and healthy status metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert "Parking Reservation System API" in data["service"]
    assert data["version"] == "1.0.0"
    assert "endpoints" in data


def test_get_slots_default(client):
    """Verify GET /slots returns list of slots with occupancy statistics."""
    response = client.get("/slots")
    assert response.status_code == 200
    data = response.get_json()
    assert data["total_slots"] == 6
    assert data["available_slots"] == 4
    assert data["occupied_slots"] == 2
    assert len(data["slots"]) == 6


def test_filter_slots_available(client):
    """Verify GET /slots?status=available returns only available slots."""
    response = client.get("/slots?status=available")
    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] == 4
    for slot in data["slots"]:
        assert slot["is_occupied"] is False


def test_filter_slots_occupied(client):
    """Verify GET /slots?status=occupied returns only occupied slots."""
    response = client.get("/slots?status=occupied")
    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] == 2
    for slot in data["slots"]:
        assert slot["is_occupied"] is True


def test_get_reservations(client):
    """Verify GET /reservations returns current list of reservations."""
    response = client.get("/reservations")
    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] == 2
    assert len(data["reservations"]) == 2
    assert data["reservations"][0]["vehicle_number"] == "KA-01-AB-1234"


def test_create_reservation_success(client):
    """Verify POST /reservations books an available slot successfully."""
    payload = {
        "slot_id": 1,
        "vehicle_number": "DL-05-XY-9999",
        "driver_name": "Vikram Singh",
    }
    response = client.post("/reservations", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "Reservation created successfully."
    assert data["reservation"]["slot_id"] == 1
    assert data["reservation"]["vehicle_number"] == "DL-05-XY-9999"

    # Verify that slot 1 is now occupied
    slots_resp = client.get("/slots")
    slots_data = slots_resp.get_json()
    slot_1 = next(s for s in slots_data["slots"] if s["id"] == 1)
    assert slot_1["is_occupied"] is True
    assert slots_data["available_slots"] == 3


def test_create_reservation_already_occupied(client):
    """Verify booking an already occupied slot returns 409 Conflict."""
    payload = {
        "slot_id": 2,  # Slot 2 is occupied in initial state
        "vehicle_number": "MH-12-PQ-0001",
        "driver_name": "Test Driver",
    }
    response = client.post("/reservations", json=payload)
    assert response.status_code == 409
    data = response.get_json()
    assert data["error"] == "Conflict"


def test_create_reservation_missing_fields(client):
    """Verify missing required fields returns 400 Bad Request."""
    payload = {"slot_id": 1}
    response = client.post("/reservations", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Bad Request"


def test_create_reservation_slot_not_found(client):
    """Verify booking a non-existent slot returns 404 Not Found."""
    payload = {
        "slot_id": 9999,
        "vehicle_number": "UP-16-ZZ-1234",
        "driver_name": "Test Driver",
    }
    response = client.post("/reservations", json=payload)
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "Not Found"


def test_metrics_prometheus_format(client):
    """Verify GET /metrics returns standard Prometheus text format."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.content_type
    content = response.data.decode("utf-8")
    assert "parking_api_http_requests_total" in content
    assert "parking_total_slots 6" in content
    assert "parking_available_slots 4" in content
    assert "parking_occupied_slots 2" in content
    assert "parking_active_reservations 2" in content
    assert "parking_api_up 1" in content


def test_metrics_json_format(client):
    """Verify GET /metrics?format=json returns valid JSON object."""
    response = client.get("/metrics?format=json")
    assert response.status_code == 200
    assert "application/json" in response.content_type
    data = response.get_json()
    assert data["parking_total_slots"] == 6
    assert data["parking_available_slots"] == 4
    assert data["parking_occupied_slots"] == 2
    assert data["parking_api_up"] == 1


def test_not_found_handler(client):
    """Verify non-existent routes return 404 JSON response."""
    response = client.get("/non-existent-route")
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "Not Found"
