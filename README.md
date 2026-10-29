ChargeSpot — EV Charging Availability & Usage Analytics

“A little more charge, a little less waiting.”

ChargeSpot is a Python and MongoDB-based application that helps users explore EV charging stations, check connector availability, manage charging sessions, and view usage analytics. It also includes a basic machine-learning feature to predict possible station congestion.

## Key Features

1. **Dashboard:** Shows station statistics, connector availability, energy usage, and recent sessions.
2. **Find a Station:** Search and filter stations by city, connector type, status, and charging speed.
3. **Manage Stations:** Add, view, update, and delete station records with validation.
4. **Charging Sessions:** Start and complete sessions while updating connector status.
5. **Insights & ML:** Uses five MongoDB aggregation pipelines to analyze charging activity and a Decision Tree model to estimate congestion.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| MongoDB | Stores station and session data |
| PyMongo | Connects Python to MongoDB |
| Streamlit | Builds the user interface |
| Pandas and Plotly | Data handling and charts |
| scikit-learn | Congestion prediction |
| python-dotenv | Manages configuration |

## Database Design

The project uses two main MongoDB collections:

- **`stations`** — stores station details and embedded connector information.
- **`charging_sessions`** — stores session details separately and links them to stations using `station_id`.

This structure keeps connector information easy to access while allowing charging history to grow independently.

## Testing

The project includes two test scripts:

- `test_crud.py` checks database operations, validation, session management, and indexing.
- `test_aggregations.py` verifies the five analytics pipelines.

The tests passed during the recorded verification. The database contained 10 stations, 33 connectors, and 42 charging-session records.

## Machine Learning

A Decision Tree model estimates whether a station may be busy using charging-related inputs. The reported evaluation accuracy was 91.3% on demonstration data. This result does not guarantee the same accuracy with real-world charging data.

## Running the Project

```bash
cd ~/Documents/ChargeSpot
source .venv/bin/activate
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

ChargeSpot demonstrates how MongoDB, Python, and basic machine learning can work together to manage charging information and generate useful insights.
