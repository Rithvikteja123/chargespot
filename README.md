# ChargeSpot — EV Charging Availability & Usage Analytics System

> **“A little more charge, a little less waiting.”**  
> Academic Project for **CSE494: Intelligent NoSQL Databases**

ChargeSpot is a full-stack EV charging availability tracker and usage analytics platform built with **Python**, **MongoDB**, **PyMongo**, and **Streamlit**. It models a realistic EV charging network across urban corridors, providing real-time connector availability, charging session lifecycle management, powerful MongoDB aggregation pipelines, and an explainable Machine Learning model for station congestion prediction.

---

## 🌟 Key Features

1. **Live Network Dashboard (`app.py`)**:
   - Real-time KPI metric cards (Total Stations, Available, Occupied, Out of Service, Energy Delivered).
   - Interactive Plotly Donut Chart of live connector availability.
   - Live feed of active and recent charging sessions.
   - Quick-glance cards showing power rating and plug distribution.

2. **Station Directory & Multi-Parameter Filter (`pages/1_Find_a_Station.py`)**:
   - Case-insensitive regex search by station name, city, or locality.
   - Dynamic filters by City, Station Status, Connector Standard (CCS2, Type 2, CHAdeMO, GB/T), and Minimum Speed (kW).
   - Expandable station details with individual connector pricing and one-click demo session starter.

3. **Station Management & CRUD Control Panel (`pages/2_Manage_Stations.py`)**:
   - **Create (`insert_one`)**: Add new stations with client-side & MongoDB collection-level `$jsonSchema` validation.
   - **Read (`find`, `find_one`)**: Tabular overview of all station documents and embedded connectors.
   - **Update (`update_one`)**: Modify station metadata and toggle individual connector statuses using the MongoDB array positional operator (`$`).
   - **Delete (`delete_one`)**: Safe station deletion with referential integrity guard preventing deletion if active sessions exist.

4. **Charging Session Lifecycle Manager (`pages/3_Charging_Sessions.py`)**:
   - **Active Sessions**: Monitor ongoing charging in real-time.
   - **Complete Session**: Record energy consumed (kWh) and duration; automatically transitions connector status from `occupied` back to `available`.
   - **Plug-In Demonstration**: Start new sessions with strict business consistency checks (connector must be `available` and station must be `operational`).
   - **History Archive**: Search and filter past sessions, duration calculations, and test session deletion.

5. **Insights: NoSQL Aggregations & Machine Learning (`pages/4_Insights.py`)**:
   - **Aggregation Pipeline 1**: Connector availability breakdown (`$unwind`, `$group`).
   - **Aggregation Pipeline 2**: Energy consumption per station (`$match`, `$group`, `$lookup`, `$project`, `$sort`).
   - **Aggregation Pipeline 3**: Most used station ranking (`$group`, `$lookup`, `$sort`, `$limit`).
   - **Aggregation Pipeline 4**: Session status & energy delivery distribution.
   - **Aggregation Pipeline 5**: Connector standard distribution and average tariff.
   - **Explainable ML Feature**: Predicts station congestion probability using a scikit-learn `DecisionTreeClassifier` (features: hour of day, weekend flag, charging speed, connector count, peak hours).

---

## 🏗️ Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Database** | MongoDB Community Server (v7.0) | Document store for stations and sessions |
| **Driver** | PyMongo (v4.19) | Native Python-to-MongoDB connection and CRUD |
| **UI Framework**| Streamlit (v1.66) | Reactive web interface with custom CSS design |
| **Analytics** | MongoDB Aggregations & Pandas | NoSQL pipeline execution and data tabularization |
| **Visuals** | Plotly Express | Interactive charts (Donut, Horizontal Bar, Distribution) |
| **Machine Learning**| scikit-learn (v1.9) | Explainable Decision Tree congestion classifier |
| **Configuration**| `python-dotenv` | Secure `.env` environment variable management |

---

## 📂 Project Structure

```text
ChargeSpot/
├── app.py                      # Main entrypoint & Network KPI dashboard
├── config.py                   # Environment configuration loader
├── styles.py                   # Custom CSS design system (Forest green & warm tones)
├── requirements.txt            # Python dependencies
├── .env                        # Local database connection URI (not tracked in Git)
├── .env.example                # Safe environment variable template
├── .gitignore                  # Git exclusions (.venv, .env, caches)
├── README.md                   # Project documentation & run guide
├── db/
│   ├── __init__.py
│   ├── connection.py           # Reusable MongoClient & ping check
│   ├── validators.py           # MongoDB collection-level $jsonSchema definitions
│   └── seed_data.py            # Deterministic upsert seed script (10 stations, 42 sessions)
├── services/
│   ├── __init__.py
│   ├── station_service.py      # Station CRUD & search service
│   ├── session_service.py      # Session lifecycle & connector synchronization
│   └── analytics_service.py    # MongoDB aggregation pipelines & KPIs
├── ml/
│   ├── __init__.py
│   └── busy_predictor.py       # scikit-learn DecisionTreeClassifier model
├── pages/
│   ├── 1_Find_a_Station.py     # Search and filter directory
│   ├── 2_Manage_Stations.py    # CRUD management tabs
│   ├── 3_Charging_Sessions.py  # Session lifecycle management
│   └── 4_Insights.py           # Aggregation analytics & ML prediction
├── tests/
│   ├── test_crud.py            # Automated CRUD, validation & explain() test suite
│   └── test_aggregations.py    # Aggregation pipelines output verification
└── docs/
    └── project_report.md       # Comprehensive academic project report & viva guide
```

---

## 🚀 Quickstart & Setup Guide

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.14 on macOS)
- MongoDB Community Server running on `localhost:27017`

To verify MongoDB is running:
```bash
mongosh --eval "db.runCommand({ ping: 1 })"
```

### 2. Environment Setup
```bash
# Clone or navigate into the repository
cd ~/Documents/ChargeSpot

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Initialize Database & Seed Sample Records
```bash
# Apply $jsonSchema validation rules
python db/validators.py

# Seed initial database with sample stations and sessions
python db/seed_data.py --reset
```

### 4. Run Automated Test Verification
```bash
# Verify CRUD operations, validation rejection, and explain() index scan
python tests/test_crud.py

# Verify all 5 MongoDB aggregation pipelines
python tests/test_aggregations.py
```

### 5. Launch the Streamlit Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Automated Test Verification

The project includes two comprehensive automated test suites:

- **`tests/test_crud.py`**:
  1. Tests MongoDB `$jsonSchema` rejection of invalid records (negative speed, invalid enum).
  2. Tests `insert_one()` for valid stations.
  3. Tests `find_one()` query retrieval.
  4. Tests `update_one()` for station metadata.
  5. Tests business rule: session start locks connector to `occupied`.
  6. Tests referential integrity: prevents station deletion when active sessions exist.
  7. Tests business rule: session end records energy and frees connector to `available`.
  8. Tests `delete_one()` clean-up.
  9. Tests query performance via `explain()` confirming `IXSCAN` usage.

- **`tests/test_aggregations.py`**:
  Executes and prints the real output for all 5 aggregation pipelines directly from `chargespot_db`.

---

## 🎓 Academic Viva Highlights

1. **Why embed connectors but reference charging sessions?**
   - Connectors are bounded in quantity (2 to 5 per station) and are always accessed alongside station details. Embedding avoids unnecessary joins for basic lookups.
   - Charging sessions grow continuously over time. Embedding them would breach MongoDB's 16MB document limit and degrade query latency. Reference by `station_id` allows clean `$lookup` and `$group` aggregations.

2. **How does MongoDB validation work?**
   - Implemented at collection-level via `$jsonSchema` using `db.command("collMod", ...)`. MongoDB natively validates BSON types, required fields, minimum numeric constraints, and allowed enum values before committing writes to disk.

3. **How does the ML busy predictor work?**
   - Uses a shallow `DecisionTreeClassifier` (depth=4) trained on temporal features (hour, weekend, peak window) and station power. It generates explainable rules without overfitting, strictly separated from real database status.
