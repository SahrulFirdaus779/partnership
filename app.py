import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import re
import html

st.set_page_config(
    page_title="Dashboard Agenda Qurban 1447 H",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CUSTOM CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
[data-testid="stAppViewContainer"] { background-color: #fcfcfd; }
[data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #f1f5f9; }
.kpi-card { background: #ffffff; border: 1px solid #f1f5f9; border-radius: 16px; padding: 20px; text-align: center; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
.kpi-label { font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 8px; }
.kpi-value { font-size: 32px; font-weight: 800; color: #0f172a; line-height: 1; }
.kpi-sub { font-size: 11px; color: #94a3b8; }
.calendar-header-row { display: grid; grid-template-columns: repeat(7, 1fr); gap: 10px; margin-bottom: 10px; text-align: center; }
.calendar-day-label { font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase; }
.calendar-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 10px; }
.day-box { background: #f8fafc; border: 1px solid #f1f5f9; border-radius: 12px; min-height: 130px; padding: 10px; transition: all 0.2s ease; }
.day-box:hover { background: #ffffff; border-color: #cbd5e1; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
.day-num { font-size: 15px; font-weight: 800; color: #cbd5e1; margin-bottom: 6px; }
.day-num.active { color: #1e293b; }
.dot-container { display: flex; gap: 3px; margin-bottom: 6px; flex-wrap: wrap; }
.dot { width: 7px; height: 7px; border-radius: 50%; }
.event-text { font-size: 10px; font-weight: 600; color: #475569; line-height: 1.3; margin-bottom: 4px; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
.cat-kunjungan { background: #3b82f6; }
.cat-rapat { background: #a855f7; }
.cat-survey { background: #f97316; }
.cat-canvasing { background: #10b981; }
.cat-promo { background: #facc15; }
.cat-safari { background: #ec4899; }
.cat-raya { background: #ef4444; }
.cat-default { background: #94a3b8; }
.legend-box { display: flex; gap: 12px; flex-wrap: wrap; padding: 12px; background: #ffffff; border: 1px solid #f1f5f9; border-radius: 12px; margin-bottom: 20px; }
.legend-item { display: flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 600; color: #64748b; }
</style>
""", unsafe_allow_html=True)

# ── DATA PROCESSING ──────────────────────────────────────────
def categorize(text):
    text = text.lower()
    if any(k in text for k in ["kunjungan", "silaturahmi", "sdit", "sdn", "mit ", "sekolah"]): return "Kunjungan"
    if any(k in text for k in ["rapat", "meeting", "olah data", "fiksasi"]): return "Rapat"
    if "canvasing" in text: return "Canvasing"
    if any(k in text for k in ["survey", "kandang", "hewan"]): return "Survey"
    if any(k in text for k in ["promo", "early bird", "launching", "flash sale", "harga"]): return "Promo"
    if "safari dongeng" in text: return "Safari"
    if any(k in text for k in ["idul adha", "tasyrik"]): return "Raya"
    return "Lainnya"

def get_cat_class(cat):
    m = {"Kunjungan":"cat-kunjungan","Rapat":"cat-rapat","Survey":"cat-survey","Canvasing":"cat-canvasing","Promo":"cat-promo","Safari":"cat-safari","Raya":"cat-raya"}
    return m.get(cat, "cat-default")

@st.cache_data
def load_data():
    fp = "agenda partnership.csv"
    if not os.path.exists(fp): return pd.DataFrame(), []
    try:
        content = ""
        for enc in ['utf-8-sig', 'utf-8', 'latin-1']:
            try:
                with open(fp, 'r', encoding=enc) as f: content = f.read()
                break
            except: continue
        if not content: return pd.DataFrame(), []
        lines = content.splitlines()
        data, weeks = [], []
        curr_m, switched = "April", False
        days_names = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
        for i in range(len(lines)):
            line = lines[i].strip()
            if not line: continue
            parts = line.split(';')
            if len(parts) >= 2 and parts[1].strip() == 'Kegiatan':
                dates = parts[2:9]
                if i + 1 < len(lines):
                    ap = lines[i+1].strip().split(';')
                    if len(ap) >= 2 and ap[1].strip() == 'Agenda Qurban 1447 H':
                        agendas, week_d = ap[2:9], []
                        for idx, d_str in enumerate(dates):
                            ds = d_str.strip()
                            if ds and ds.isdigit():
                                day = int(ds)
                                if not switched and day == 1 and i > 15: curr_m, switched = "Mei", True
                                txt = agendas[idx].strip() if idx < len(agendas) else ""
                                evs = []
                                if txt:
                                    items = re.split(r' - | \| | \n ', txt)
                                    for it in items:
                                        if it.strip():
                                            c = categorize(it.strip())
                                            evs.append({"text": html.escape(it.strip()), "cat": c})
                                            data.append({"Tanggal": day, "Bulan": curr_m, "FullDate": f"{day} {curr_m} 2025", "Agenda": it.strip(), "Kategori": c, "Hari": days_names[idx], "MO": 4 if curr_m=="April" else 5})
                                week_d.append({"day": day, "month": curr_m, "events": evs})
                            else: week_d.append({"day": "", "month": "", "events": []})
                        weeks.append(week_d)
        return pd.DataFrame(data), weeks
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame(), []

df_raw, all_weeks = load_data()

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🐄 Qurban 1447 H")
    month_sel = st.selectbox("Pilih Bulan", ["Semua", "April", "Mei"])
    cs = sorted(df_raw["Kategori"].unique())
    cat_sel = st.multiselect("Filter Kategori", cs, default=cs)
    st.markdown("---")
    if not df_raw.empty:
        st.download_button("📥 Download Data CSV", data=df_raw.to_csv(index=False), file_name="agenda_partnership_clean.csv", mime="text/csv")

# ── FILTERING ─────────────────────────────────────────────────
df = df_raw.copy()
if month_sel != "Semua": df = df[df["Bulan"] == month_sel]
if cat_sel: df = df[df["Kategori"].isin(cat_sel)]

# ── KPI SECTION ───────────────────────────────────────────────
st.markdown(f"### 📊 Ringkasan Agenda {month_sel if month_sel != 'Semua' else 'April - Mei'}")
c1, c2, c3, c4, c5 = st.columns(5)
stts = [("Total", len(df), "#2563eb", c1), ("Kunjungan", len(df[df["Kategori"]=="Kunjungan"]), "#3b82f6", c2), ("Canvasing", len(df[df["Kategori"]=="Canvasing"]), "#10b981", c3), ("Promo", len(df[df["Kategori"]=="Promo"]), "#eab308", c4), ("Rapat", len(df[df["Kategori"]=="Rapat"]), "#a855f7", c5)]
for l, v, c, col in stts:
    with col: st.markdown(f'<div class="kpi-card"><div class="kpi-label">{l}</div><div class="kpi-value" style="color:{c}">{v}</div><div class="kpi-sub">Kegiatan</div></div>', unsafe_allow_html=True)

# ── NEW VISUALIZATIONS ────────────────────────────────────────
st.markdown("---")
col_chart1, col_chart2 = st.columns([1.5, 1])

with col_chart1:
    st.markdown("#### 📈 Tren Intensitas Kegiatan")
    df_trend = df.groupby(["MO", "Bulan", "Tanggal"]).size().reset_index(name="Jumlah")
    df_trend["Tgl"] = df_trend["Tanggal"].astype(str) + " " + df_trend["Bulan"]
    fig_trend = px.line(df_trend, x="Tgl", y="Jumlah", markers=True, color_discrete_sequence=["#2563eb"])
    fig_trend.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10), xaxis_title="", yaxis_title="Jumlah Agenda", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_trend, use_container_width=True)

with col_chart2:
    st.markdown("#### 📅 Beban Kerja per Hari")
    df_day = df["Hari"].value_counts().reindex(["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]).reset_index()
    df_day.columns = ["Hari", "Jumlah"]
    fig_day = px.bar(df_day, x="Hari", y="Jumlah", color="Jumlah", color_continuous_scale="Blues")
    fig_day.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10), showlegend=False, xaxis_title="", yaxis_title="", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_day, use_container_width=True)

# ── CALENDAR ──────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🗓️ Kalender Visual")
leg = '<div class="legend-box">'
for cat in ["Kunjungan", "Rapat", "Survey", "Canvasing", "Promo", "Safari", "Raya"]:
    leg += f'<div class="legend-item"><div class="dot {get_cat_class(cat)}"></div>{cat}</div>'
st.markdown(leg + '</div>', unsafe_allow_html=True)

for m in (["April", "Mei"] if month_sel == "Semua" else [month_sel]):
    st.markdown(f"#### 📅 {m} 2025")
    hdr = '<div class="calendar-header-row">'
    for d in ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]: hdr += f'<div class="calendar-day-label">{d}</div>'
    st.markdown(hdr + '</div>', unsafe_allow_html=True)
    grid = '<div class="calendar-grid">'
    for week in all_weeks:
        if any(d["month"] == m for d in week):
            for day in week:
                if day["month"] == m and day["day"] != "":
                    evs = [e for e in day["events"] if e["cat"] in cat_sel]
                    dots = "".join([f'<div class="dot {get_cat_class(e["cat"])}"></div>' for e in evs])
                    txts = "".join([f'<div class="event-text">{e["text"]}</div>' for e in evs[:2]])
                    if len(evs)>2: txts += f'<div style="font-size:9px;color:#94a3b8">+{len(evs)-2} lagi</div>'
                    grid += f'<div class="day-box"><div class="day-num active">{day["day"]}</div><div class="dot-container">{dots}</div>{txts}</div>'
                else: grid += '<div class="day-box" style="opacity:0.1"></div>'
    st.markdown(grid + '</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# ── INSPECTOR & TABLE ─────────────────────────────────────────
st.markdown("---")
col_ins, col_tbl = st.columns([1, 1.5])

with col_ins:
    st.markdown("#### 🔍 Inspektur Agenda")
    if not df.empty:
        sel_date = st.selectbox("Pilih Tanggal untuk Detail:", df["FullDate"].unique())
        details = df[df["FullDate"] == sel_date]
        for _, row in details.iterrows():
            st.info(f"**{row['Kategori']}**\n\n{row['Agenda']}")
    else:
        st.write("Tidak ada data.")

with col_tbl:
    st.markdown("#### 📋 Daftar Lengkap")
    sq = st.text_input("Cari cepat...", placeholder="Lokasi, instansi, atau kegiatan...")
    dfv = df[["FullDate", "Kategori", "Agenda"]].copy()
    if sq: dfv = dfv[dfv.apply(lambda r: sq.lower() in str(r).lower(), axis=1)]
    st.dataframe(dfv, use_container_width=True, height=250)

# Footer
st.markdown('<div style="text-align:center;margin-top:60px;padding:40px;color:#94a3b8;border-top:1px solid #f1f5f9;font-size:12px;">Partnership Qurban 1447 H · Zakat Sukses</div>', unsafe_allow_html=True)