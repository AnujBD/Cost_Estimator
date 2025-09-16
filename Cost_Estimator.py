import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- Page Config ---
st.set_page_config(page_title="❄️ Snowflake Cost Estimator", layout="wide")
st.title("❄️ Snowflake Cost Estimator")
st.markdown("Estimate your **annual Snowflake costs** and explore **potential savings**.")

# --- Sidebar Inputs ---
st.sidebar.header("Enter Your Snowflake Usage Details")

# Compute Inputs
num_vws = st.sidebar.number_input("Number of Virtual Warehouses", min_value=1, value=2)
vw_size = st.sidebar.selectbox("Warehouse Size", ["X-Small", "Small", "Medium", "Large", "X-Large"])
hours_per_day = st.sidebar.number_input("Average Hours per Day", min_value=1, value=12)
active_days_per_month = st.sidebar.slider("Active Days per Month", 1, 31, 22)

# Smooth Growth Setting for Compute
compute_growth = st.sidebar.slider("Monthly Compute Growth (%)", 0, 20, 0)

# Storage Inputs
storage_tb = st.sidebar.number_input("Average Storage (TB)", min_value=0.0, value=5.0)
storage_growth = st.sidebar.slider("Monthly Storage Growth (%)", 0, 20, 2)

# Data Transfer Inputs
data_transfer_tb = st.sidebar.number_input("Data Transfer Out (TB)", min_value=0.0, value=1.0)
transfer_growth = st.sidebar.slider("Monthly Data Transfer Growth (%)", 0, 20, 3)

# Discount
discount_pct = st.sidebar.slider("Base Discount (%)", 0, 50, 0)

# Savings Optimization
st.sidebar.header("Potential Savings Options")
pause_hours_per_day = st.sidebar.number_input("Pause Hours Per Day (Compute Savings)", min_value=0, max_value=24, value=0)
reduce_vw_size = st.sidebar.selectbox("Optional Reduced Warehouse Size", ["Same", "X-Small", "Small", "Medium", "Large"])
additional_discount = st.sidebar.slider("Extra Discount (%) if optimizing usage", 0, 50, 0)

# --- Pricing Constants ---
CREDIT_COST = 2.0  # $ per credit
STORAGE_COST_PER_TB = 40  # $ per TB/month
DATA_TRANSFER_COST_PER_TB = 90  # $ per TB/month
size_credit_mapping = {"X-Small": 1, "Small": 2, "Medium": 4, "Large": 8, "X-Large": 16}

# --- Monthly Computation ---
# FIX: use 'ME' instead of deprecated 'M'
months = pd.date_range(start="2024-01-01", periods=12, freq='ME').strftime("%b")

compute_costs, storage_costs, transfer_costs = [], [], []
storage_current = storage_tb
transfer_current = data_transfer_tb

for month in range(12):
    # Smooth growth for compute based on sidebar selection
    monthly_compute = (
        num_vws * size_credit_mapping[vw_size] * hours_per_day *
        active_days_per_month * CREDIT_COST * (1 + (month * compute_growth / 100))
    )
    compute_costs.append(monthly_compute)

    # Storage growth
    monthly_storage = storage_current * STORAGE_COST_PER_TB
    storage_costs.append(monthly_storage)
    storage_current *= (1 + storage_growth / 100)

    # Data transfer growth
    monthly_transfer = transfer_current * DATA_TRANSFER_COST_PER_TB
    transfer_costs.append(monthly_transfer)
    transfer_current *= (1 + transfer_growth / 100)

# Apply base discount
compute_costs = [c * (1 - discount_pct / 100) for c in compute_costs]
storage_costs = [s * (1 - discount_pct / 100) for s in storage_costs]
transfer_costs = [t * (1 - discount_pct / 100) for t in transfer_costs]

total_costs = np.array(compute_costs) + np.array(storage_costs) + np.array(transfer_costs)
total_annual_cost = total_costs.sum()

# --- Savings Optimization ---
optimized_size_credit = size_credit_mapping[vw_size] if reduce_vw_size == "Same" else size_credit_mapping[reduce_vw_size]

optimized_compute_costs = []
storage_current_opt = storage_tb
transfer_current_opt = data_transfer_tb

for month in range(12):
    effective_hours = max(hours_per_day - pause_hours_per_day, 0)
    monthly_compute_opt = (
        num_vws * optimized_size_credit * effective_hours *
        active_days_per_month * CREDIT_COST * (1 + (month * compute_growth / 100))
    )
    optimized_compute_costs.append(monthly_compute_opt)

    storage_current_opt *= (1 + storage_growth / 100)
    transfer_current_opt *= (1 + transfer_growth / 100)

# Apply combined discount for optimized costs
total_discount_opt = discount_pct + additional_discount
optimized_compute_costs = [c * (1 - total_discount_opt / 100) for c in optimized_compute_costs]
optimized_storage_costs = [s * (1 - total_discount_opt / 100) for s in storage_costs]
optimized_transfer_costs = [t * (1 - total_discount_opt / 100) for t in transfer_costs]

total_optimized_costs = (
    np.array(optimized_compute_costs) +
    np.array(optimized_storage_costs) +
    np.array(optimized_transfer_costs)
)
total_optimized_annual = total_optimized_costs.sum()

total_savings = total_annual_cost - total_optimized_annual
savings_pct = (total_savings / total_annual_cost) * 100 if total_annual_cost > 0 else 0

# --- Results Display ---
st.header("💰 Annual Cost Estimate")
st.metric("Total Annual Cost", f"${total_annual_cost:,.2f}")

# --- Cost Breakdown Table ---
st.subheader("Cost Breakdown")
cost_breakdown = pd.DataFrame({
    "Category": ["Compute", "Storage", "Data Transfer"],
    "Cost": [sum(compute_costs), sum(storage_costs), sum(transfer_costs)]
})

# Create a separate display dataframe for formatted cost
cost_breakdown_display = cost_breakdown.copy()
cost_breakdown_display["Cost"] = cost_breakdown_display["Cost"].apply(lambda x: f"${x:,.0f}")
st.table(cost_breakdown_display)

# --- Pie Chart ---
fig_pie = px.pie(
    cost_breakdown,
    names='Category',
    values='Cost',
    title='Cost Distribution',
    hover_data={'Cost': ':.2f'}
)
fig_pie.update_traces(
    hovertemplate='%{label}: $%{value:,.2f} <br>(%{percent})',
    textinfo='percent+label'
)
st.plotly_chart(fig_pie, use_container_width=True)

# --- Monthly Stacked Bar Chart ---
monthly_df = pd.DataFrame({
    "Month": months,
    "Compute": compute_costs,
    "Storage": storage_costs,
    "Data Transfer": transfer_costs
})

fig_bar = px.bar(
    monthly_df,
    x="Month",
    y=["Compute", "Storage", "Data Transfer"],
    title="Monthly Cost Breakdown",
    labels={"value": "Cost ($)", "variable": "Category"},
    hover_data={"value": ":,.2f"}
)
fig_bar.update_traces(hovertemplate='%{x}: $%{value:,.2f}')
st.plotly_chart(fig_bar, use_container_width=True)

# --- Monthly Total Cost Line Chart ---
fig_line = px.line(
    monthly_df,
    x="Month",
    y=total_costs,
    title="Monthly Total Cost Trend",
    labels={"y": "Total Cost ($)"}
)
fig_line.update_traces(hovertemplate='%{x}: $%{y:,.2f}')
st.plotly_chart(fig_line, use_container_width=True)

# --- Potential Savings Section ---
st.header("💡 Potential Savings After Optimization")
st.metric(
    "Annual Cost After Optimization",
    f"${total_optimized_annual:,.2f}",
    delta=f"-${total_savings:,.2f} ({savings_pct:.1f}%)"
)

savings_df = pd.DataFrame({
    "Category": ["Compute", "Storage", "Data Transfer"],
    "Current Cost": [sum(compute_costs), sum(storage_costs), sum(transfer_costs)],
    "Optimized Cost": [sum(optimized_compute_costs), sum(optimized_storage_costs), sum(optimized_transfer_costs)]
})

fig_savings = px.bar(
    savings_df,
    x="Category",
    y=["Current Cost", "Optimized Cost"],
    title="Cost Savings by Category",
    barmode="group",
    labels={"value": "Cost ($)", "variable": "Status"},
    hover_data={"value": ":,.2f"}
)
fig_savings.update_traces(hovertemplate='%{x}: $%{value:,.2f}')
st.plotly_chart(fig_savings, use_container_width=True)
