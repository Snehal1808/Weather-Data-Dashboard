import requests
import mysql.connector
from datetime import datetime

# Configuration - Ensure 'host' has NO http:// or trailing /
DB_CONFIG = {
    "host": "kafka-18fe5c85-snehalsubu18-7942.d.aivencloud.com",
    "user": "avnadmin",
    "password": "YOUR_ACTUAL_PASSWORD_HERE",
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
        # Note the ssl_disabled=False here as well
        conn = mysql.connector.connect(**DB_CONFIG, ssl_disabled=False)
        cursor = conn.cursor()
        query = "INSERT INTO weather_logs (city, temperature, humidity, pressure, description) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (CITY, data['temp'], data['humidity'], data['pressure'], data['desc']))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ [{datetime.now()}] Data successfully pushed to Aiven.")
    except Exception as e:
        print(f"❌ Database Error: {e}")

def predict_tomorrow():
    try:
        conn = mysql.connector.connect(**DB_CONFIG, ssl_disabled=False)
        cursor = conn.cursor()
        cursor.execute("SELECT temperature FROM weather_logs ORDER BY recorded_at DESC LIMIT 24")
        rows = cursor.fetchall()
        conn.close()

        if len(rows) < 5: return "More data needed"

        temps = [r[0] for r in rows]
        # Weighted average: Recent readings are 50% of the prediction
        prediction = (temps[0] * 0.5) + (sum(temps[1:5]) / 4 * 0.5)
        return round(prediction, 2)
    except:
        return "N/A"

if __name__ == "__main__":
    weather_data = fetch_weather()
    store_data(weather_data)
    print(f"Current Temp: {weather_data['temp']}°C")
    print(f"Predicted Temp: {predict_tomorrow()}°C")
