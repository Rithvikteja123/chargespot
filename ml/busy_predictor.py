"""
ml/busy_predictor.py
Machine Learning Feature for ChargeSpot: Station Busy Prediction.

Academic Objective:
Demonstrates a transparent, explainable Machine Learning classifier
(scikit-learn DecisionTreeClassifier) predicting EV station congestion
based on temporal features (hour, weekday) and station characteristics.

Academic Integrity & Constraints:
- Clearly documented as a demonstration model trained on synthetic historical patterns.
- Evaluation metrics (Accuracy, Classification Report) are computed using train/test split.
- Predictions NEVER overwrite real MongoDB connector availability.
"""

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

class StationBusyPredictor:
    def __init__(self, random_state=42):
        self.random_state = random_state
        self.model = DecisionTreeClassifier(
            max_depth=4,              # Keep tree shallow for explainability and viva defense
            min_samples_split=10,
            random_state=self.random_state
        )
        self.feature_names = [
            "hour_of_day",       # 0 to 23
            "is_weekend",        # 1 for Sat/Sun, 0 for Mon-Fri
            "charging_speed_kw", # e.g. 22, 60, 120, 150
            "total_connectors",  # 2 to 5
            "is_peak_hours"      # 1 if 9am-12pm or 5pm-8pm, else 0
        ]
        self.is_trained = False
        self.accuracy = 0.0
        self.train_size = 0
        self.test_size = 0

    def generate_synthetic_training_data(self, n_samples=600):
        """
        Generates realistic synthetic observations representing typical EV usage patterns.
        Peak hours (9-12 AM, 5-8 PM) and weekends exhibit significantly higher demand.
        """
        np.random.seed(self.random_state)
        
        hours = np.random.randint(6, 23, size=n_samples)
        days = np.random.randint(0, 7, size=n_samples)
        is_weekend = (days >= 5).astype(int)
        speeds = np.random.choice([22, 50, 60, 120, 150], size=n_samples)
        connectors = np.random.choice([2, 3, 4], size=n_samples)
        is_peak = (((hours >= 9) & (hours <= 12)) | ((hours >= 17) & (hours <= 20))).astype(int)

        # Realistic probability of station being busy
        busy_prob = (
            0.45 * is_peak +
            0.25 * is_weekend +
            0.15 * (speeds >= 100).astype(int) -
            0.15 * (connectors >= 4).astype(int) +
            np.random.normal(0, 0.08, size=n_samples)
        )
        # Threshold at 0.40 to determine binary label (1 = Busy, 0 = Moderate/Available)
        labels = (busy_prob > 0.40).astype(int)

        df = pd.DataFrame({
            "hour_of_day": hours,
            "is_weekend": is_weekend,
            "charging_speed_kw": speeds,
            "total_connectors": connectors,
            "is_peak_hours": is_peak,
            "is_busy": labels
        })
        return df

    def train(self):
        """Trains the Decision Tree classifier with train/test split."""
        df = self.generate_synthetic_training_data()
        X = df[self.feature_names]
        y = df["is_busy"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=self.random_state, stratify=y
        )

        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        
        self.accuracy = round(accuracy_score(y_test, y_pred) * 100, 1)
        self.train_size = len(X_train)
        self.test_size = len(X_test)
        self.is_trained = True

        return {
            "accuracy": self.accuracy,
            "train_size": self.train_size,
            "test_size": self.test_size,
            "feature_importance": dict(zip(self.feature_names, [round(f, 3) for f in self.model.feature_importances_]))
        }

    def predict(self, hour_of_day, day_name, charging_speed_kw, total_connectors):
        """
        Predicts busy likelihood for user-selected station attributes.
        Returns: {
            prediction: 'High Congestion (Busy)' | 'Low/Moderate Demand (Available)',
            probability_busy: float,
            explanation: str
        }
        """
        if not self.is_trained:
            self.train()

        is_weekend = 1 if day_name in ["Saturday", "Sunday"] else 0
        is_peak = 1 if (9 <= hour_of_day <= 12) or (17 <= hour_of_day <= 20) else 0

        input_data = pd.DataFrame([{
            "hour_of_day": hour_of_day,
            "is_weekend": is_weekend,
            "charging_speed_kw": charging_speed_kw,
            "total_connectors": total_connectors,
            "is_peak_hours": is_peak
        }])[self.feature_names]

        prediction_val = int(self.model.predict(input_data)[0])
        prob = self.model.predict_proba(input_data)[0]
        busy_pct = round(float(prob[1]) * 100, 1)

        # Explainable reasoning
        reasons = []
        if is_peak:
            reasons.append("Office rush hours (9-12 AM or 5-8 PM)")
        if is_weekend:
            reasons.append("Weekend intercity travel demand")
        if charging_speed_kw >= 100:
            reasons.append(f"Fast charger ({charging_speed_kw} kW) in high demand")
        if total_connectors <= 2:
            reasons.append(f"Limited connector capacity ({total_connectors} plugs)")
        elif total_connectors >= 4:
            reasons.append(f"Higher bay capacity ({total_connectors} plugs) reduces wait times")

        explanation = "; ".join(reasons) if reasons else "Regular off-peak travel window"

        return {
            "prediction_label": "High Congestion (Likely Busy)" if prediction_val == 1 else "Normal / Available",
            "is_busy": bool(prediction_val == 1),
            "probability_busy": busy_pct,
            "probability_available": round(100.0 - busy_pct, 1),
            "explanation": explanation
        }


# Singleton instance for the application
predictor = StationBusyPredictor()
predictor.train()
