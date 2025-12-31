import requests
import mysql.connector
from datetime import datetime, timedelta

# Configuration
API_KEY = "1f8e5fb2fb0083baea9f23a7b0c6c4aa"
CITY = "Delhi"
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "password",
    "database": "weather_db"
}

def fetch_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    response = requests.get(url).json()
    return {
        "temp": response['main']['temp'],
        "humidity": response['main']['humidity'],
        "pressure": response['main']['pressure'],
        "desc": response['weather'][0]['description']
    }

def store_data(data):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    query = "INSERT INTO weather_logs (city, temperature, humidity, pressure, description) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (CITY, data['temp'], data['humidity'], data['pressure'], data['desc']))
    conn.commit()
    cursor.close()
    conn.close()

def predict_tomorrow():
    """Predicts tomorrow's temp using a 24-hour weighted moving average."""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Fetch last 24 entries
    cursor.execute("SELECT temperature FROM weather_logs ORDER BY recorded_at DESC LIMIT 24")
    rows = cursor.fetchall()
    
    if len(rows) < 5:
        return "Need more data for prediction..."

    temps = [r[0] for r in rows]
    # Simple Prediction: Current Average + (Current - Previous Trend)
    avg_temp = sum(temps) / len(temps)
    prediction = avg_temp + (temps[0] - temps[-1]) * 0.1
    
    conn.close()
    return round(prediction, 2)

# Execution
weather_data = fetch_weather()
store_data(weather_data)
print(f"Current Temp in {CITY}: {weather_data['temp']}°C")
print(f"Predicted Temp for Tomorrow: {predict_tomorrow()}°C")
