import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Utility function to convert temperature
def convert_temperature(temp, from_unit='kelvin', to_unit='celsius'):
    """
    Convert temperature from one unit to another (Kelvin, Celsius, Fahrenheit).
    :param temp: Temperature value to convert.
    :param from_unit: The unit of the input temperature ('kelvin', 'celsius', 'fahrenheit').
    :param to_unit: The unit of the output temperature ('kelvin', 'celsius', 'fahrenheit').
    :return: Converted temperature.
    """
    if from_unit == 'kelvin':
        if to_unit == 'celsius':
            return temp - 273.15
        elif to_unit == 'fahrenheit':
            return (temp - 273.15) * 9/5 + 32
    elif from_unit == 'celsius':
        if to_unit == 'kelvin':
            return temp + 273.15
        elif to_unit == 'fahrenheit':
            return (temp * 9/5) + 32
    elif from_unit == 'fahrenheit':
        if to_unit == 'celsius':
            return (temp - 32) * 5/9
        elif to_unit == 'kelvin':
            return (temp - 32) * 5/9 + 273.15
    return temp  # Return input temp if no conversion needed

# Utility function to trigger alerts
def send_alert(alert_message, alert_email):
    """
    Send an email alert when a weather threshold is breached.
    :param alert_message: The content of the alert.
    :param alert_email: The recipient email address.
    """
    sender_email = os.getenv('ALERT_EMAIL_SENDER')
    sender_password = os.getenv('ALERT_EMAIL_PASSWORD')
    subject = "Weather Alert Notification"
    
    # Email setup
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = alert_email
    msg['Subject'] = subject

    msg.attach(MIMEText(alert_message, 'plain'))

    # SMTP server configuration
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = os.getenv('SMTP_PORT', 587)

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(sender_email, sender_password)
        
        # Send the email
        server.sendmail(sender_email, alert_email, msg.as_string())
        print(f"Alert sent to {alert_email}")
    except Exception as e:
        print(f"Failed to send alert: {e}")
    finally:
        server.quit()

# Utility function to check temperature threshold
def check_temperature_threshold(current_temp, user_threshold, breach_count=0):
    """
    Check if the current temperature breaches the user-defined threshold.
    :param current_temp: The current temperature.
    :param user_threshold: The user-defined threshold.
    :param breach_count: Number of consecutive breaches. If 2 or more, trigger alert.
    :return: Updated breach count.
    """
    if current_temp >= user_threshold:
        breach_count += 1
        if breach_count >= 2:
            return True, breach_count
    else:
        breach_count = 0  # Reset breach count if temperature is back to normal
    return False, breach_count

# Example for alerting mechanism
def handle_alerts(current_temp, location, user_threshold, breach_count, alert_email):
    """
    Handle the alerting logic and send an email if needed.
    :param current_temp: The current temperature to check against the threshold.
    :param location: The location where the temperature was recorded.
    :param user_threshold: The user-defined threshold for alerts.
    :param breach_count: Current breach count for consecutive alerts.
    :param alert_email: The email address to send alerts to.
    :return: Updated breach count.
    """
    alert_triggered, breach_count = check_temperature_threshold(current_temp, user_threshold, breach_count)

    if alert_triggered:
        alert_message = (f"ALERT! The temperature in {location} has exceeded {user_threshold}°C "
                         f"for two consecutive updates. Current temperature: {current_temp}°C.")
        send_alert(alert_message, alert_email)

    return breach_count

# Utility function to parse temperature and condition from API response
def parse_weather_data(data):
    """
    Parse the temperature and weather condition from the weather API response.
    :param data: The weather data returned by the API.
    :return: Parsed temperature and condition.
    """
    temp = data['main']['temp']
    condition = data['weather'][0]['main']
    return temp, condition

