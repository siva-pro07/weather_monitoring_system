from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from backend.weather import fetch_weather_data, process_weather_data
import atexit
import os

# Configuration
API_KEY = 'cbebc392610c2fb05e60e28609166f53'  # Read API key from environment variables
LOCATIONS = ['Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Kolkata', 'Hyderabad']
FETCH_INTERVAL = 5  # Interval in minutes (can be customized)

def fetch_and_process_weather():
    """
    Fetch weather data for all configured locations and process them.
    """
    for location in LOCATIONS:
        try:
            print(f"Fetching weather data for {location}...")
            weather_data = fetch_weather_data(API_KEY, location)
            daily_summary = process_weather_data(weather_data)
            print(f"Processed data for {location}: {daily_summary}")
        except Exception as e:
            print(f"Failed to fetch/process weather data for {location}: {e}")

# Set up the background scheduler
scheduler = BackgroundScheduler()

# Schedule the task to run every FETCH_INTERVAL minutes
scheduler.add_job(
    func=fetch_and_process_weather,
    trigger=IntervalTrigger(minutes=FETCH_INTERVAL),
    id='weather_fetch_job',
    name='Fetch and process weather data every 5 minutes',
    replace_existing=True
)

# Start the scheduler
scheduler.start()
print("Scheduler started, fetching weather data every", FETCH_INTERVAL, "minutes.")

# Shut down the scheduler when the program exits
atexit.register(lambda: scheduler.shutdown())

