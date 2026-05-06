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
    page_title="Strategic BI Dashboard",
    page_icon="📈",
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
.hero-banner { background: #ffffff; border: 1px solid #f1f5f9; border-radius: 24px; padding: 32px; margin-bottom: 24px; text-align: center; }
.hero-title { font-size: 26px; font-weight: 800; color: #1e293b; margin: 0; }
.hero-title span { color: #2563eb; }
.kpi-card { background: #ffffff; border: 1px solid #f1f5f9; border-radius: 20px; padding: 24px; flex: 1; text-align: center; border: 1px solid #f1f5f9; }
.kpi-label { font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 12px; }
.kpi-value { font-size: 32px; font-weight: 800; color: #0f172a; line-height: 1; }
.achieve-bar-bg { background: #f1f5f9; height: 10px; border-radius: 10px; margin-top: 12px; overflow: hidden; }
.achieve-bar-fill { background: linear-gradient(90deg, #2563eb, #2dd4bf); height: 100%; border-radius: 10px; }
</style>
"""), unsafe_allow_html=True)

# ── UTILS ────────────────────────────────────────────────────
def clean_money(val):
    if pd.isna(val) or val == "" or val == "-" or val == " " or val == "  ": return 0
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
                if len(curr_week) == 7: weeks.append(curr_week); curr_week = []
            if curr_week: curr_week += [{"day": "", "month": m_name, "events": []}] * (7 - len(curr_week)); weeks.append(curr_week)
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
        df["Capaian %"] = (df["Real_KPI"] / df["Target_KPI"].replace(0, 1)).fillna(0)
        df["Kecamatan"] = df["Kecamatan"].fillna("Unknown").str.upper().str.strip()
        df["Status"] = df["Status"].fillna("LEADS").str.upper().str.strip().str.replace("A", " ")
        df["Type"] = df["Type"].fillna("LAINNYA").str.upper().str.strip()
        if "No" not in df.columns: df["No"] = range(1, len(df)+1)
        pj_v = [c for c in df.columns if "PJ" in c or "Handling" in c]
        if pj_v: df = df.rename(columns={pj_v[0]: "PIC_ZS"})
        else: df["PIC_ZS"] = "Unassigned"
        return df
    except: return pd.DataFrame()

# ── SIDEBAR (CONSOLIDATED) ───────────────────────────────────
st.sidebar.markdown("### 📈 BI Strategic Filters")
f_paths = ["00. Pipeline Idul Adha 1447H.xlsx - Master.csv", "00. Pipeline Idul Adha 1447H.xlsx - Idul Adha.csv", "00. Pipeline Idul Adha 1447H.xlsx - Copy of Umum.csv"]
all_k, all_s, all_t = set(), set(), set()
for f in f_paths:
    d = load_pipeline(f)
    if not d.empty:
        all_k.update(d["Kecamatan"].unique())
        all_s.update(d["Status"].unique())
        all_t.update(d["Type"].unique())

sb_k = st.sidebar.multiselect("Filter Kecamatan", sorted(list(all_k)), default=sorted(list(all_k)))
sb_s = st.sidebar.multiselect("Filter Status", sorted(list(all_s)), default=sorted(list(all_s)))
sb_t = st.sidebar.multiselect("Filter Tipe Mitra", sorted(list(all_t)), default=sorted(list(all_t)))
sb_q = st.sidebar.text_input("🔍 Cari Calon Mitra", "").upper()

st.sidebar.markdown("---")
df_a, w_a = load_agenda()
sb_b = st.sidebar.selectbox("Bulan Agenda", ["Semua", "April", "Mei"])
sb_ac = []
if not df_a.empty:
    cl = sorted(df_a["Kategori"].unique().tolist())
    sb_ac = st.sidebar.multiselect("Kategori Agenda", cl, default=cl)

# ── RENDERING ENGINE ─────────────────────────────────────────
def render_pipeline(df, title):
    st.markdown(f'<div class="hero-banner"><div class="hero-title">Strategic BI: <span>{title}</span></div></div>', unsafe_allow_html=True)
    if df.empty:
        st.warning("Data file tidak ditemukan.")
        return
        
    df_f = df.copy()
    if sb_k: df_f = df_f[df_f["Kecamatan"].isin(sb_k)]
    if sb_s: df_f = df_f[df_f["Status"].isin(sb_s)]
    if sb_t: df_f = df_f[df_f["Type"].isin(sb_t)]
    if sb_q: df_f = df_f[df_f["Calon Mitra"].str.upper().str.contains(sb_q, na=False)]
    
    t, r = df_f["Target_KPI"].sum(), df_f["Real_KPI"].sum()
    p = (r/t*100) if t>0 else 0
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Partnership volume</div><div class="kpi-value">{len(df_f)}</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Forecast Revenue</div><div class="kpi-value">Rp {t:,.0f}</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="kpi-card"><div class="kpi-label">Achievement</div><div class="kpi-value" style="color:#2dd4bf">Rp {r:,.0f}</div><div class="kpi-sub">{p:.1f}% Target</div><div class="achieve-bar-bg"><div class="achieve-bar-fill" style="width:{min(p,100)}%"></div></div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.markdown("#### 🔄 Conversion Funnel")
        cts = df_f["Status"].value_counts().reset_index()
        if not cts.empty:
            fig = go.Figure(go.Funnel(y=cts["Status"], x=cts["count"], textinfo="value+percent initial"))
            fig.update_layout(height=350, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("Tidak ada data.")
    with col2:
        st.markdown("#### 🏆 Top PIC Performance")
        if r > 0:
            pd_d = df_f.groupby("PIC_ZS")["Real_KPI"].sum().reset_index().sort_values("Real_KPI", ascending=False).head(8)
            fig_p = px.bar(pd_d, x="Real_KPI", y="PIC_ZS", orientation="h", color="Real_KPI", color_continuous_scale="Tealgrn")
            fig_p.update_layout(height=350, showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=0,b=0))
            st.plotly_chart(fig_p, use_container_width=True)
        else: st.info("Belum ada realisasi.")
    with col3:
        st.markdown("#### 🧩 Segmentation Treemap")
        # CRITICAL FIX: Filter out 0-value nodes for Treemap to avoid ZeroDivisionError in weighted average
        df_tree = df_f[df_f["Target_KPI"] > 0]
        if not df_tree.empty:
            try:
                fig_t = px.treemap(df_tree, path=["Type", "Status"], values="Target_KPI", color="Target_KPI", color_continuous_scale="Purples")
                fig_t.update_layout(height=350, margin=dict(t=0,b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_t, use_container_width=True)
            except: st.info("Gagal memproses visualisasi treemap.")
        else: st.info("Tidak ada target nilai untuk divisualisasikan.")

    st.markdown("#### 📋 Consolidated Master Data")
    req = ["No", "Calon Mitra", "Status", "Capaian %", "Target_KPI", "Real_KPI", "Kecamatan", "Type", "PIC_ZS", "Notes & History"]
    df_disp = df_f[[c for c in req if c in df_f.columns]].copy()
    def style_s(v):
        v = str(v).lower()
        if "won" in v: return "background-color: #dcfce7; color: #166534; font-weight: bold;"
        if "lost" in v: return "background-color: #fee2e2; color: #991b1b;"
        if "proposal" in v: return "background-color: #fef9c3; color: #854d0e;"
        return ""
    st.dataframe(df_disp.style.applymap(style_s, subset=["Status"]), use_container_width=True, height=500,
                 column_config={"Capaian %": st.column_config.ProgressColumn("Capaian", min_value=0, max_value=1, format="%.1f"), "Target_KPI": st.column_config.NumberColumn("Target (Rp)", format="Rp %.0f"), "Real_KPI": st.column_config.NumberColumn("Real (Rp)", format="Rp %.0f")})

# ── MAIN TABS ────────────────────────────────────────────────
tabs = st.tabs(["🗓️ Agenda Operasional", "🏛️ Master Database", "🐄 Qurban Pipeline", "🤝 Umum Pipeline"])
with tabs[0]:
    if not df_a.empty:
        st.markdown('<div class="hero-banner"><div class="hero-title">Monitoring <span>Agenda Strategis</span></div></div>', unsafe_allow_html=True)
        df_af = df_a.copy()
        if sb_ac: df_af = df_af[df_af["Kategori"].isin(sb_ac)]
        if sb_b != "Semua": df_af = df_af[df_af["Bulan"] == sb_b]
        st.markdown('<div class="calendar-container">', unsafe_allow_html=True)
        for m in (["April", "Mei"] if sb_b == "Semua" else [sb_b]):
            st.markdown(f"#### 📅 Jadwal {m} 2025")
            grid = '<div class="calendar-grid">'
            for week in w_a:
                if any(d["month"] == m for d in week):
                    for d in week:
                        if d["month"] == m and d["day"] != "":
                            m_map = {"Canvasing Partnership":"cat-canvasing", "Silaturahmi Sekolah":"cat-kunjungan", "Safari Dongeng Qurban":"cat-safari", "Promo Early Bird":"cat-promo", "Rapat / Meeting":"cat-rapat", "Survei Vendor":"cat-survey", "Pelatihan Pemotongan":"cat-pelatihan", "Hari Raya":"cat-raya"}
                            f_evs = [e for e in d["events"] if (not sb_ac) or (e["cat"] in sb_ac)]
                            dots = "".join([f'<div class="dot {m_map.get(e["cat"], "cat-default")}"></div>' for e in f_evs])
                            tt = f"<b>{d['day']} {d['month']}</b><hr>" + "".join([f"• {e['text']}<br>" for e in f_evs])
                            grid += f'<div class="day-box"><div class="day-num active">{d['day']}</div><div class="dot-container">{dots}</div><div class="tt-box">{tt}</div></div>'
                        else: grid += '<div class="day-box" style="opacity:0.1"></div>'
            st.markdown(grid + '</div><br>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.dataframe(df_af[["FullDate", "Kategori", "Agenda"]], use_container_width=True, height=400)

f_titles = ["Konsolidasi Master", "Pipeline Qurban", "Kemitraan Umum"]
for i, tab in enumerate(tabs[1:]):
    with tab:
        df_x = load_pipeline(f_paths[i])
        render_pipeline(df_x, f_titles[i])

st.markdown('<div style="text-align:center;margin-top:60px;padding:40px;color:#94a3b8;border-top:1px solid #f1f5f9;font-size:12px;">Business Intelligence Dashboard · Zakat Sukses · 1447 H</div>', unsafe_allow_html=True)