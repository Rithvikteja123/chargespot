"""
services/analytics_service.py
MongoDB Aggregation Pipelines for ChargeSpot Analytics.

Academic Objective:
Demonstrates core NoSQL aggregation pipeline stages:
$match, $unwind, $group, $sort, $project, and $lookup.
"""

from db.connection import db

def get_connector_status_counts():
    """
    Aggregation Pipeline 1: Count connectors by status (available, occupied, out_of_service).
    
    Stages:
    1. $unwind: Deconstructs the 'connectors' array so each connector becomes a separate document.
    2. $group: Groups by 'connectors.status' and computes the sum count for each status.
    3. $project: Formats the output fields cleanly.
    4. $sort: Sorts alphabetically by status.
    """
    pipeline = [
        {"$unwind": "$connectors"},
        {
            "$group": {
                "_id": "$connectors.status",
                "count": {"$sum": 1}
            }
        },
        {
            "$project": {
                "_id": 0,
                "status": "$_id",
                "count": 1
            }
        },
        {"$sort": {"count": -1}}
    ]
    return list(db.stations.aggregate(pipeline))

def get_energy_consumption_by_station():
    """
    Aggregation Pipeline 2: Calculate total and average energy consumed per station.
    
    Stages:
    1. $match: Filters only completed charging sessions.
    2. $group: Groups by station_id, sums energy_kwh, counts sessions, and calculates average energy.
    3. $lookup: Performs a left outer join with the 'stations' collection to fetch station name and city.
    4. $unwind: Flattens the joined 'station_info' array into a single nested document.
    5. $project: Shapes the final presentation schema and rounds numerical values.
    6. $sort: Orders stations from highest energy consumer to lowest.
    """
    pipeline = [
        {"$match": {"status": "completed"}},
        {
            "$group": {
                "_id": "$station_id",
                "total_energy_kwh": {"$sum": "$energy_kwh"},
                "avg_energy_kwh": {"$avg": "$energy_kwh"},
                "session_count": {"$sum": 1}
            }
        },
        {
            "$lookup": {
                "from": "stations",
                "localField": "_id",
                "foreignField": "station_id",
                "as": "station_info"
            }
        },
        {
            "$unwind": {
                "path": "$station_info",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$project": {
                "_id": 0,
                "station_id": "$_id",
                "station_name": {"$ifNull": ["$station_info.name", "$_id"]},
                "city": {"$ifNull": ["$station_info.city", "Unknown"]},
                "total_energy_kwh": {"$round": ["$total_energy_kwh", 2]},
                "avg_energy_kwh": {"$round": ["$avg_energy_kwh", 2]},
                "session_count": 1
            }
        },
        {"$sort": {"total_energy_kwh": -1}}
    ]
    return list(db.charging_sessions.aggregate(pipeline))

def get_most_used_stations():
    """
    Aggregation Pipeline 3: Rank stations by total number of sessions.
    
    Stages:
    1. $group: Counts all sessions per station_id regardless of status.
    2. $lookup: Joins station details for name and city.
    3. $unwind: Flattens station info.
    4. $sort: Sorts descending by session count.
    5. $limit: Returns top 8 stations.
    """
    pipeline = [
        {
            "$group": {
                "_id": "$station_id",
                "session_count": {"$sum": 1}
            }
        },
        {
            "$lookup": {
                "from": "stations",
                "localField": "_id",
                "foreignField": "station_id",
                "as": "station_info"
            }
        },
        {"$unwind": {"path": "$station_info", "preserveNullAndEmptyArrays": True}},
        {
            "$project": {
                "_id": 0,
                "station_id": "$_id",
                "station_name": {"$ifNull": ["$station_info.name", "$_id"]},
                "city": {"$ifNull": ["$station_info.city", "Unknown"]},
                "session_count": 1
            }
        },
        {"$sort": {"session_count": -1}},
        {"$limit": 8}
    ]
    return list(db.charging_sessions.aggregate(pipeline))

def get_session_status_breakdown():
    """
    Aggregation Pipeline 4: Group charging sessions by status (completed, in_progress, cancelled).
    
    Stages:
    1. $group: Groups by session status and sums energy delivered.
    2. $project: Formats fields and rounds energy.
    3. $sort: Sorts by count descending.
    """
    pipeline = [
        {
            "$group": {
                "_id": "$status",
                "count": {"$sum": 1},
                "total_energy": {"$sum": "$energy_kwh"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "status": "$_id",
                "count": 1,
                "total_energy": {"$round": ["$total_energy", 2]}
            }
        },
        {"$sort": {"count": -1}}
    ]
    return list(db.charging_sessions.aggregate(pipeline))

def get_connector_type_distribution():
    """
    Aggregation Pipeline 5: Distribution of connector standards across network.
    """
    pipeline = [
        {"$unwind": "$connectors"},
        {
            "$group": {
                "_id": "$connectors.connector_type",
                "count": {"$sum": 1},
                "avg_price": {"$avg": "$connectors.price_per_kwh"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "connector_type": "$_id",
                "count": 1,
                "avg_price": {"$round": ["$avg_price", 2]}
            }
        },
        {"$sort": {"count": -1}}
    ]
    return list(db.stations.aggregate(pipeline))

def get_network_kpis():
    """Computes high-level KPIs for the home dashboard using fast aggregations."""
    total_stations = db.stations.count_documents({})
    
    # Connector status breakdown
    status_counts = {item["status"]: item["count"] for item in get_connector_status_counts()}
    available = status_counts.get("available", 0)
    occupied = status_counts.get("occupied", 0)
    out_of_service = status_counts.get("out_of_service", 0)
    total_connectors = available + occupied + out_of_service

    # Total energy consumed
    energy_res = list(db.charging_sessions.aggregate([
        {"$match": {"status": "completed"}},
        {"$group": {"_id": None, "total": {"$sum": "$energy_kwh"}}}
    ]))
    total_energy = round(energy_res[0]["total"], 1) if energy_res else 0.0

    total_sessions = db.charging_sessions.count_documents({})
    active_sessions = db.charging_sessions.count_documents({"status": "in_progress"})

    return {
        "total_stations": total_stations,
        "total_connectors": total_connectors,
        "available_connectors": available,
        "occupied_connectors": occupied,
        "out_of_service_connectors": out_of_service,
        "total_energy_kwh": total_energy,
        "total_sessions": total_sessions,
        "active_sessions": active_sessions
    }
