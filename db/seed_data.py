"""
db/seed_data.py
Populates chargespot_db with realistic demo EV charging stations and sessions.

Design Principles:
- Uses BSON-compatible datetime objects for accurate date calculations.
- Uses upsert logic based on deterministic IDs (CS001-CS010, SESS-1001-SESS-1042)
  so running this script multiple times will update rather than duplicate data.
- Ensures consistency: stations with active ('in_progress') sessions have matching
  connectors marked as 'occupied'.
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add project root to sys.path so it runs both as a script and as a module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import UpdateOne
from db.connection import db, check_connection


def create_indexes():
    """Ensure unique and query indexes exist on key fields."""
    # Stations index: unique station_id, plus index on city for filtering
    db.stations.create_index("station_id", unique=True)
    db.stations.create_index("city")
    db.stations.create_index("status")

    # Charging sessions index: unique session_id, plus index on station_id and status
    db.charging_sessions.create_index("session_id", unique=True)
    db.charging_sessions.create_index("station_id")
    db.charging_sessions.create_index("status")
    db.charging_sessions.create_index("started_at")
    print("✓ Created indexes on stations and charging_sessions collections.")

def get_seed_stations():
    base_time = datetime(2026, 1, 15, 10, 0, 0)
    return [
        {
            "station_id": "CS001",
            "name": "Campus North Charging Hub",
            "city": "Phagwara",
            "location": {
                "city": "Phagwara",
                "area": "University North Campus",
                "address": "Gate 1, Academic Avenue"
            },
            "connector_type": "CCS2",
            "charging_speed_kw": 60,
            "status": "operational",
            "created_at": base_time,
            "connectors": [
                {"connector_id": "C1", "connector_type": "CCS2", "power_kw": 60.0, "price_per_kwh": 14.50, "status": "available"},
                {"connector_id": "C2", "connector_type": "CCS2", "power_kw": 60.0, "price_per_kwh": 14.50, "status": "occupied"},
                {"connector_id": "C3", "connector_type": "Type 2", "power_kw": 22.0, "price_per_kwh": 11.00, "status": "available"},
                {"connector_id": "C4", "connector_type": "Type 2", "power_kw": 22.0, "price_per_kwh": 11.00, "status": "out_of_service"}
            ]
        },
        {
            "station_id": "CS002",
            "name": "GT Road FastCharge Plaza",
            "city": "Phagwara",
            "location": {
                "city": "Phagwara",
                "area": "National Highway 44",
                "address": "Plot 18, GT Road Highway Service Lane"
            },
            "connector_type": "CCS2",
            "charging_speed_kw": 120,
            "status": "operational",
            "created_at": base_time + timedelta(days=2),
            "connectors": [
                {"connector_id": "C1", "connector_type": "CCS2", "power_kw": 120.0, "price_per_kwh": 18.00, "status": "occupied"},
                {"connector_id": "C2", "connector_type": "CCS2", "power_kw": 120.0, "price_per_kwh": 18.00, "status": "available"},
                {"connector_id": "C3", "connector_type": "CHAdeMO", "power_kw": 50.0, "price_per_kwh": 15.50, "status": "available"}
            ]
        },
        {
            "station_id": "CS003",
            "name": "Model Town Supercharge",
            "city": "Jalandhar",
            "location": {
                "city": "Jalandhar",
                "area": "Model Town Market",
                "address": "Opposite Central Park, Mall Road"
            },
            "connector_type": "CCS2",
            "charging_speed_kw": 50,
            "status": "operational",
            "created_at": base_time + timedelta(days=5),
            "connectors": [
                {"connector_id": "C1", "connector_type": "CCS2", "power_kw": 50.0, "price_per_kwh": 15.00, "status": "available"},
                {"connector_id": "C2", "connector_type": "Type 2", "power_kw": 22.0, "price_per_kwh": 12.00, "status": "available"},
                {"connector_id": "C3", "connector_type": "Type 2", "power_kw": 22.0, "price_per_kwh": 12.00, "status": "occupied"}
            ]
        },
        {
            "station_id": "CS004",
            "name": "BMC Chowk EcoStation",
            "city": "Jalandhar",
            "location": {
                "city": "Jalandhar",
                "area": "Civil Lines",
                "address": "BMC Chowk, Near City Centre"
            },
            "connector_type": "CCS2",
            "charging_speed_kw": 60,
            "status": "operational",
            "created_at": base_time + timedelta(days=7),
            "connectors": [
                {"connector_id": "C1", "connector_type": "CCS2", "power_kw": 60.0, "price_per_kwh": 16.00, "status": "available"},
                {"connector_id": "C2", "connector_type": "CCS2", "power_kw": 60.0, "price_per_kwh": 16.00, "status": "available"},
                {"connector_id": "C3", "connector_type": "GB/T", "power_kw": 30.0, "price_per_kwh": 13.50, "status": "out_of_service"}
            ]
        },
        {
            "station_id": "CS005",
            "name": "Sarabha Nagar EV Pod",
            "city": "Ludhiana",
            "location": {
                "city": "Ludhiana",
                "area": "Sarabha Nagar",
                "address": "Block B, Main Market complex"
            },
            "connector_type": "Type 2",
            "charging_speed_kw": 22,
            "status": "operational",
            "created_at": base_time + timedelta(days=10),
            "connectors": [
                {"connector_id": "C1", "connector_type": "Type 2", "power_kw": 22.0, "price_per_kwh": 12.50, "status": "available"},
                {"connector_id": "C2", "connector_type": "Type 2", "power_kw": 22.0, "price_per_kwh": 12.50, "status": "available"},
                {"connector_id": "C3", "connector_type": "CCS2", "power_kw": 50.0, "price_per_kwh": 16.50, "status": "occupied"}
            ]
        },
        {
            "station_id": "CS006",
            "name": "Ferozepur Road FastPort",
            "city": "Ludhiana",
            "location": {
                "city": "Ludhiana",
                "area": "Ferozepur Road",
                "address": "Near Westend Mall, NH5"
            },
            "connector_type": "CCS2",
            "charging_speed_kw": 150,
            "status": "operational",
            "created_at": base_time + timedelta(days=12),
            "connectors": [
                {"connector_id": "C1", "connector_type": "CCS2", "power_kw": 150.0, "price_per_kwh": 19.50, "status": "available"},
                {"connector_id": "C2", "connector_type": "CCS2", "power_kw": 150.0, "price_per_kwh": 19.50, "status": "available"},
                {"connector_id": "C3", "connector_type": "CCS2", "power_kw": 60.0, "price_per_kwh": 16.00, "status": "available"},
                {"connector_id": "C4", "connector_type": "CHAdeMO", "power_kw": 50.0, "price_per_kwh": 15.00, "status": "out_of_service"}
            ]
        },
        {
            "station_id": "CS007",
            "name": "Heritage Walk Green Station",
            "city": "Amritsar",
            "location": {
                "city": "Amritsar",
                "area": "Town Hall",
                "address": "Heritage Walk Entry, Town Hall Parking"
            },
            "connector_type": "CCS2",
            "charging_speed_kw": 60,
            "status": "operational",
            "created_at": base_time + timedelta(days=14),
            "connectors": [
                {"connector_id": "C1", "connector_type": "CCS2", "power_kw": 60.0, "price_per_kwh": 15.50, "status": "occupied"},
                {"connector_id": "C2", "connector_type": "CCS2", "power_kw": 60.0, "price_per_kwh": 15.50, "status": "available"},
                {"connector_id": "C3", "connector_type": "Type 2", "power_kw": 22.0, "price_per_kwh": 12.00, "status": "available"}
            ]
        },
        {
            "station_id": "CS008",
            "name": "Ranjit Avenue SpeedCharger",
            "city": "Amritsar",
            "location": {
                "city": "Amritsar",
                "area": "Ranjit Avenue",
                "address": "B-Block Commercial District"
            },
            "connector_type": "CCS2",
            "charging_speed_kw": 120,
            "status": "operational",
            "created_at": base_time + timedelta(days=16),
            "connectors": [
                {"connector_id": "C1", "connector_type": "CCS2", "power_kw": 120.0, "price_per_kwh": 18.50, "status": "available"},
                {"connector_id": "C2", "connector_type": "CCS2", "power_kw": 120.0, "price_per_kwh": 18.50, "status": "available"},
                {"connector_id": "C3", "connector_type": "Type 2", "power_kw": 22.0, "price_per_kwh": 12.00, "status": "available"}
            ]
        },
        {
            "station_id": "CS009",
            "name": "Sector 17 Plaza Electric Point",
            "city": "Chandigarh",
            "location": {
                "city": "Chandigarh",
                "area": "Sector 17-C",
                "address": "Underground Parking Complex, Sector 17"
            },
            "connector_type": "CCS2",
            "charging_speed_kw": 50,
            "status": "operational",
            "created_at": base_time + timedelta(days=18),
            "connectors": [
                {"connector_id": "C1", "connector_type": "CCS2", "power_kw": 50.0, "price_per_kwh": 16.00, "status": "occupied"},
                {"connector_id": "C2", "connector_type": "Type 2", "power_kw": 22.0, "price_per_kwh": 12.50, "status": "available"},
                {"connector_id": "C3", "connector_type": "Type 2", "power_kw": 22.0, "price_per_kwh": 12.50, "status": "available"},
                {"connector_id": "C4", "connector_type": "GB/T", "power_kw": 30.0, "price_per_kwh": 13.00, "status": "out_of_service"}
            ]
        },
        {
            "station_id": "CS010",
            "name": "IT Park HighPower Station",
            "city": "Chandigarh",
            "location": {
                "city": "Chandigarh",
                "area": "Rajiv Gandhi IT Park",
                "address": "Tech Boulevard, DLF Commercial Complex"
            },
            "connector_type": "CCS2",
            "charging_speed_kw": 150,
            "status": "maintenance",
            "created_at": base_time + timedelta(days=20),
            "connectors": [
                {"connector_id": "C1", "connector_type": "CCS2", "power_kw": 150.0, "price_per_kwh": 20.00, "status": "out_of_service"},
                {"connector_id": "C2", "connector_type": "CCS2", "power_kw": 150.0, "price_per_kwh": 20.00, "status": "out_of_service"},
                {"connector_id": "C3", "connector_type": "Type 2", "power_kw": 22.0, "price_per_kwh": 13.00, "status": "out_of_service"}
            ]
        }
    ]

def get_seed_sessions():
    """Generates 42 realistic charging sessions across recent dates."""
    vehicles = [
        "EV-NEXON-01", "EV-NEXON-02", "EV-TIAGO-03", "EV-ZS-04",
        "EV-IONIQ-05", "EV-KONA-06", "EV-CURVV-07", "EV-XUV400-08",
        "EV-SEAL-09", "EV-PUNCH-10"
    ]
    
    # 6 currently active (in_progress) sessions that align with the 'occupied' connectors above:
    active_sessions = [
        {"session_id": "SESS-1001", "station_id": "CS001", "connector_id": "C2", "vehicle_id": "EV-NEXON-01",
         "started_at": datetime(2026, 10, 28, 11, 30), "ended_at": None, "energy_kwh": 12.4, "status": "in_progress"},
        {"session_id": "SESS-1002", "station_id": "CS002", "connector_id": "C1", "vehicle_id": "EV-ZS-04",
         "started_at": datetime(2026, 10, 28, 11, 45), "ended_at": None, "energy_kwh": 22.8, "status": "in_progress"},
        {"session_id": "SESS-1003", "station_id": "CS003", "connector_id": "C3", "vehicle_id": "EV-TIAGO-03",
         "started_at": datetime(2026, 10, 28, 11, 50), "ended_at": None, "energy_kwh": 5.2, "status": "in_progress"},
        {"session_id": "SESS-1004", "station_id": "CS005", "connector_id": "C3", "vehicle_id": "EV-IONIQ-05",
         "started_at": datetime(2026, 10, 28, 11, 15), "ended_at": None, "energy_kwh": 31.0, "status": "in_progress"},
        {"session_id": "SESS-1005", "station_id": "CS007", "connector_id": "C1", "vehicle_id": "EV-KONA-06",
         "started_at": datetime(2026, 10, 28, 12, 0), "ended_at": None, "energy_kwh": 8.5, "status": "in_progress"},
        {"session_id": "SESS-1006", "station_id": "CS009", "connector_id": "C1", "vehicle_id": "EV-SEAL-09",
         "started_at": datetime(2026, 10, 28, 11, 20), "ended_at": None, "energy_kwh": 28.0, "status": "in_progress"}
    ]

    # Completed historical sessions (SESS-1007 to SESS-1042 = 36 completed sessions)
    historical_sessions = []
    random.seed(494)  # Deterministic seed for reproducible grading
    
    station_ids = ["CS001", "CS002", "CS003", "CS004", "CS005", "CS006", "CS007", "CS008", "CS009"]
    base_past = datetime(2026, 10, 1)

    for i in range(7, 43):
        sess_id = f"SESS-{1000 + i}"
        st_id = random.choice(station_ids)
        conn_id = random.choice(["C1", "C2", "C3"])
        veh_id = random.choice(vehicles)
        
        day_offset = random.randint(1, 27)
        hour = random.randint(7, 21)
        minute = random.choice([0, 15, 30, 45])
        duration_minutes = random.randint(25, 80)
        
        start_time = base_past + timedelta(days=day_offset, hours=hour, minutes=minute)
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Energy consumption roughly 15 kWh to 55 kWh
        energy = round(random.uniform(14.0, 52.5), 2)
        
        # Occasional cancelled session
        status = "cancelled" if i in [12, 28] else "completed"
        if status == "cancelled":
            energy = round(random.uniform(0.5, 2.5), 2)
            end_time = start_time + timedelta(minutes=random.randint(3, 8))

        historical_sessions.append({
            "session_id": sess_id,
            "station_id": st_id,
            "connector_id": conn_id,
            "vehicle_id": veh_id,
            "started_at": start_time,
            "ended_at": end_time,
            "energy_kwh": energy,
            "status": status
        })

    return active_sessions + historical_sessions

def seed_database(reset=False):
    """Inserts or upserts sample data into MongoDB."""
    if not check_connection():
        print("✗ Cannot seed data: MongoDB connection failed.")
        return False

    if reset:
        db.stations.drop()
        db.charging_sessions.drop()
        print("✓ Dropped existing collections for fresh seed.")

    create_indexes()

    stations = get_seed_stations()
    station_ops = [
        UpdateOne({"station_id": s["station_id"]}, {"$set": s}, upsert=True)
        for s in stations
    ]
    st_res = db.stations.bulk_write(station_ops)
    print(f"✓ Stations seeded: {len(stations)} total (Upserted: {len(st_res.upserted_ids)}, Modified: {st_res.modified_count})")

    sessions = get_seed_sessions()
    sess_ops = [
        UpdateOne({"session_id": s["session_id"]}, {"$set": s}, upsert=True)
        for s in sessions
    ]
    sess_res = db.charging_sessions.bulk_write(sess_ops)
    print(f"✓ Sessions seeded: {len(sessions)} total (Upserted: {len(sess_res.upserted_ids)}, Modified: {sess_res.modified_count})")

    # Summary check
    print("\n--- Current Database Summary ---")
    print(f"Total stations: {db.stations.count_documents({})}")
    print(f"Total charging sessions: {db.charging_sessions.count_documents({})}")
    print(f"Active sessions: {db.charging_sessions.count_documents({'status': 'in_progress'})}")
    print(f"Completed sessions: {db.charging_sessions.count_documents({'status': 'completed'})}")
    return True

if __name__ == "__main__":
    import sys
    do_reset = "--reset" in sys.argv
    seed_database(reset=do_reset)
