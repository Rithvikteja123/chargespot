# ChargeSpot: EV Charging Availability and Usage Analytics System

---

**Course:** CSE494 – Intelligent NoSQL Databases  
**Assignment:** Academic Task 2  
**Submitted by:** Rithvik Teja  
**Programme:** B.Tech Computer Science and Engineering  
**University:** Lovely Professional University  
**GitHub Repository:** https://github.com/Rithvikteja123/chargespot  
**Submission Date:** October 2026

---

## 1. Abstract

The increasing adoption of electric vehicles has created a need for systems that help drivers identify charging stations, check connector availability, and understand usage patterns. ChargeSpot is a MongoDB-backed application that demonstrates how NoSQL database principles can be applied to EV charging data management.

The application stores charging station information with embedded connector details, and references charging sessions as a separate collection. PyMongo connects the Python application to MongoDB, while Streamlit provides the interactive web interface.

**Verified database statistics at time of testing:**
- 10 charging stations across Punjab and Chandigarh
- 33 total connectors (20 available, 6 occupied, 7 out of service)
- 42 charging session records (34 completed, 6 in progress, 2 cancelled)
- 1,145.8 kWh total energy delivered across completed sessions
- Machine learning model test accuracy: **91.3%**

**Keywords:** MongoDB, NoSQL, PyMongo, Python, Streamlit, EV charging, aggregation, schema validation, machine learning, DecisionTreeClassifier.

---

## 2. Introduction

Electric vehicles are becoming an important part of modern transportation. Finding a suitable charging station and checking connector availability can be inconvenient. Charging operators also require a structured system to manage station information and analyse facility utilisation.

ChargeSpot provides a centralised database for station details, connector status, and charging sessions. MongoDB was chosen because its document-oriented structure naturally supports nested connector data, flexible schema evolution, and expressive multi-stage aggregation pipelines.

The project demonstrates: document design, embedded and referenced relationships, collection-level validation, indexing, CRUD operations, aggregation pipelines, and machine learning integration.

---

## 3. Problem Statement

EV charging information becomes difficult to manage when station details, connector availability, and session records are maintained separately. Without a structured system:
- Connector statuses become inconsistent when sessions start and end.
- Invalid data (negative charging speeds, unsupported connector types) can pollute records.
- Usage pattern analysis requires transferring all data to Python rather than using efficient database-side aggregations.

ChargeSpot addresses these problems by enforcing schema rules at the database level, managing session-connector state transitions atomically, and generating analytics directly within MongoDB's aggregation engine.

---

## 4. Objectives

1. Design `chargespot_db` with collections for EV charging stations and sessions.
2. Represent station and connector data using a hybrid embedded-and-referenced document model.
3. Implement MongoDB collection-level `$jsonSchema` validation.
4. Perform all four CRUD operations using PyMongo.
5. Manage charging session lifecycle with connector state synchronisation.
6. Implement five MongoDB aggregation pipelines for analytics.
7. Build a polished Streamlit user interface.
8. Create and verify a unique index on `station_id` using `explain()`.
9. Integrate an explainable Machine Learning congestion predictor.
10. Test all operations with automated scripts and document verified outputs.

---

## 5. Scope

ChargeSpot is a demonstration application with sample data. Its scope includes:

- **Station Discovery:** Multi-parameter search and filtering.
- **Station Management:** Full CRUD with MongoDB validation.
- **Session Lifecycle:** Start, complete, and cancel sessions with connector sync.
- **Analytics:** Five MongoDB aggregation pipelines with Plotly charts.
- **Congestion Prediction:** Explainable DecisionTreeClassifier demonstration.

The application does not connect to live charging-network APIs.

---

## 6. System Architecture

```
Layer 1: User Interface
  Streamlit Pages (app.py + 4 pages/)
          |
Layer 2: Application Logic
  station_service.py | session_service.py | analytics_service.py
          |                    |
Layer 3: DB Integration    Layer 5: ML Prediction
  PyMongo (connection.py)    busy_predictor.py (DecisionTreeClassifier)
          |
Layer 4: Database
  MongoDB Community Server 7.0
  chargespot_db: stations + charging_sessions
  $jsonSchema validation + B-Tree indexes
```

**Key Design Decisions:**
- Service layer keeps database operations separate from Streamlit UI code.
- ML module reads station attributes but NEVER writes to MongoDB.
- MongoDB URI loaded from `.env` file via `python-dotenv` (excluded from Git).

---

## 7. Project Structure

```
ChargeSpot/
├── app.py                      <- Home dashboard (Streamlit entry point)
├── config.py                   <- Environment variable loader
├── styles.py                   <- Custom CSS design system
├── requirements.txt
├── .env                        <- MongoDB URI (NOT in Git)
├── .env.example                <- Safe template for version control
├── .gitignore
├── README.md
├── db/
│   ├── connection.py           <- MongoClient + ping check
│   ├── validators.py           <- $jsonSchema collection validators
│   └── seed_data.py            <- Deterministic upsert seed script
├── services/
│   ├── station_service.py      <- Station CRUD + search
│   ├── session_service.py      <- Session lifecycle management
│   └── analytics_service.py   <- MongoDB aggregation pipelines
├── ml/
│   └── busy_predictor.py       <- DecisionTreeClassifier model
├── pages/
│   ├── 1_Find_a_Station.py
│   ├── 2_Manage_Stations.py
│   ├── 3_Charging_Sessions.py
│   └── 4_Insights.py
├── tests/
│   ├── test_crud.py            <- 9 automated CRUD/validation tests
│   └── test_aggregations.py   <- 5 aggregation pipeline tests
├── report_screenshots/         <- Evidence screenshots for submission
└── docs/
    └── FINAL_PROJECT_REPORT.md <- This document
```

---

## 8. Technologies Used

| Technology      | Version | Purpose                              |
|:----------------|:--------|:-------------------------------------|
| Python          | 3.14.5  | Application logic and service modules|
| MongoDB         | 7.0.28  | NoSQL document database              |
| PyMongo         | 4.19.0  | Python driver for MongoDB            |
| Streamlit       | 1.66.1  | Reactive web UI                      |
| Pandas          | 3.1.0   | Tabular data formatting              |
| Plotly          | 7.1.0   | Interactive charts                   |
| scikit-learn    | 1.9.1   | DecisionTreeClassifier               |
| python-dotenv   | 1.2.4   | Secure environment variable loading  |
| numpy           | 2.5.4   | Synthetic dataset generation for ML  |

---

## 9. Database Design

### 9.1 Database: `chargespot_db`

Collections:
1. `stations` — station documents with embedded connector arrays
2. `charging_sessions` — referenced session history

### 9.2 Embedding vs. Referencing

| Relationship          | Pattern                    | Justification                                                      |
|:----------------------|:---------------------------|:-------------------------------------------------------------------|
| Station → Connectors  | Embedded Array (1:Few)     | Max 2–5 connectors per station. Always retrieved together. Enables atomic updates using `$` positional operator. |
| Station → Sessions    | Referenced Collection (1:Many) | Sessions grow without bound. Embedding would breach MongoDB's 16 MB document limit. Separate collection allows independent indexing and efficient `$group` aggregations. |

### 9.3 `stations` Collection — Actual Document

```json
{
  "_id": { "$oid": "6ae2ddb04ae46060caa3c9ce" },
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
  "created_at": { "$date": "2026-01-15T10:00:00.000Z" },
  "connectors": [
    { "connector_id": "C1", "connector_type": "CCS2",   "power_kw": 60.0, "price_per_kwh": 14.50, "status": "available"     },
    { "connector_id": "C2", "connector_type": "CCS2",   "power_kw": 60.0, "price_per_kwh": 14.50, "status": "occupied"      },
    { "connector_id": "C3", "connector_type": "Type 2", "power_kw": 22.0, "price_per_kwh": 11.00, "status": "available"     },
    { "connector_id": "C4", "connector_type": "Type 2", "power_kw": 22.0, "price_per_kwh": 11.00, "status": "out_of_service" }
  ]
}
```

### 9.4 `charging_sessions` Collection — Actual Document

```json
{
  "_id": { "$oid": "6ae2ddb04ae46060caa3c9e2" },
  "session_id":  "SESS-1001",
  "station_id":  "CS001",
  "connector_id":"C2",
  "vehicle_id":  "EV-NEXON-01",
  "started_at":  { "$date": "2026-10-28T11:30:00.000Z" },
  "ended_at":    null,
  "energy_kwh":  12.4,
  "status":      "in_progress"
}
```

### 9.5 Seed Dataset Summary

| Dataset            | Count                                          |
|:-------------------|:-----------------------------------------------|
| Total Stations     | 10 (CS001–CS010)                               |
| Cities Covered     | Phagwara, Jalandhar, Ludhiana, Amritsar, CHD   |
| Total Connectors   | 33                                             |
| Connector Standards| CCS2 (18), Type 2 (11), CHAdeMO (2), GB/T (2) |
| Total Sessions     | 42                                             |
| Active Sessions    | 6 (in_progress)                                |
| Completed Sessions | 34                                             |
| Cancelled Sessions | 2                                              |

---

## 10. MongoDB Schema Validation

### 10.1 Implementation

Validation is applied at the MongoDB collection level using `$jsonSchema`. Registered via `collMod` in `db/validators.py`:

```python
db.command({
    "collMod": "stations",
    "validator": STATION_SCHEMA,
    "validationLevel": "moderate"
})
```

`validationLevel: "moderate"`:
- New inserts must pass or they are rejected.
- Updates are validated on modified documents.
- Pre-existing violating documents are not retroactively rejected (safe schema evolution).

### 10.2 Stations Validator (key rules)

```python
STATION_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["station_id","name","city","location","connectors","status","created_at"],
        "properties": {
            "name": { "bsonType": "string", "minLength": 3 },
            "charging_speed_kw": { "bsonType": ["double","int","long"], "minimum": 1 },
            "status": { "enum": ["operational","maintenance","closed"] },
            "created_at": { "bsonType": "date" },
            "connectors": {
                "bsonType": "array", "minItems": 1,
                "items": {
                    "required": ["connector_id","connector_type","power_kw","price_per_kwh","status"],
                    "properties": {
                        "connector_type": { "enum": ["CCS2","Type 2","CHAdeMO","GB/T"] },
                        "power_kw":    { "bsonType": ["double","int","long"], "minimum": 1 },
                        "price_per_kwh":{ "bsonType": ["double","int","long"], "minimum": 0 },
                        "status": { "enum": ["available","occupied","out_of_service"] }
                    }
                }
            }
        }
    }
}
```

### 10.3 Validation Rejection — Verified Test Output

```
--- TEST 1: Demonstrating $jsonSchema Validation Rejection ---
Attempting to insert document with negative speed and invalid enum...
Result: Success=False, Message='Validation failed: Document failed validation'
PASSED: MongoDB schema validation successfully rejected the malformed document.
```

The invalid document had: `charging_speed_kw: -50` (violates `minimum: 1`), `status: "not_a_valid_status"` (violates `enum`), and `connectors: []` (violates `minItems: 1`).

---

## 11. Indexing and Query Performance

### 11.1 Indexes Created

**Stations:**
```python
db.stations.create_index("station_id", unique=True)  # B-Tree unique
db.stations.create_index("city")
db.stations.create_index("status")
```

**Charging Sessions:**
```python
db.charging_sessions.create_index("session_id", unique=True)
db.charging_sessions.create_index("station_id")
db.charging_sessions.create_index("status")
db.charging_sessions.create_index("started_at")
```

### 11.2 explain() Verification

```python
explain_res = db.stations.find({"station_id": "CS001"}).explain()
```

**Verified Output:**
```
--- TEST 9: MongoDB Index explain() Demonstration ---
Execution Stage: FETCH (Input stage: IXSCAN)
Query uses 'IXSCAN' (Index Scan) instead of 'COLLSCAN' (Full Collection Scan).
PASSED: Unique index on 'station_id' demonstrated via explain()
```

`IXSCAN` (O log N) vs `COLLSCAN` (O N). The unique index on `station_id` also acts as a database-level constraint preventing duplicate station IDs regardless of application code.

---

## 12. Application Modules and UI

### 12.1 Home Dashboard (`app.py`)

- KPI cards: Total Stations, Available/Occupied/Out-of-Service Connectors, Energy Delivered.
- Plotly donut chart: live connector status proportions.
- Recent sessions table: last 5 sessions.
- Station Quick View cards with colour-coded connector summaries.
- Sidebar: MongoDB connection status and viva navigation guide.

Design: warm off-white background (`#F8F9F5`), forest-green primary (`#1B4332`), Google Fonts (Plus Jakarta Sans).

### 12.2 Find a Station (`pages/1_Find_a_Station.py`)

- Case-insensitive regex search: `{"$regex": text, "$options": "i"}` across name, station_id, location.area.
- Filter by City (`distinct()`), Status, Connector Standard, and Minimum Speed.
- Expandable station cards with connector details and inline session launcher.

### 12.3 Manage Stations (`pages/2_Manage_Stations.py`)

| Tab | Operation | PyMongo Method |
|:----|:----------|:---------------|
| All Stations | Read | `find({}).sort()` |
| Add Station  | Create | `insert_one()` |
| Edit & Availability | Update | `update_one($set)` and `update_one` with `$` positional |
| Delete Station | Delete | `delete_one()` with active-session guard |

### 12.4 Charging Sessions (`pages/3_Charging_Sessions.py`)

Session lifecycle with connector state synchronisation:
1. **Start:** `insert_one()` session + `update_one($set connectors.$.status: "occupied")`.
2. **Complete:** `update_one($set status: "completed", ended_at, energy_kwh)` + `update_one($set connectors.$.status: "available")`.
3. **Cancel:** `update_one($set status: "cancelled")` + connector returned to `available`.

Business rules: Cannot start on occupied/out_of_service connectors; cannot delete stations with active sessions.

### 12.5 Insights & ML (`pages/4_Insights.py`)

- Tab 1: Five aggregation pipeline results as Plotly bar, donut, and pie charts.
- Tab 2: Interactive `DecisionTreeClassifier` with Station, Day, Hour inputs and explainable output.

---

## 13. CRUD Operations

### 13.1 Create — `insert_one()`

```python
def create_station(station_data):
    try:
        station_data["created_at"] = datetime.now()
        res = db.stations.insert_one(station_data)
        return True, f"Station '{station_data['station_id']}' added successfully."
    except DuplicateKeyError:
        return False, f"Station ID already exists."
    except WriteError as e:
        return False, f"Validation failed: {e.details.get('errmsg', str(e))}"
```

**Verified:** `Station 'CS999' added successfully. PASSED`

### 13.2 Read — `find()` and `find_one()`

```python
def search_stations(search_text=None, city=None, status=None,
                    connector_type=None, min_speed=None):
    query = {}
    if search_text:
        regex = {"$regex": search_text, "$options": "i"}
        query["$or"] = [{"station_id": regex}, {"name": regex},
                        {"location.area": regex}, {"location.address": regex}]
    if city and city != "All":   query["city"] = city
    if min_speed and min_speed > 0: query["charging_speed_kw"] = {"$gte": min_speed}
    if connector_type != "All":  query["connectors.connector_type"] = connector_type
    return list(db.stations.find(query).sort("station_id", 1))
```

**Verified:** `Retrieved station: Viva Demonstration Charging Hub in Phagwara, connectors: 2. PASSED`

### 13.3 Update — `update_one()` with `$set` and `$` Positional Operator

```python
# Update station metadata
db.stations.update_one({"station_id": station_id}, {"$set": update_fields})

# Update one specific connector in the embedded array
db.stations.update_one(
    {"station_id": station_id, "connectors.connector_id": connector_id},
    {"$set": {"connectors.$.status": new_status}}  # $ = matched connector element
)
```

The `$` operator identifies the **first array element that matched the query** — allowing targeted connector updates without rewriting the entire array.

**Verified:** `Updated station name: 'Viva Super Hub (Upgraded)', Speed: 120 kW. PASSED`

### 13.4 Delete — `delete_one()` with Referential Integrity Guard

```python
def delete_station(station_id):
    active_count = db.charging_sessions.count_documents(
        {"station_id": station_id, "status": "in_progress"})
    if active_count > 0:
        return False, f"Cannot delete station '{station_id}': {active_count} active session(s)."
    result = db.stations.delete_one({"station_id": station_id})
    return (result.deleted_count > 0), "Deleted successfully."
```

**Verified:**
```
TEST 6: PASSED - Deletion blocked: 'Cannot delete station CS999: 1 active charging session(s).'
TEST 8: PASSED - After session ended, station CS999 deleted successfully.
```

### 13.5 Session-Connector State Synchronisation

**Verified:**
```
TEST 5: Connector C1 transitioned to 'occupied'. PASSED
TEST 7: Connector C1 returned to 'available'. Logged 32.40 kWh. PASSED
```

---

## 14. MongoDB Aggregation Pipelines

### Pipeline 1: Connector Status Count

**Stages:** `$unwind` → `$group` → `$project` → `$sort`

```python
pipeline = [
    {"$unwind": "$connectors"},
    {"$group": {"_id": "$connectors.status", "count": {"$sum": 1}}},
    {"$project": {"_id": 0, "status": "$_id", "count": 1}},
    {"$sort": {"count": -1}}
]
```

`$unwind` deconstructs the embedded `connectors` array — a station with 4 connectors becomes 4 documents, one per connector. `$group` then counts by status.

**Verified Output:**
```
Status: available       Count: 20
Status: out_of_service  Count: 7
Status: occupied        Count: 6
```

### Pipeline 2: Energy by Station (`$match → $group → $lookup → $project → $sort`)

```python
pipeline = [
    {"$match": {"status": "completed"}},
    {"$group": {"_id": "$station_id",
                "total_energy_kwh": {"$sum": "$energy_kwh"},
                "avg_energy_kwh":   {"$avg": "$energy_kwh"},
                "session_count":    {"$sum": 1}}},
    {"$lookup": {"from": "stations", "localField": "_id",
                 "foreignField": "station_id", "as": "station_info"}},
    {"$unwind": {"path": "$station_info", "preserveNullAndEmptyArrays": True}},
    {"$project": {"_id": 0, "station_id": "$_id",
                  "station_name": {"$ifNull": ["$station_info.name", "$_id"]},
                  "city":         {"$ifNull": ["$station_info.city", "Unknown"]},
                  "total_energy_kwh": {"$round": ["$total_energy_kwh", 2]},
                  "avg_energy_kwh":   {"$round": ["$avg_energy_kwh",   2]},
                  "session_count": 1}},
    {"$sort": {"total_energy_kwh": -1}}
]
```

`$lookup` performs a left-outer join between `charging_sessions` (localField `station_id`) and `stations` (foreignField `station_id`), similar to SQL `LEFT JOIN`.

**Verified Output:**
```
[CS004] BMC Chowk EcoStation        Total: 247.97 kWh | Avg:  31.0 kWh | Sessions: 8
[CS003] Model Town Supercharge      Total: 187.30 kWh | Avg: 37.46 kWh | Sessions: 5
[CS005] Sarabha Nagar EV Pod        Total: 169.83 kWh | Avg: 33.97 kWh | Sessions: 5
[CS007] Heritage Walk Green Station Total: 160.91 kWh | Avg: 32.18 kWh | Sessions: 5
[CS008] Ranjit Avenue SpeedCharger  Total: 151.69 kWh | Avg: 37.92 kWh | Sessions: 4
```

### Pipeline 3: Most Used Stations

**Stages:** `$group → $lookup → $unwind → $project → $sort → $limit`

**Verified Output:**
```
#1 [CS004] BMC Chowk EcoStation        Sessions: 9
#2 [CS003] Model Town Supercharge      Sessions: 6
#3 [CS007] Heritage Walk Green Station Sessions: 6
#4 [CS005] Sarabha Nagar EV Pod        Sessions: 6
#5 [CS008] Ranjit Avenue SpeedCharger  Sessions: 5
```

### Pipeline 4: Session Status Breakdown

**Stages:** `$group → $project → $sort`

**Verified Output:**
```
Status: completed    Sessions: 34  Energy: 1145.85 kWh
Status: in_progress  Sessions:  6  Energy:  107.90 kWh
Status: cancelled    Sessions:  2  Energy:    3.07 kWh
```

### Pipeline 5: Connector Standard Distribution

**Stages:** `$unwind → $group → $project → $sort`

**Verified Output:**
```
Type: CCS2      Count: 18  Avg Price: Rs.17.08/kWh
Type: Type 2    Count: 11  Avg Price: Rs.12.09/kWh
Type: CHAdeMO   Count:  2  Avg Price: Rs.15.25/kWh
Type: GB/T      Count:  2  Avg Price: Rs.13.25/kWh
```

---

## 15. Machine Learning

### 15.1 Model: DecisionTreeClassifier (scikit-learn)

Chosen because decision trees produce interpretable rules, a shallow tree (depth=4) resists overfitting on small synthetic datasets, and feature importances enable step-by-step explanation during viva.

### 15.2 Features and Target

| Feature           | Type    | Description                           |
|:------------------|:--------|:--------------------------------------|
| `hour_of_day`     | int     | Hour of requested visit (0–23)        |
| `is_weekend`      | binary  | 1 = Saturday/Sunday                   |
| `charging_speed_kw`| numeric| Station hardware power rating         |
| `total_connectors`| int    | Physical bay count                    |
| `is_peak_hours`   | binary  | 1 = 09:00–12:00 or 17:00–20:00        |
| **`is_busy`**     | **binary (target)**| **1 = High Congestion**|

### 15.3 Training Data

600 synthetic samples, `numpy.random.seed(42)` for reproducibility. Busy probability formula:

```
busy_prob = 0.45 * is_peak + 0.25 * is_weekend
          + 0.15 * (speed >= 100) - 0.15 * (connectors >= 4)
          + gaussian_noise(0, 0.08)
label = 1 if busy_prob > 0.40
```

### 15.4 Train/Test Split

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y)
# Training: 450 samples | Test: 150 samples
```

`stratify=y` ensures the busy/not-busy ratio is identical in both splits.

**Verified Accuracy: 91.3%**

### 15.5 Academic Safeguards

- Model never calls `insert_one()`, `update_one()`, or any write method.
- All prediction results clearly labelled as demonstration outputs on the Insights page.
- Accuracy reflects synthetic data patterns; real-world re-training would be required for production use.

---

## 16. Testing and Verified Results

### 16.1 Test Matrix

| Test  | Operation              | Method             | Expected                   | Result    |
|:------|:-----------------------|:-------------------|:---------------------------|:----------|
| TC-01 | Schema Validation      | `insert_one` (bad) | Rejected with WriteError   | PASSED |
| TC-02 | Create Station         | `insert_one` CS999 | Document stored            | PASSED |
| TC-03 | Read Station           | `find_one`         | Document retrieved         | PASSED |
| TC-04 | Update Station         | `update_one($set)` | Speed updated to 120 kW    | PASSED |
| TC-05 | Session Start + Sync   | `insert_one` + `update_one($)` | Connector → occupied | PASSED |
| TC-06 | Referential Guard      | `delete_one` blocked| Error: active session     | PASSED |
| TC-07 | Session End + Sync     | `update_one` x2    | Connector → available      | PASSED |
| TC-08 | Delete Records         | `delete_one` x2    | Records removed            | PASSED |
| TC-09 | Index explain()        | `.explain()`       | IXSCAN winning plan        | PASSED |
| TC-10–14 | 5 Aggregations     | `.aggregate()` x5  | Correct totals             | PASSED |

### 16.2 Full CRUD Test Output

```
============================================================
CHARGESPOT: CRUD & VALIDATION TEST SUITE
============================================================
✓ MongoDB Connection Verified.

--- TEST 1: $jsonSchema Validation Rejection ---
Result: Success=False, Message='Validation failed: Document failed validation'
✓ PASSED: MongoDB rejected the malformed document.

--- TEST 2: CREATE Station (insert_one) ---
Create CS999: Station 'CS999' added successfully.
✓ PASSED

--- TEST 3: READ Station (find_one) ---
Retrieved: Viva Demonstration Charging Hub in Phagwara, connectors: 2
✓ PASSED

--- TEST 4: UPDATE Station (update_one) ---
Updated name: 'Viva Super Hub (Upgraded)', Speed: 120 kW
✓ PASSED

--- TEST 5: Start Session + Connector -> occupied ---
Session 'SESS-TEST-999' started! Connector 'C1' is now occupied.
✓ PASSED

--- TEST 6: Prevent Deletion with Active Session ---
Cannot delete station 'CS999': there are 1 active charging session(s).
✓ PASSED: Referential integrity rule enforced.

--- TEST 7: End Session + Connector -> available ---
Session 'SESS-TEST-999' completed. Logged 32.40 kWh.
✓ PASSED

--- TEST 8: DELETE Records ---
Deleted session 'SESS-TEST-999'. Deleted station 'CS999'.
✓ PASSED

--- TEST 9: Index explain() ---
Execution Stage: FETCH (Input stage: IXSCAN)
✓ PASSED: IXSCAN confirmed on station_id index.

============================================================
ALL 9 TESTS PASSED!
============================================================
```

### 16.3 Full Aggregation Test Output

```
=================================================================
CHARGESPOT: MONGODB AGGREGATION PIPELINES VERIFICATION
=================================================================

--- KPI Summary ---
  total_stations: 10 | total_connectors: 33
  available: 20 | occupied: 6 | out_of_service: 7
  total_energy_kwh: 1145.8 | total_sessions: 42 | active: 6

--- Pipeline 1: Connectors by Status ---
  available: 20 | out_of_service: 7 | occupied: 6

--- Pipeline 2: Energy by Station (top 5) ---
  CS004: 247.97 kWh | CS003: 187.30 kWh | CS005: 169.83 kWh
  CS007: 160.91 kWh | CS008: 151.69 kWh

--- Pipeline 3: Most Used Stations ---
  CS004: 9 sessions | CS003: 6 | CS007: 6 | CS005: 6 | CS008: 5

--- Pipeline 4: Sessions by Status ---
  completed: 34 (1145.85 kWh) | in_progress: 6 | cancelled: 2

--- Pipeline 5: Connector Standards ---
  CCS2: 18 (avg Rs.17.08) | Type2: 11 | CHAdeMO: 2 | GB/T: 2

=================================================================
ALL AGGREGATION PIPELINES VERIFIED SUCCESSFULLY!
=================================================================
```

### 16.4 Verified Database Metrics

| Metric                        | Verified Value   |
|:------------------------------|:-----------------|
| Total stations                | 10               |
| Total connectors              | 33               |
| Available connectors          | 20               |
| Occupied connectors           | 6                |
| Out-of-service connectors     | 7                |
| Total session records         | 42               |
| Active (in-progress) sessions | 6                |
| Completed sessions            | 34               |
| Cancelled sessions            | 2                |
| Total energy (completed)      | 1,145.85 kWh     |
| ML model test accuracy        | 91.3%            |
| ML training samples           | 450              |
| ML test samples               | 150              |

---

## 17. Limitations and Future Scope

### Limitations

- Uses locally generated demonstration data, not live EV network feeds.
- No user authentication, payment processing, or hardware integration.
- ML model trained on synthetic data; real-world accuracy would require actual charging logs.
- Not production-hardened (single user, no concurrency controls).

### Future Scope

- Integration with real charging station APIs (OCPP protocol).
- Geospatial search using MongoDB `$geoNear`.
- Role-based access control for operators and drivers.
- Real-time connector updates via WebSocket or MQTT.
- Docker containerisation with CI/CD pipeline.
- Improved ML forecasting using actual historical session data.

---

## 18. Conclusion

ChargeSpot demonstrates how MongoDB's document model, embedded arrays, collection-level schema validation, B-Tree indexing, and multi-stage aggregation pipelines can be combined into a practical, working application.

The project successfully implements:
- Hybrid embedded/referenced document design with justified choices.
- Collection-level `$jsonSchema` validation rejecting invalid records at the database level.
- All four CRUD operations verified through an automated nine-test suite.
- Five aggregation pipelines using `$match`, `$unwind`, `$group`, `$lookup`, `$project`, `$sort`, `$limit`.
- B-Tree index verified via `explain()` confirming `IXSCAN` execution.
- Explainable `DecisionTreeClassifier` safely isolated from actual database state.
- Polished Streamlit interface connecting all database features to an interactive UI.

Every metric in this report reflects genuine execution output from the `chargespot_db` database and test scripts.

---

## 19. References

1. MongoDB, Inc. *MongoDB Manual — $jsonSchema*. https://www.mongodb.com/docs/manual/reference/operator/query/jsonSchema/
2. MongoDB, Inc. *Aggregation Pipeline Stages*. https://www.mongodb.com/docs/manual/reference/operator/aggregation-pipeline/
3. MongoDB, Inc. *PyMongo 4.x Documentation*. https://www.mongodb.com/docs/languages/python/pymongo-driver/current/
4. Streamlit Inc. *Streamlit Documentation*. https://docs.streamlit.io/
5. Pedregosa et al. *scikit-learn: Machine Learning in Python*. JMLR 12:2825-2830, 2011. https://scikit-learn.org/stable/
6. Python Software Foundation. *Python 3 Documentation*. https://docs.python.org/3/
7. Chodorow, K. *MongoDB: The Definitive Guide* (3rd ed.). O'Reilly Media, 2019.
8. CSE494 – Intelligent NoSQL Databases, Academic Task 2 Assignment Instructions. Lovely Professional University, 2026.

---

## 20. Appendix

### A. GitHub Repository

**URL:** https://github.com/Rithvikteja123/chargespot  
**Branch:** `main`  
**Commit message:** `Initial commit: ChargeSpot EV Charging Analytics System - CSE494`  
**Files committed:** 24 tracked files (source, services, tests, docs)  
**Excluded from repo (via .gitignore):** `.env`, `.venv/`, `__pycache__/`, `report_screenshots/`

### B. Installation and Run Commands

```bash
# 1. Navigate to project
cd ~/Documents/ChargeSpot

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Apply $jsonSchema validators to MongoDB
python db/validators.py

# 4. Seed the database (safe upsert — safe to re-run)
python db/seed_data.py --reset

# 5. Run CRUD test suite
python tests/test_crud.py

# 6. Run aggregation test suite
python tests/test_aggregations.py

# 7. Launch Streamlit application
streamlit run app.py
```

### C. Environment Configuration

```bash
# .env (excluded from Git)
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=chargespot_db

# .env.example (committed to Git — no credentials)
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=chargespot_db
```

### D. Viva Preparation — 15 Questions and Answers

**Q1. Why did you choose MongoDB for this project?**  
MongoDB's document model naturally stores nested connector data inside station documents without requiring a separate connector table. Its aggregation pipeline processes analytics inside the database engine without transferring all data to Python.

**Q2. What is the difference between embedding and referencing in MongoDB?**  
Embedding stores related data inside the same document (station → connectors). Referencing stores related data in a separate collection and links via a shared field (sessions reference station_id). I embedded connectors because they are few and always fetched with the station; I referenced sessions because they grow without bound over time.

**Q3. What is $jsonSchema validation and why use it at the database level?**  
`$jsonSchema` is a MongoDB collection-level validator that runs inside the MongoDB engine. It rejects invalid documents regardless of which application or script submits them. Application-level checks can be bypassed; database-level validation cannot.

**Q4. What does $unwind do in an aggregation pipeline?**  
`$unwind` deconstructs an array field. A document with an array of 4 connectors becomes 4 separate documents, one per connector. This enables `$group` to count or sum values across individual connector elements.

**Q5. What is the $ positional operator in update_one()?**  
The `$` is a placeholder for the first element in an array that matched the query condition. In `{"$set": {"connectors.$.status": "occupied"}}`, the `$` resolves to the specific connector whose `connector_id` matched the query filter.

**Q6. What is $lookup and how does it differ from SQL JOIN?**  
`$lookup` performs a left outer join between the current collection and another collection on matching field values. Unlike SQL JOINs, `$lookup` returns an array of matched documents (rather than flat rows) and executes as one stage in a sequential pipeline.

**Q7. Why is the unique index on station_id important?**  
It enforces database-level uniqueness — two stations cannot share the same ID regardless of application logic. It also converts O(N) collection scans into O(log N) B-Tree traversals, verified via `explain()` showing `IXSCAN`.

**Q8. Why was DecisionTreeClassifier chosen over neural networks?**  
Decision trees produce explicit, inspectable rules (IF hour > 17 AND weekend THEN busy). A shallow tree (depth=4) resists overfitting on a small synthetic dataset. Neural networks would require much larger training data and provide no interpretable decision path.

**Q9. What does validationLevel: moderate mean?**  
`moderate` means new inserts and updates must satisfy the validator, but pre-existing documents that already violate the schema are not retroactively rejected. This allows safe schema evolution — you can add stricter rules without invalidating existing data.

**Q10. Why are charging sessions stored in a separate collection instead of embedded?**  
Sessions are unbounded — a high-traffic station could accumulate thousands of session records. Embedding all sessions inside the station document would eventually exceed MongoDB's 16 MB document size limit and degrade write performance on every session update.

**Q11. How does the connector status synchronise when a session starts?**  
`session_service.py` executes two sequential `update_one()` calls: the first inserts the session document; the second uses `update_one({"connectors.connector_id": cid}, {"$set": {"connectors.$.status": "occupied"}})` to mark that specific connector as occupied.

**Q12. What happens if you try to delete a station with active sessions?**  
`station_service.py` first calls `count_documents({"station_id": id, "status": "in_progress"})`. If the count is greater than zero, deletion is blocked and an error message is returned. This prevents orphaned session records.

**Q13. What does stratify=y do in the train_test_split?**  
`stratify=y` ensures the proportion of busy/not-busy labels is identical in both the training and test sets. Without stratification, random sampling might place most busy samples in training and most not-busy in test (or vice versa), producing misleadingly high test accuracy.

**Q14. How does the aggregation KPI pipeline count available connectors?**  
`$unwind "$connectors"` → `$group {"_id": "$connectors.status", "count": {"$sum": 1}}`. The result is a document per status. Python code then picks the count where `status == "available"`.

**Q15. What is PyMongo's DuplicateKeyError and when is it raised?**  
`DuplicateKeyError` is raised by `insert_one()` when the document being inserted has a value for an indexed field (like `station_id`) that already exists in the collection. It is a subclass of `WriteError`. ChargeSpot catches it separately to provide a clear user-facing message rather than a generic database error.

