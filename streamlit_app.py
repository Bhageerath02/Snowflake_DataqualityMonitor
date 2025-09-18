# streamlit run app.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# ---------- Page Setup ----------
# ---------- Header ----------
HEADER_CSS = """
<style>
.header-main {font-size:32px; font-weight:700; margin-bottom:0; color:#222;}
.header-sub {font-size:18px; font-weight:400; color:#555; margin-top:4px; margin-bottom:25px;}
</style>
"""
st.markdown(HEADER_CSS, unsafe_allow_html=True)

st.markdown("<div class='header-main'>Snowflake Data Quality Monitor</div>", unsafe_allow_html=True)
st.markdown("<div class='header-sub'>Code Force 360</div>", unsafe_allow_html=True)

st.set_page_config(page_title="Snowflake Data Quality Monitor", layout="wide")

# ---------- Custom CSS ----------
BASE_CSS = """
<style>
.block-container {padding-top: 1rem; max-width: 1400px;}
/* Header */
.header-title {font-size:26px; font-weight:700; margin-bottom:0;}
.header-sub {font-size:18px; font-weight:500; color:#444; margin-top:2px; margin-bottom:25px;}
.brand {font-size:15px; font-weight:400; color:#888; margin-top:-15px; margin-bottom:25px;}
/* KPI tiles */
.kpi-row {display:grid; grid-template-columns: repeat(5, 1fr); gap:12px; margin:10px 0 20px;}
.kpi {border:1px solid #E6E6E6; border-radius:10px; background:#FFFFFF; padding:14px 16px;}
.kpi h4 {font-size:13px; font-weight:500; color:#555; margin:0 0 6px 0;}
.kpi .v {font-size:22px; font-weight:600; color:#111;}
/* Section headers */
.hdr {font-size:16px; font-weight:600; margin:18px 0 10px 0;}
/* Metric cards grid */
.grid {display:grid; grid-template-columns: repeat(4, 1fr); gap:12px;}
.card {border:1px solid #E6E6E6; border-radius:10px; background:#FFFFFF; padding:14px;}
.card h5 {font-size:13px; font-weight:600; margin:0 0 6px 0;}
</style>
"""
st.markdown(BASE_CSS, unsafe_allow_html=True)

# ---------- Header ----------
st.markdown("<div class='header-title'>Snowflake Data Quality Monitor</div>", unsafe_allow_html=True)
st.markdown("<div class='brand'>Code Force 360</div>", unsafe_allow_html=True)

# ---------- Sidebar ----------
st.sidebar.markdown("### Navigation")
page = st.sidebar.radio("", ["Overview", "Run History", "Dashboard", "Table Metrics"])
st.sidebar.markdown("---")
st.sidebar.caption("Resources")
st.sidebar.markdown("- Workloads\n- Warehouses\n- Usage Groups\n- Lineage")

# ---------- Mock Data ----------
np.random.seed(42)
now = datetime.utcnow()
tables = ["sales_transactions","customer_info","orders","inventory","employees","claims","iot","tickets"]

monitor_df = pd.DataFrame({
    "Name": ["Usage Digest","Spend Report","Sales Nulls","Customer Regex","Orders Freshness","Inventory Duplicates","Employees PII","IoT Anomaly"],
    "Table": tables[:8],
    "Status": np.random.choice(["OK","Triggered","Failing","Disabled"], size=8, p=[0.55,0.2,0.15,0.10]),
    "Data Source": np.random.choice(["SQL","Workload","Usage Group"], size=8),
    "Type": np.random.choice(["Digest","Anomaly","Freshness","Regex","Duplicates"], size=8),
    "Schedule": np.random.choice(["Hourly","Daily","Weekly"], size=8),
    "Created By": np.random.choice(["deepika","mike","raj","jeff"], size=8),
    "Destination": np.random.choice(["ops@team.com","alerts@team.com"], size=8)
})

dq_metrics = ["Row Count","Null %","Zero %","Duplicate %","Min","Max","StdDev","Regex Valid %","Outlier %","Freshness (hrs)"]
dq_snap = pd.DataFrame({"Table": tables})
for m in dq_metrics:
    if m=="Row Count":
        dq_snap[m] = np.random.randint(2000,5000,size=len(tables))
    elif m.endswith("%"):
        dq_snap[m] = np.round(np.random.uniform(0,10,len(tables)),2)
    elif m in ["Min","Max","StdDev"]:
        dq_snap[m] = np.round(np.random.uniform(0,100,len(tables)),2)
    else:
        dq_snap[m] = np.round(np.random.uniform(1,48,len(tables)),1)

# ---------- KPI Tiles ----------
def kpi_tiles(df):
    total = len(df)
    passing = (df["Status"]=="OK").sum()
    trig = (df["Status"]=="Triggered").sum()
    fail = (df["Status"]=="Failing").sum()
    dis = (df["Status"]=="Disabled").sum()
    kpi_cols = st.columns(5)
    vals = [("Total",total),("Passing",passing),("Triggered",trig),("Failing",fail),("Disabled",dis)]
    for i,(t,v) in enumerate(vals):
        with kpi_cols[i]:
            st.markdown(f"<div class='kpi'><h4>{t}</h4><div class='v'>{v}</div></div>", unsafe_allow_html=True)

# ---------- Overview ----------
if page=="Overview":
    st.markdown("<div class='hdr'>Monitors Overview</div>", unsafe_allow_html=True)
    kpi_tiles(monitor_df)
    st.dataframe(monitor_df, use_container_width=True)

# ---------- Run History ----------
elif page=="Run History":
    st.markdown("<div class='hdr'>Run History</div>", unsafe_allow_html=True)
    dates = pd.date_range(end=now, periods=14)
    hist = pd.DataFrame({"Window":dates})
    for t in tables[:5]:
        hist[t] = np.round(np.random.uniform(80,100,len(dates)),1)
    st.line_chart(hist.set_index("Window"))

# ---------- Dashboard ----------
elif page=="Dashboard":
    st.markdown("<div class='hdr'>Data Quality Dashboard</div>", unsafe_allow_html=True)
    kpi_tiles(monitor_df)

    selected_table = st.selectbox("Select a table", tables)
    snap = dq_snap[dq_snap["Table"]==selected_table].iloc[0].to_dict()

    st.markdown(f"#### Metrics for {selected_table}")
    cols = st.columns(4)
    for i,m in enumerate(dq_metrics):
        with cols[i%4]:
            st.markdown(f"<div class='card'><h5>{m}</h5><div class='v'>{snap[m]}</div></div>", unsafe_allow_html=True)

    st.markdown("**Historical Trend Example (% Nulls)**")
    idx = pd.date_range(end=now, periods=10)
    trend = pd.DataFrame({"Window":idx,"Null %":np.random.uniform(5,15,10)})
    st.line_chart(trend.set_index("Window"))

# ---------- Table Metrics ----------
else:
    st.markdown("<div class='hdr'>Drilldown: Table Metrics</div>", unsafe_allow_html=True)
    selected_table = st.selectbox("Select Table", tables)
    snap = dq_snap[dq_snap["Table"]==selected_table].iloc[0].to_dict()

    st.markdown("### Current Metrics")
    cols = st.columns(4)
    for i,m in enumerate(dq_metrics):
        with cols[i%4]:
            st.markdown(f"<div class='card'><h5>{m}</h5><div class='v'>{snap[m]}</div></div>", unsafe_allow_html=True)

    st.markdown("### Historical Trend (all metrics)")
    idx = pd.date_range(end=now, periods=12)
    trend = pd.DataFrame({"Window":idx})
    for m in ["Null %","Zero %","Duplicate %","Outlier %"]:
        trend[m] = np.random.uniform(0,12,len(idx))
    st.line_chart(trend.set_index("Window"))
