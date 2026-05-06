import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import re
import html
import textwrap
from datetime import datetime

st.set_page_config(
    page_title="Pusat Kendali Eksekutif · Zakat Sukses",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── EXECUTIVE DESIGN SYSTEM (INDONESIA) ────────────────────────
st.markdown(textwrap.dedent("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
[data-testid="stAppViewContainer"] { background-color: #fcfcfd; }
[data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #f1f5f9; }
.hero-banner { background: #ffffff; border: 1px solid #f1f5f9; border-radius: 24px; padding: 32px; margin-bottom: 24px; text-align: center; }
.hero-title { font-size: 26px; font-weight: 800; color: #1e293b; margin: 0; }
.hero-title span { color: #2563eb; }
.kpi-card { background: #ffffff; border: 1px solid #f1f5f9; border-radius: 20px; padding: 24px; flex: 1; text-align: center; border: 1px solid #f1f5f9; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); }
.kpi-label { font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 12px; }
.kpi-value { font-size: 30px; font-weight: 800; color: #0f172a; line-height: 1; }
.kpi-sub { font-size: 12px; color: #94a3b8; margin-top: 6px; font-weight: 600; }
.achieve-bar-bg { background: #f1f5f9; height: 8px; border-radius: 10px; margin-top: 12px; overflow: hidden; }
.achieve-bar-fill { background: linear-gradient(90deg, #2563eb, #2dd4bf); height: 100%; border-radius: 10px; }
</style>
"""), unsafe_allow_html=True)

# ── UTILS ────────────────────────────────────────────────────
def clean_money(val):
    if pd.isna(val) or val == "" or val == "-" or val == " ": return 0
    s = str(val).replace("Rp", "").replace(".", "").replace(",", "").strip()
    try: return float(re.sub(r'[^0-9]', '', s))
    except: return 0

def get_probability(status):
    s = str(status).upper()
    if "WON" in s: return 1.0
    if "NEGOTIATION" in s or "PROPOSAL" in s: return 0.6
    if "CONTACTED" in s: return 0.2
    if "LEADS" in s: return 0.05
    if "LOST" in s: return 0.0
    return 0.1

# ── LOADERS ──────────────────────────────────────────────────
@st.cache_data
def load_pipeline(path):
    if not os.path.exists(path): return pd.DataFrame()
    try:
        temp_df = pd.read_csv(path, nrows=10, header=None)
        h_idx = 0
        for i, r in temp_df.iterrows():
            if "Calon Mitra" in str(r.values): h_idx = i; break
        df = pd.read_csv(path, skiprows=h_idx)
        df = df.dropna(subset=["Calon Mitra"])
        df.columns = [c.strip() for c in df.columns]
        t_col = [c for c in df.columns if "Target" in c][0]
        r_col = [c for c in df.columns if "Realisasi" in c][0]
        df["Target_KPI"] = df[t_col].apply(clean_money)
        df["Real_KPI"] = df[r_col].apply(clean_money)
        df["Kecamatan"] = df["Kecamatan"].fillna("LAINNYA").str.upper().str.strip()
        df["Status"] = df["Status"].fillna("LEADS").str.upper().str.strip()
        df["Type"] = df["Type"].fillna("LAINNYA").str.upper().str.strip()
        df["Expected_Revenue"] = df["Target_KPI"] * df["Status"].apply(get_probability)
        pj_v = [c for c in df.columns if "PJ" in c or "Handling" in c]
        if pj_v: df = df.rename(columns={pj_v[0]: "PIC"})
        else: df["PIC"] = "Unassigned"
        return df
    except: return pd.DataFrame()

# ── DATA CONSOLIDATION ───────────────────────────────────────
f_paths = ["00. Pipeline Idul Adha 1447H.xlsx - Master.csv", "00. Pipeline Idul Adha 1447H.xlsx - Idul Adha.csv", "00. Pipeline Idul Adha 1447H.xlsx - Copy of Umum.csv"]
f_names = ["Master Database", "Pipeline Idul Adha", "Pipeline Umum"]
all_dfs = []
for i, fp in enumerate(f_paths):
    d = load_pipeline(fp)
    if not d.empty: d["Sumber"] = f_names[i]; all_dfs.append(d)
all_df = pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()

# ── SIDEBAR (INDONESIA) ──────────────────────────────────────
st.sidebar.markdown("### 🏆 Kendali Strategis")
if not all_df.empty:
    sb_k = st.sidebar.multiselect("Filter Wilayah (Kecamatan)", sorted(all_df["Kecamatan"].unique()), default=sorted(all_df["Kecamatan"].unique()))
    sb_s = st.sidebar.multiselect("Filter Status Pipeline", sorted(all_df["Status"].unique()), default=sorted(all_df["Status"].unique()))
    sb_q = st.sidebar.text_input("🔍 Cari Nama Mitra", "").upper()
else: sb_k, sb_s, sb_q = [], [], ""

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Segarkan Data"): st.rerun()

# ── RENDERING ENGINE ─────────────────────────────────────────
def render_pipeline_view(df, title):
    st.markdown(f'<div class="hero-banner"><div class="hero-title">Analisis: <span>{title}</span></div></div>', unsafe_allow_html=True)
    if df.empty: return st.warning("Data tidak ditemukan.")
    
    df_f = df[(df["Kecamatan"].isin(sb_k)) & (df["Status"].isin(sb_s))]
    if sb_q: df_f = df_f[df_f["Calon Mitra"].str.upper().str.contains(sb_q, na=False)]
    
    t, r = df_f["Target_KPI"].sum(), df_f["Real_KPI"].sum()
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Volume Leads</div><div class="kpi-value">{len(df_f)}</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Nilai Target</div><div class="kpi-value">Rp {t:,.0f}</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Capaian Saat Ini</div><div class="kpi-value" style="color:#2dd4bf">Rp {r:,.0f}</div><div class="kpi-sub">{(r/t*100 if t>0 else 0):.1f}% Target</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 🔄 Corong Konversi")
        cts = df_f["Status"].value_counts().reset_index()
        st.plotly_chart(go.Figure(go.Funnel(y=cts["Status"], x=cts["count"], textinfo="value+percent initial")).update_layout(height=350, margin=dict(t=0,b=0)), use_container_width=True)
    with col2:
        st.markdown("#### 🏆 Performa PIC (Tim)")
        if r > 0:
            pd_d = df_f.groupby("PIC")["Real_KPI"].sum().reset_index().sort_values("Real_KPI", ascending=False).head(5)
            st.plotly_chart(px.bar(pd_d, x="Real_KPI", y="PIC", orientation="h", color="Real_KPI", color_continuous_scale="Tealgrn").update_layout(height=350, showlegend=False), use_container_width=True)
        else: st.info("Belum ada realisasi.")
    with col3:
        st.markdown("#### 🧩 Segmentasi Nilai")
        df_tree = df_f[df_f["Target_KPI"] > 0]
        if not df_tree.empty:
            st.plotly_chart(px.treemap(df_tree, path=["Type", "Status"], values="Target_KPI", color="Target_KPI", color_continuous_scale="Purples").update_layout(height=350), use_container_width=True)
        else: st.info("Tidak ada nilai target.")

    st.markdown("#### 📋 Data Rincian Terkonsolidasi")
    csv = df_f.to_csv(index=False).encode('utf-8')
    st.download_button(label="📥 Ekspor Data ke CSV", data=csv, file_name=f'data_{title.lower()}.csv')
    
    color_fn = lambda v: "background-color: #dcfce7; color: #166534; font-weight: bold;" if "WON" in str(v).upper() else ""
    styler = df_f.style
    if hasattr(styler, 'map'): styler = styler.map(color_fn, subset=["Status"])
    else: styler = styler.applymap(color_fn, subset=["Status"])
    
    st.dataframe(styler, use_container_width=True, height=400,
                 column_config={"Capaian %": st.column_config.ProgressColumn("Progres", min_value=0, max_value=1, format="%.1f"), "Target_KPI": st.column_config.NumberColumn("Target (Rp)", format="Rp %.0f"), "Real_KPI": st.column_config.NumberColumn("Real (Rp)", format="Rp %.0f")})

# ── MAIN TABS ────────────────────────────────────────────────
tabs = st.tabs(["🚀 Ringkasan Eksekutif", "🏛️ Database Utama", "🐄 Pipeline Idul Adha", "🤝 Pipeline Umum"])

with tabs[0]:
    st.markdown('<div class="hero-banner"><div class="hero-title">Pusat Kendali <span>Strategis Eksekutif</span></div></div>', unsafe_allow_html=True)
    if not all_df.empty:
        df_f = all_df[(all_df["Kecamatan"].isin(sb_k)) & (all_df["Status"].isin(sb_s))]
        if sb_q: df_f = df_f[df_f["Calon Mitra"].str.upper().str.contains(sb_q, na=False)]
        
        t, r, e = df_f["Target_KPI"].sum(), df_f["Real_KPI"].sum(), df_f["Expected_Revenue"].sum()
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Nilai Pipeline</div><div class="kpi-value">Rp {t:,.0f}</div><div class="kpi-sub">Total Potensi</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Prediksi Realisasi</div><div class="kpi-value" style="color:#2563eb">Rp {e:,.0f}</div><div class="kpi-sub">Estimasi Berdasarkan Probabilitas</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Realisasi Aktual</div><div class="kpi-value" style="color:#2dd4bf">Rp {r:,.0f}</div><div class="kpi-sub">{(r/t*100 if t>0 else 0):.1f}% Capaian</div></div>', unsafe_allow_html=True)
        with c4:
            health = (df_f["Notes & History"].dropna().count() / len(df_f) * 100) if len(df_f) > 0 else 0
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Indeks Kesehatan Data</div><div class="kpi-value" style="color:{"#f43f5e" if health < 50 else "#22c55e"}">{health:.0f}%</div><div class="kpi-sub">Kelengkapan Dokumentasi Tim</div></div>', unsafe_allow_html=True)
            
        st.markdown("---")
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("#### 🗺️ Kekuatan Donasi per Wilayah (Kecamatan)")
            reg_d = df_f.groupby("Kecamatan")["Real_KPI"].sum().sort_values(ascending=False).head(10).reset_index()
            st.plotly_chart(px.bar(reg_d, x="Real_KPI", y="Kecamatan", orientation="h", color="Real_KPI", color_continuous_scale="Agsunset").update_layout(height=400, showlegend=False), use_container_width=True)
        with col_r:
            st.markdown("#### 💎 Mitra Strategis Utama (Berdasarkan Nilai)")
            top_p = df_f.sort_values("Target_KPI", ascending=False).head(8)
            st.plotly_chart(px.bar(top_p, x="Target_KPI", y="Calon Mitra", color="Status", orientation="h").update_layout(height=400), use_container_width=True)
        
        st.markdown("---")
        st.markdown("#### 📑 Tindakan Strategis Segera (Prioritas Tinggi)")
        action_df = df_f[df_f["Status"].isin(["PROPOSAL SENT", "NEGOTIATION", "CONTACTED"])].sort_values("Target_KPI", ascending=False).head(10)
        st.table(action_df[["Calon Mitra", "Status", "Target_KPI", "PIC"]])

for i, tab in enumerate(tabs[1:]):
    with tab:
        d_raw = load_pipeline(f_paths[i])
        render_pipeline_view(d_raw, f_names[i])

st.sidebar.markdown("---")
st.sidebar.caption("Dashboard Eksekutif v2.0 · Zakat Sukses")
st.markdown('<div style="text-align:center;margin-top:60px;padding:40px;color:#94a3b8;border-top:1px solid #f1f5f9;font-size:12px;">Pusat Kendali BI Eksekutif · Didukung oleh Analisis Strategis · Zakat Sukses</div>', unsafe_allow_html=True)