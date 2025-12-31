import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error

st.set_page_config(page_title="Cloud Weather Tracker", layout="wide")

def get_db_connection():
    """Establishes connection using Streamlit Secrets and SSL."""
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"],
        port=st.secrets["mysql"]["port"],
        ssl_disabled=False,  # Required for Aiven
        connect_timeout=10    # Prevents infinite hanging
    )

st.title("🌡️ Delhi Weather Live Trends")

# Use a spinner to show progress
with st.spinner('Establishing secure connection to Aiven Cloud...'):
    try:
        conn = get_db_connection()
        query = "SELECT * FROM weather_logs ORDER BY recorded_at DESC LIMIT 50"
        df = pd.read_sql(query, conn)
        conn.close()

        if not df.empty:
            # Top Metrics Row
            current = df.iloc[0]
            c1, c2, c3 = st.columns(3)
            c1.metric("Temperature", f"{current['temperature']}°C")
            c2.metric("Humidity", f"{current['humidity']}%")
            c3.metric("Condition", str(current['description']).capitalize())

            # Temperature Chart
            st.subheader("Historical Temperature Trend")
            df['recorded_at'] = pd.to_datetime(df['recorded_at'])
            st.line_chart(data=df.set_index('recorded_at')['temperature'])
            
            # Prediction Display (Calculated on the fly from DB data)
            avg_temp = df['temperature'].mean()
            st.info(f"💡 Based on recent data, the average trend is {round(avg_temp, 2)}°C")
            
        else:
            st.warning("Database connected, but no data found. Please run code.py locally to upload data.")

    except Error as e:
        st.error(f"Database Connection Failed: {e}")
        st.info("Check if you have added 0.0.0.0/0 to Aiven 'Allowed IP Addresses'.")
