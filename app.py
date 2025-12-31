import streamlit as st
import pandas as pd
import mysql.connector

st.set_page_config(page_title="Weather Trends", page_icon="🌦️")
st.title("🌦️ Weather Trend Dashboard")

def get_historical_data():
    try:
        # These keys must match exactly what you type in Streamlit Secrets
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            port=st.secrets["mysql"]["port"]
        )
        query = "SELECT city, temperature, humidity, pressure, description, recorded_at FROM weather_logs ORDER BY recorded_at DESC LIMIT 100"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return pd.DataFrame()

data = get_historical_data()

if not data.empty:
    city_name = data['city'].iloc[0]
    st.subheader(f"Recent Trends for {city_name}")
    
    # Metrics row
    col1, col2, col3 = st.columns(3)
    col1.metric("Current Temp", f"{data['temperature'].iloc[0]}°C")
    col2.metric("Humidity", f"{data['humidity'].iloc[0]}%")
    col3.metric("Pressure", f"{data['pressure'].iloc[0]} hPa")

    # Interactive Chart
    st.write("### Temperature over Time")
    chart_data = data.set_index('recorded_at')[['temperature']]
    st.line_chart(chart_data)

    # Data Table
    with st.expander("View Raw Log Data"):
        st.dataframe(data)
else:
    st.warning("No data found in the cloud database. Run 'code.py' locally to push some data!")
