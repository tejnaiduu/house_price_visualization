import streamlit as st
import pandas as pd
import plotly.express as px

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="House Price Analytics",
    layout="wide"
)

st.markdown(
    "<h1 style='text-align:center;'>🏠 House Price Analytics Dashboard</h1>",
    unsafe_allow_html=True
)

# =============================
# LOAD DATA
# =============================
@st.cache_data
def load_data():
    df = pd.read_csv("./house_prices_1000_extended.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df

df = load_data()

# =============================
# SIDEBAR FILTERS
# =============================
st.sidebar.header("🔎 Filters")

locations = st.sidebar.multiselect(
    "Location",
    df["location"].unique(),
    default=df["location"].unique()
)

house_types = st.sidebar.multiselect(
    "House Type",
    df["house_type"].unique(),
    default=df["house_type"].unique()
)

bedrooms = st.sidebar.multiselect(
    "Bedrooms",
    sorted(df["bedrooms"].unique()),
    default=sorted(df["bedrooms"].unique())
)

date_range = st.sidebar.date_input(
    "Date Range",
    [df["date"].min(), df["date"].max()]
)

# =============================
# APPLY FILTERS
# =============================
filtered_df = df[
    (df["location"].isin(locations)) &
    (df["house_type"].isin(house_types)) &
    (df["bedrooms"].isin(bedrooms)) &
    (df["date"] >= pd.to_datetime(date_range[0])) &
    (df["date"] <= pd.to_datetime(date_range[1]))
].copy()

if filtered_df.empty:
    st.warning("No data available for selected filters.")
    st.stop()

# =============================
# COLOR THEMES
# =============================
trend_colors = px.colors.qualitative.Set2
bar_colors = px.colors.qualitative.Pastel
growth_colors = px.colors.sequential.Teal
box_colors = px.colors.qualitative.Bold

# =============================
# 📈 PRICE TREND
# =============================
st.subheader("📈 Price Trend Over Time")

line_fig = px.line(
    filtered_df,
    x="date",
    y="price",
    color="location",
    line_dash="house_type",
    markers=True,
    color_discrete_sequence=trend_colors,
    template="plotly_white"
)

st.plotly_chart(line_fig, use_container_width=True)

# ==================================================
# ⭐ MONTH-WISE AVERAGE PRICE BY LOCATION (NEW)
# ==================================================
st.subheader("📊 Month-wise Average Price by Location")

filtered_df["year_month"] = filtered_df["date"].dt.to_period("M").astype(str)

monthly_avg = (
    filtered_df
    .groupby(["year_month", "location"], as_index=False)["price"]
    .mean()
)

month_fig = px.line(
    monthly_avg,
    x="year_month",
    y="price",
    color="location",
    markers=True,
    color_discrete_sequence=trend_colors,
    template="plotly_white"
)

month_fig.update_layout(
    xaxis_title="Month",
    yaxis_title="Average Price (₹)"
)

st.plotly_chart(month_fig, use_container_width=True)

# =============================
# 📊 AVG PRICE BY HOUSE TYPE
# =============================
st.subheader("🏘️ Average Price by House Type")

avg_type = filtered_df.groupby("house_type", as_index=False)["price"].mean()

bar_type_fig = px.bar(
    avg_type,
    x="house_type",
    y="price",
    color="house_type",
    text_auto=".2s",
    template="plotly_white"
)

st.plotly_chart(bar_type_fig, use_container_width=True)

# =============================
# 📦 BOX PLOT
# =============================
st.subheader("📦 Price Distribution by Bedrooms")

box_fig = px.box(
    filtered_df,
    x="bedrooms",
    y="price",
    color="bedrooms",
    template="plotly_white"
)

st.plotly_chart(box_fig, use_container_width=True)

# =============================
# 📈 YEAR-WISE GROWTH %
# =============================
st.subheader("📈 Year-wise Price Growth (%)")

filtered_df["year"] = filtered_df["date"].dt.year

yearly_avg = (
    filtered_df
    .groupby("year", as_index=False)["price"]
    .mean()
    .sort_values("year")
)

yearly_avg["growth_percent"] = yearly_avg["price"].pct_change() * 100
yearly_avg = yearly_avg.dropna()

growth_fig = px.bar(
    yearly_avg,
    x="year",
    y="growth_percent",
    text=yearly_avg["growth_percent"].round(2),
    color="growth_percent",
    color_continuous_scale=growth_colors,
    template="plotly_white"
)

growth_fig.update_layout(coloraxis_showscale=False)

st.plotly_chart(growth_fig, use_container_width=True)

# =============================
# ⭐ KPI METRICS
# =============================
st.subheader("📌 Key Metrics")

c1, c2, c3 = st.columns(3)

c1.metric("Average Price", f"₹ {int(filtered_df.price.mean()):,}")
c2.metric("Maximum Price", f"₹ {int(filtered_df.price.max()):,}")
c3.metric("Minimum Price", f"₹ {int(filtered_df.price.min()):,}")

# =============================
# DATA TABLE
# =============================
with st.expander("📄 View Filtered Data"):
    st.dataframe(filtered_df)
