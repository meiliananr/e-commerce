import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from babel.numbers import format_currency

sns.set(style='dark')

st.title("Proyek Analisis Data Dashboard")
st.text('Meiliana Nurul Rahmah')
st.header('E-Commerce')

# Load data
order = st.file_uploader("Order", type=["csv"])
if order is not None:
    order = pd.read_csv(order)
costumer = st.file_uploader("costumer", type=["csv"])
if costumer is not None:
    costumer = pd.read_csv(costumer)
produk = st.file_uploader("produk", type=["csv"])
if produk is not None:
    produk = pd.read_csv(produk)
item = st.file_uploader("order_item", type=["csv"])
if item is not None:
    item = pd.read_csv(item)

# Merge data
order['order_id'] = order['order_id'].astype(str)
item['order_id'] = item['order_id'].astype(str)
merged_data = pd.merge(order, item, on='order_id')

merged_data['product_id'] = merged_data['product_id'].astype(str)
produk['product_id'] = produk['product_id'].astype(str)
dataset = pd.merge(merged_data, produk, on='product_id')

dataset['customer_id'] = dataset['customer_id'].astype(str)
costumer['customer_id'] = costumer['customer_id'].astype(str)
data = pd.merge(dataset, costumer, on='customer_id')

# Function to create daily orders dataframe
def create_daily_orders_df(data):
    daily_orders_df = data.resample(rule='D', on='order_approved_at').agg({
        "order_id": "nunique",
        "price": "sum"
    }).reset_index()
    daily_orders_df.rename(columns={"order_id": "order_count", "price": "revenue"}, inplace=True)
    return daily_orders_df

# Function to create sum order items dataframe
def create_sum_order_items_df(data):
    return data.groupby("product_category_name")["product_photos_qty"].sum().sort_values(ascending=False).reset_index()

# Function to create by city dataframe
def create_bycity_df(data):
    bycity_df = data.groupby(by="customer_city").customer_id.nunique().reset_index()
    bycity_df.rename(columns={"customer_id": "customer_count"}, inplace=True)
    return bycity_df

data['amount'] = data['freight_value'] + data['price']

# Function to create RFM dataframe
def create_rfm_df(data):
    rfm_df = data.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max",
        "order_id": "nunique",
        "amount": "sum"
    })
    rfm_df.columns = ["customer_id", "order_purchase_timestamp", "frequency", "monetary"]
    rfm_df["order_purchase_timestamp"] = rfm_df["order_purchase_timestamp"].dt.date
    recent_date = data["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["order_purchase_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("order_purchase_timestamp", axis=1, inplace=True)
    return rfm_df

# Sidebar for date input
with st.sidebar:
    st.image("https://tse4.mm.bing.net/th?id=OIP.zJ8vShkW1E62A9g14Lh9mAHaDl&pid=Api&P=0&h=180")
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=data["order_approved_at"].min(), max_value=data["order_approved_at"].max(),
        value=[data["order_approved_at"].min(), data["order_approved_at"].max()]
    )

# Filtering data based on selected date range
main_df = data[
    (data['order_purchase_timestamp'] >= start_date) &
    (data['order_purchase_timestamp'] <= end_date)
]

# Analytical section
daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
bycity_df = create_bycity_df(main_df)
rfm_df = create_rfm_df(main_df)

# Visualization section
st.subheader('Daily Orders')
col1, col2 = st.columns(2)
with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)

with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "IDR", locale='es_CO')
    st.metric("Total Revenue", value=total_revenue)

fig1, ax = plt.subplots(figsize=(16, 8))
ax.plot(daily_orders_df["order_approved_at"], daily_orders_df["order_count"], marker='o', linewidth=2, color="#90CAF9")
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot_chart(fig1)

st.subheader("Best & Worst Performing Product")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(x="product_photos_qty", y="product_category_name", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x="product_photos_qty", y="product_category_name", data=sum_order_items_df.sort_values(by="product_photos_qty", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot_chart(fig)

st.subheader("Number of Customer by City")
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
fig2, ax = plt.subplots(figsize=(20, 10))
ax = sns.barplot(x="customer_count", y="customer_city", data=bycity_df.sort_values(by="customer_count", ascending=False).head(5), palette= colors)
ax.set_ylabel(None)
ax.set_xlabel("Costumer Count", fontsize=30)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=20)
st.pyplot_chart(fig2)

st.subheader("Best Customer Based on RFM Parameters")
col1, col2, col3 = st.columns(3)
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "IDR", locale='es_CO')
    st.metric("Average Monetary", value=avg_frequency)

text = st.text_area('Feedback')
st.write('Feedback: ', text)
