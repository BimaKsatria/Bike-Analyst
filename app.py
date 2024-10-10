import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_monthly_user_df(df):
    df['dteday'] = pd.DatetimeIndex(df['dteday']).strftime('%Y-%m')

    monthly_users_df = df.groupby('dteday').agg({
        "casual_y": "sum",    
        "registered_y": "sum" 
    }).reset_index()

    monthly_users_df['total_users'] = monthly_users_df['casual_y'] + monthly_users_df['registered_y']
    monthly_users_df['user_change'] = monthly_users_df['total_users'].diff()
    monthly_users_df['user_change_pct'] = (monthly_users_df['user_change'] / monthly_users_df['total_users'].shift(1)) * 100

    return monthly_users_df

def create_users_by_season_df(df):
    users_by_season_df = all_df.groupby('season').agg({
        "casual_y": "sum",     # Jumlah total pengguna casual per musim
        "registered_y": "sum"  # Jumlah total pengguna terdaftar per musim
    }).reset_index()

    # Hitung total pengguna (casual + registered) per musim
    users_by_season_df['total_users'] = users_by_season_df['casual_y'] + users_by_season_df['registered_y']
    return users_by_season_df

def create_user_by_holiday(df):
    # Mengonversi kolom 'dteday' menjadi datetime
    all_df['dteday'] = pd.to_datetime(all_df['dteday'])

    # Menambahkan kolom 'day_type' untuk menandai weekday/weekend
    all_df['day_type'] = all_df['dteday'].dt.day_name().apply(lambda x: 'Weekend' if x in ['Saturday', 'Sunday'] else 'Weekday')

    # Menghitung total peminjaman untuk weekday dan weekend
    weekday_total = all_df[all_df['day_type'] == 'Weekday']['count_y'].sum()
    weekend_total = all_df[all_df['day_type'] == 'Weekend']['count_y'].sum()

    # Membuat DataFrame untuk visualisasi
    total_counts = pd.DataFrame({
        'day_type': ['Hari Kerja', 'Hari Libur'],
        'total_rentals': [weekday_total, weekend_total]
    })
    return total_counts

def create_daily_users_df(df):
    # Mengelompokkan data berdasarkan nama hari dan menghitung total peminjaman per hari
    daily_usage = all_df.groupby('weekday').agg({
        "count_y": "sum"  # Menghitung total peminjaman per hari
    }).reset_index()

    # Mengurutkan hari sesuai urutan dalam seminggu
    days_order = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']  # Pastikan nama hari sesuai
    daily_usage['weekday'] = pd.Categorical(daily_usage['weekday'], categories=days_order, ordered=True)
    daily_usage = daily_usage.sort_values('weekday')
    return daily_usage


all_df = pd.read_csv("all_data.csv")

# Memastikan kolom dteday ada
all_df['dteday'] = pd.to_datetime(all_df['dteday'])

# Mengambil min dan max date
min_date = all_df["dteday"].min()
max_date = all_df["dteday"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://raw.githubusercontent.com/BimaKsatria/Dataset/refs/heads/main/Assets/bicyclecrew_com.jfif")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date.date(),
        max_value=max_date.date(),
        value=[min_date.date(), max_date.date()]
    )

# Konversi start_date dan end_date dari format date_input (datetime.date) ke pd.Timestamp
start_date = pd.Timestamp(start_date)
end_date = pd.Timestamp(end_date)

# Filter DataFrame berdasarkan rentang tanggal
main_df = all_df[(all_df["dteday"] >= start_date) & (all_df["dteday"] <= end_date)]

# Mengupdate DataFrame berdasarkan data yang sudah difilter
monthly_users_df = create_monthly_user_df(main_df)
users_by_season_df = create_users_by_season_df(main_df)
total_counts = create_user_by_holiday(main_df)
daily_usage = create_daily_users_df(main_df)

st.header('Analis Data Bike Sharing :sparkles:')
st.subheader('Banyak Pengguna Bulanan')

# Membuat dua kolom di Streamlit
col1, col2 = st.columns(2)

with col1:
    total_users = monthly_users_df['total_users'].sum()
    st.metric("Total Pengguna", value=total_users)

with col2:
    latest_user_change = monthly_users_df['user_change'].iloc[-1]
    st.metric("Perubahan Bulanan", value=latest_user_change)

# Visualisasi data menggunakan matplotlib
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    monthly_users_df["dteday"], monthly_users_df["total_users"],
    marker='o', linewidth=2, label="Total Users", color="#90CAF9"
)

# Menambahkan judul dan label
ax.set_title("Total Pengguna per Bulan", fontsize=20)
ax.set_xlabel("Bulan", fontsize=15)
ax.set_ylabel("Total Pengguna", fontsize=15)

# Menambah ukuran label pada sumbu
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

# Membuat label bulan (x-axis) miring
ax.set_xticklabels(monthly_users_df["dteday"], fontsize=15, rotation=45, fontstyle='italic')

# Menambahkan legenda
ax.legend(fontsize=15)

# Menampilkan plot di Streamlit
st.pyplot(fig)

st.subheader("Dampak Cuaca Terhadap Pengguna Sepeda")

fig, ax = plt.subplots(figsize=(16, 8))

sns.barplot(
    y="total_users",  
    x="season",  
    data=users_by_season_df.sort_values(by="total_users", ascending=False),
    ax=ax
)

ax.set_title("Jumlah Pengguna Berdasarkan Musim", loc="center", fontsize=20)
ax.set_ylabel("Jumlah Pengguna", fontsize=15)
ax.set_xlabel("Musim", fontsize=15)
ax.tick_params(axis='x', labelsize=20)
ax.tick_params(axis='y', labelsize=15)

st.pyplot(fig)

st.subheader("Total Peminjaman Sepeda Pada Hari kerja dan Hari Libur")
plt.figure(figsize=(16, 8))
sns.barplot(data=total_counts, x='day_type', y='total_rentals')
plt.title('Total Peminjaman Sepeda: Weekday vs Weekend', fontsize=20)
plt.ylabel('Total Peminjaman', fontsize=15)
plt.xlabel('Tipe Hari', fontsize=15)
st.pyplot(plt)


st.subheader("Total Peminjaman Sepeda per Hari dalam Seminggu")
fig, ax = plt.subplots(figsize=(16, 6))
ax.pie(daily_usage['count_y'], labels=daily_usage['weekday'], autopct='%1.1f%%', startangle=140, colors=sns.color_palette('viridis', len(daily_usage)))
plt.axis('equal')  # Equal aspect ratio ensures that pie chart is a circle.
plt.show()
st.pyplot(fig)
