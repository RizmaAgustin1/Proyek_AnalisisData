import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from babel.numbers import format_currency

# --- Setup Layout ---
st.set_page_config(page_title='Bike Sharing Dashboard', layout='wide')

# --- Fungsi Helper ---
def get_summary_stats(df):
    """Mengembalikan ringkasan statistik dari DataFrame."""
    return df.describe().T 

def rental_trend_per_month(df):
    return df.groupby("mnth")["cnt"].sum().reset_index()

def rental_by_holiday(df):
    return df.groupby(["holiday"])[["casual", "registered", "cnt"]].sum().reset_index()

def rental_by_weather(df):
    return df.groupby(["weathersit", "holiday"])["cnt"].mean().reset_index()

# --- Load Data ---
day_df = pd.read_csv("day.csv")
day_df["dteday"] = pd.to_datetime(day_df["dteday"])
day_df.sort_values(by="dteday", inplace=True)
day_df.reset_index(drop=True, inplace=True)

# --- Sidebar ---
with st.sidebar:
    #Menambahkan logo perusahaan
    st.markdown(
    """
    <div style="text-align: center;">
        <h2>Rizma's Dashboard</h2>
        <img src="https://raw.githubusercontent.com/RizmaAgustin1/Proyek_Analisis_Data/main/logo.png" width="120">
    </div>
    """,
    unsafe_allow_html=True
    )
    start_date, end_date = st.date_input("Pilih rentang", [day_df["dteday"].min(), day_df["dteday"].max()])
    start_date, end_date = pd.to_datetime(start_date), pd.to_datetime(end_date)
    
# --- Filter Data ---
main_df = day_df[(day_df["dteday"] >= start_date) & (day_df["dteday"] <= end_date)]

# --- Dashboard ---
st.title("📊 Bike Sharing Dashboard")
st.markdown("### Analisis Pola Penyewaan Sepeda")

# Metrics berdasarkan rentang tanggal yang dipilih
total_rentals = main_df["cnt"].sum()
avg_rentals_per_day = round(main_df["cnt"].mean(), 2)
highest_rental_day = main_df.loc[main_df["cnt"].idxmax(), "dteday"] if not main_df.empty else None
lowest_rental_day = main_df.loc[main_df["cnt"].idxmin(), "dteday"] if not main_df.empty else None

col1, col2, col3 = st.columns(3)
col1.metric("Total Rentals", value=f"{total_rentals:,}")
col2.metric("Avg Rentals per Day", value=f"{avg_rentals_per_day:,}")

# Menampilkan peak rental day hanya jika ada data dalam rentang tanggal yang dipilih
if highest_rental_day is not None:
    col3.metric("Peak Rental Day", value=highest_rental_day.strftime("%Y-%m-%d"))

# --- Tren Penyewaan Sepeda ---
monthly_rentals = rental_trend_per_month(main_df)
month_names = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
monthly_rentals["mnth"] = monthly_rentals["mnth"].apply(lambda x: month_names[x-1])
fig1 = px.line(monthly_rentals, x="mnth", y="cnt", markers=True, 
               title="Tren Penyewaan Sepeda per Bulan",
               labels={"mnth": "Bulan", "cnt": "Jumlah Penyewaan"})
st.plotly_chart(fig1, use_container_width=True)

# --- Penggunaan Sepeda pada Hari Libur ---
usage_by_holiday = rental_by_holiday(main_df).melt(id_vars="holiday", value_vars=["casual", "registered", "cnt"],
                                                    var_name="user_type", value_name="count")

# Ubah label kategori hari libur
usage_by_holiday["holiday"] = usage_by_holiday["holiday"].map({0: "Hari Kerja", 1: "Hari Libur"})

fig2 = px.bar(usage_by_holiday, x="holiday", y="count", color="user_type", 
              barmode="group", title="Pola Penggunaan Sepeda pada Hari Kerja vs Hari Libur",
              labels={"holiday": "Hari", "count": "Jumlah Penyewaan", "user_type": "Tipe Pengguna"})
st.plotly_chart(fig2, use_container_width=True)

# --- Pengaruh Cuaca terhadap Penyewaan Sepeda ---
weather_impact = rental_by_weather(main_df)

# Ubah label kategori cuaca
weather_impact["weathersit"] = weather_impact["weathersit"].map({1: "Cerah", 2: "Berawan", 3: "Hujan / Buruk"})

fig3 = px.bar(weather_impact, x="weathersit", y="cnt", color="holiday", 
              title="Pengaruh Cuaca terhadap Penyewaan Sepeda",
              labels={"weathersit": "Kondisi Cuaca", "cnt": "Rata-rata Penyewaan", "holiday": "Hari"})
st.plotly_chart(fig3, use_container_width=True)

# --- Korelasi Cuaca & Penyewaan Sepeda ---
weather_cols = ['temp', 'atemp', 'hum', 'windspeed', 'weathersit', 'cnt']
correlation_matrix = main_df[weather_cols].corr()
fig4 = px.imshow(correlation_matrix, text_auto=True, color_continuous_scale="RdBu", 
                 title="Korelasi Cuaca & Penyewaan Sepeda", labels=dict(color="Correlation"))
st.plotly_chart(fig4, use_container_width=True)