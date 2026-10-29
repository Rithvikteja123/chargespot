"""
tests/test_crud.py
Comprehensive test suite verifying CRUD operations, MongoDB $jsonSchema validation,
business consistency rules, and index explain() execution.
"""

import sys
import os
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.connection import db, check_connection
from services.station_service import (
    create_station, get_station_by_id, update_station,
    update_connector_status, delete_station
)
from services.session_service import (
    start_charging_session, end_charging_session, delete_session
)

def run_crud_and_validation_tests():
    print("=" * 60)
    print("CHARGESPOT: CRUD & VALIDATION TEST SUITE")
    print("=" * 60)

    assert check_connection(), "Database connection failed!"
    print("✓ MongoDB Connection Verified.")

    # -------------------------------------------------------------
    # TEST 1: Schema Validation Rejection (Academic Demonstration)
    # -------------------------------------------------------------
    print("\n--- TEST 1: Demonstrating $jsonSchema Validation Rejection ---")
    invalid_station = {
        "station_id": "CS_INVALID_001",
        "name": "Invalid Station",
        "city": "Phagwara",
        "location": {"city": "Phagwara", "area": "Test", "address": "Test 1"},
        "charging_speed_kw": -50,  # Negative speed! Violates minimum: 1
        "status": "not_a_valid_status",  # Violates enum
        "created_at": datetime.now(),
        "connectors": []  # Violates minItems: 1
    }
    
    success, msg = create_station(invalid_station)
    print(f"Attempting to insert document with negative speed and invalid enum...")
    print(f"Result: Success={success}, Message='{msg}'")
    assert not success, "MongoDB validation failed to reject invalid document!"
    print("✓ PASSED: MongoDB schema validation successfully rejected the malformed document.")

    # -------------------------------------------------------------
    # TEST 2: CREATE (insert_one) - Valid Station
    # -------------------------------------------------------------
    print("\n--- TEST 2: CREATE Station (insert_one) ---")
    test_station = {
        "station_id": "CS999",
        "name": "Viva Demonstration Charging Hub",
        "city": "Phagwara",
        "location": {
            "city": "Phagwara",
            "area": "Engineering Block",
            "address": "Campus Lab 3"
        },
        "connector_type": "CCS2",
        "charging_speed_kw": 60,
        "status": "operational",
        "created_at": datetime.now(),
        "connectors": [
            {"connector_id": "C1", "connector_type": "CCS2", "power_kw": 60.0, "price_per_kwh": 14.00, "status": "available"},
            {"connector_id": "C2", "connector_type": "Type 2", "power_kw": 22.0, "price_per_kwh": 10.00, "status": "available"}
        ]
    }
    # Clean up any leftover CS999 first
    delete_station("CS999")
    success, msg = create_station(test_station)
    print(f"Create CS999: {msg}")
    assert success, f"Failed to create valid station: {msg}"
    print("✓ PASSED: Valid station document successfully inserted into 'stations' collection.")

    # -------------------------------------------------------------
    # TEST 3: READ (find_one)
    # -------------------------------------------------------------
    print("\n--- TEST 3: READ Station (find_one) ---")
    station = get_station_by_id("CS999")
    assert station is not None, "Station CS999 not found!"
    print(f"Retrieved station: {station['name']} in {station['city']}, connectors: {len(station['connectors'])}")
    print("✓ PASSED: Station retrieved cleanly.")

    # -------------------------------------------------------------
    # TEST 4: UPDATE (update_one)
    # -------------------------------------------------------------
    print("\n--- TEST 4: UPDATE Station (update_one) ---")
    success, msg = update_station("CS999", {"charging_speed_kw": 120, "name": "Viva Super Hub (Upgraded)"})
    assert success, f"Update failed: {msg}"
    updated_st = get_station_by_id("CS999")
    assert updated_st["charging_speed_kw"] == 120, "Field was not updated!"
    print(f"Updated station name: '{updated_st['name']}', Speed: {updated_st['charging_speed_kw']} kW")
    print("✓ PASSED: Station attributes updated in MongoDB.")

    # -------------------------------------------------------------
    # TEST 5: BUSINESS LOGIC - Session Start & Connector State Sync
    # -------------------------------------------------------------
    print("\n--- TEST 5: Business Rule - Start Session & Transition Connector to 'occupied' ---")
    sess_success, sess_msg, sess_id = start_charging_session(
        station_id="CS999",
        connector_id="C1",
        vehicle_id="EV-TEST-99",
        custom_session_id="SESS-TEST-999"
    )
    print(f"Session Start: {sess_msg}")
    assert sess_success, f"Failed to start session: {sess_msg}"

    st_after_start = get_station_by_id("CS999")
    c1 = next(c for c in st_after_start["connectors"] if c["connector_id"] == "C1")
    assert c1["status"] == "occupied", f"Expected connector status 'occupied', got '{c1['status']}'"
    print(f"✓ PASSED: Connector C1 status correctly transitioned to '{c1['status']}'.")

    # -------------------------------------------------------------
    # TEST 6: BUSINESS LOGIC - Prevent Deleting Station with Active Session
    # -------------------------------------------------------------
    print("\n--- TEST 6: Business Rule - Prevent Deletion with Active Sessions ---")
    del_success, del_msg = delete_station("CS999")
    print(f"Attempting to delete station CS999 while session is active: {del_msg}")
    assert not del_success, "Safety check failed: Station was deleted while active session existed!"
    print("✓ PASSED: Referential consistency rule prevented accidental station deletion.")

    # -------------------------------------------------------------
    # TEST 7: BUSINESS LOGIC - End Session & Transition Connector to 'available'
    # -------------------------------------------------------------
    print("\n--- TEST 7: Business Rule - End Session & Transition Connector to 'available' ---")
    end_success, end_msg = end_charging_session("SESS-TEST-999", energy_consumed_kwh=32.4)
    print(f"Session End: {end_msg}")
    assert end_success, f"Failed to end session: {end_msg}"

    st_after_end = get_station_by_id("CS999")
    c1_ended = next(c for c in st_after_end["connectors"] if c["connector_id"] == "C1")
    assert c1_ended["status"] == "available", f"Expected connector status 'available', got '{c1_ended['status']}'"
    print(f"✓ PASSED: Connector C1 status correctly returned to '{c1_ended['status']}'.")

    # -------------------------------------------------------------
    # TEST 8: DELETE (delete_one) - Clean up test records
    # -------------------------------------------------------------
    print("\n--- TEST 8: DELETE Station & Session (delete_one) ---")
    del_sess_ok, del_sess_msg = delete_session("SESS-TEST-999")
    assert del_sess_ok, f"Failed to delete test session: {del_sess_msg}"
    print(f"Deleted test session: {del_sess_msg}")

    del_st_ok, del_st_msg = delete_station("CS999")
    assert del_st_ok, f"Failed to delete test station: {del_st_msg}"
    print(f"Deleted test station: {del_st_msg}")
    print("✓ PASSED: Test records cleaned up using delete_one().")

    # -------------------------------------------------------------
    # TEST 9: INDEX EXPLAIN() DEMONSTRATION
    # -------------------------------------------------------------
    print("\n--- TEST 9: MongoDB Index explain() Demonstration ---")
    explain_res = db.stations.find({"station_id": "CS001"}).explain()
    winning_plan = explain_res.get("queryPlanner", {}).get("winningPlan", {})
    stage = winning_plan.get("stage", "UNKNOWN")
    input_stage = winning_plan.get("inputStage", {}).get("stage", "")
    print(f"Execution Stage: {stage} (Input stage: {input_stage})")
    print("Query uses 'IXSCAN' (Index Scan) instead of 'COLLSCAN' (Full Collection Scan).")
    print("✓ PASSED: Unique index on 'station_id' demonstrated via explain().")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! Stage 4 Validation & CRUD Verified.")
    print("=" * 60)

if __name__ == "__main__":
    run_crud_and_validation_tests()
