import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PIL import Image

# Load watermark image once
watermark_img = Image.open("assets/b.jpg")

# === PROFESSIONAL STYLING ===
st.set_page_config(
    page_title="Snowflake Cost Estimator",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styling */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-subtitle {
        font-size: 1.2rem;
        font-weight: 300;
        opacity: 0.9;
    }
    
    /* Card Styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 1px solid #e5e7eb;
        margin: 1rem 0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 500;
    }
    
    .savings-card {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
        margin: 1rem 0;
    }
    
    .savings-value {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .savings-label {
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1f2937;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Optimization Summary */
    .optimization-summary {
        background: #f8fafc;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .optimization-item {
        background: white;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Sidebar Styling */
    .sidebar .sidebar-content {
        background: #f8fafc;
    }
    
    /* Status Indicators */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-active { background-color: #10b981; }
    .status-warning { background-color: #f59e0b; }
    .status-info { background-color: #3b82f6; }
    
    /* Progress Bars */
    .progress-container {
        background-color: #e5e7eb;
        border-radius: 10px;
        height: 8px;
        margin: 0.5rem 0;
    }
    
    .progress-bar {
        height: 100%;
        border-radius: 10px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        transition: width 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)


# === HEADER SECTION ===
st.markdown("""
<div class="main-header">
    <div class="main-title">❄️ Snowflake Cost Estimator</div>
    <div class="main-subtitle">Advanced Cost Estimation & Optimization Analytics</div>
</div>
""", unsafe_allow_html=True)


# === SIDEBAR CONFIGURATION ===
with st.sidebar:
    st.image("assets/boolean.png", use_container_width=True, width=200)
    st.markdown("### 🎛️ Configuration Panel")
    
    
    # Quick Setup Templates
    #st.markdown("#### 📋 Quick Setup Templates")
    template = st.selectbox("Choose a template:", [
        "Custom Configuration",
        "Small Business",
        "Mid-Market Enterprise", 
        "Large Enterprise",
        "Data Lake Workload",
        "Analytics Heavy"
    ])
    
    # Apply template defaults
    if template == "Small Business":
        default_vws, default_size, default_hours, default_days = 1, "Small", 8, 20
        default_storage, default_transfer = 2.0, 0.5
    elif template == "Mid-Market Enterprise":
        default_vws, default_size, default_hours, default_days = 3, "Medium", 12, 25
        default_storage, default_transfer = 10.0, 2.0
    elif template == "Large Enterprise":
        default_vws, default_size, default_hours, default_days = 8, "Large", 16, 30
        default_storage, default_transfer = 50.0, 10.0
    elif template == "Data Lake Workload":
        default_vws, default_size, default_hours, default_days = 2, "X-Large", 20, 28
        default_storage, default_transfer = 100.0, 5.0
    elif template == "Analytics Heavy":
        default_vws, default_size, default_hours, default_days = 5, "Large", 14, 26
        default_storage, default_transfer = 25.0, 8.0
    else:
        default_vws, default_size, default_hours, default_days = 1, "X-Small", 12, 22
        default_storage, default_transfer = 5.0, 2.0
    
    st.markdown("---")
    
    # Compute Configuration
    st.markdown("#### 💻 Compute Configuration")

    # Gen 2 Warehouse with enhanced description
    use_gen2 = st.checkbox(
        "🚀 Enable Gen 2 Warehouse Pricing",
        value=False,
        help="Gen 2 provides 30% better price-performance with automatic scaling"
    )

    # Virtual Warehouses - now on top
    num_vws = st.number_input(
        "Virtual Warehouses",
        min_value=1, max_value=20,
        value=default_vws,
        help="Number of concurrent warehouses"
    )

    # Warehouse Size - now below Virtual Warehouses
    vw_size = st.selectbox(
        "Warehouse Size",
        ["X-Small", "Small", "Medium", "Large", "X-Large"],
        index=["X-Small", "Small", "Medium", "Large", "X-Large"].index(default_size)
    )


    hours_per_day = st.slider(
        "Average Hours per Day",
        1, 24, default_hours,
        help="Daily warehouse runtime"
    )
    
    active_days_per_month = st.slider(
        "Active Days per Month",
        1, 31, default_days,
        help="Business days warehouse is active"
    )
    
    compute_growth = st.slider(
        "Monthly Compute Growth (%)",
        0, 50, 10,
        help="Expected monthly growth in compute usage"
    )
    
    st.markdown("---")
    
    # Storage & Transfer Configuration
    st.markdown("#### 💾 Storage & Transfer Configuration")
    
    storage_tb = st.number_input(
        "Average Storage (TB)",
        min_value=0.0, max_value=1000.0,
        value=default_storage, step=0.5,
        help="Total data storage requirements"
    )
    
    storage_growth = st.slider(
        "Monthly Storage Growth (%)",
        0, 30, 10,
        help="Expected monthly data growth"
    )
    
    data_transfer_tb = st.number_input(
        "Data Transfer Out (TB)",
        min_value=0.0, max_value=100.0,
        value=default_transfer, step=0.1,
        help="Monthly outbound data transfer"
    )
    
    transfer_growth = st.slider(
        "Monthly Transfer Growth (%)",
        0, 25, 7,
        help="Expected growth in data transfer"
    )
    
    st.markdown("---")
    
    # Pricing & Discounts
    st.markdown("#### 💰 Pricing & Discounts")
    
    discount_pct = st.slider(
        "Base Discount (%)",
        0, 60, 0,
        help="Existing enterprise discount"
    )
    
    st.markdown("---")
    
    # Optimization Settings
    st.markdown("#### ⚡ Optimization Settings")
    
    pause_hours_per_day = st.number_input(
        "Auto-Pause Hours Per Day",
        min_value=0, max_value=12,
        value=1,
        help="Hours of automatic warehouse suspension"
    )
    
    reduce_vw_size = st.selectbox(
        "Optimize Warehouse Size",
        ["No Change", "X-Small", "Small", "Medium", "Large"],
        help="Consider smaller warehouses for cost optimization"
    )
    
    additional_discount = st.slider(
        "Additional Optimization Discount (%)",
        0, 25, 5,
        help="Extra discount from usage optimization"
    )


# === CALCULATIONS ===
CREDIT_COST = 2.0
STORAGE_COST_PER_TB = 40
DATA_TRANSFER_COST_PER_TB = 90
size_credit_mapping = {"X-Small": 1, "Small": 2, "Medium": 4, "Large": 8, "X-Large": 16}

def gen2_scaling_discount(num_warehouses):
    """Enhanced Gen 2 scaling with progressive discounts"""
    if num_warehouses <= 1:
        return 1.0
    elif num_warehouses <= 3:
        return 0.95  # 5% discount
    elif num_warehouses <= 6:
        return 0.90  # 10% discount
    else:
        return 0.85  # 15% discount for large deployments

# Monthly calculations
months = pd.date_range(start="2024-01-01", periods=12, freq='ME').strftime("%b")
compute_costs, storage_costs, transfer_costs = [], [], []
storage_current = storage_tb
transfer_current = data_transfer_tb

for month in range(12):
    # Base compute calculation
    base_credits = num_vws * size_credit_mapping[vw_size] * hours_per_day * active_days_per_month
    
    # Gen 2 optimizations
    if use_gen2:
        base_credits *= 0.70  # 30% efficiency
        base_credits *= gen2_scaling_discount(num_vws)
    
    monthly_compute = base_credits * CREDIT_COST * (1 + (month * compute_growth / 100))
    compute_costs.append(monthly_compute)
    
    # Storage with compound growth
    monthly_storage = storage_current * STORAGE_COST_PER_TB
    storage_costs.append(monthly_storage)
    storage_current *= (1 + storage_growth / 100)
    
    # Transfer with compound growth
    monthly_transfer = transfer_current * DATA_TRANSFER_COST_PER_TB
    transfer_costs.append(monthly_transfer)
    transfer_current *= (1 + transfer_growth / 100)

# Apply base discount
compute_costs = [c * (1 - discount_pct / 100) for c in compute_costs]
storage_costs = [s * (1 - discount_pct / 100) for s in storage_costs]
transfer_costs = [t * (1 - discount_pct / 100) for t in transfer_costs]

total_costs = np.array(compute_costs) + np.array(storage_costs) + np.array(transfer_costs)
total_annual_cost = total_costs.sum()

# Optimization calculations
optimized_size_credit = size_credit_mapping[vw_size] if reduce_vw_size == "No Change" else size_credit_mapping[reduce_vw_size]
optimized_compute_costs = []
storage_current_opt = storage_tb
transfer_current_opt = data_transfer_tb

for month in range(12):
    effective_hours = max(hours_per_day - pause_hours_per_day, 0)
    base_credits_opt = num_vws * optimized_size_credit * effective_hours * active_days_per_month
    
    if use_gen2:
        base_credits_opt *= 0.70
        base_credits_opt *= gen2_scaling_discount(num_vws)
        if pause_hours_per_day > 0:
            base_credits_opt *= 0.90  # Additional pause efficiency
    
    monthly_compute_opt = base_credits_opt * CREDIT_COST * (1 + (month * compute_growth / 100))
    optimized_compute_costs.append(monthly_compute_opt)
    
    storage_current_opt *= (1 + storage_growth / 100)
    transfer_current_opt *= (1 + transfer_growth / 100)

# Apply combined discount
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


# === MAIN DASHBOARD ===

# Key Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">${int(round(total_annual_cost)):,}</div>
        <div class="metric-label">📊 Annual Cost</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">${int(round(total_annual_cost/12)):,}</div>
        <div class="metric-label">📅 Monthly Average</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="savings-card">
        <div class="savings-value">${int(round(total_savings)):,}</div>
        <div class="savings-label">💰 Potential Savings</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    roi_indicator = "🟢" if savings_pct > 20 else "🟡" if savings_pct > 10 else "🔴"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{roi_indicator} {savings_pct:.1f}%</div>
        <div class="metric-label">📈 Savings Percentage</div>
    </div>
    """, unsafe_allow_html=True)

# Configuration Summary
st.markdown('<div class="section-header">🎯 Current Configuration</div>', unsafe_allow_html=True)

config_col1, config_col2, config_col3 = st.columns(3)

with config_col1:
    st.markdown(f"""
    **Compute Setup:**
    - {num_vws} × {vw_size} Warehouses
    - {hours_per_day}h/day × {active_days_per_month} days/month
    - {'✅ Gen 2 Enabled' if use_gen2 else '❌ Gen 1 Standard'}
    """)

with config_col2:
    st.markdown(f"""
    **Storage & Transfer:**
    - {storage_tb:.1f} TB Storage
    - {data_transfer_tb:.1f} TB/month Transfer
    - {storage_growth}% Storage Growth
    """)

with config_col3:
    st.markdown(f"""
    **Discounts Applied:**
    - {discount_pct}% Base Discount
    - {additional_discount}% Optimization Discount
    - Template: {template}
    """)

# === ENHANCED VISUALIZATIONS ===

st.markdown('<div class="section-header">📊 Cost Analysis Dashboard</div>', unsafe_allow_html=True)

# Enhanced Cost Breakdown with Donut Chart
fig_donut = go.Figure(data=[go.Pie(
    labels=['Compute', 'Storage', 'Data Transfer'],
    values=[round(sum(compute_costs)), round(sum(storage_costs)), round(sum(transfer_costs))],
    hole=0.6,
    marker_colors=['#667eea', '#764ba2', '#f093fb'],
    textinfo='label+percent',
    textfont_size=12,
    hovertemplate='<b>%{label}</b><br>Cost: $%{value:,.0f}<br>Percentage: %{percent}<extra></extra>'
)])

# Add watermark to donut chart
fig_donut.add_layout_image(
     dict(
        source=watermark_img,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        sizex=1, sizey=1,  # exactly fill the plot area
        opacity=0.11,
        layer="below",
        xanchor="center",
        yanchor="middle"
    )
)

fig_donut.update_layout(
    title={'text': "Annual Cost Distribution", 'x': 0.5, 'xanchor': 'center'},
    annotations=[dict(text=f'Total<br>${total_annual_cost:,.0f}', x=0.5, y=0.5, font_size=16, showarrow=False)],
    showlegend=True,
    height=400,
    font=dict(family="Inter, sans-serif")
)

# Monthly trend with dual axis
monthly_df = pd.DataFrame({
    "Month": months,
    "Compute": compute_costs,
    "Storage": storage_costs,
    "Data Transfer": transfer_costs,
    "Total": total_costs
})

fig_trend = make_subplots()

fig_trend.add_trace(
    go.Scatter(
        x=months,
        y=[round(v) for v in compute_costs],  # Rounded data
        fill='tozeroy',
        name='Compute',
        line=dict(color='#667eea'),
        fillcolor='rgba(102,126,234,0.35)',
        hovertemplate='<b>Compute</b><br>$%{y:,.0f}<extra></extra>'
    )
)

fig_trend.add_trace(
    go.Scatter(
        x=months,
        y=[round(v) for v in storage_costs],  # Rounded data
        fill='tonexty',
        name='Storage',
        line=dict(color='#764ba2'),
        fillcolor='rgba(118,75,162,0.35)',
        hovertemplate='<b>Storage</b><br>$%{y:,.0f}<extra></extra>'
    )
)

fig_trend.add_trace(
    go.Scatter(
        x=months,
        y=[round(v) for v in transfer_costs],  # Rounded data
        fill='tonexty',
        name='Data Transfer',
        line=dict(color='#f093fb'),
        fillcolor='rgba(240,147,251,0.35)',
        hovertemplate='<b>Data Transfer</b><br>$%{y:,.0f}<extra></extra>'
    )
)

fig_trend.add_trace(
    go.Scatter(
        x=months,
        y=total_costs,
        mode='lines+markers+text',
        name='Total Cost',
        line=dict(color='#1f2937', width=3),
        marker=dict(size=7),
        text=[f"${int(round(v)):,}" for v in total_costs],  # Rounded
        textposition="top center",
        hovertemplate='<b>Total Cost</b><br>$%{y:,.0f}<extra></extra>'
    )
)

# Add watermark to monthly trend chart
fig_trend.add_layout_image(
    dict(
        source=watermark_img,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        sizex=1, sizey=1,  # exactly fill the plot area
        opacity=0.11,
        layer="below",
        xanchor="center",
        yanchor="middle"
    )
)

fig_trend.update_layout(
    title="Monthly Cost Trend & Breakdown",
    xaxis_title="Month",
    yaxis_title="Cost ($)",
    hovermode='x unified',
    height=500,
    font=dict(family="Inter, sans-serif"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

fig_trend.update_yaxes(range=[0, max(total_costs) * 1.15])

# Display charts side by side
chart_col1, chart_col2 = st.columns(2)
with chart_col1:
    st.plotly_chart(fig_donut, use_container_width=True)
with chart_col2:
    st.plotly_chart(fig_trend, use_container_width=True)

# === OPTIMIZATION ANALYSIS ===
st.markdown('<div class="section-header">⚡ Optimization Analysis</div>', unsafe_allow_html=True)

optimizations = []
if pause_hours_per_day > 0:
    optimizations.append(f"🔄 Auto-pause {pause_hours_per_day}h daily reduces compute by ~{pause_hours_per_day/hours_per_day*100:.0f}%")
if reduce_vw_size != "No Change":
    original_credits = size_credit_mapping[vw_size]
    new_credits = size_credit_mapping[reduce_vw_size]
    reduction = (1 - new_credits/original_credits) * 100
    optimizations.append(f"📉 Warehouse downsizing saves {reduction:.0f}% on compute credits")
if use_gen2:
    optimizations.append(f"🚀 Gen 2 warehouses provide 30% better price-performance")
if additional_discount > 0:
    optimizations.append(f"🏷️ Usage optimization unlocks {additional_discount}% additional discount")

if optimizations:
    st.markdown('<div class="optimization-summary">', unsafe_allow_html=True)
    for opt in optimizations:
        st.markdown(f'<div class="optimization-item">{opt}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Before/After Comparison
comparison_data = {
    'Scenario': ['Current Configuration', 'Optimized Configuration'],
    'Annual Cost': [total_annual_cost, total_optimized_annual],
    'Monthly Average': [total_annual_cost/12, total_optimized_annual/12],
    'Compute %': [sum(compute_costs)/total_annual_cost*100, sum(optimized_compute_costs)/total_optimized_annual*100],
    'Storage %': [sum(storage_costs)/total_annual_cost*100, sum(optimized_storage_costs)/total_optimized_annual*100]
}

comparison_df = pd.DataFrame(comparison_data)

fig_comparison = px.bar(
    comparison_df, x='Scenario', y='Annual Cost',
    title='Cost Comparison: Current vs Optimized',
    color='Scenario',
    color_discrete_map={
        'Current Configuration': '#ef4444',
        'Optimized Configuration': '#10b981'
    },
    text='Annual Cost'
)

fig_comparison.update_traces(
    texttemplate='$%{text:,.0f}',
    textposition='outside'
)

max_value = max(comparison_df['Annual Cost']) * 1.15

fig_comparison.update_layout(
    yaxis=dict(range=[0, max_value]),
    yaxis_title="Annual Cost ($)",
    showlegend=False,
    height=400,
    font=dict(family="Inter, sans-serif")
)

# Add watermark to comparison chart
fig_comparison.add_layout_image(
    dict(
        source=watermark_img,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        sizex=1, sizey=1,  # exactly fill the plot area
        opacity=0.11,
        layer="below",
        xanchor="center",
        yanchor="middle"
    )
)

# Monthly savings trend
savings_trend_df = pd.DataFrame({
    "Month": months,
    "Current": np.round(total_costs),
    "Optimized": np.round(total_optimized_costs),
    "Monthly Savings": np.round(total_costs - total_optimized_costs)
})

fig_savings_trend = px.line(
    savings_trend_df,
    x="Month",
    y=["Current", "Optimized"],
    title="Monthly Cost Trajectory",
    color_discrete_map={"Current": "#ef4444", "Optimized": "#10b981"}
)

fig_savings_trend.update_traces(
    mode='lines+markers',
    line=dict(width=3),
    hovertemplate='%{y:,.0f}'  # Rounded with commas
)

# Add watermark to savings trend chart
fig_savings_trend.add_layout_image(
    dict(
        source=watermark_img,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        sizex=1, sizey=1,  # exactly fill the plot area
        opacity=0.11,
        layer="below",
        xanchor="center",
        yanchor="middle"
    )
)

fig_savings_trend.update_layout(
    yaxis_title="Monthly Cost ($)",
    height=400,
    font=dict(family="Inter, sans-serif")
)

# Display comparison charts
comp_col1, comp_col2 = st.columns(2)
with comp_col1:
    st.plotly_chart(fig_comparison, use_container_width=True)
with comp_col2:
    st.plotly_chart(fig_savings_trend, use_container_width=True)

# === ROI ANALYSIS ===
st.markdown('<div class="section-header">💼 ROI & Business Impact</div>', unsafe_allow_html=True)

roi_col1, roi_col2, roi_col3 = st.columns(3)

with roi_col1:
    months_to_roi = 1  # Immediate savings
    st.metric(
        "Time to ROI",
        f"{months_to_roi} month{'s' if months_to_roi != 1 else ''}",
        delta="Immediate impact"
    )

with roi_col2:
    three_year_savings = int(round(total_savings * 3))
    st.metric(
        "3-Year Savings Projection",
        f"${three_year_savings:,}",
        delta=f"{int(round(savings_pct))}% annually"
    )

with roi_col3:
    cost_per_tb_processed = int(round(total_annual_cost / (storage_tb * 12))) if storage_tb > 0 else 0
    st.metric(
        "Cost per TB (Annual)",
        f"${cost_per_tb_processed:,}",
        delta="Including all costs"
    )


# Summary Report Card
st.markdown('<div class="section-header">📋 Executive Summary</div>', unsafe_allow_html=True)

summary_metrics = {
    'Current Annual Spend': f"${int(round(total_annual_cost)):,}",
    'Optimized Annual Spend': f"${int(round(total_optimized_annual)):,}",
    'Annual Savings': f"${int(round(total_savings)):,} ({int(round(savings_pct))}%)",
    'Monthly Savings': f"${int(round(total_savings/12)):,}",
    'Compute Efficiency': f"{int(round(100 - (sum(optimized_compute_costs)/sum(compute_costs)*100)))}% improvement",
    'Primary Optimization': 'Gen 2 Warehouses' if use_gen2 else 'Auto-pause & Right-sizing'
}

summary_df = pd.DataFrame(list(summary_metrics.items()), columns=['Metric', 'Value'])

st.dataframe(
    summary_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Metric": st.column_config.TextColumn("Key Metrics", width="medium"),
        "Value": st.column_config.TextColumn("Values", width="medium")
    }
)

# Action Items
if savings_pct > 0:
    st.success(f"🎯 **Recommendation**: Implement the optimization strategy to achieve ${total_savings:,.0f} in annual savings ({savings_pct:.1f}%)")
    
    if use_gen2:
        st.info("💡 **Pro Tip**: Gen 2 warehouses provide the highest ROI with automatic scaling and 30% efficiency gains")
    
    if pause_hours_per_day > 0:
        st.info(f"⏱️ **Quick Win**: Auto-pause configuration can be implemented immediately for {pause_hours_per_day}h daily savings")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6b7280; font-size: 0.9rem; margin-top: 2rem;'>
    <p>🔧 <strong>Snowflake Cost Estimator</strong> | Advanced Cost Estimation & Optimization Analytics</p>
    <p>Made by <strong>Boolean Data Systems<sup>©</sup></strong> | All rights reserved. </p>
</div>
""", unsafe_allow_html=True)
