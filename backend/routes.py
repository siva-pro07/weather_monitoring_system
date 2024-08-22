from flask import Blueprint, render_template, jsonify, request
from flask import render_template
from backend.models import TriggeredAlert, WeatherData
from backend.weather import fetch_weather_data, process_weather_data
from backend.utils import convert_temperature, handle_alerts, parse_weather_data
from backend.scheduler import scheduler
import os

# Create a Blueprint for routes
bp = Blueprint('routes', __name__)

# Configuration
API_KEY = 'cbebc392610c2fb05e60e28609166f53'
LOCATIONS = ['Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Kolkata', 'Hyderabad']

# Route for the main dashboard
@bp.route('/')
def index():
    cities = LOCATIONS
    api_key = API_KEY  # Replace with your API key
    
    weather_data = {}

    # Fetch and process weather data for each city dynamically
    for city in cities:
        try:
            data = fetch_weather_data(api_key, city)
            processed_data = process_weather_data(data)
            weather_data[city] = {
                'temperature': processed_data['avg_temp'],
                'condition': processed_data['dominant_condition'],
                'max_temp': processed_data['max_temp'],
                'min_temp': processed_data['min_temp'],
                'dominant_condition': processed_data['dominant_condition']
            }
        except Exception as e:
            print(f"Error fetching data for {city}: {e}")
            weather_data[city] = {
                'temperature': None,
                'condition': None,
                'max_temp': None,
                'min_temp': None,
                'dominant_condition': None
            }

    return render_template('index.html', cities=cities, weather_data=weather_data)

@bp.route('/alerts')
def alerts():
    # Fetch alerts from the database (replace with actual query)
    alerts = TriggeredAlert.query.all()
    
    return render_template('alerts.html', alerts=alerts)


# API endpoint to fetch and display current weather data for a specific location
@bp.route('/api/weather/<location>', methods=['GET'])
def get_weather(location):
    if location not in LOCATIONS:
        return jsonify({"error": "Location not supported"}), 400
    
    try:
        weather_data = fetch_weather_data(API_KEY, location)
        parsed_temp, condition = parse_weather_data(weather_data)
        daily_summary = process_weather_data(weather_data)
        return jsonify({
            'location': location,
            'temperature': parsed_temp,
            'condition': condition,
            'summary': daily_summary
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API endpoint to convert temperature units
@bp.route('/api/convert_temperature', methods=['POST'])
def convert_temp():
    data = request.json
    temp = data.get('temperature')
    from_unit = data.get('from_unit', 'kelvin')
    to_unit = data.get('to_unit', 'celsius')
    
    if temp is None:
        return jsonify({"error": "Temperature value is required"}), 400
    
    converted_temp = convert_temperature(temp, from_unit, to_unit)
    return jsonify({'converted_temperature': converted_temp})

# API endpoint to check and handle weather alerts
@bp.route('/api/alert/<location>', methods=['GET'])
def check_alert(location):
    user_threshold = float(request.args.get('threshold', 35))  # Default threshold is 35°C
    alert_email = request.args.get('email', os.getenv('DEFAULT_ALERT_EMAIL'))
    
    if location not in LOCATIONS:
        return jsonify({"error": "Location not supported"}), 400
    
    try:
        # Fetch weather data
        weather_data = fetch_weather_data(API_KEY, location)
        parsed_temp, condition = parse_weather_data(weather_data)
        
        # Handle alerts
        breach_count = 0  # Initialize breach count (could be stored in session or DB for persistence)
        breach_count = handle_alerts(parsed_temp, location, user_threshold, breach_count, alert_email)
        
        return jsonify({
            'location': location,
            'temperature': parsed_temp,
            'threshold': user_threshold,
            'alert_triggered': breach_count >= 2
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to trigger scheduler manually (if needed)
@bp.route('/api/scheduler/start', methods=['POST'])
def start_scheduler():
    try:
        # Start the scheduler if not running
        if not scheduler.running:
            scheduler.start()
            return jsonify({"message": "Scheduler started successfully."}), 200
        else:
            return jsonify({"message": "Scheduler is already running."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to stop scheduler (if needed)
@bp.route('/api/scheduler/stop', methods=['POST'])
def stop_scheduler():
    try:
        # Stop the scheduler
        scheduler.shutdown()
        return jsonify({"message": "Scheduler stopped successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
