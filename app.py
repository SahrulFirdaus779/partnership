import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import calendar

st.set_page_config(
    page_title="Dashboard Agenda Qurban 1447 H",
    page_icon="🐄",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }

[data-testid="stAppViewContainer"] { background: #0f1e14; }
[data-testid="stSidebar"] {
    background: #0a1510 !important;
    border-right: 1px solid rgba(251,191,36,0.15);
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] p { color: #d1fae5 !important; }
.block-container { padding: 1.5rem 2rem 3rem; }

.hero {
    background: linear-gradient(135deg, #1a4731 0%, #14532d 50%, #1a4731 100%);
    border: 1px solid rgba(251,191,36,0.25);
    border-radius: 18px;
    padding: 26px 32px;
    margin-bottom: 22px;
}
.hero h1 { font-size: 26px; font-weight: 800; color: #fff; margin: 0 0 6px; }
.hero h1 span { color: #fbbf24; }
.hero p { font-size: 13px; color: rgba(255,255,255,0.55); margin: 0; }

.kpi-box {
    background: #162a1e;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 18px 16px;
    text-align: center;
}
.kpi-box .val { font-size: 40px; font-weight: 800; line-height: 1; }
.kpi-box .lbl { font-size: 10px; font-weight: 700; letter-spacing: 1.3px; text-transform: uppercase; color: rgba(255,255,255,0.4); margin-top: 4px; }
.kpi-box .sub { font-size: 11px; color: rgba(255,255,255,0.35); margin-top: 3px; }

.sec { font-size: 15px; font-weight: 700; color: #fbbf24;
    border-left: 3px solid #fbbf24; padding-left: 10px; margin: 22px 0 12px; }

.cal-wrap { background: #162a1e; border-radius: 16px; padding: 16px; border: 1px solid rgba(255,255,255,0.06); }
.cal-month-title { font-size: 16px; font-weight: 700; color: #fbbf24; margin-bottom: 10px; }
.cal-grid { display: grid; grid-template-columns: repeat(7,1fr); gap: 3px; }
.cal-hdr { text-align:center; font-size:10px; font-weight:700; letter-spacing:1px; color:rgba(255,255,255,0.3); padding: 6px 0; }
.cal-day { border-radius: 8px; padding: 6px 4px 4px; min-height: 64px;
    font-size: 12px; font-weight: 700; color: rgba(255,255,255,0.4);
    background: rgba(255,255,255,0.02); }
.cal-day.has-event { background: rgba(255,255,255,0.05); color: #fff; }
.cal-day.empty { background: transparent; }
.cal-day.idul { background: rgba(251,191,36,0.12); color: #fbbf24 !important; }
.cal-dots { margin-top: 4px; display: flex; flex-wrap: wrap; gap: 2px; }
.dot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; }
.agenda-mini { font-size: 9px; font-weight: 500; color: rgba(255,255,255,0.45);
    line-height: 1.3; margin-top: 3px;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ── DATA ──────────────────────────────────────────────────────
@st.cache_data
def load():
    df = pd.read_csv("agenda_kalender.csv", encoding="utf-8-sig")
    df["Tanggal_Lengkap"] = pd.to_datetime(df["Tanggal_Lengkap"], errors="coerce")
    df["Kategori"] = df["Kategori"].fillna("")
    df["Agenda"]   = df["Agenda"].fillna("")
    return df

df_all = load()

CAT_COLORS = {
    "Kunjungan":        "#60a5fa",
    "Rapat":            "#c084fc",
    "Survei Vendor":    "#fb923c",
    "Canvasing":        "#4ade80",
    "Safari Dongeng":   "#f97316",
    "Promo":            "#fbbf24",
    "Pelatihan":        "#34d399",
    "Parenting":        "#a78bfa",
    "Capacity Building":"#f472b6",
    "Idul Adha":        "#fde047",
    "Hari Tasyrik":     "#fde047",
    "Lainnya":          "#94a3b8",
}

def get_cats(k):
    return [c.strip() for c in str(k).split("|") if c.strip()] if k else []

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🐄 Qurban 1447 H")
    st.markdown("**Zakat Sukses** · Tim Partnership")
    st.divider()
    bulan_sel = st.selectbox("📅 Filter Bulan", ["Semua", "April", "Mei"])
    all_cats  = sorted({c for k in df_all["Kategori"] for c in get_cats(k)})
    kat_sel   = st.multiselect("🏷️ Filter Kategori", all_cats, default=all_cats)
    st.divider()
    st.caption("Sumber data: Agenda Qurban\nApril–Mei 2025")

# ── FILTER ────────────────────────────────────────────────────
df = df_all.copy()
if bulan_sel != "Semua":
    df = df[df["Bulan"] == bulan_sel]
if kat_sel:
    df = df[df.apply(
        lambda r: any(c in kat_sel for c in get_cats(r["Kategori"])) if get_cats(r["Kategori"]) else True,
        axis=1)]

df_aktif = df[df["Ada_Kegiatan"] == "Ya"]

# ── HERO ─────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>Agenda <span>Kunjungan Partnership</span></h1>
  <p>🐄 Program Qurban 1447 H &nbsp;·&nbsp; Zakat Sukses &nbsp;·&nbsp; April – Mei 2025</p>
</div>
""", unsafe_allow_html=True)

# ── KPI ───────────────────────────────────────────────────────
cats_exp = df_aktif["Kategori"].apply(get_cats).explode()
kpis = [
    (len(df_aktif),                        "Hari Aktif",      "Ada kegiatan",          "#4ade80"),
    (cats_exp.eq("Kunjungan").sum(),        "Kunjungan",       "Ke sekolah & lembaga",  "#60a5fa"),
    (cats_exp.eq("Canvasing").sum(),        "Canvasing",       "Sekolah, masjid & CFD", "#4ade80"),
    (cats_exp.eq("Rapat").sum(),            "Rapat",           "Internal & eksternal",  "#c084fc"),
    (cats_exp.eq("Safari Dongeng").sum(),   "Safari Dongeng",  "Kegiatan edukasi",      "#f97316"),
    (cats_exp.eq("Promo").sum(),            "Hari Promo",      "Early Bird & Flash Sale","#fbbf24"),
]
cols_kpi = st.columns(6)
for col, (val, lbl, sub, color) in zip(cols_kpi, kpis):
    with col:
        st.markdown(f"""
        <div class="kpi-box">
          <div class="val" style="color:{color}">{val}</div>
          <div class="lbl">{lbl}</div>
          <div class="sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── CHARTS ────────────────────────────────────────────────────
st.markdown('<div class="sec">📊 Statistik Kegiatan</div>', unsafe_allow_html=True)
ca, cb, cc = st.columns([1.1, 1.3, 1.1])

with ca:
    cat_s = df_aktif["Kategori"].apply(get_cats).explode()
    cat_s = cat_s[cat_s.isin(kat_sel)] if kat_sel else cat_s
    cat_df = cat_s.value_counts().reset_index()
    cat_df.columns = ["Kategori","Jumlah"]
    fig1 = px.bar(cat_df, x="Jumlah", y="Kategori", orientation="h",
        color="Kategori", color_discrete_map=CAT_COLORS, text="Jumlah")
    fig1.update_traces(textposition="outside", textfont_color="#fff", marker_line_width=0)
    fig1.update_layout(
        title=dict(text="Frekuensi per Kategori", font=dict(color="#fbbf24",size=13)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ccc"), showlegend=False,
        xaxis=dict(showgrid=False, color="#666", zeroline=False),
        yaxis=dict(color="#ccc", categoryorder="total ascending"),
        margin=dict(t=36,b=4,l=4,r=44), height=290,
    )
    st.plotly_chart(fig1, use_container_width=True)

with cb:
    tl_rows = []
    for _, row in df_aktif.iterrows():
        for cat in get_cats(row["Kategori"]):
            if not kat_sel or cat in kat_sel:
                agenda_txt = str(row["Agenda"])
                tl_rows.append({
                    "Tanggal": row["Tanggal_Lengkap"],
                    "Kategori": cat,
                    "Bulan": row["Bulan"],
                    "Agenda": (agenda_txt[:55]+"…") if len(agenda_txt)>55 else agenda_txt
                })
    tl_df = pd.DataFrame(tl_rows)
    if not tl_df.empty:
        fig2 = px.scatter(tl_df, x="Tanggal", y="Kategori",
            color="Kategori", color_discrete_map=CAT_COLORS,
            hover_data={"Agenda":True,"Bulan":True}, symbol="Bulan")
        fig2.update_traces(marker=dict(size=13, line=dict(width=1.5,color="rgba(0,0,0,0.3)")))
        fig2.update_layout(
            title=dict(text="Timeline Sebaran Kegiatan", font=dict(color="#fbbf24",size=13)),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#ccc"), showlegend=False,
            xaxis=dict(color="#666", showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(color="#ccc", showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
            margin=dict(t=36,b=4,l=4,r=4), height=290,
        )
        st.plotly_chart(fig2, use_container_width=True)

with cc:
    fig3 = px.pie(cat_df, names="Kategori", values="Jumlah",
        color="Kategori", color_discrete_map=CAT_COLORS, hole=0.45)
    fig3.update_traces(textinfo="percent", textfont_size=11,
        marker=dict(line=dict(color="#0f1e14",width=2)))
    fig3.update_layout(
        title=dict(text="Proporsi Kategori", font=dict(color="#fbbf24",size=13), x=0.5),
        paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#ccc"),
        legend=dict(font=dict(size=10,color="#ccc"), bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=36,b=4,l=4,r=4), height=290,
    )
    st.plotly_chart(fig3, use_container_width=True)

# ── KALENDER VISUAL ───────────────────────────────────────────
st.markdown('<div class="sec">🗓️ Kalender Visual</div>', unsafe_allow_html=True)

def render_calendar(mname, mnum, year, df_month):
    day_ev = {}
    for _, row in df_month.iterrows():
        d = row["Tanggal_Lengkap"].day
        day_ev[d] = {"cats": get_cats(row["Kategori"]), "agenda": str(row["Agenda"])}

    first_wd    = calendar.weekday(year, mnum, 1)
    days_total  = calendar.monthrange(year, mnum)[1]
    hdrs        = ["Sen","Sel","Rab","Kam","Jum","Sab","Min"]

    h  = f'<div class="cal-wrap"><div class="cal-month-title">📅 {mname} {year}</div>'
    h += '<div class="cal-grid">'
    for hdr in hdrs:
        h += f'<div class="cal-hdr">{hdr}</div>'
    for _ in range(first_wd):
        h += '<div class="cal-day empty"></div>'
    for d in range(1, days_total + 1):
        ev = day_ev.get(d)
        if not ev:
            h += f'<div class="cal-day"><span>{d}</span></div>'
        else:
            cats    = ev["cats"]
            is_idul = any("Idul" in c or "Tasyrik" in c for c in cats)
            cls     = "cal-day has-event" + (" idul" if is_idul else "")
            dots    = "".join(
                f'<span class="dot" style="background:{CAT_COLORS.get(c,"#94a3b8")}"></span>'
                for c in cats[:5])
            short   = ev["agenda"][:38] + ("…" if len(ev["agenda"])>38 else "")
            h += f'<div class="{cls}"><span>{d}</span><div class="cal-dots">{dots}</div><div class="agenda-mini">{short}</div></div>'
    h += '</div></div>'
    return h

months_show = [("April",4),("Mei",5)] if bulan_sel == "Semua" else \
              [("April",4)] if bulan_sel == "April" else [("Mei",5)]

cal_cols = st.columns(len(months_show))
for i, (mname, mnum) in enumerate(months_show):
    df_m = df_all[(df_all["Bulan"]==mname) & (df_all["Ada_Kegiatan"]=="Ya")]
    with cal_cols[i]:
        st.markdown(render_calendar(mname, mnum, 2025, df_m), unsafe_allow_html=True)

# ── LEGENDA ───────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
leg_cols = st.columns(len(CAT_COLORS))
for i, (cat, color) in enumerate(CAT_COLORS.items()):
    with leg_cols[i % len(leg_cols)]:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px">
          <div style="width:11px;height:11px;border-radius:3px;background:{color};flex-shrink:0"></div>
          <span style="font-size:10px;color:rgba(255,255,255,0.5)">{cat}</span>
        </div>""", unsafe_allow_html=True)

# ── TABEL ─────────────────────────────────────────────────────
st.markdown('<div class="sec">📋 Daftar Agenda</div>', unsafe_allow_html=True)
tbl = df_aktif[["Tanggal_Lengkap","Hari","Bulan","Kategori","Agenda"]].copy()
if kat_sel:
    tbl = tbl[tbl["Kategori"].apply(lambda k: any(c in kat_sel for c in get_cats(k)))]
tbl["Tanggal_Lengkap"] = tbl["Tanggal_Lengkap"].dt.strftime("%-d %b %Y")
tbl.columns = ["Tanggal","Hari","Bulan","Kategori","Agenda"]
st.dataframe(tbl.reset_index(drop=True), use_container_width=True, height=270,
    column_config={
        "Agenda":   st.column_config.TextColumn("Agenda",   width="large"),
        "Kategori": st.column_config.TextColumn("Kategori", width="medium"),
    })

st.markdown("""
<div style="text-align:center;margin-top:28px;font-size:11px;color:rgba(255,255,255,0.2)">
  Dashboard Agenda Qurban 1447 H · Zakat Sukses · April–Mei 2025
</div>""", unsafe_allow_html=True)