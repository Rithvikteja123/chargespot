"""
db/validators.py
Defines and applies MongoDB collection-level $jsonSchema validation rules.

Academic Focus:
Demonstrates MongoDB's schema enforcement capabilities, ensuring data integrity
at the database level (data types, required fields, enum constraints, and numeric ranges).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo.errors import OperationFailure
from db.connection import db

STATION_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["station_id", "name", "city", "location", "connectors", "status", "created_at"],
        "properties": {
            "station_id": {
                "bsonType": "string",
                "description": "must be a string and is required (e.g., CS001)"
            },
            "name": {
                "bsonType": "string",
                "minLength": 3,
                "description": "station name must be at least 3 characters"
            },
            "city": {
                "bsonType": "string",
                "description": "city is required for location queries"
            },
            "charging_speed_kw": {
                "bsonType": ["double", "int", "long"],
                "minimum": 1,
                "description": "charging speed must be a positive number in kW"
            },
            "status": {
                "enum": ["operational", "maintenance", "closed"],
                "description": "can only be one of the enum values"
            },
            "created_at": {
                "bsonType": "date",
                "description": "must be a valid BSON date"
            },
            "connectors": {
                "bsonType": "array",
                "minItems": 1,
                "description": "must contain at least one connector",
                "items": {
                    "bsonType": "object",
                    "required": ["connector_id", "connector_type", "power_kw", "price_per_kwh", "status"],
                    "properties": {
                        "connector_id": {
                            "bsonType": "string"
                        },
                        "connector_type": {
                            "enum": ["CCS2", "Type 2", "CHAdeMO", "GB/T"],
                            "description": "must be a supported EV connector standard"
                        },
                        "power_kw": {
                            "bsonType": ["double", "int", "long"],
                            "minimum": 1,
                            "description": "power rating must be positive"
                        },
                        "price_per_kwh": {
                            "bsonType": ["double", "int", "long"],
                            "minimum": 0,
                            "description": "price per kWh cannot be negative"
                        },
                        "status": {
                            "enum": ["available", "occupied", "out_of_service"],
                            "description": "must be available, occupied, or out_of_service"
                        }
                    }
                }
            }
        }
    }
}

SESSION_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["session_id", "station_id", "connector_id", "vehicle_id", "started_at", "status"],
        "properties": {
            "session_id": {
                "bsonType": "string",
                "description": "unique session identifier"
            },
            "station_id": {
                "bsonType": "string",
                "description": "station where the session occurs"
            },
            "connector_id": {
                "bsonType": "string",
                "description": "connector identifier used"
            },
            "vehicle_id": {
                "bsonType": "string",
                "description": "identifier of the vehicle being charged"
            },
            "started_at": {
                "bsonType": "date",
                "description": "start timestamp as a BSON date"
            },
            "ended_at": {
                "bsonType": ["date", "null"],
                "description": "end timestamp as a BSON date or null if ongoing"
            },
            "energy_kwh": {
                "bsonType": ["double", "int", "long"],
                "minimum": 0,
                "description": "energy consumed cannot be negative"
            },
            "status": {
                "enum": ["in_progress", "completed", "cancelled"],
                "description": "valid session states"
            }
        }
    }
}

def apply_validation_rules():
    """Applies or updates collection-level validators using collMod."""
    schemas = {
        "stations": STATION_SCHEMA,
        "charging_sessions": SESSION_SCHEMA
    }
    
    existing_collections = db.list_collection_names()
    
    for coll_name, schema in schemas.items():
        if coll_name in existing_collections:
            try:
                db.command({
                    "collMod": coll_name,
                    "validator": schema,
                    "validationLevel": "moderate"
                })
                print(f"✓ Updated $jsonSchema validation for '{coll_name}'")
            except OperationFailure as e:
                print(f"⚠ Could not modify validator for {coll_name}: {e}")
        else:
            db.create_collection(coll_name, validator=schema, validationLevel="moderate")
            print(f"✓ Created collection '{coll_name}' with $jsonSchema validation")

if __name__ == "__main__":
    apply_validation_rules()
