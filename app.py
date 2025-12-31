import streamlit as st
import pandas as pd
import mysql.connector

st.title("🌦️ Weather Trend Dashboard")

def get_historical_data():
    conn = mysql.connector.connect(**{
        "host": "localhost", "user": "root", "password": "password", "database": "weather_db"
    })
    df = pd.read_sql("SELECT * FROM weather_logs ORDER BY recorded_at DESC LIMIT 100", conn)
    conn.close()
    return df

data = get_historical_data()

if not data.empty:
    st.subheader(f"Recent Trends for {data['city'].iloc[0]}")
    
    # Temperature Chart
    st.line_chart(data.set_index('recorded_at')['temperature'])
    
    # Metrics
    col1, col2 = st.columns(2)
    col1.metric("Current Temp", f"{data['temperature'].iloc[0]}°C")
    col2.metric("Humidity", f"{data['humidity'].iloc[0]}%")
else:
    st.write("No data found. Run the fetch script first!")
