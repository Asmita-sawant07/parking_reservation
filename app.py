"""
Parking Reservation System - Flask REST API
Phase 1: DevOps Pipeline College Project

This service provides RESTful endpoints to check API health,
manage parking slot availability, view reservations, and expose
system metrics for Prometheus monitoring.
"""

from datetime import datetime, timezone
import os
from flask import Flask, jsonify, request, Response

app = Flask(__name__)

# Request counter for Prometheus metric monitoring
TOTAL_REQUESTS = 0

# Sample in-memory parking slots dataset
INITIAL_SLOTS = [
    {
        "id": 1,
        "slot_number": "A-101",
        "floor": 1,
        "slot_type": "standard",
        "is_occupied": False,
    },
    {
        "id": 2,
        "slot_number": "A-102",
        "floor": 1,
        "slot_type": "compact",
        "is_occupied": True,
    },
    {
        "id": 3,
        "slot_number": "B-201",
        "floor": 2,
        "slot_type": "ev",
        "is_occupied": False,
    },
    {
        "id": 4,
        "slot_number": "B-202",
        "floor": 2,
        "slot_type": "standard",
        "is_occupied": False,
    },
    {
        "id": 5,
        "slot_number": "C-301",
        "floor": 3,
        "slot_type": "accessible",
        "is_occupied": True,
    },
    {
        "id": 6,
        "slot_number": "C-302",
        "floor": 3,
        "slot_type": "standard",
        "is_occupied": False,
    },
]

# Sample in-memory reservations dataset
INITIAL_RESERVATIONS = [
    {
        "id": 1,
        "slot_id": 2,
        "slot_number": "A-102",
        "vehicle_number": "KA-01-AB-1234",
        "driver_name": "Rahul Sharma",
        "start_time": "2026-10-16T10:00:00Z",
        "status": "ACTIVE",
    },
    {
        "id": 2,
        "slot_id": 5,
        "slot_number": "C-301",
        "vehicle_number": "MH-02-CD-5678",
        "driver_name": "Anita Desai",
        "start_time": "2026-10-16T11:30:00Z",
        "status": "ACTIVE",
    },
]

# Active runtime state
parking_slots = [slot.copy() for slot in INITIAL_SLOTS]
reservations = [res.copy() for res in INITIAL_RESERVATIONS]


def reset_state():
    """Reset in-memory data to initial state. Useful for test isolation."""
    global parking_slots, reservations, TOTAL_REQUESTS
    parking_slots = [slot.copy() for slot in INITIAL_SLOTS]
    reservations = [res.copy() for res in INITIAL_RESERVATIONS]
    TOTAL_REQUESTS = 0


@app.before_request
def count_requests():
    """Increment global request counter for every incoming request."""
    global TOTAL_REQUESTS
    TOTAL_REQUESTS += 1


@app.route("/", methods=["GET"])
def health_check():
    """
    Endpoint 1: Health check
    Returns the status and service metadata.
    """
    return (
        jsonify(
            {
                "status": "healthy",
                "service": "Parking Reservation System API",
                "version": "1.0.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "endpoints": {
                    "health": "GET /",
                    "slots": "GET /slots",
                    "reservations": "GET /reservations",
                    "metrics": "GET /metrics",
                },
            }
        ),
        200,
    )


@app.route("/slots", methods=["GET"])
def get_slots():
    """
    Endpoint 2: List parking slots and availability.
    Supports optional query filter: ?status=available or ?status=occupied
    """
    status_filter = request.args.get("status", "").strip().lower()

    if status_filter == "available":
        filtered_slots = [s for s in parking_slots if not s["is_occupied"]]
    elif status_filter == "occupied":
        filtered_slots = [s for s in parking_slots if s["is_occupied"]]
    else:
        filtered_slots = parking_slots

    total_slots = len(parking_slots)
    occupied_slots = sum(1 for s in parking_slots if s["is_occupied"])
    available_slots = total_slots - occupied_slots

    return (
        jsonify(
            {
                "total_slots": total_slots,
                "available_slots": available_slots,
                "occupied_slots": occupied_slots,
                "count": len(filtered_slots),
                "slots": filtered_slots,
            }
        ),
        200,
    )


@app.route("/reservations", methods=["GET"])
def get_reservations():
    """
    Endpoint 3: List reservations.
    Returns all existing parking reservations.
    """
    return (
        jsonify(
            {
                "count": len(reservations),
                "reservations": reservations,
            }
        ),
        200,
    )


@app.route("/reservations", methods=["POST"])
def create_reservation():
    """
    Bonus helper endpoint: Reserve a parking slot.
    Allows easy functional testing and end-to-end demonstrations.
    """
    data = request.get_json(silent=True)
    if not data:
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": "Request body must be valid JSON.",
                }
            ),
            400,
        )

    required_fields = ["slot_id", "vehicle_number", "driver_name"]
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": f"Missing required fields: {', '.join(missing)}",
                }
            ),
            400,
        )

    slot_id = data["slot_id"]
    target_slot = next((s for s in parking_slots if s["id"] == slot_id), None)

    if not target_slot:
        return (
            jsonify(
                {
                    "error": "Not Found",
                    "message": f"Slot with ID {slot_id} does not exist.",
                }
            ),
            404,
        )

    if target_slot["is_occupied"]:
        return (
            jsonify(
                {
                    "error": "Conflict",
                    "message": f"Slot {target_slot['slot_number']} is already occupied.",
                }
            ),
            409,
        )

    # Mark slot as occupied
    target_slot["is_occupied"] = True

    # Generate new reservation
    new_id = (max([r["id"] for r in reservations], default=0)) + 1
    new_reservation = {
        "id": new_id,
        "slot_id": target_slot["id"],
        "slot_number": target_slot["slot_number"],
        "vehicle_number": str(data["vehicle_number"]).strip(),
        "driver_name": str(data["driver_name"]).strip(),
        "start_time": datetime.now(timezone.utc).isoformat(),
        "status": "ACTIVE",
    }
    reservations.append(new_reservation)

    return (
        jsonify(
            {
                "message": "Reservation created successfully.",
                "reservation": new_reservation,
            }
        ),
        201,
    )


@app.route("/metrics", methods=["GET"])
def get_metrics():
    """
    Endpoint 4: System and application metrics.
    By default outputs Prometheus text format for monitoring integration.
    Also supports ?format=json or Accept: application/json for REST consumers.
    """
    total_slots = len(parking_slots)
    occupied_slots = sum(1 for s in parking_slots if s["is_occupied"])
    available_slots = total_slots - occupied_slots
    active_reservations = sum(1 for r in reservations if r.get("status") == "ACTIVE")

    # If client requests JSON format explicitly
    requested_format = request.args.get("format", "").strip().lower()
    accept_header = request.headers.get("Accept", "")

    if requested_format == "json" or "application/json" in accept_header:
        return (
            jsonify(
                {
                    "http_requests_total": TOTAL_REQUESTS,
                    "parking_total_slots": total_slots,
                    "parking_available_slots": available_slots,
                    "parking_occupied_slots": occupied_slots,
                    "parking_active_reservations": active_reservations,
                    "parking_api_up": 1,
                }
            ),
            200,
        )

    # Prometheus exposition standard plain text format
    prometheus_metrics = (
        "# HELP parking_api_http_requests_total Total number of HTTP requests processed.\n"
        "# TYPE parking_api_http_requests_total counter\n"
        f"parking_api_http_requests_total {TOTAL_REQUESTS}\n\n"
        "# HELP parking_total_slots Total configured parking slots.\n"
        "# TYPE parking_total_slots gauge\n"
        f"parking_total_slots {total_slots}\n\n"
        "# HELP parking_available_slots Number of currently available parking slots.\n"
        "# TYPE parking_available_slots gauge\n"
        f"parking_available_slots {available_slots}\n\n"
        "# HELP parking_occupied_slots Number of currently occupied parking slots.\n"
        "# TYPE parking_occupied_slots gauge\n"
        f"parking_occupied_slots {occupied_slots}\n\n"
        "# HELP parking_active_reservations Number of currently active reservations.\n"
        "# TYPE parking_active_reservations gauge\n"
        f"parking_active_reservations {active_reservations}\n\n"
        "# HELP parking_api_up Service availability indicator (1 = up).\n"
        "# TYPE parking_api_up gauge\n"
        "parking_api_up 1\n"
    )

    return Response(
        prometheus_metrics,
        mimetype="text/plain; version=0.0.4; charset=utf-8",
        status=200,
    )


@app.errorhandler(404)
def handle_not_found(error):
    """Handle 404 errors with structured JSON response."""
    return (
        jsonify(
            {
                "error": "Not Found",
                "message": "The requested URL was not found on the server.",
            }
        ),
        404,
    )


@app.errorhandler(500)
def handle_internal_error(error):
    """Handle 500 errors with structured JSON response."""
    return (
        jsonify(
            {
                "error": "Internal Server Error",
                "message": "An unexpected error occurred on the server.",
            }
        ),
        500,
    )


if __name__ == "__main__":
    # In production and Docker, debug mode should remain disabled
    # Port defaults to 5000 as required
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))

    # Flask debug mode is strictly disabled by default
    debug_mode = os.environ.get("FLASK_DEBUG", "0").strip().lower() in ("1", "true")

    print(f"Starting Parking Reservation API on http://{host}:{port} (debug={debug_mode})")
    app.run(host=host, port=port, debug=debug_mode)
