import requests
import mysql.connector
from datetime import datetime

DB_CONFIG = {
    "host": "kafka-18fe5c85-snehalsubu18-7942.d.aivencloud.com",
    "user": "avnadmin",
    "password": "DP19",
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
        print("✅ Data pushed to Aiven Cloud.")
    except Exception as e:
        print(f"❌ Error: {e}")

def predict_tomorrow():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        # Get last 24 hours of data
        cursor.execute("SELECT temperature FROM weather_logs ORDER BY recorded_at DESC LIMIT 24")
        rows = cursor.fetchall()
        conn.close()

        if len(rows) < 5:
            return "Collecting data..."

        temps = [r[0] for r in rows]
        avg_temp = sum(temps) / len(temps)
        
        # Calculate trend (Current - Oldest in window)
        trend = (temps[0] - temps[-1]) * 0.2 
        prediction = avg_temp + trend
        
        return round(prediction, 2)
    except:
        return "N/A"

if __name__ == "__main__":
    data = fetch_weather()
    store_data(data)
    print(f"Current: {data['temp']}°C | Predicted: {predict_tomorrow()}°C")
