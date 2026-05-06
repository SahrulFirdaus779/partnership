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
    page_title="Executive Partnership Dashboard",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── EXECUTIVE DESIGN SYSTEM ────────────────────────────────────
st.markdown(textwrap.dedent("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
[data-testid="stAppViewContainer"] { background-color: #fcfcfd; }
[data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #f1f5f9; }

.hero-banner { background: #ffffff; border: 1px solid #f1f5f9; border-radius: 24px; padding: 32px; margin-bottom: 24px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); }
.hero-title { font-size: 26px; font-weight: 800; color: #1e293b; margin: 0; }
.hero-title span { color: #2563eb; }

.kpi-card { background: #ffffff; border: 1px solid #f1f5f9; border-radius: 20px; padding: 24px; flex: 1; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.01); border: 1px solid #f1f5f9; }
.kpi-label { font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 12px; }
.kpi-value { font-size: 32px; font-weight: 800; color: #0f172a; line-height: 1; }
.kpi-sub { font-size: 12px; color: #94a3b8; font-weight: 600; margin-top: 4px; }

.achieve-bar-bg { background: #f1f5f9; height: 10px; border-radius: 10px; margin-top: 12px; overflow: hidden; }
.achieve-bar-fill { background: linear-gradient(90deg, #2563eb, #2dd4bf); height: 100%; border-radius: 10px; }

.calendar-container { background: #ffffff; border: 1px solid #f1f5f9; border-radius: 24px; padding: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); }
.day-box { background: #f8fafc; border: 1px solid #f1f5f9; border-radius: 12px; min-height: 120px; padding: 10px; position: relative; }
.day-num { font-size: 14px; font-weight: 800; color: #e2e8f0; margin-bottom: 6px; }
.day-num.active { color: #1e293b; }

.dot-container { display: flex; gap: 4px; margin-bottom: 4px; flex-wrap: wrap; }
.dot { width: 7px; height: 7px; border-radius: 50%; }
.tt-box { visibility: hidden; width: 240px; background: #1e293b; color: #fff; border-radius: 8px; padding: 12px; position: absolute; z-index: 999; bottom: 105%; left: 50%; margin-left: -120px; opacity: 0; transition: all 0.3s ease; font-size: 11px; pointer-events: none; }
.day-box:hover .tt-box { visibility: visible; opacity: 1; }

.cat-kunjungan { background: #2dd4bf; }
.cat-rapat { background: #a855f7; }
.cat-survey { background: #84cc16; }
.cat-canvasing { background: #d97706; }
.cat-promo { background: #f43f5e; }
.cat-safari { background: #3b82f6; }
.cat-raya { background: #9f1239; }
.cat-pelatihan { background: #fbbf24; }
.cat-default { background: #94a3b8; }
</style>
"""), unsafe_allow_html=True)

# ── SHARED UTILS ─────────────────────────────────────────────
def clean_money(val):
    if pd.isna(val) or val == "" or val == "-": return 0
    s = str(val).replace("Rp", "").replace(".", "").replace(",", "").strip()
    try: return float(re.sub(r'[^0-9]', '', s))
    except: return 0

def categorize(text):
    text = str(text).lower().strip()
    if any(k in text for k in ["pelatihan", "pemotongan"]): return "Pelatihan Pemotongan"
    if any(k in text for k in ["canvasing", "canvassing", "kanvasing", "cfd"]): return "Canvasing Partnership"
    if any(k in text for k in ["kunjungan", "silaturahmi", "sdit", "sdn", "mit ", "sekolah", "masjid"]): return "Silaturahmi Sekolah"
    if any(k in text for k in ["safari", "dongeng"]): return "Safari Dongeng Qurban"
    if any(k in text for k in ["promo", "early bird", "flash sale"]): return "Promo Early Bird"
    if any(k in text for k in ["rapat", "meeting", "olah data", "fiksasi", "bpk", "management", "persiapan", "pembahasan"]): return "Rapat / Meeting"
    if any(k in text for k in ["survey", "kandang", "vendor"]): return "Survei Vendor"
    if any(k in text for k in ["idul adha", "tasyrik"]): return "Hari Raya"
    return "Lainnya"

def get_cat_class(cat):
    m = {"Canvasing Partnership":"cat-canvasing", "Silaturahmi Sekolah":"cat-kunjungan", "Safari Dongeng Qurban":"cat-safari", "Promo Early Bird":"cat-promo", "Rapat / Meeting":"cat-rapat", "Survei Vendor":"cat-survey", "Pelatihan Pemotongan":"cat-pelatihan", "Hari Raya":"cat-raya"}
    return m.get(cat, "cat-default")

# ── LOADERS ──────────────────────────────────────────────────
@st.cache_data
def load_agenda():
    fp = "daftar rincian agenda.csv"
    if not os.path.exists(fp): return pd.DataFrame(), []
    try:
        df = pd.read_csv(fp)
        if df.columns[0].startswith('Unnamed') or df.columns[0] == '': df = df.iloc[:, 1:]
        df["Kategori"] = df["Agenda"].apply(categorize)
        df["Bulan"] = df["FullDate"].apply(lambda x: str(x).split(' ')[1] if len(str(x).split(' ')) > 1 else "Unknown")
        df["Tanggal"] = df["FullDate"].apply(lambda x: int(str(x).split(' ')[0]) if str(x).split(' ')[0].isdigit() else 0)
        weeks = []
        for m_name, start_pad in [("April", 1), ("Mei", 3)]:
            days_in_month = 30 if m_name == "April" else 31
            curr_week = [{"day": "", "month": m_name, "events": []}] * start_pad
            for d in range(1, days_in_month + 1):
                evs_df = df[(df["Bulan"] == m_name) & (df["Tanggal"] == d)]
                evs = [{"text": html.escape(str(row["Agenda"])), "cat": row["Kategori"]} for _, row in evs_df.iterrows()]
                curr_week.append({"day": d, "month": m_name, "events": evs})
                if len(curr_week) == 7:
                    weeks.append(curr_week); curr_week = []
            if curr_week:
                curr_week += [{"day": "", "month": m_name, "events": []}] * (7 - len(curr_week))
                weeks.append(curr_week)
        return df, weeks
    except: return pd.DataFrame(), []

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
        df["Achievement %"] = (df["Real_KPI"] / df["Target_KPI"]).fillna(0).replace([float('inf'), float('-inf')], 0)
        if "No" not in df.columns: df["No"] = range(1, len(df)+1)
        pj_v = [c for c in df.columns if "PJ" in c or "Handling" in c]
        if pj_v: df = df.rename(columns={pj_v[0]: "PJ Handling"})
        df["Status"] = df["Status"].fillna("Leads").str.replace("A", " ").str.strip()
        return df
    except: return pd.DataFrame()

# ── RENDERING ────────────────────────────────────────────────
def render_pipeline_view(df, title):
    st.markdown(f'<div class="hero-banner"><div class="hero-title">Executive Pipeline: <span>{title}</span></div></div>', unsafe_allow_html=True)
    t, r = df["Target_KPI"].sum(), df["Real_KPI"].sum()
    p = (r/t*100) if t>0 else 0
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Volume Leads</div><div class="kpi-value">{len(df)}</div><div class="kpi-sub">Entitas Terdaftar</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Potensi Target</div><div class="kpi-value">Rp {t:,.0f}</div><div class="kpi-sub">Forecast Pendapatan</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Capaian</div><div class="kpi-value" style="color:#2dd4bf">Rp {r:,.0f}</div><div class="kpi-sub">{p:.1f}% Akumulasi</div><div class="achieve-bar-bg"><div class="achieve-bar-fill" style="width:{min(p,100)}%"></div></div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    col1, col2 = st.columns([1.5, 1])
    with col1:
        st.markdown("#### 📊 Funneling Status")
        counts = df["Status"].value_counts().reset_index()
        fig = px.bar(counts, x="count", y="Status", orientation="h", color="count", color_continuous_scale="Blues")
        fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=350, margin=dict(t=0, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("#### 📍 Sebaran Wilayah")
        kec = df["Kecamatan"].value_counts().head(8).reset_index()
        fig_pie = px.pie(kec, values="count", names="Kecamatan", hole=0.5, color_discrete_sequence=px.colors.sequential.Teal)
        fig_pie.update_layout(margin=dict(t=0, b=0))
        st.plotly_chart(fig_pie, use_container_width=True)
    
    st.markdown("#### 📋 Data Rincian Terpadu")
    # Professional Styling for Table
    req = ["No", "Calon Mitra", "Status", "Achievement %", "Target_KPI", "Real_KPI", "Kecamatan", "Type", "PIC Contac", "PJ Handling", "Last Activity", "Notes & History"]
    df_disp = df[[c for c in req if c in df.columns]].copy()
    
    st.dataframe(df_disp, use_container_width=True, height=500,
                 column_config={
                     "Status": st.column_config.SelectboxColumn("Status", options=df["Status"].unique().tolist(), required=True),
                     "Achievement %": st.column_config.ProgressColumn("Capaian (%)", min_value=0, max_value=1, format="%.1f"),
                     "Target_KPI": st.column_config.NumberColumn("Target (Rp)", format="Rp %.0f"),
                     "Real_KPI": st.column_config.NumberColumn("Realisasi (Rp)", format="Rp %.0f"),
                     "PIC Contac": st.column_config.TextColumn("Kontak PIC")
                 })

# ── MAIN APP ─────────────────────────────────────────────────
tabs = st.tabs(["🗓️ Agenda Kerja", "🏛️ Master Pipeline", "🐄 Idul Adha", "🤝 Umum"])

with tabs[0]:
    df_a, w_a = load_agenda()
    if not df_a.empty:
        st.markdown('<div class="hero-banner"><div class="hero-title">Monitoring <span>Agenda Kerja</span> Operasional</div></div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        for col, lab, val in zip([c1,c2,c3,c4], ["Total Hari", "Silaturahmi", "Safari Dongeng", "Canvasing"], [df_a["FullDate"].nunique(), len(df_a[df_a["Kategori"]=="Silaturahmi Sekolah"]), len(df_a[df_a["Kategori"]=="Safari Dongeng Qurban"]), len(df_a[df_a["Kategori"]=="Canvasing Partnership"])]):
            with col: st.markdown(f'<div class="kpi-card"><div class="kpi-label">{lab}</div><div class="kpi-value">{val}</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="calendar-container">', unsafe_allow_html=True)
        for m in ["April", "Mei"]:
            st.markdown(f"#### 📅 {m} 2025")
            grid = '<div class="calendar-grid">'
            for week in w_a:
                if any(d["month"] == m for d in week):
                    for d in week:
                        if d["month"] == m and d["day"] != "":
                            dots = "".join([f'<div class="dot {get_cat_class(e["cat"])}"></div>' for e in d["events"]])
                            tt = f"<b>{d['day']} {d['month']}</b><hr>" + "".join([f"• {e['text']}<br>" for e in d["events"]])
                            grid += f'<div class="day-box"><div class="day-num active">{d["day"]}</div><div class="dot-container">{dots}</div><div class="tt-box">{tt}</div></div>'
                        else: grid += '<div class="day-box" style="opacity:0.1"></div>'
            st.markdown(grid + '</div><br>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("#### 📋 Log Aktivitas Terpadu")
        st.dataframe(df_a[["FullDate", "Kategori", "Agenda"]], use_container_width=True, height=400,
                     column_config={
                         "Kategori": st.column_config.TextColumn("Kategori Aktivitas")
                     })

f_ps = ["00. Pipeline Idul Adha 1447H.xlsx - Master.csv", "00. Pipeline Idul Adha 1447H.xlsx - Idul Adha.csv", "00. Pipeline Idul Adha 1447H.xlsx - Copy of Umum.csv"]
f_ts = ["Master Kemitraan", "Program Qurban 1447H", "Partnership Umum"]
for i, tab in enumerate(tabs[1:]):
    with tab:
        df_x = load_pipeline(f_ps[i])
        if not df_x.empty: render_pipeline_view(df_x, f_ts[i])
        else: st.warning(f"Data {f_ts[i]} tidak ditemukan.")

# Footer
st.markdown('<div style="text-align:center;margin-top:60px;padding:40px;color:#94a3b8;border-top:1px solid #f1f5f9;font-size:12px;">Executive Management Dashboard · Zakat Sukses</div>', unsafe_allow_html=True)