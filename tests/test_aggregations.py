"""
tests/test_aggregations.py
Verifies and displays output for all MongoDB aggregation pipelines.
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.analytics_service import (
    get_connector_status_counts,
    get_energy_consumption_by_station,
    get_most_used_stations,
    get_session_status_breakdown,
    get_connector_type_distribution,
    get_network_kpis
)

def test_all_aggregations():
    print("=" * 65)
    print("CHARGESPOT: MONGODB AGGREGATION PIPELINES VERIFICATION")
    print("=" * 65)

    # 1. Network KPIs
    print("\n--- KPI Summary ---")
    kpis = get_network_kpis()
    for k, v in kpis.items():
        print(f"  {k}: {v}")
    assert kpis["total_stations"] > 0, "No stations found!"
    assert kpis["total_connectors"] > 0, "No connectors counted!"

    # 2. Pipeline 1: Connectors by status
    print("\n--- Pipeline 1: Connectors by Status ($unwind, $group) ---")
    status_counts = get_connector_status_counts()
    for row in status_counts:
        print(f"  Status: {row['status']:<15} Count: {row['count']}")
    assert len(status_counts) > 0

    # 3. Pipeline 2: Energy consumption by station
    print("\n--- Pipeline 2: Energy by Station ($match, $group, $lookup, $project) ---")
    energy_by_station = get_energy_consumption_by_station()
    for row in energy_by_station[:5]:
        print(f"  [{row['station_id']}] {row['station_name']:<30} Total: {row['total_energy_kwh']:>7} kWh | Avg: {row['avg_energy_kwh']:>5} kWh | Sessions: {row['session_count']}")
    assert len(energy_by_station) > 0

    # 4. Pipeline 3: Most used stations
    print("\n--- Pipeline 3: Most Used Stations ($group, $lookup, $sort, $limit) ---")
    most_used = get_most_used_stations()
    for rank, row in enumerate(most_used[:5], start=1):
        print(f"  #{rank} [{row['station_id']}] {row['station_name']:<30} Sessions: {row['session_count']}")
    assert len(most_used) > 0

    # 5. Pipeline 4: Session status breakdown
    print("\n--- Pipeline 4: Sessions by Status ($group, $project) ---")
    sessions_by_status = get_session_status_breakdown()
    for row in sessions_by_status:
        print(f"  Status: {row['status']:<15} Sessions: {row['count']:<4} Energy: {row['total_energy']} kWh")
    assert len(sessions_by_status) > 0

    # 6. Pipeline 5: Connector types
    print("\n--- Pipeline 5: Connector Standards Distribution ---")
    types = get_connector_type_distribution()
    for row in types:
        print(f"  Type: {row['connector_type']:<12} Count: {row['count']:<4} Avg Price: ₹{row['avg_price']}/kWh")
    assert len(types) > 0

    print("\n" + "=" * 65)
    print("ALL AGGREGATION PIPELINES VERIFIED SUCCESSFULLY!")
    print("=" * 65)

if __name__ == "__main__":
    test_all_aggregations()
