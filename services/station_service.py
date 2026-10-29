"""
services/station_service.py
Service layer handling CRUD operations and queries for EV charging stations.

Demonstrates:
- insert_one() with error handling for schema violations & duplicate keys
- find() and find_one() with filtering and projection
- update_one() using $set and array positional operator ($)
- delete_one() with referential business checks against active sessions
"""

from datetime import datetime
from pymongo.errors import DuplicateKeyError, WriteError, PyMongoError
from db.connection import db

def get_all_stations(filter_query=None):
    """Retrieve all stations, optionally matching a filter dict."""
    try:
        query = filter_query or {}
        # Exclude internal MongoDB _id from direct UI rendering or return as string
        cursor = db.stations.find(query).sort("station_id", 1)
        return list(cursor)
    except PyMongoError as e:
        print(f"Error fetching stations: {e}")
        return []

def get_station_by_id(station_id):
    """Fetch a single station by its unique station_id."""
    try:
        return db.stations.find_one({"station_id": station_id})
    except PyMongoError as e:
        print(f"Error finding station {station_id}: {e}")
        return None

def search_stations(search_text=None, city=None, status=None, connector_type=None, min_speed=None):
    """Filter stations by multiple search criteria."""
    query = {}
    
    if search_text:
        # Match station_id, name, or area case-insensitively
        regex = {"$regex": search_text, "$options": "i"}
        query["$or"] = [
            {"station_id": regex},
            {"name": regex},
            {"location.area": regex},
            {"location.address": regex}
        ]

    if city and city != "All":
        query["city"] = city

    if status and status != "All":
        query["status"] = status

    if min_speed and min_speed > 0:
        query["charging_speed_kw"] = {"$gte": min_speed}

    if connector_type and connector_type != "All":
        query["connectors.connector_type"] = connector_type

    try:
        return list(db.stations.find(query).sort("station_id", 1))
    except PyMongoError as e:
        print(f"Error executing search query: {e}")
        return []

def create_station(station_data):
    """
    Insert a new station document into MongoDB.
    Returns (success: bool, message: str)
    """
    try:
        if not station_data.get("created_at"):
            station_data["created_at"] = datetime.now()

        res = db.stations.insert_one(station_data)
        return True, f"Station '{station_data['station_id']}' added successfully."
    except DuplicateKeyError:
        return False, f"Station ID '{station_data.get('station_id')}' already exists."
    except WriteError as e:
        return False, f"Validation failed: {e.details.get('errmsg', str(e))}"
    except PyMongoError as e:
        return False, f"Database error: {str(e)}"

def update_station(station_id, update_fields):
    """
    Update station attributes such as name, city, location, speed, or status.
    Returns (success: bool, message: str)
    """
    try:
        result = db.stations.update_one(
            {"station_id": station_id},
            {"$set": update_fields}
        )
        if result.matched_count == 0:
            return False, f"Station '{station_id}' not found."
        return True, f"Station '{station_id}' updated successfully."
    except WriteError as e:
        return False, f"Update rejected by schema validator: {e.details.get('errmsg', str(e))}"
    except PyMongoError as e:
        return False, f"Database update error: {str(e)}"

def update_connector_status(station_id, connector_id, new_status):
    """
    Update the status of a specific nested connector using the $ positional operator.
    Allowed statuses: 'available', 'occupied', 'out_of_service'
    """
    valid_statuses = ["available", "occupied", "out_of_service"]
    if new_status not in valid_statuses:
        return False, f"Invalid connector status. Must be one of {valid_statuses}."

    try:
        result = db.stations.update_one(
            {"station_id": station_id, "connectors.connector_id": connector_id},
            {"$set": {"connectors.$.status": new_status}}
        )
        if result.matched_count == 0:
            return False, f"Connector '{connector_id}' on station '{station_id}' not found."
        return True, f"Connector '{connector_id}' set to '{new_status}'."
    except PyMongoError as e:
        return False, f"Failed to update connector status: {str(e)}"

def delete_station(station_id):
    """
    Deletes a station after checking for ongoing active charging sessions.
    Business rule: prevent deleting a station that has in-progress charging sessions.
    """
    try:
        active_count = db.charging_sessions.count_documents({
            "station_id": station_id,
            "status": "in_progress"
        })
        if active_count > 0:
            return False, f"Cannot delete station '{station_id}': there are {active_count} active charging session(s)."

        result = db.stations.delete_one({"station_id": station_id})
        if result.deleted_count == 0:
            return False, f"Station '{station_id}' not found."
        return True, f"Station '{station_id}' deleted successfully."
    except PyMongoError as e:
        return False, f"Failed to delete station: {str(e)}"

def get_unique_cities():
    """Retrieve distinct list of cities from stations collection."""
    try:
        return db.stations.distinct("city")
    except PyMongoError:
        return []
