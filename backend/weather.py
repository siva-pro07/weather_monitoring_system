import requests
from datetime import datetime
from statistics import mean
from collections import Counter

# Dictionary to hold daily weather data
daily_data = {}

def fetch_weather_data(api_key, location):
    """
    Fetch real-time weather data from OpenWeatherMap API for a given location.
    """
    url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def process_weather_data(data):
    """
    Process the weather data for a single timestamp. 
    Update the daily summary with the new data and calculate daily aggregates.
    """
    temp = data['main']['temp']
    condition = data['weather'][0]['main']
    timestamp = data['dt']

    # Convert timestamp to a date string (e.g., '2024-08-21')
    date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    
    # Initialize daily data structure if the date doesn't exist
    if date not in daily_data:
        daily_data[date] = {
            'temperatures': [],
            'conditions': []
        }
    
    # Add the new temperature and condition to the daily data
    daily_data[date]['temperatures'].append(temp)
    daily_data[date]['conditions'].append(condition)
    
    # Calculate aggregates for the day
    avg_temp = round(mean(daily_data[date]['temperatures']),2)
    max_temp = max(daily_data[date]['temperatures'])
    min_temp = min(daily_data[date]['temperatures'])
    dominant_condition = Counter(daily_data[date]['conditions']).most_common(1)[0][0]

    # Return the summary for the current date
    return {
        'date': date,
        'avg_temp': avg_temp,
        'max_temp': max_temp,
        'min_temp': min_temp,
        'dominant_condition': dominant_condition
    }

def calculate_daily_summary(date):
    """
    Calculate and return the summary for a specific date. 
    This can be called for historical analysis.
    """
    if date not in daily_data:
        return None
    
    temperatures = daily_data[date]['temperatures']
    conditions = daily_data[date]['conditions']

    avg_temp = mean(temperatures)
    max_temp = max(temperatures)
    min_temp = min(temperatures)
    dominant_condition = Counter(conditions).most_common(1)[0][0]

    return {
        'date': date,
        'avg_temp': avg_temp,
        'max_temp': max_temp,
        'min_temp': min_temp,
        'dominant_condition': dominant_condition
    }
