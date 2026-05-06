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
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── EXECUTIVE DESIGN SYSTEM (ADVANCED) ─────────────────────────
st.markdown(textwrap.dedent("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
[data-testid="stAppViewContainer"] { background-color: #f8fafc; }
[data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #f1f5f9; }
.hero-banner { background: white; border: 1px solid #e2e8f0; border-radius: 24px; padding: 32px; margin-bottom: 24px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); }
.hero-title { font-size: 28px; font-weight: 800; color: #0f172a; margin: 0; }
.hero-title span { color: #2563eb; }
.kpi-card { background: white; border: 1px solid #e2e8f0; border-radius: 20px; padding: 24px; text-align: center; height: 100%; transition: transform 0.2s; }
.kpi-card:hover { transform: translateY(-2px); border-color: #3b82f6; }
.kpi-label { font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px; }
.kpi-value { font-size: 32px; font-weight: 800; color: #1e293b; line-height: 1; }
.kpi-delta { font-size: 12px; font-weight: 600; margin-top: 8px; color: #10b981; }
.partner-card { background: #f1f5f9; border-radius: 16px; padding: 20px; border-left: 5px solid #2563eb; margin-top: 20px; }
.partner-name { font-size: 18px; font-weight: 800; color: #1e293b; }
.partner-detail { font-size: 13px; color: #64748b; margin-top: 4px; }
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
    if any(k in s for k in ["NEGOTIATION", "PROPOSAL", "FOLLOW UP"]): return 0.6
    if "CONTACTED" in s: return 0.2
    if "LEADS" in s: return 0.05
    return 0.0

def make_wa_link(num):
    if pd.isna(num) or str(num).strip() == "": return ""
    clean = re.sub(r'[^0-9]', '', str(num))
    if clean.startswith('0'): clean = '62' + clean[1:]
    return f"https://wa.me/{clean}"

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
        if "PIC Contac" in df.columns: df["WhatsApp"] = df["PIC Contac"].apply(make_wa_link)
        pj_v = [c for c in df.columns if "PJ" in c or "Handling" in c]
        if pj_v: df = df.rename(columns={pj_v[0]: "PIC_ZS"})
        else: df["PIC_ZS"] = "Unassigned"
        return df
    except: return pd.DataFrame()

# ── DATA CONSOLIDATION ───────────────────────────────────────
f_paths = ["00. Pipeline Idul Adha 1447H.xlsx - Master.csv", "00. Pipeline Idul Adha 1447H.xlsx - Idul Adha.csv", "00. Pipeline Idul Adha 1447H.xlsx - Copy of Umum.csv"]
f_names = ["Master", "Idul Adha", "Umum"]
all_dfs = []
for i, fp in enumerate(f_paths):
    d = load_pipeline(fp)
    if not d.empty: d["Sumber"] = f_names[i]; all_dfs.append(d)
all_df = pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()

# ── SIDEBAR ──────────────────────────────────────────────────
st.sidebar.markdown("### 👑 Pusat Kendali Strategis")
if not all_df.empty:
    sb_k = st.sidebar.multiselect("Pilih Wilayah", sorted(all_df["Kecamatan"].unique()), default=sorted(all_df["Kecamatan"].unique()))
    sb_s = st.sidebar.multiselect("Filter Status", sorted(all_df["Status"].unique()), default=sorted(all_df["Status"].unique()))
    st.sidebar.markdown("---")
    st.sidebar.markdown("#### ⚡ Aksi Cepat")
    p_high = st.sidebar.checkbox("💎 Mitra Nilai Tinggi (> Rp 10 Jt)")
    p_low_act = st.sidebar.checkbox("⚠️ Butuh Follow Up")
    sb_q = st.sidebar.text_input("🔍 Cari Nama Mitra", "").upper()
else: sb_k, sb_s, sb_q, p_high, p_low_act = [], [], "", False, False

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Segarkan Data"): st.rerun()

# ── RENDERING ENGINE ─────────────────────────────────────────
def render_bi_view(df, title):
    st.markdown(f'<div class="hero-banner"><div class="hero-title">Wawasan Strategis: <span>{title}</span></div></div>', unsafe_allow_html=True)
    if df.empty: return st.warning("Data tidak tersedia.")
    
    df_f = df[(df["Kecamatan"].isin(sb_k)) & (df["Status"].isin(sb_s))]
    if sb_q: df_f = df_f[df_f["Calon Mitra"].str.upper().str.contains(sb_q, na=False)]
    if p_high: df_f = df_f[df_f["Target_KPI"] > 10000000]
    if p_low_act: df_f = df_f[df_f["Notes & History"].isna() | (df_f["Notes & History"] == "")]
    
    # SORT BY TARGET DESCENDING
    df_f = df_f.sort_values("Target_KPI", ascending=False)
    
    t, r, e = df_f["Target_KPI"].sum(), df_f["Real_KPI"].sum(), df_f["Expected_Revenue"].sum()
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Volume Pipeline</div><div class="kpi-value">{len(df_f)}</div><div class="kpi-delta">↑ Strategis</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Estimasi BI</div><div class="kpi-value" style="color:#2563eb">Rp {e:,.0f}</div><div class="kpi-delta">↑ Forecast</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Realisasi Aktual</div><div class="kpi-value" style="color:#10b981">Rp {r:,.0f}</div><div class="kpi-delta">↑ Capaian</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    col_l, col_r = st.columns([1.5, 1])
    with col_l:
        st.markdown("#### 📊 Visualisasi Performa")
        sub1, sub2 = st.columns(2)
        with sub1:
            cts = df_f["Status"].value_counts().reset_index()
            st.plotly_chart(go.Figure(go.Funnel(y=cts["Status"], x=cts["count"], textinfo="value+percent initial")).update_layout(height=300, margin=dict(t=0,b=0)), use_container_width=True)
        with sub2:
            dt = df_f[df_f["Target_KPI"] > 0]
            if not dt.empty: st.plotly_chart(px.treemap(dt, path=["Type", "Status"], values="Target_KPI", color="Target_KPI", color_continuous_scale="Blues").update_layout(height=300), use_container_width=True)
    with col_r:
        st.markdown("#### 💎 Kecerdasan Mitra")
        sel_p = st.selectbox("Pilih Mitra untuk Detail", ["-- Pilih Mitra --"] + sorted(df_f["Calon Mitra"].tolist()), key=f"s_{title}")
        if sel_p != "-- Pilih Mitra --":
            pdat = df_f[df_f["Calon Mitra"] == sel_p].iloc[0]
            st.markdown(f'<div class="partner-card"><div class="partner-name">{pdat["Calon Mitra"]}</div><div class="partner-detail"><b>Status:</b> {pdat["Status"]} | <b>Target:</b> Rp {pdat["Target_KPI"]:,.0f}</div><hr><div class="partner-detail"><b>Catatan:</b><br>{pdat["Notes & History"] if pd.notna(pdat["Notes & History"]) else "-"}</div></div>', unsafe_allow_html=True)
            if pd.notna(pdat.get("WhatsApp")) and pdat["WhatsApp"] != "": st.link_button("💬 Hubungi via WA", pdat["WhatsApp"])

    st.markdown("#### 📋 Data Rincian (Urut Berdasarkan Nilai Tertinggi)")
    color_fn = lambda v: "background-color: #dcfce7; color: #166534; font-weight: bold;" if "WON" in str(v).upper() else ""
    styler = df_f.style
    if hasattr(styler, 'map'): styler = styler.map(color_fn, subset=["Status"])
    else: styler = styler.applymap(color_fn, subset=["Status"])
    st.dataframe(styler, use_container_width=True, height=500, column_config={"WhatsApp": st.column_config.LinkColumn("Chat WA", display_text="Buka WA 💬"), "Target_KPI": st.column_config.NumberColumn("Target (Rp)", format="Rp %.0f"), "Real_KPI": st.column_config.NumberColumn("Real (Rp)", format="Rp %.0f")})

# ── MAIN TABS ────────────────────────────────────────────────
tabs = st.tabs(["🚀 Ringkasan Eksekutif", "🏛️ Database Utama", "🐄 Pipeline Idul Adha", "🤝 Pipeline Umum"])

with tabs[0]:
    st.markdown('<div class="hero-banner"><div class="hero-title">Executive <span>Command Center</span> Zakat Sukses</div></div>', unsafe_allow_html=True)
    if not all_df.empty:
        df_f = all_df[(all_df["Kecamatan"].isin(sb_k)) & (all_df["Status"].isin(sb_s))]
        if sb_q: df_f = df_f[df_f["Calon Mitra"].str.upper().str.contains(sb_q, na=False)]
        if p_high: df_f = df_f[df_f["Target_KPI"] > 10000000]
        if p_low_act: df_f = df_f[df_f["Notes & History"].isna() | (df_f["Notes & History"] == "")]
        
        t, r, e = df_f["Target_KPI"].sum(), df_f["Real_KPI"].sum(), df_f["Expected_Revenue"].sum()
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Nilai Pipeline</div><div class="kpi-value">Rp {t:,.0f}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Prediksi Realisasi</div><div class="kpi-value" style="color:#2563eb">Rp {e:,.0f}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Realisasi Aktual</div><div class="kpi-value" style="color:#10b981">Rp {r:,.0f}</div></div>', unsafe_allow_html=True)
        with c4:
            h = (df_f["Notes & History"].dropna().count() / len(df_f) * 100) if len(df_f) > 0 else 0
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Kesehatan Data</div><div class="kpi-value" style="color:{"#f43f5e" if h < 50 else "#10b981"}">{h:.0f}%</div></div>', unsafe_allow_html=True)
            
        st.markdown("---")
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("#### 🗺️ Kekuatan Wilayah (Urutan Realisasi)")
            reg_d = df_f.groupby("Kecamatan")["Real_KPI"].sum().sort_values(ascending=False).head(10).reset_index()
            st.plotly_chart(px.bar(reg_d, x="Real_KPI", y="Kecamatan", orientation="h", color="Real_KPI", color_continuous_scale="Blues").update_layout(yaxis={'categoryorder':'total ascending'}), use_container_width=True)
        with col_r:
            st.markdown("#### 💎 Mitra Strategis Teratas (Berdasarkan Nilai)")
            top_p = df_f.sort_values("Target_KPI", ascending=False).head(8)
            st.plotly_chart(px.bar(top_p, x="Target_KPI", y="Calon Mitra", color="Status", orientation="h").update_layout(yaxis={'categoryorder':'total ascending'}), use_container_width=True)
        
        st.markdown("---")
        st.markdown("#### 📑 Tindakan Strategis Prioritas (Berdasarkan Nilai Tertinggi)")
        action_df = df_f[df_f["Status"].isin(["NEGOTIATION", "PROPOSAL SENT"])].sort_values("Target_KPI", ascending=False).head(10)
        st.table(action_df[["Calon Mitra", "Status", "Target_KPI", "PIC_ZS"]])

for i, tab in enumerate(tabs[1:]):
    with tab:
        d_raw = load_pipeline(f_paths[i])
        render_bi_view(d_raw, f_names[i])

st.markdown('<div style="text-align:center;margin-top:60px;padding:40px;color:#94a3b8;border-top:1px solid #f1f5f9;font-size:12px;">Executive BI Command Center · Zakat Sukses · 1447 H</div>', unsafe_allow_html=True)