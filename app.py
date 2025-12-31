import streamlit as st
import pandas as pd
import mysql.connector
import requests
import plotly.express as px
from mysql.connector import Error

# --- DATABASE CONNECTION ---
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=st.secrets["mysql"]["port"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"]
        )
        return conn
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None

# --- INITIALIZE DATABASE TABLE ---
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

# --- API INTEGRATION ---
def fetch_and_save(city):
    api_key = st.secrets["openweathermap"]["api_key"]
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    response = requests.get(url)
    if response.status_status == 200:
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
        st.error("Failed to fetch data. Check your City Name or API Key.")
        return False

# --- STREAMLIT UI ---
st.set_page_config(page_title="Weather Trends", layout="wide")
init_db()

st.title("☁️ Weather Data Dashboard & Predictor")
st.markdown("Fetching live data from OpenWeatherMap and storing in Cloud MySQL.")

# Sidebar for controls
st.sidebar.header("Settings")
city_input = st.sidebar.text_input("Enter City", "London")

if st.sidebar.button("Update Live Data"):
    with st.spinner('Fetching...'):
        if fetch_and_save(city_input):
            st.sidebar.success(f"Data logged for {city_input}!")

# --- DATA VISUALIZATION ---
conn = get_db_connection()
if conn:
    query = f"SELECT * FROM daily_weather WHERE city='{city_input}' ORDER BY timestamp DESC"
    df = pd.read_sql(query, conn)
    conn.close()

    if not df.empty:
        # 1. Metrics Row
        col1, col2, col3 = st.columns(3)
        latest = df.iloc[0]
        
        # Simple Prediction: Average of last 5 entries
        predicted_temp = round(df['temperature'].head(5).mean(), 1)

        col1.metric("Current Temp", f"{latest['temperature']}°C", f"{latest['description']}")
        col2.metric("Humidity", f"{latest['humidity']}%")
        col3.metric("Predicted (Next Day)", f"{predicted_temp}°C", help="Based on 5-day moving average")

        # 2. Trend Chart
        st.subheader("📈 Temperature Trends")
        fig = px.line(df, x='timestamp', y='temperature', 
                     title=f"Historical Temperature in {city_input}",
                     labels={'timestamp': 'Time', 'temperature': 'Temp (°C)'},
                     template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        # 3. Data Table
        with st.expander("📂 View Historical Logs"):
            st.dataframe(df, use_container_width=True)
    else:
        st.info("No data available for this city yet. Click 'Update Live Data' in the sidebar.")
