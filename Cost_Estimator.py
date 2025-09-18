import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- Page Config ---
st.set_page_config(page_title="❄️ Snowflake Cost Estimator", layout="wide")
st.title("❄️ Snowflake Cost Estimator")
st.markdown("Estimate your **annual Snowflake costs** and explore **potential savings**, including **Gen 2 Warehouse benefits**.")

# --- Sidebar Inputs ---
st.sidebar.header("Enter Your Snowflake Usage Details")

# Gen 2 Warehouse Toggle
use_gen2 = st.sidebar.checkbox("Enable Gen 2 Warehouse Pricing", value=False)

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

# --- Helper function for Gen 2 scaling discount ---
def gen2_scaling_discount(num_warehouses):
    """Applies up to 20% discount for scaling Gen 2 warehouses."""
    additional_discount = min((num_warehouses - 1) * 0.05, 0.20) if num_warehouses > 1 else 0
    return 1 - additional_discount

# --- Monthly Computation ---
months = pd.date_range(start="2024-01-01", periods=12, freq='ME').strftime("%b")

compute_costs, storage_costs, transfer_costs = [], [], []
storage_current = storage_tb
transfer_current = data_transfer_tb

for month in range(12):
    base_credits = num_vws * size_credit_mapping[vw_size] * hours_per_day * active_days_per_month

    # Adjust compute cost for Gen 2 if enabled
    if use_gen2:
        # 30% more efficient credits
        base_credits *= 0.70
        # Scaling efficiency for multiple warehouses
        base_credits *= gen2_scaling_discount(num_vws)

    monthly_compute = base_credits * CREDIT_COST * (1 + (month * compute_growth / 100))
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
    base_credits_opt = num_vws * optimized_size_credit * effective_hours * active_days_per_month

    if use_gen2:
        # Gen 2 adjustments
        base_credits_opt *= 0.70  # 30% more efficient
        base_credits_opt *= gen2_scaling_discount(num_vws)
        # Additional 10% efficiency for paused hours
        if pause_hours_per_day > 0:
            base_credits_opt *= 0.90

    monthly_compute_opt = base_credits_opt * CREDIT_COST * (1 + (month * compute_growth / 100))
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
st.markdown(
    f"""
    <div style='
        display: flex;
        flex-wrap: nowrap;
        align-items: center;
        gap: 15px;
        white-space: nowrap;
        padding: 15px 20px;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        background-color: #f9fafb;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        width: fit-content;
        margin: 20px auto;
    '>
        <h2 style='margin: 0; font-weight: 600; color: #333;'>💰 Total Annual Cost:</h2>
        <h2 style='margin: 0; font-weight: 700; color: #2E86C1;'>${total_annual_cost:,.2f}</h2>
    </div>
    """,
    unsafe_allow_html=True
)






if use_gen2:
    st.success("Gen 2 Warehouse pricing applied: **30% credit efficiency**, scaling discounts, and pause optimization.")

# --- Cost Breakdown Table ---
st.subheader("Cost Breakdown")

cost_breakdown = pd.DataFrame({
    "Category": ["Compute", "Storage", "Data Transfer"],
    "Cost": [sum(compute_costs), sum(storage_costs), sum(transfer_costs)]
})

# Format the cost values
cost_breakdown_display = cost_breakdown.copy()
cost_breakdown_display["Cost"] = cost_breakdown_display["Cost"].apply(lambda x: f"${x:,.0f}")

# Display as dataframe without index
st.dataframe(cost_breakdown_display, hide_index=True)



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

# --- Monthly Stacked Bar Chart with Total Labels ---
monthly_df = pd.DataFrame({
    "Month": months,
    "Compute": compute_costs,
    "Storage": storage_costs,
    "Data Transfer": transfer_costs
})

# Calculate total for each month
monthly_df["Total"] = monthly_df[["Compute", "Storage", "Data Transfer"]].sum(axis=1)

# Create stacked bar chart
fig_bar = px.bar(
    monthly_df,
    x="Month",
    y=["Compute", "Storage", "Data Transfer"],
    title="Monthly Cost Breakdown",
    labels={"value": "Cost ($)", "variable": "Category"},
    hover_data={"value": ":,.2f"}
)

# Update bar hovertemplate
fig_bar.update_traces(hovertemplate='%{x}: $%{value:,.2f}')

# --- Add total cost as text above each stacked bar ---
# Calculate the top position of each bar
for i, month in enumerate(monthly_df["Month"]):
    total = monthly_df.loc[i, "Total"]
    fig_bar.add_annotation(
        x=month,
        y=total,
        text=f"${total:,.0f}",  # formatted total value
        showarrow=False,
        font=dict(size=12, color="#333", family="Arial"),
        yshift=8  # position slightly above the bar
    )

# Improve overall layout
fig_bar.update_layout(
    barmode='stack',
    yaxis_title="Cost ($)",
    xaxis_title="Month",
    legend_title_text="Category",
    margin=dict(t=40, b=40),
)

st.plotly_chart(fig_bar, use_container_width=True)


# --- Monthly Total Cost Line Chart ---
fig_line = px.line(
    monthly_df,
    x="Month",
    y=["Compute", "Storage", "Data Transfer"],
    title="Monthly Total Cost Trend by Category",
    labels={"value": "Cost ($)", "variable": "Category"},
    hover_data={"value": ":,.2f"}
)

# Improve hover and legend
fig_line.update_traces(mode='lines+markers', hovertemplate='%{x}: $%{y:,.2f}')
fig_line.update_layout(
    legend_title_text="Cost Category",
    yaxis_title="Cost ($)",
    xaxis_title="Month"
)

st.plotly_chart(fig_line, use_container_width=True)


# --- Potential Savings Section ---
st.header("💡 Potential Savings After Optimization")

# Savings Metric
st.metric(
    "Annual Cost After Optimization",
    f"${total_optimized_annual:,.2f}",
    delta=f"-${total_savings:,.2f} ({savings_pct:.1f}%)"
)

# --- Optimization Summary ---
optimizations = []

if pause_hours_per_day > 0:
    optimizations.append(f"Paused warehouses for **{pause_hours_per_day} hours/day** to reduce compute usage.")

if reduce_vw_size != "Same":
    optimizations.append(f"Reduced warehouse size to **{reduce_vw_size}** for lower compute costs.")

if additional_discount > 0:
    optimizations.append(f"Applied an **extra {additional_discount}% discount** due to optimized usage.")

if use_gen2:
    optimizations.append("Enabled **Gen 2 Warehouse Pricing** with 30% credit efficiency and scaling discounts.")

# If no optimizations were applied
if not optimizations:
    optimizations.append("No additional optimizations applied.")

# Display in a nice card-like container
st.subheader("Summary of Optimizations Applied")
st.markdown(
    """
    <style>
        .optimization-box {
            background-color: #f9fafb;
            border: 1px solid #e5e7eb;
            padding: 15px;
            border-radius: 10px;
            margin-top: 10px;
        }
        .optimization-box ul {
            margin: 0;
            padding-left: 20px;
        }
        .optimization-box li {
            margin-bottom: 8px;
            font-size: 16px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<div class='optimization-box'><ul>" + "".join([f"<li>{item}</li>" for item in optimizations]) + "</ul></div>", unsafe_allow_html=True)

# --- Cost Savings by Category Chart with Totals ---
savings_df = pd.DataFrame({
    "Category": ["Compute", "Storage", "Data Transfer"],
    "Current Cost": [sum(compute_costs), sum(storage_costs), sum(transfer_costs)],
    "Optimized Cost": [sum(optimized_compute_costs), sum(optimized_storage_costs), sum(optimized_transfer_costs)]
})

# Create grouped bar chart
fig_savings = px.bar(
    savings_df,
    x="Category",
    y=["Current Cost", "Optimized Cost"],
    title="Cost Savings by Category",
    barmode="group",
    labels={"value": "Cost ($)", "variable": "Status"},
    hover_data={"value": ":,.2f"}
)

# Update hovertemplate
fig_savings.update_traces(hovertemplate='%{x}: $%{value:,.2f}')

for trace in fig_savings.data:
    trace.text = [f"${v:,.0f}" for v in trace.y]
    trace.textposition = "inside"



# Improve layout
fig_savings.update_layout(
    yaxis_title="Cost ($)",
    xaxis_title="Category",
    legend_title_text="Status",
    margin=dict(t=40, b=40),
)

# Display the chart
st.plotly_chart(fig_savings, use_container_width=True)
