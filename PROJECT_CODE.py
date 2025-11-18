import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ----------------------------------------------------
# 🌆 PAGE CONFIGURATION
# ----------------------------------------------------
st.set_page_config(
    page_title="India Air Quality Dashboard",
    layout="wide",
    page_icon="🌍",
)

# ----------------------------------------------------
# 🎨 CUSTOM STYLING
# ----------------------------------------------------
st.markdown("""
    <style>
        .main {
            background-color: #f8f9fa;
        }
        h1, h2, h3 {
            color: #2b2d42;
        }
        .stMetric {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .css-1v3fvcr {
            background-color: #ffffff;
        }
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 🧾 TITLE
# ----------------------------------------------------
st.title("🌆 India Air Quality Monitoring Dashboard")
st.markdown("### 📊 Analyze air pollution trends across Indian cities with real-time insights")

# ----------------------------------------------------
# 📂 LOAD DATA
# ----------------------------------------------------
try:
    df = pd.read_csv("city_day.csv")
    st.success("✅ Data loaded successfully!")
except Exception as e:
    st.error("❌ Error loading CSV file.")
    st.stop()

# ----------------------------------------------------
# 🧹 CLEAN DATA
# ----------------------------------------------------
if 'Datetime' in df.columns:
    df['Date'] = pd.to_datetime(df['Datetime'], errors='coerce')
else:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

df = df.dropna(subset=['City', 'Date'])
df = df.sort_values(by='Date')

# ----------------------------------------------------
# 🎛️ SIDEBAR FILTERS
# ----------------------------------------------------
st.sidebar.header("🧭 Filter Options")

cities = sorted(df['City'].unique())
selected_cities = st.sidebar.multiselect("🏙️ Select Cities", cities, default=["Delhi", "Mumbai", "Chennai"])

date_range = st.sidebar.date_input(
    "📅 Select Date Range",
    [df['Date'].min(), df['Date'].max()]
)

pollutants = ['PM2.5', 'PM10', 'NO2', 'SO2', 'O3', 'CO']
selected_pollutant = st.sidebar.selectbox("🌫️ Select Pollutant", pollutants)

# Filter data
mask = (
    (df['City'].isin(selected_cities)) &
    (df['Date'] >= pd.Timestamp(date_range[0])) &
    (df['Date'] <= pd.Timestamp(date_range[-1]))
)
filtered_df = df.loc[mask]

# ----------------------------------------------------
# 📊 KPI METRICS
# ----------------------------------------------------
st.markdown("## 🌍 Overall Air Quality Indicators")

col1, col2, col3 = st.columns(3)
if 'AQI' in filtered_df.columns and not filtered_df.empty:
    avg_aqi = filtered_df['AQI'].mean()
    worst_city = filtered_df.groupby('City')['AQI'].mean().idxmax()
    best_city = filtered_df.groupby('City')['AQI'].mean().idxmin()

    col1.metric("Average AQI", f"{avg_aqi:.1f}")
    col2.metric("Worst Air Quality City", worst_city)
    col3.metric("Best Air Quality City", best_city)
else:
    st.warning("⚠️ AQI data not found in dataset.")

# ----------------------------------------------------
# 🌫️ POLLUTANT TRENDS (LINE CHART)
# ----------------------------------------------------
st.markdown("## 📈 Pollutant Level Trends")

fig = px.line(
    filtered_df,
    x="Date",
    y=selected_pollutant,
    color="City",
    title=f"{selected_pollutant} Levels Over Time",
    template="plotly_white",
    markers=True
)
fig.update_layout(legend_title_text="City", title_font=dict(size=20))
st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# 🏙️ CITY-WISE AQI COMPARISON (BAR CHART)
# ----------------------------------------------------
st.markdown("## 🏙️ Average AQI Comparison Between Cities")

if 'AQI' in filtered_df.columns:
    aqi_avg = filtered_df.groupby('City')['AQI'].mean().reset_index()
    fig2 = px.bar(
        aqi_avg,
        x="City",
        y="AQI",
        color="AQI",
        color_continuous_scale="RdYlGn_r",
        title="Average AQI by City",
        template="plotly_white",
    )
    st.plotly_chart(fig2, use_container_width=True)

# ----------------------------------------------------
# 📦 POLLUTANT DISTRIBUTION (BOX PLOT)
# ----------------------------------------------------
st.markdown("## 📦 Pollutant Distribution Across Cities")

fig3 = px.box(
    filtered_df,
    x="City",
    y=selected_pollutant,
    color="City",
    title=f"{selected_pollutant} Distribution",
    template="plotly_white"
)
st.plotly_chart(fig3, use_container_width=True)

# ----------------------------------------------------
# 🚦 AQI ALERTS
# ----------------------------------------------------
st.markdown("## 🚦 Latest AQI Alerts")

for city in selected_cities:
    city_data = filtered_df[filtered_df['City'] == city]
    if 'AQI' in city_data.columns and not city_data['AQI'].dropna().empty:
        latest_aqi = city_data['AQI'].iloc[-1]
        if latest_aqi <= 50:
            st.success(f"✅ {city}: Good (AQI: {latest_aqi:.1f})")
        elif latest_aqi <= 100:
            st.info(f"🟡 {city}: Moderate (AQI: {latest_aqi:.1f})")
        elif latest_aqi <= 200:
            st.warning(f"🟠 {city}: Poor (AQI: {latest_aqi:.1f})")
        else:
            st.error(f"🔴 {city}: Severe (AQI: {latest_aqi:.1f})")
    else:
        st.write(f"{city}: No recent AQI data available.")
