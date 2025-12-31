import streamlit as st
import pandas as pd
import mysql.connector

st.set_page_config(page_title="Cloud Weather Tracker", layout="wide")

def get_db_connection():
    # Adding ssl_disabled=False or providing ssl details is required for Aiven
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"],
        port=st.secrets["mysql"]["port"],
        ssl_disabled=False # Tells the connector to use SSL
    )

st.title("🌡️ Delhi Weather Live Trends")

# Use a loading spinner so you know the app is working
with st.spinner('Connecting to Cloud Database...'):
    try:
        conn = get_db_connection()
        query = "SELECT * FROM weather_logs ORDER BY recorded_at DESC LIMIT 50"
        df = pd.read_sql(query, conn)
        conn.close()

        if not df.empty:
            current = df.iloc[0]
            c1, c2, c3 = st.columns(3)
            c1.metric("Temperature", f"{current['temperature']}°C")
            c2.metric("Humidity", f"{current['humidity']}%")
            c3.metric("Condition", str(current['description']).capitalize())

            st.subheader("Temperature Trend")
            st.line_chart(data=df.set_index('recorded_at')['temperature'])
        else:
            st.warning("Database is connected, but no data was found. Run code.py locally!")
            
    except Exception as e:
        st.error("Connection Failed!")
        st.exception(e) # This will print the full error on the screen instead of a blank page
