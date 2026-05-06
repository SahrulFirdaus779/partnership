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
    page_title="Dashboard Partnership Zakat Sukses",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── PREMIUM CSS ───────────────────────────────────────────────
st.markdown(textwrap.dedent("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }

[data-testid="stAppViewContainer"] { background-color: #fcfcfd; }
[data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #f1f5f9; }

.hero-banner { background: #ffffff; border: 1px solid #f1f5f9; border-radius: 20px; padding: 24px; margin-bottom: 20px; text-align: center; }
.hero-title { font-size: 24px; font-weight: 800; color: #1e293b; margin: 0; }
.hero-title span { color: #2563eb; }

.kpi-row { display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }
.kpi-card { background: #ffffff; border: 1px solid #f1f5f9; border-radius: 16px; padding: 20px; flex: 1; min-width: 160px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
.kpi-label { font-size: 10px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 8px; }
.kpi-value { font-size: 24px; font-weight: 800; color: #0f172a; line-height: 1; }

/* Calendar & Table Styling */
.calendar-container { background: #ffffff; border: 1px solid #f1f5f9; border-radius: 20px; padding: 24px; margin-bottom: 24px; }
.calendar-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 12px; }
.day-box { background: #f8fafc; border: 1px solid #f1f5f9; border-radius: 12px; min-height: 120px; padding: 12px; position: relative; }
.day-box:hover { background: #ffffff; border-color: #cbd5e1; }
.day-num { font-size: 14px; font-weight: 800; color: #e2e8f0; margin-bottom: 8px; }
.day-num.active { color: #1e293b; }
.tt-box { visibility: hidden; width: 240px; background: #1e293b; color: #fff; border-radius: 8px; padding: 12px; position: absolute; z-index: 999; bottom: 105%; left: 50%; margin-left: -120px; opacity: 0; transition: all 0.3s ease; font-size: 11px; pointer-events: none; }
.day-box:hover .tt-box { visibility: visible; opacity: 1; }

/* Category Colors */
.cat-kunjungan { background: #2dd4bf; }
.cat-rapat { background: #a855f7; }
.cat-survey { background: #84cc16; }
.cat-canvasing { background: #d97706; }
.cat-promo { background: #f43f5e; }
.cat-safari { background: #3b82f6; }
.cat-raya { background: #9f1239; }
.cat-pelatihan { background: #fbbf24; }
.cat-default { background: #94a3b8; }
.dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; }
</style>
"""), unsafe_allow_html=True)

# ── AGENDA LOGIC ─────────────────────────────────────────────
def categorize(text):
    text = text.lower().strip()
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

@st.cache_data
def load_agenda_data():
    fp = "daftar rincian agenda.csv"
    if not os.path.exists(fp): return pd.DataFrame(), []
    try:
        df = pd.read_csv(fp)
        if df.columns[0].startswith('Unnamed') or df.columns[0] == '': df = df.iloc[:, 1:]
        df["Kategori"] = df["Agenda"].apply(categorize)
        df["Bulan"] = df["FullDate"].apply(lambda x: x.split(' ')[1])
        df["Tanggal"] = df["FullDate"].apply(lambda x: int(x.split(' ')[0]))
        weeks = []
        for m_name, start_pad in [("April", 1), ("Mei", 3)]:
            days_in_month = 30 if m_name == "April" else 31
            curr_week = [{"day": "", "month": m_name, "events": []}] * start_pad
            for d in range(1, days_in_month + 1):
                evs_df = df[(df["Bulan"] == m_name) & (df["Tanggal"] == d)]
                evs = [{"text": html.escape(row["Agenda"]), "cat": row["Kategori"]} for _, row in evs_df.iterrows()]
                curr_week.append({"day": d, "month": m_name, "events": evs})
                if len(curr_week) == 7:
                    weeks.append(curr_week)
                    curr_week = []
            if curr_week:
                curr_week += [{"day": "", "month": m_name, "events": []}] * (7 - len(curr_week))
                weeks.append(curr_week)
        return df, weeks
    except: return pd.DataFrame(), []

# ── PIPELINE LOGIC ───────────────────────────────────────────
def clean_money(val):
    if pd.isna(val) or val == "": return 0
    s = str(val).replace("Rp", "").replace(".", "").replace(",", "").strip()
    try: return float(re.sub(r'[^0-9]', '', s))
    except: return 0

@st.cache_data
def load_pipeline_data():
    files = [
        "00. Pipeline Idul Adha 1447H.xlsx - Master.csv",
        "00. Pipeline Idul Adha 1447H.xlsx - Idul Adha.csv",
        "00. Pipeline Idul Adha 1447H.xlsx - Copy of Umum.csv"
    ]
    all_dfs = []
    for f in files:
        if os.path.exists(f):
            try:
                # Find the header row (usually contains 'Calon Mitra')
                temp_df = pd.read_csv(f, nrows=10, header=None)
                header_idx = 0
                for idx, row in temp_df.iterrows():
                    if "Calon Mitra" in str(row.values):
                        header_idx = idx
                        break
                df = pd.read_csv(f, skiprows=header_idx)
                # Cleanup empty columns/rows
                df = df.dropna(subset=["Calon Mitra"])
                df["Source"] = f.split(" - ")[-1].replace(".csv", "")
                all_dfs.append(df)
            except: continue
    
    if not all_dfs: return pd.DataFrame()
    full_df = pd.concat(all_dfs, ignore_index=True)
    
    # Financial cleaning
    # Some files use ' Target' or 'Target '
    target_col = [c for c in full_df.columns if "Target" in str(c)][0]
    real_col = [c for c in full_df.columns if "Realisasi" in str(c)][0]
    full_df["Target_Clean"] = full_df[target_col].apply(clean_money)
    full_df["Realisasi_Clean"] = full_df[real_col].apply(clean_money)
    
    # Status normalization
    full_df["Status"] = full_df["Status"].fillna("Unknown").str.replace("A", " ").str.strip()
    return full_df

# ── MAIN NAVIGATION ──────────────────────────────────────────
tab_agenda, tab_pipeline = st.tabs(["🗓️ Agenda Terverifikasi", "📊 Pipeline Partnership"])

# ── TAB 1: AGENDA ────────────────────────────────────────────
with tab_agenda:
    df_ag, weeks_ag = load_agenda_data()
    if not df_ag.empty:
        st.markdown('<div class="hero-banner"><div class="hero-title">Kalender <span>Agenda</span> Terpadu</div></div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Hari</div><div class="kpi-value">{df_ag["FullDate"].nunique()}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Mitra Sekolah</div><div class="kpi-value">{len(df_ag[df_ag["Kategori"]=="Silaturahmi Sekolah"])}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Safari Dongeng</div><div class="kpi-value">{len(df_ag[df_ag["Kategori"]=="Safari Dongeng Qurban"])}</div></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Canvasing</div><div class="kpi-value">{len(df_ag[df_ag["Kategori"]=="Canvasing Partnership"])}</div></div>', unsafe_allow_html=True)
        
        m_sel = st.selectbox("Bulan Agenda", ["Semua", "April", "Mei"])
        st.markdown('<div class="calendar-container">', unsafe_allow_html=True)
        for m in (["April", "Mei"] if m_sel == "Semua" else [m_sel]):
            st.markdown(f"#### 📅 {m} 2025")
            hdr = '<div style="display:grid;grid-template-columns:repeat(7,1fr);text-align:center;margin-bottom:10px;font-size:11px;font-weight:700;color:#94a3b8">'
            for d in ["SEN", "SEL", "RAB", "KAM", "JUM", "SAB", "MIN"]: hdr += f'<div>{d}</div>'
            st.markdown(hdr + '</div>', unsafe_allow_html=True)
            grid = '<div class="calendar-grid">'
            for week in weeks_ag:
                if any(d["month"] == m for d in week):
                    for day in week:
                        if day["month"] == m and day["day"] != "":
                            dots = "".join([f'<div class="dot {get_cat_class(e["cat"])}"></div>' for e in day["events"]])
                            tt = f"<b>{day['day']} {day['month']}</b><hr>" + "".join([f"• {e['text']}<br>" for e in day["events"]])
                            grid += f'<div class="day-box"><div class="day-num active">{day["day"]}</div><div>{dots}</div><div class="tt-box">{tt}</div></div>'
                        else: grid += '<div class="day-box" style="opacity:0.1"></div>'
            st.markdown(grid + '</div><br>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else: st.warning("File 'daftar rincian agenda.csv' tidak ditemukan.")

# ── TAB 2: PIPELINE ──────────────────────────────────────────
with tab_pipeline:
    df_pip = load_pipeline_data()
    if not df_pip.empty:
        st.markdown('<div class="hero-banner"><div class="hero-title">Monitoring <span>Pipeline</span> Partnership</div></div>', unsafe_allow_html=True)
        
        # Dashboard Filter
        col_f1, col_f2 = st.columns(2)
        with col_f1: source_sel = st.multiselect("Sumber Data", df_pip["Source"].unique(), default=df_pip["Source"].unique())
        with col_f2: status_sel = st.multiselect("Status Filter", df_pip["Status"].unique(), default=df_pip["Status"].unique())
        
        dfp = df_pip[(df_pip["Source"].isin(source_sel)) & (df_pip["Status"].isin(status_sel))]
        
        # Financial Cards
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Calon Mitra</div><div class="kpi-value">{len(dfp)}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Target</div><div class="kpi-value">Rp {dfp["Target_Clean"].sum():,.0f}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Realisasi</div><div class="kpi-value" style="color:#10b981">Rp {dfp["Realisasi_Clean"].sum():,.0f}</div></div>', unsafe_allow_html=True)
        
        st.markdown("---")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("#### 🔄 Funnel Status")
            fig_funnel = px.bar(dfp["Status"].value_counts().reset_index(), x="count", y="Status", orientation="h", color="count", color_continuous_scale="Blues")
            fig_funnel.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10), showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_funnel, use_container_width=True)
        with col_c2:
            st.markdown("#### 📍 Sebaran Wilayah (Kecamatan)")
            fig_loc = px.bar(dfp["Kecamatan"].value_counts().head(10).reset_index(), x="count", y="Kecamatan", orientation="h", color="count", color_continuous_scale="Purples")
            fig_loc.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10), showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_loc, use_container_width=True)
        
        st.markdown("#### 📋 Database Pipeline")
        st.dataframe(dfp[["Calon Mitra", "Kecamatan", "Type", "Status", "Target_Clean", "Realisasi_Clean", "PJ Handling"]], use_container_width=True, height=400)
    else: st.warning("Data Pipeline tidak ditemukan atau format tidak sesuai.")

# Footer
st.markdown('<div style="text-align:center;margin-top:60px;padding:40px;color:#94a3b8;border-top:1px solid #f1f5f9;font-size:12px;">Dashboard Partnership Qurban 1447 H · Terpadu</div>', unsafe_allow_html=True)