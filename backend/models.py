from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class WeatherData(db.Model):
    """
    Model to store raw weather data retrieved from the OpenWeatherMap API.
    """
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    feels_like = db.Column(db.Float, nullable=False)
    condition = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<WeatherData {self.location} - {self.temperature}°C at {self.timestamp}>"

class DailySummary(db.Model):
    """
    Model to store the daily aggregated weather data for each location.
    """
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    avg_temp = db.Column(db.Float, nullable=False)
    max_temp = db.Column(db.Float, nullable=False)
    min_temp = db.Column(db.Float, nullable=False)
    dominant_condition = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<DailySummary {self.location} - {self.date}>"

class AlertThreshold(db.Model):
    """
    Model to store user-configurable alert thresholds for temperature and conditions.
    """
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(100), nullable=False)
    temperature_threshold = db.Column(db.Float, nullable=False, default=35.0)
    condition_threshold = db.Column(db.String(100), nullable=True)  # e.g., "Rain", "Snow"
    consecutive_breach_count = db.Column(db.Integer, default=0)  # Tracks consecutive breaches

    def __repr__(self):
        return f"<AlertThreshold {self.location} - {self.temperature_threshold}°C>"

class TriggeredAlert(db.Model):
    """
    Model to store triggered alerts when a threshold is breached.
    """
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    alert_message = db.Column(db.String(255), nullable=False)
    alert_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_email = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<TriggeredAlert {self.location} - {self.alert_time}>"
