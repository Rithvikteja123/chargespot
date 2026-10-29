"""
services/session_service.py
Service layer handling charging session lifecycle and connector state synchronization.

Enforces Academic Business Rules:
1. Sessions can only start if connector is 'available' and station is 'operational'.
2. Starting a session transitions connector to 'occupied'.
3. Ending a session records end time & energy consumed, transitioning connector to 'available'.
4. Connector statuses remain synchronized with charging session operations.
"""

from datetime import datetime
from pymongo.errors import DuplicateKeyError, WriteError, PyMongoError
from db.connection import db
from services.station_service import get_station_by_id, update_connector_status

def get_all_sessions(limit=100, status_filter=None):
    """Retrieve sessions sorted newest first."""
    query = {}
    if status_filter and status_filter != "All":
        query["status"] = status_filter
    try:
        return list(db.charging_sessions.find(query).sort("started_at", -1).limit(limit))
    except PyMongoError as e:
        print(f"Error fetching sessions: {e}")
        return []

def get_active_sessions():
    """Fetch all ongoing in_progress sessions."""
    try:
        return list(db.charging_sessions.find({"status": "in_progress"}).sort("started_at", -1))
    except PyMongoError as e:
        print(f"Error fetching active sessions: {e}")
        return []

def get_session_by_id(session_id):
    """Fetch single session by session_id."""
    try:
        return db.charging_sessions.find_one({"session_id": session_id})
    except PyMongoError as e:
        print(f"Error finding session {session_id}: {e}")
        return None

def start_charging_session(station_id, connector_id, vehicle_id, custom_session_id=None):
    """
    Start a charging session and transition the corresponding connector to 'occupied'.
    Returns (success: bool, message: str, session_id: str)
    """
    station = get_station_by_id(station_id)
    if not station:
        return False, f"Station '{station_id}' does not exist.", None

    if station.get("status") != "operational":
        return False, f"Cannot start session: Station '{station_id}' is currently '{station.get('status')}'.", None

    target_connector = next(
        (c for c in station.get("connectors", []) if c["connector_id"] == connector_id),
        None
    )
    if not target_connector:
        return False, f"Connector '{connector_id}' does not exist on station '{station_id}'.", None

    if target_connector.get("status") != "available":
        return False, f"Connector '{connector_id}' is '{target_connector.get('status')}', not available.", None

    # Generate or validate session ID
    if custom_session_id:
        session_id = custom_session_id.strip()
    else:
        now_ts = datetime.now().strftime("%m%d%H%M%S")
        session_id = f"SESS-{now_ts}"

    session_doc = {
        "session_id": session_id,
        "station_id": station_id,
        "connector_id": connector_id,
        "vehicle_id": vehicle_id.strip(),
        "started_at": datetime.now(),
        "ended_at": None,
        "energy_kwh": 0.0,
        "status": "in_progress"
    }

    try:
        # Step 1: Insert session
        db.charging_sessions.insert_one(session_doc)
        
        # Step 2: Synchronize connector state
        update_connector_status(station_id, connector_id, "occupied")
        
        return True, f"Session '{session_id}' started! Connector '{connector_id}' is now occupied.", session_id
    except DuplicateKeyError:
        return False, f"Session ID '{session_id}' already exists.", None
    except WriteError as e:
        return False, f"Validation error: {e.details.get('errmsg', str(e))}", None
    except PyMongoError as e:
        return False, f"Database error: {str(e)}", None

def end_charging_session(session_id, energy_consumed_kwh):
    """
    End an active charging session, record final energy consumption,
    and release the connector back to 'available'.
    Returns (success: bool, message: str)
    """
    if energy_consumed_kwh < 0:
        return False, "Energy consumed cannot be negative."

    session = get_session_by_id(session_id)
    if not session:
        return False, f"Session '{session_id}' not found."

    if session.get("status") != "in_progress":
        return False, f"Session '{session_id}' is already {session.get('status')}."

    now = datetime.now()
    try:
        # Step 1: Update session document
        db.charging_sessions.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "ended_at": now,
                    "energy_kwh": round(float(energy_consumed_kwh), 2),
                    "status": "completed"
                }
            }
        )

        # Step 2: Check current connector status before resetting
        station = get_station_by_id(session["station_id"])
        if station:
            conn = next((c for c in station.get("connectors", []) if c["connector_id"] == session["connector_id"]), None)
            # Only reset if not flagged out_of_service by maintenance
            if conn and conn.get("status") != "out_of_service":
                update_connector_status(session["station_id"], session["connector_id"], "available")

        return True, f"Session '{session_id}' completed. Logged {energy_consumed_kwh:.2f} kWh."
    except PyMongoError as e:
        return False, f"Failed to end session: {str(e)}"

def cancel_charging_session(session_id):
    """Cancel an active session and free up the connector."""
    session = get_session_by_id(session_id)
    if not session:
        return False, f"Session '{session_id}' not found."

    if session.get("status") != "in_progress":
        return False, f"Cannot cancel session with status '{session.get('status')}'."

    try:
        db.charging_sessions.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "ended_at": datetime.now(),
                    "status": "cancelled"
                }
            }
        )
        update_connector_status(session["station_id"], session["connector_id"], "available")
        return True, f"Session '{session_id}' has been cancelled."
    except PyMongoError as e:
        return False, f"Database error: {str(e)}"

def delete_session(session_id):
    """Delete a test session record."""
    try:
        res = db.charging_sessions.delete_one({"session_id": session_id})
        if res.deleted_count == 0:
            return False, f"Session '{session_id}' not found."
        return True, f"Session '{session_id}' deleted."
    except PyMongoError as e:
        return False, f"Database error: {str(e)}"
