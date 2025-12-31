import streamlit as st
import pandas as pd
import mysql.connector

st.set_page_config(page_title="Cloud Weather Tracker", layout="wide")

def get_db_connection():
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"],
        port=st.secrets["mysql"]["port"]
    )

st.title("🌡️ Delhi Weather Live Trends")

try:
    conn = get_db_connection()
    query = "SELECT * FROM weather_logs ORDER BY recorded_at DESC LIMIT 50"
    df = pd.read_sql(query, conn)
    conn.close()

    if not df.empty:
        # Top Metrics
        current = df.iloc[0]
        c1, c2, c3 = st.columns(3)
        c1.metric("Temperature", f"{current['temperature']}°C")
        c2.metric("Humidity", f"{current['humidity']}%")
        c3.metric("Condition", current['description'].capitalize())

        # Chart
        st.subheader("Temperature Trend (Last 50 Readings)")
        st.line_chart(data=df.set_index('recorded_at')['temperature'])
    else:
        st.info("Database is empty. Run code.py to add data.")

except Exception as e:
    st.error("Connection Failed. Check your Streamlit Secrets.")
    st.write(e)
