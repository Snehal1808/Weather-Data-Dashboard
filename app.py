import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
import requests
import plotly.express as px

# --- DATABASE CONNECTION WITH TIMEOUT & SSL ---
def get_db_connection():
    try:
        # We add connection_timeout so the app doesn't hang if the DB is down
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=st.secrets["mysql"]["port"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            connection_timeout=5, 
            use_pure=True # Helps with compatibility in cloud environments
        )
        return conn
    except Error as e:
        st.error(f"🔌 Database Connection Error: {e}")
        st.info("Check if your Cloud DB allowlist includes IP 0.0.0.0/0")
        return None

# --- DATABASE INITIALIZATION ---
def init_db():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_weather (
                id INT AUTO_INCREMENT PRIMARY KEY,
                city VARCHAR(100),
                temperature FLOAT,
                humidity INT,
                description VARCHAR(255),
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()

# --- API LOGIC ---
def fetch_and_save(city):
    api_key = st.secrets["openweathermap"]["api_key"]
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            res = response.json()
            data = (res['name'], res['main']['temp'], res['main']['humidity'], res['weather'][0]['description'])
            
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                query = "INSERT INTO daily_weather (city, temperature, humidity, description) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, data)
                conn.commit()
                cursor.close()
                conn.close()
                return True
        else:
            st.error(f"API Error: Received status code {response.status_code}")
    except Exception as e:
        st.error(f"Request failed: {e}")
    return False

# --- STREAMLIT UI ---
st.set_page_config(page_title="Weather Dashboard", layout="wide")
init_db()

st.title("🌡️ Weather Data Dashboard")

# Sidebar
st.sidebar.header("Control Panel")
city_input = st.sidebar.text_input("City Name", "London")

if st.sidebar.button("Fetch Live Data"):
    with st.spinner('Syncing with API...'):
        if fetch_and_save(city_input):
            st.sidebar.success("Database Updated!")

# Data Display Logic
conn = get_db_connection()
if conn:
    # Use a try-block for the query to handle empty tables gracefully
    try:
        query = f"SELECT * FROM daily_weather WHERE city='{city_input}' ORDER BY timestamp DESC"
        df = pd.read_sql(query, conn)
        
        if not df.empty:
            # Metrics
            c1, c2, c3 = st.columns(3)
            latest = df.iloc[0]
            prediction = round(df['temperature'].mean(), 1) # Simple Moving Average

            c1.metric("Current Temp", f"{latest['temperature']}°C")
            c2.metric("Humidity", f"{latest['humidity']}%")
            c3.metric("Predicted (Avg)", f"{prediction}°C")

            # Chart
            fig = px.line(df, x='timestamp', y='temperature', title=f"Temp Trend: {city_input}")
            st.plotly_chart(fig, use_container_width=True)
            
            # Table
            st.dataframe(df)
        else:
            st.warning(f"No records found for {city_input}. Click 'Fetch Live Data' to start.")
            
    except Exception as e:
        st.error(f"Data processing error: {e}")
    finally:
        conn.close()
