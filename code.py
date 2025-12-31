import requests
import mysql.connector
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
API_KEY = "1f8e5fb2fb0083baea9f23a7b0c6c4aa"
CITY = "London"
DB_CONFIG = {
    "host": "http://kafka-18fe5c85-snehalsubu18-7942.d.aivencloud.com/",
    "user": "root",
    "password": "DP19",
    "database": "weather_db"
}

def fetch_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url).json()
    return {
        "city": response["name"],
        "temp": response["main"]["temp"],
        "humidity": response["main"]["humidity"],
        "desc": response["weather"][0]["description"]
    }

def store_in_db(data):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    query = "INSERT INTO daily_weather (city, temperature, humidity, description) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (data['city'], data['temp'], data['humidity'], data['desc']))
    conn.commit()
    cursor.close()
    conn.close()

def predict_tomorrow():
    conn = mysql.connector.connect(**DB_CONFIG)
    # Fetch last 7 entries for the trend
    df = pd.read_sql(f"SELECT temperature FROM daily_weather WHERE city='{CITY}' ORDER BY timestamp DESC LIMIT 7", conn)
    conn.close()

    if len(df) < 2:
        return "Not enough data to predict."

    # Simple Moving Average + Trend Adjustment
    avg_temp = df['temperature'].mean()
    latest_temp = df['temperature'].iloc[0]
    
    # Simple Logic: Predicted = Average of recent days weighted by the latest trend
    prediction = (avg_temp + latest_temp) / 2
    return round(prediction, 2)

# --- EXECUTION ---
try:
    current_data = fetch_weather(CITY)
    store_in_db(current_data)
    
    print(f"Current Weather in {CITY}: {current_data['temp']}°C, {current_data['desc']}")
    
    tomorrow_prediction = predict_tomorrow()
    print(f"Predicted Temperature for tomorrow: {tomorrow_prediction}°C")

except Exception as e:
    print(f"Error: {e}")
