import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Page configuration
st.set_page_config(page_title="African Climate Dashboard", layout="wide")

# Title
st.title(" African Climate Trend Analysis")
st.markdown("### Supporting Ethiopia's COP32 Preparations")
st.markdown("**Data Source:** NASA POWER (2015-2026)")

# Load data function
@st.cache_data
def load_data():
    countries = ['ethiopia', 'kenya', 'nigeria', 'sudan', 'tanzania']
    dfs = []
    for country in countries:
        df = pd.read_csv(f'data/{country}.csv')
        df = df.replace(-999, np.nan)
        df['Country'] = country.capitalize()
        df['Date'] = pd.to_datetime(df['YEAR'].astype(str) + df['DOY'].astype(str).str.zfill(3), format='%Y%j')
        df['Year'] = df['Date'].dt.year
        df['Month'] = df['Date'].dt.month
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)

# Load data
df = load_data()

# Sidebar filters
st.sidebar.header(" Filters")

# Country multi-select
countries = st.sidebar.multiselect(
    "Select Countries",
    options=df['Country'].unique(),
    default=df['Country'].unique().tolist()
)

# Year range slider
min_year = int(df['Year'].min())
max_year = int(df['Year'].max())
year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Variable selector
variable = st.sidebar.selectbox(
    "Select Variable",
    options=['T2M', 'PRECTOTCORR', 'RH2M', 'WS2M'],
    format_func=lambda x: {
        'T2M': ' Temperature (°C)',
        'PRECTOTCORR': ' Rainfall (mm/day)',
        'RH2M': ' Humidity (%)',
        'WS2M': ' Wind Speed (m/s)'
    }.get(x, x)
)

# Variable labels
var_labels = {
    'T2M': 'Temperature (°C)',
    'PRECTOTCORR': 'Rainfall (mm/day)',
    'RH2M': 'Humidity (%)',
    'WS2M': 'Wind Speed (m/s)'
}

# Filter data
filtered_df = df[
    (df['Country'].isin(countries)) &
    (df['Year'] >= year_range[0]) &
    (df['Year'] <= year_range[1])
]

# Dashboard layout - two columns
col1, col2 = st.columns(2)

# Plot 1: Time Series
with col1:
    st.subheader(f" {var_labels[variable]} - Time Series")
    fig, ax = plt.subplots(figsize=(10, 5))
    for country in countries:
        country_data = filtered_df[filtered_df['Country'] == country]
        monthly_avg = country_data.groupby('Date')[variable].mean().reset_index()
        ax.plot(monthly_avg['Date'], monthly_avg[variable], label=country, linewidth=1.5)
    ax.set_xlabel('Date')
    ax.set_ylabel(var_labels[variable])
    ax.set_title(f'{var_labels[variable]} Comparison (2015-2026)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

# Plot 2: Boxplot
with col2:
    st.subheader(f" {var_labels[variable]} - Distribution")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(x='Country', y=variable, data=filtered_df, ax=ax)
    ax.set_xlabel('Country')
    ax.set_ylabel(var_labels[variable])
    ax.set_title(f'{var_labels[variable]} Distribution by Country')
    plt.xticks(rotation=45)
    st.pyplot(fig)

# Plot 3: Monthly Average (Bar Chart)
st.subheader(f" Monthly Average {var_labels[variable]}")
monthly_avg = filtered_df.groupby(['Country', 'Month'])[variable].mean().reset_index()
fig, ax = plt.subplots(figsize=(12, 6))
for country in countries:
    country_data = monthly_avg[monthly_avg['Country'] == country]
    ax.plot(country_data['Month'], country_data[variable], marker='o', linewidth=1.5, label=country)
ax.set_xlabel('Month')
ax.set_ylabel(var_labels[variable])
ax.set_title(f'Monthly Average {var_labels[variable]}')
ax.set_xticks(range(1, 13))
ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
ax.legend()
ax.grid(True, alpha=0.3)
st.pyplot(fig)

# Summary Statistics
st.subheader(" Summary Statistics")
st.dataframe(filtered_df.groupby('Country')[variable].describe().round(2))

# Footer
st.markdown("---")
st.markdown("**Prepared for:** Ethiopian Ministry of Planning and Development | COP32 (Addis Ababa, 2027)")