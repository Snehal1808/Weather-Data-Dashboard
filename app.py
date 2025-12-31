import streamlit as st
import pandas as pd
import mysql.connector
import requests
import plotly.express as px
from datetime import datetime

# --- CONFIG ---
API_KEY = "1f8e5fb2fb0083baea9f23a7b0c6c4aa"
DB_CONFIG = {
    "host": "http://kafka-18fe5c85-snehalsubu18-7942.d.aivencloud.com/",
    "user": "root",
    "password": "DP19",
    "database": "weather_db"
}

# --- FUNCTIONS ---
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def fetch_and_save(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    res = requests.get(url).json()
    
    data = (res['name'], res['main']['temp'], res['main']['humidity'], res['weather'][0]['description'])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO daily_weather (city, temperature, humidity, description) VALUES (%s, %s, %s, %s)", data)
    conn.commit()
    cursor.close()
    conn.close()

# --- DASHBOARD UI ---
st.set_page_config(page_title="Weather Insights", layout="wide")
st.title("☁️ Real-Time Weather Dashboard")

city_input = st.sidebar.text_input("Enter City", "London")

if st.sidebar.button("Update Data"):
    fetch_and_save(city_input)
    st.sidebar.success(f"Updated data for {city_input}")

# Load Data from MySQL
conn = get_db_connection()
df = pd.read_sql(f"SELECT * FROM daily_weather WHERE city='{city_input}' ORDER BY timestamp DESC", conn)
conn.close()

if not df.empty:
    # Top Level Metrics
    col1, col2, col3 = st.columns(3)
    latest = df.iloc[0]
    
    col1.metric("Current Temp", f"{latest['temperature']}°C")
    col2.metric("Humidity", f"{latest['humidity']}%")
    
    # Prediction Logic (Simple Moving Average)
    prediction = round(df['temperature'].head(7).mean(), 2)
    col3.metric("Predicted Tomorrow", f"{prediction}°C")

    # Visualization
    st.subheader("Temperature Trend")
    fig = px.line(df, x='timestamp', y='temperature', title=f"Temperature Over Time: {city_input}")
    st.plotly_chart(fig, use_container_width=True)

    # Raw Data Table
    with st.expander("View Raw Data"):
        st.write(df)
else:
    st.warning("No data found in database. Click 'Update Data' to fetch your first record.")
