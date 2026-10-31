# ChargeSpot Presentation — Speaker Notes & Viva Defense Guide

**Course:** CSE494 – Intelligent NoSQL Databases  
**Project:** ChargeSpot — EV Charging Availability & Usage Analytics System  
**Student:** Rithvik Teja  
**Institution:** Lovely Professional University  
**Repository:** [github.com/Rithvikteja123/chargespot](https://github.com/Rithvikteja123/chargespot)  
**Presentation Files:**
- PowerPoint: [`docs/ChargeSpot_Presentation.pptx`](file:///Users/rithvikteja/Documents/ChargeSpot/docs/ChargeSpot_Presentation.pptx)
- Slide Deck PDF: [`docs/ChargeSpot_Presentation.pdf`](file:///Users/rithvikteja/Documents/ChargeSpot/docs/ChargeSpot_Presentation.pdf)
- Complete Project Report: [`docs/FINAL_PROJECT_REPORT.md`](file:///Users/rithvikteja/Documents/ChargeSpot/docs/FINAL_PROJECT_REPORT.md)

---

## Slide 1: Title & Overview (Hero Visual)
**Visual:** High-resolution futuristic EV charging station with luminous green/cyan illumination, project metadata, and live network health status tags.  
**Speaking Script:**
> "Good morning, respected professors and evaluators. My name is Rithvik Teja, and today I am excited to present ChargeSpot — an EV Charging Availability and Usage Analytics System that I built for CSE494.
> 
> As electric vehicles become mainstream across India, drivers face a very real problem: pulling up to a charging station with low battery only to find broken connectors or 45-minute queues. ChargeSpot solves this by combining an intelligent MongoDB document design with real-time PyMongo tracking and predictive machine learning.
> 
> Let me walk you through the problem, the database architecture, and a live demonstration of our results."

---

## Slide 2: The Driver's Dilemma (The Real-World Problem)
**Visual:** Driver cockpit with a 4% critical battery alert, alongside 3 color-coded problem story cards addressing "ghost chargers", queue bottlenecks, and operator blind spots.  
**Speaking Script:**
> "To understand why ChargeSpot matters, imagine you are driving an EV at 8 PM after a long workday. Your battery indicator turns red at 4%. You navigate to a nearby station shown on Google Maps. When you arrive, both fast chargers are occupied, and the third is broken. This is the 'Ghost Charger' problem.
> 
> Traditional relational databases make tracking nested real-time equipment status slow and prone to locks. ChargeSpot was built specifically to eliminate this anxiety through atomic document updates and machine learning."

---

## Slide 3: The ChargeSpot Solution & Course Objectives
**Visual:** 3 core solution pillars (Discover, Active Charging Simulator, Predictive AI) and direct mapping to 6 CSE494 course criteria.  
**Speaking Script:**
> "Here is what makes ChargeSpot unique: it satisfies real driver needs while systematically fulfilling every single requirement of our CSE494 course syllabus.
> 
> On the practical side, users can search stations, monitor active plugs, simulate live charging sessions, and predict wait times. On the academic side, it implements schema validation, atomic PyMongo updates, five multi-stage aggregation pipelines, and machine learning. Everything you see is verifiable in code."

---

## Slide 4: System Architecture & Technology Stack
**Visual:** 4-tier modular architecture (Streamlit UI, Python Service Layer, Scikit-Learn Engine, MongoDB NoSQL Store) and end-to-end dataflow pipeline.  
**Speaking Script:**
> "Here you see our 4-tier architecture. At the top, Streamlit delivers an interactive web interface with Plotly charts. The Python service layer acts as the controller, managing business rules like locking a connector when a session starts.
> 
> Our scikit-learn model runs side-by-side to provide instant busy-hour predictions. And at the foundation is MongoDB 7.0, handling all persistence and aggregations with sub-5 millisecond response times."

---

## Slide 5: MongoDB Document Design (Embedding vs. Referencing)
**Visual:** JSON document schemas comparing `stations` (embedded connectors) with `charging_sessions` (referenced foreign keys), plus `$jsonSchema` validation rules.  
**Speaking Script:**
> "A common viva question is: 'Why not embed everything in MongoDB?' Here is the exact architectural reason:
> 
> Connectors are embedded because every station has only two to six connectors — this is a classic 1-to-Few pattern. Fetching a station gives us all plug statuses in one single atomic disk read.
> 
> However, charging sessions represent an unbounded 1-to-Many relationship. A busy station can have thousands of sessions. If we embedded them inside the station document, we would soon hit MongoDB's 16MB document size limit. Therefore, we reference `station_id` and join them cleanly during analytics using `$lookup`."

---

## Slide 6: Live Application Demonstration (Home & Find Modules)
**Visual:** Real screenshots of the Home Dashboard (KPI cards + live donut chart) and Find a Station (multi-attribute filtering with slot badges).  
**Speaking Script:**
> "Here you can see actual screenshots of our running application. On the left is the Home Dashboard. Notice the high-level KPI cards and the live status donut chart. These aren't static mockups — they query MongoDB directly when the page loads.
> 
> On the right is the Find a Station module. Drivers can filter by city, minimum charging speed, or connector standard. Each card displays clear, color-coded badges showing available, occupied, or out-of-service ports."

---

## Slide 7: Database Aggregations & Analytics
**Visual:** Real Insights page screenshot showing energy distribution, along with a walkthrough of the 5 core aggregation pipelines and verified output metrics.  
**Speaking Script:**
> "Examiners frequently test aggregation pipelines in viva. In ChargeSpot, we wrote five pipelines. The most advanced is Pipeline 2. Instead of pulling all records into Python and looping over them, we let MongoDB execute a multi-stage pipeline: filtering completed sessions with `$match`, grouping total energy, and performing a `$lookup` join with the stations collection to fetch station names.
> 
> This demonstrates that all data processing remains inside the database engine, adhering to optimal NoSQL performance standards."

---

## Slide 8: Machine Learning — Station Congestion Predictor
**Visual:** Decision tree concept artwork paired with the live prediction UI screenshot, 5 input features, and academic synthetic disclosure.  
**Speaking Script:**
> "For our course, the faculty requested a machine learning component. I chose a Decision Tree classifier specifically because it is interpretable — it avoids the 'black-box' opacity of neural networks. During a viva, I can show the exact split conditions, such as 'is it between 5 PM and 8 PM on a weekday?'
> 
> I trained it on 600 synthetic charging profiles using 5 features. It achieved 91.3% test accuracy. In our live app, drivers can input their departure time and station type, and the model instantly warns them whether they should expect an open charger or high queue congestion."

---

## Slide 9: Testing, Quality Assurance & Index Optimization
**Visual:** 14 automated passing test matrix, Sessions manager screenshot, and dark terminal proof of `explain()` confirming `IXSCAN` index usage.  
**Speaking Script:**
> "Reliability is crucial for this project. We wrote automated test suites covering all four CRUD operations, schema rejection, and lifecycle synchronization. Test 7 specifically verifies referential integrity: if you try to delete a charging station while a car is actively plugged into it, the system rejects the operation.
> 
> On the performance side, we ran PyMongo's `explain()` method. The query planner confirmed an `IXSCAN` using our compound B-Tree index, executing in just 0.32 milliseconds. This proves $O(\log N)$ efficiency over full collection `COLLSCAN`."

---

## Slide 10: Conclusion & Future Scope
**Visual:** Smart green city eco-transit hub, 4 key verified quantitative metric tiles, future production roadmap, and viva conclusion.  
**Speaking Script:**
> "To summarize, ChargeSpot demonstrates a complete, end-to-end implementation of an intelligent NoSQL database system. We achieved hybrid document modeling, collection-level validation, compound index performance, five aggregation pipelines, and an explainable machine learning module.
> 
> In the future, this system could be connected to real OCPP chargers and utilize MongoDB 2dsphere indexes for live GPS navigation. Thank you so much for your time and attention. I look forward to your questions!"

---

## Top 5 Likely Viva Questions & Ready Answers

### Q1: Why did you choose MongoDB instead of a relational database like MySQL or PostgreSQL?
**Answer:**
> "In an EV charging network, charging stations have nested structures — a station contains multiple connectors with varying hardware standards and power outputs. In relational databases, this requires multiple joined tables (`stations`, `connectors`, `connector_types`). With MongoDB, we store connectors directly inside the station document. A driver looking up a station fetches everything in a single $O(1)$ disk read. Furthermore, schema flexibility allows different stations to store distinct attributes (e.g., parking fees or solar canopy details) without modifying relational table schemas."

### Q2: What is the difference between embedding and referencing in your design?
**Answer:**
> "We used both patterns based on entity cardinality and lifecycle:
> 1. **Embedded:** Connectors inside `stations`. Every station has a bounded 1-to-Few relationship (2 to 6 connectors). They are always queried together with the station.
> 2. **Referenced:** `charging_sessions` in a separate collection referencing `station_id`. Sessions represent an unbounded 1-to-Many relationship that grows continuously. Embedding sessions would risk hitting MongoDB's 16MB document size limit and cause severe write amplification."

### Q3: How did you implement schema validation in MongoDB?
**Answer:**
> "We enforced database-level validation using MongoDB's `$jsonSchema` operator during collection creation. We defined mandatory fields (`station_id`, `name`, `connectors`), set positive numeric bounds on `charging_speed_kw`, and restricted statuses to strict enums (`operational`, `maintenance`). We verified this in automated test `TC-01`, which deliberately inserted an invalid record and confirmed that MongoDB threw a `WriteError` rejection."

### Q4: Explain how Pipeline 2 computes energy delivered per station.
**Answer:**
> "Pipeline 2 consists of five sequential stages:
> 1. `$match`: Filters for records where `status: "completed"`.
> 2. `$group`: Groups by `station_id` and calculates `$sum: "$energy_kwh"`.
> 3. `$lookup`: Performs a left outer join with the `stations` collection on `station_id` to retrieve the human-readable station name and city.
> 4. `$project`: Reshapes the output into clean, consumer-ready fields.
> 5. `$sort`: Orders the results in descending order by total energy delivered."

### Q5: How does your Decision Tree ML model integrate with MongoDB?
**Answer:**
> "The machine learning model acts purely as an analytical read-only layer. When a driver selects a station on the Insights page, the application pulls that station's capacity (`charging_speed_kw`, `total_connectors`) from MongoDB. These parameters, combined with the target departure hour and day of week, are passed to the scikit-learn `DecisionTreeClassifier`. The model computes the probability of congestion and renders advice in the UI, without writing anything to the database."
