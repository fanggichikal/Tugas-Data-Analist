import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sn
import streamlit as st
from babel.numbers import format_currency

data = pd.read_csv("D:/BelajarPython/submition/dashboard/maindatautama.csv")
data.head()
# print(data.head())

data.info()
# print(data.info())
# print(data.columns)

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_approved_at').agg({
        "order_id": "nunique",
        "price_x": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price_x": "revenue"
    }, inplace=True)
    
    return daily_orders_df

def create_sum_product_df(df):
    bysum_product_df = df.groupby("product_category_name").price_x.sum().sort_values(ascending=False).reset_index()
    return bysum_product_df

def create_customerreview_df(df):
   bycustomerreview_df = df.groupby(by="review_score").customer_id.nunique().reset_index()
   bycustomerreview_df.rename(columns={
    "customer_id": "customer_count"
}, inplace=True)    
   
   return bycustomerreview_df
    

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_approved_at": "max", #mengambil tanggal order terakhir
        "order_id": "nunique",
        "price_x": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_approved_at"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df

datetime_columns = ["order_approved_at", "order_estimated_delivery_date"]
data.sort_values(by="order_approved_at", inplace=True)
data.reset_index(inplace=True)
 
for column in datetime_columns:
    data[column] = pd.to_datetime(data[column])
    
min_date = data["order_approved_at"].min()
max_date = data["order_approved_at"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
main_df = data[(data["order_approved_at"] >= str(start_date)) & 
                (data["order_approved_at"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
bysum_product_df = create_sum_product_df(main_df)
bycustomerreview_df = create_customerreview_df(main_df)
rfm_df = create_rfm_df(main_df)

st.header('Dashboard :')

st.subheader('Daily Orders')
 
col1, col2 = st.columns(2)
 
with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "AUD", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)


st.subheader("Best & Worst Performing Product")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
 
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
sn.barplot(x="price_x", y="product_category_name", data=bysum_product_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)
 
sn.barplot(x="price_x", y="product_category_name", data=bysum_product_df.sort_values(by="price_x", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
 
st.pyplot(fig)


st.subheader("Best & Worst Customer Review")
 
# Periksa bahwa kolom yang digunakan benar
fig, ax = plt.subplots(figsize=(20, 10))

# Pastikan 'byreview_df' sudah diurutkan dengan benar
sorted_df = bycustomerreview_df.sort_values(by="customer_count", ascending=False)

# Membuat barplot
sn.barplot(
    y="customer_count",  # Variabel yang ingin diplot di sumbu Y
    x="review_score",    # Variabel yang ingin diplot di sumbu X
    data=sorted_df,      # Data yang digunakan
    palette='Blues',     # Ganti dengan palette warna yang sesuai (misalnya 'Blues')
    ax=ax                # Pastikan ax digunakan dengan benar
)

# Menambahkan judul dan penyesuaian label
ax.set_title("Number of Customers by Review Score", loc="center", fontsize=50)
ax.set_ylabel(None)
ax.set_xlabel("Review Score", fontsize=35)  # Set label X jika diperlukan
ax.tick_params(axis='x', labelsize=35)
ax.tick_params(axis='y', labelsize=30)

# Menampilkan plot di Streamlit
st.pyplot(fig)

st.subheader("Best Customer Based on RFM Parameters")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
 
sn.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)
 
sn.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)
 
sn.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)
 
st.pyplot(fig)
 
st.caption('Copyright (c) Dicoding 2023')
