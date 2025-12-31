import requests
import mysql.connector
from datetime import datetime

# Configuration - Replace with your Cloud DB details
DB_CONFIG = {
    "host": "kafka-18fe5c85-snehalsubu18-7942.d.aivencloud.com", # Remove http:// and /
    "user": "avnadmin",
    "password": "your-actual-password",
    "database": "defaultdb",
    "port": 26243 
}

API_KEY = "1f8e5fb2fb0083baea9f23a7b0c6c4aa"
CITY = "Delhi"

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
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = "INSERT INTO weather_logs (city, temperature, humidity, pressure, description) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (CITY, data['temp'], data['humidity'], data['pressure'], data['desc']))
        conn.commit()
        cursor.close()
        conn.close()
        print("Data successfully logged to Cloud DB.")
    except Exception as e:
        print(f"Error storing data: {e}")

def predict_tomorrow():
    """Predicts tomorrow's temp using a weighted moving average of the last 24 logs."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT temperature FROM weather_logs ORDER BY recorded_at DESC LIMIT 24")
        rows = cursor.fetchall()
        conn.close()

        if len(rows) < 5:
            return "Need more data (at least 5 logs)..."

        temps = [r[0] for r in rows]
        
        # Weighted Moving Average: More weight to recent data
        # Weights: 0.5 for most recent, 0.3 for middle, 0.2 for older
        weights = [0.5, 0.3, 0.2]
        recent_avg = (temps[0] * weights[0]) + (temps[1] * weights[1]) + (temps[2] * weights[2])
        
        # Trend factor: Is it getting hotter or colder?
        trend = temps[0] - temps[-1]
        prediction = recent_avg + (trend * 0.1)
        
        return round(prediction, 2)
    except Exception as e:
        return f"Error: {e}"

# Execution
if __name__ == "__main__":
    weather_data = fetch_weather()
    store_data(weather_data)
    print(f"--- Weather Report for {CITY} ---")
    print(f"Current Temp: {weather_data['temp']}°C")
    print(f"Predicted Temp for Tomorrow: {predict_tomorrow()}°C")
