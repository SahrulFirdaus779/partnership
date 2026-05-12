import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
from datetime import datetime

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Pipeline Idul Adha 1447H",
    page_icon="🐄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS DENGAN HEADER TABEL BERWARNA ─────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

  * {
    font-family: 'Inter', sans-serif;
  }

  .stApp {
    background: linear-gradient(135deg, #f5f7fc 0%, #ffffff 100%);
  }
  
  .block-container {
    padding: 1.5rem 2rem 2rem;
    max-width: 1400px;
  }

  /* SIDEBAR STYLING */
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1119 0%, #1a1c2e 100%) !important;
    border-right: 1px solid #2d3047 !important;
  }
  
  [data-testid="stSidebar"] * {
    color: #e2e4f0 !important;
  }
  
  [data-testid="stSidebar"] .stSelectbox label,
  [data-testid="stSidebar"] .stTextInput label,
  [data-testid="stSidebar"] .stNumberInput label {
    font-size: 11px;
    font-weight: 700;
    color: #8b92b0 !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
  }
  
  [data-testid="stSidebar"] .stTextInput input,
  [data-testid="stSidebar"] .stNumberInput input {
    background: #252842 !important;
    border: 1px solid #3d405b !important;
    color: #ffffff !important;
    border-radius: 10px !important;
  }
  
  [data-testid="stSidebar"] .stSelectbox > div > div {
    background: #252842 !important;
    border: 1px solid #3d405b !important;
    border-radius: 10px !important;
  }
  
  [data-testid="stSidebar"] hr {
    border-color: #3d405b !important;
    margin: 20px 0;
  }
  
  [data-testid="stSidebar"] .stButton > button {
    background: #EA5C1F !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease;
  }
  
  [data-testid="stSidebar"] .stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(234,92,31,0.3);
  }

  /* SECTION TITLE */
  .sec-title {
    font-size: 16px;
    font-weight: 700;
    color: #1a1c2e;
    margin-bottom: 16px;
    margin-top: 8px;
    letter-spacing: -0.3px;
    border-left: 4px solid #EA5C1F;
    padding-left: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  /* KPI CARDS */
  [data-testid="metric-container"] {
    background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
    border: 1px solid #e8ecf2;
    border-radius: 16px;
    padding: 16px 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    transition: all 0.3s ease;
  }
  
  [data-testid="metric-container"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.08);
    border-color: #EA5C1F;
  }
  
  [data-testid="metric-container"] label {
    font-size: 11px !important;
    color: #6b7280 !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
  }
  
  [data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 28px !important;
    font-weight: 800 !important;
    color: #1a1c2e !important;
  }

  /* ========== TABEL DENGAN HEADER BERWARNA ========== */
  /* Container tabel */
  .stDataFrame {
    border-radius: 16px !important;
    overflow: hidden !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  }
  
  /* Header tabel - WARNA ORANGE GRADASI */
  div[data-testid="stDataFrame"] thead tr th {
    background: linear-gradient(135deg, #EA5C1F 0%, #c2410c 100%) !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    padding: 14px 16px !important;
    border: none !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  
  /* Isi tabel */
  div[data-testid="stDataFrame"] tbody tr td {
    padding: 12px 16px !important;
    border-bottom: 1px solid #f0f2f6 !important;
    color: #1e293b !important;
    font-size: 13px !important;
    background-color: #ffffff !important;
  }
  
  /* Hover effect pada baris */
  div[data-testid="stDataFrame"] tbody tr:hover td {
    background-color: #fff7ed !important;
  }
  
  /* Zebra stripe untuk tabel */
  div[data-testid="stDataFrame"] tbody tr:nth-child(even) td {
    background-color: #fafafa !important;
  }
  
  div[data-testid="stDataFrame"] tbody tr:nth-child(even):hover td {
    background-color: #fff7ed !important;
  }

  /* EXPANDER */
  .streamlit-expanderHeader {
    background: linear-gradient(135deg, #f8f9ff 0%, #ffffff 100%) !important;
    border: 1px solid #e8ecf2 !important;
    border-radius: 12px !important;
    color: #1a1c2e !important;
    font-weight: 600 !important;
  }
  
  .streamlit-expanderContent {
    background: #ffffff !important;
    border: 1px solid #e8ecf2 !important;
    border-top: none !important;
    border-radius: 0 0 12px 12px !important;
  }

  /* DOWNLOAD BUTTON */
  .stDownloadButton > button {
    background: linear-gradient(135deg, #1a1c2e 0%, #252842 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease;
  }
  
  .stDownloadButton > button:hover {
    background: #EA5C1F !important;
    transform: translateY(-2px);
  }
  
  /* DIVIDER */
  hr {
    border-color: #e8ecf2 !important;
    margin: 24px 0 !important;
  }
  
  /* ALERT */
  .stAlert {
    border-radius: 12px !important;
    border-left: 4px solid #EA5C1F !important;
  }
  
  /* HEADING */
  h1 {
    font-size: 28px !important;
    margin-bottom: 4px !important;
    color: #1a1c2e !important;
  }
  
  /* CAPTION */
  .stCaption {
    color: #64748b !important;
    font-size: 12px !important;
  }
</style>
""", unsafe_allow_html=True)

# ─── STATUS & TYPE CONFIG ──────────────────────────────────────────────────
STATUS_CONFIG = {
    "Leads": {"color": "#64748b", "bg": "#f1f5f9", "icon": "🎯"},
    "Contacted": {"color": "#3b82f6", "bg": "#eff6ff", "icon": "📞"},
    "Proposal Sent": {"color": "#ea580c", "bg": "#fff7ed", "icon": "📄"},
    "Closed Won": {"color": "#059669", "bg": "#ecfdf5", "icon": "✅"},
    "Closed Lost": {"color": "#dc2626", "bg": "#fef2f2", "icon": "❌"},
}

TYPE_COLORS = {
    "Sekolah": "#EA5C1F",
    "Masjid": "#3b82f6", 
    "Yayasan": "#8b5cf6",
    "Majelis": "#ec489a",
    "Perusahaan": "#1a1c2e",
    "Komunitas": "#06b6d4",
}

# ─── FUNGSI UTILITY ─────────────────────────────────────────────────────────
def clean_phone(phone):
    if not phone or str(phone).lower() == "nan" or str(phone).strip() == "-":
        return ""
    digits = re.sub(r"\D", "", str(phone))
    if digits.startswith("0"):
        digits = "62" + digits[1:]
    elif digits.startswith("8"):
        digits = "62" + digits
    return digits

# ─── LOAD DATA ─────────────────────────────────────────────────────────────
SHEET_ID = "1AetsUA__rVYEXn-t6-OZoopBNu1TWtrz"
SHEET_GID = "1298999788"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={SHEET_GID}"

@st.cache_data(ttl=300, show_spinner="Memuat data dari Google Sheets...")
def load_data():
    df = pd.read_csv(CSV_URL, header=None)
    
    # Cari header row
    header_row = None
    for i, row in df.iterrows():
        vals = [str(v).strip() for v in row.values]
        if any("Calon Mitra" in v for v in vals):
            header_row = i
            break
        if "No" in vals and "Status" in vals:
            header_row = i
            break
    
    if header_row is None:
        header_row = 2
    
    df.columns = df.iloc[header_row]
    df = df.iloc[header_row + 1:].reset_index(drop=True)
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(how="all")
    
    # Mapping kolom
    rename_dict = {}
    for col in df.columns:
        col_lower = col.lower()
        if "calon mitra" in col_lower or col_lower == "nama":
            rename_dict[col] = "Nama"
        elif col_lower == "no":
            rename_dict[col] = "No"
        elif "alamat" in col_lower:
            rename_dict[col] = "Alamat"
        elif "kelurahan" in col_lower:
            rename_dict[col] = "Kelurahan"
        elif "kecamatan" in col_lower:
            rename_dict[col] = "Kecamatan"
        elif "type" in col_lower or "tipe" in col_lower:
            rename_dict[col] = "Type"
        elif "pic" in col_lower and ("contact" in col_lower or "contac" in col_lower):
            rename_dict[col] = "PIC_Contact"
        elif "pic" in col_lower and "name" in col_lower:
            rename_dict[col] = "PIC_Name"
        elif "status" in col_lower:
            rename_dict[col] = "Status"
        elif "next" in col_lower and "follow" in col_lower:
            rename_dict[col] = "Next_FollowUp"
        elif "last" in col_lower and "act" in col_lower:
            rename_dict[col] = "Last_Activity"
        elif "notes" in col_lower or "history" in col_lower:
            rename_dict[col] = "Notes"
        elif "target" in col_lower:
            rename_dict[col] = "Target"
        elif "realisasi" in col_lower:
            rename_dict[col] = "Realisasi"
        elif "pj" in col_lower or "handling" in col_lower:
            rename_dict[col] = "PJ"
    
    df = df.rename(columns=rename_dict)
    
    # Tambahkan kolom yang hilang
    required_cols = ["Nama", "Type", "Kecamatan", "PIC_Name", "PIC_Contact", "Status", "PJ", "Next_FollowUp", "Last_Activity", "Notes"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = ""
    
    # Bersihkan data
    df = df[df["Nama"].notna() & (df["Nama"].astype(str).str.strip() != "") & (df["Nama"].astype(str).str.strip() != "nan")]
    df["Status"] = df["Status"].fillna("Leads").astype(str).str.strip()
    
    def normalize_status(val):
        v = str(val).lower()
        if "won" in v:
            return "Closed Won"
        if "lost" in v:
            return "Closed Lost"
        if "proposal" in v:
            return "Proposal Sent"
        if "contact" in v:
            return "Contacted"
        if "leads" in v:
            return "Leads"
        return "Leads"
    
    df["Status"] = df["Status"].apply(normalize_status)
    df["Type"] = df["Type"].fillna("-").astype(str).str.strip()
    df["Kecamatan"] = df["Kecamatan"].fillna("-").astype(str).str.strip()
    df["PJ"] = df["PJ"].fillna("").astype(str).str.strip().str.title()
    df["PIC_Name"] = df["PIC_Name"].fillna("-").astype(str).str.strip()
    
    # WhatsApp
    df["PIC_Contact_Raw"] = df["PIC_Contact"].fillna("-").astype(str).str.strip()
    df["WA_Number"] = df["PIC_Contact_Raw"].apply(clean_phone)
    df["WA_Link"] = df["WA_Number"].apply(lambda x: f"https://wa.me/{x}" if x else "")
    
    # Filter valid status
    valid_statuses = {"Leads", "Contacted", "Proposal Sent", "Closed Won", "Closed Lost"}
    df = df[df["Status"].isin(valid_statuses)]
    
    # Hapus baris legend
    df = df[~df["Nama"].str.lower().str.startswith(("biru", "hijau", "ungu", "kuning", "merah", "keterangan", "legend"), na=False)]
    
    return df.reset_index(drop=True)

# ─── LOAD DATA ───────────────────────────────────────────────────────────────

try:
    df = load_data()
    # st.success(f"✅ Berhasil memuat {len(df)} data mitra")
except Exception as e:
    st.error(f"❌ Gagal memuat data: {e}")
    st.stop()

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🐄 Pipeline Idul Adha")
    st.markdown("---")
    
    search = st.text_input("🔍 Cari Mitra", placeholder="Nama / Kecamatan / PIC")
    
    statuses = ["Semua"] + sorted(df["Status"].unique().tolist())
    sel_status = st.selectbox("📌 Status", statuses)
    
    types = ["Semua"] + sorted(df["Type"].unique().tolist())
    sel_type = st.selectbox("🏛️ Tipe Mitra", types)
    
    pjs_raw = df["PJ"].replace("", "Belum ditugaskan").unique().tolist()
    pjs = ["Semua"] + sorted([p for p in pjs_raw if p])
    sel_pj = st.selectbox("👤 PJ Handling", pjs)
    
    st.markdown("---")
    st.markdown("### 🎯 Target")
    target_qurban = st.number_input("Target Qurban (ekor)", min_value=0, value=50, step=5)
    
    st.markdown("---")
    st.caption(f"📊 Total Data: **{len(df)}** Mitra")
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        load_data.clear()  # Hanya hapus cache fungsi load_data, bukan seluruh cache global
        st.rerun()

# ─── FILTER ──────────────────────────────────────────────────────────────────
filtered = df.copy()
if search:
    q = search.lower()
    # Optimasi: Menggunakan vektorisasi Pandas (jauh lebih cepat dibanding .apply row-by-row)
    search_cols = ["Nama", "Kecamatan", "PIC_Name", "PJ"]
    combined_text = filtered[search_cols].astype(str).agg(' '.join, axis=1).str.lower()
    filtered = filtered[combined_text.str.contains(q, na=False, regex=False)]
if sel_status != "Semua":
    filtered = filtered[filtered["Status"] == sel_status]
if sel_type != "Semua":
    filtered = filtered[filtered["Type"] == sel_type]
if sel_pj != "Semua":
    actual_pj = "" if sel_pj == "Belum ditugaskan" else sel_pj
    filtered = filtered[filtered["PJ"] == actual_pj]

# ─── HEADER ──────────────────────────────────────────────────────────────────
st.markdown('<h1>🐄 Pipeline Partnership Idul Adha 1447H</h1>', unsafe_allow_html=True)
st.caption("📡 Data realtime dari Google Sheets · Zakat Sukses")
st.markdown("---")

# ─── KPI CARDS ──────────────────────────────────────────────────────────────
sc = filtered["Status"].value_counts()
real_qurban = sc.get("Closed Won", 0)
conversion_rate = (real_qurban / len(filtered) * 100) if len(filtered) > 0 else 0

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("🎯 Total Mitra", f"{len(filtered):,}")
with col2:
    delta_value = real_qurban - target_qurban
    st.metric("✅ Closed Won", f"{real_qurban:,}", delta=f"{delta_value:+d}")
with col3:
    st.metric("📄 Proposal Sent", f"{sc.get('Proposal Sent', 0):,}")
with col4:
    st.metric("📞 Contacted", f"{sc.get('Contacted', 0):,}")
with col5:
    st.metric("🎯 Leads", f"{sc.get('Leads', 0):,}")
with col6:
    st.metric("📈 Conversion Rate", f"{conversion_rate:.1f}%")

if sc.get("Closed Lost", 0) > 0:
    st.warning(f"⚠️ **Closed Lost:** {sc.get('Closed Lost', 0)} mitra tidak berhasil")

# ALERT MASS-UNASSIGNED
unassigned_count = len(df[df["PJ"] == ""])
if len(df) > 0 and (unassigned_count / len(df) > 0.5):
    st.error(f"🚨 **ALERT:** {unassigned_count} mitra ({unassigned_count/len(df)*100:.0f}%) belum ditugaskan ke PJ! Segera distribusikan beban kerja tim.")

st.markdown("")

# ─── VISUALIZATIONS ROW ─────────────────────────────────────────────────────
col_a, col_b, col_c = st.columns([1, 1, 1])

with col_a:
    st.markdown('<div class="sec-title">🎯 Pipeline Funnel</div>', unsafe_allow_html=True)
    order = ["Leads", "Contacted", "Proposal Sent", "Closed Won"]
    funnel_df = filtered["Status"].value_counts().reindex(order, fill_value=0).reset_index()
    funnel_df.columns = ["Status", "Jumlah"]
    
    fig1 = go.Figure(go.Funnel(
        y=funnel_df["Status"],
        x=funnel_df["Jumlah"],
        textinfo="value+percent initial",
        textfont=dict(size=13, color="white", family="Inter"),
        marker=dict(color=["#94a3b8", "#3b82f6", "#ea580c", "#059669"]),
        connector=dict(line=dict(color="#cbd5e1", width=2))
    ))
    fig1.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=20, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", size=12),
    )
    st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

with col_b:
    st.markdown('<div class="sec-title">🏛️ Distribusi Tipe Mitra</div>', unsafe_allow_html=True)
    type_df = filtered["Type"].value_counts().reset_index()
    type_df.columns = ["Type", "Jumlah"]
    type_df = type_df[type_df["Type"] != "-"]
    
    colors2 = [TYPE_COLORS.get(t, "#94a3b8") for t in type_df["Type"]]
    
    fig2 = go.Figure(go.Bar(
        y=type_df["Type"],
        x=type_df["Jumlah"],
        orientation="h",
        marker=dict(color=colors2, cornerradius=8),
        text=type_df["Jumlah"],
        textposition="outside",
        textfont=dict(size=12, color="#1a1c2e")
    ))
    fig2.update_layout(
        height=300,
        margin=dict(l=0, r=40, t=20, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor="#e2e8f0", zeroline=False),
        yaxis=dict(showgrid=False, autorange="reversed"),
        showlegend=False,
    )
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

with col_c:
    st.markdown('<div class="sec-title">📍 Konsentrasi Kecamatan</div>', unsafe_allow_html=True)
    kec_df = filtered[filtered["Kecamatan"] != "-"]["Kecamatan"].value_counts().reset_index()
    kec_df.columns = ["Kecamatan", "Jumlah"]
    
    if len(kec_df) > 0:
        # Ambil Top 10 agar visualisasi tetap rapi dan terbaca jelas
        top_kec_df = kec_df.head(10).sort_values("Jumlah", ascending=True)
        
        fig3 = go.Figure(go.Bar(
            y=top_kec_df["Kecamatan"],
            x=top_kec_df["Jumlah"],
            orientation="h",
            marker=dict(color="#EA5C1F", cornerradius=6),
            text=top_kec_df["Jumlah"],
            textposition="outside",
            textfont=dict(size=12, color="#1a1c2e")
        ))
        fig3.update_layout(
            height=300,
            margin=dict(l=0, r=40, t=20, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=True, gridcolor="#e2e8f0", zeroline=False, visible=False),
            yaxis=dict(showgrid=False),
            showlegend=False,
            font=dict(family="Inter")
        )
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Data kecamatan tidak tersedia")

st.markdown("---")

# ─── PJ HANDLING TABLE ──────────────────────────────────────────────────────
st.markdown('<div class="sec-title">👤 Performa PJ Handling</div>', unsafe_allow_html=True)

pj_df = filtered.copy()
pj_df["PJ_clean"] = pj_df["PJ"].replace("", "Belum ditugaskan")
pj_summary = pj_df.groupby("PJ_clean").agg(
    Total=("Nama", "count"),
    Won=("Status", lambda x: (x == "Closed Won").sum()),
    Proposal=("Status", lambda x: (x == "Proposal Sent").sum()),
    Contacted=("Status", lambda x: (x == "Contacted").sum()),
    Lost=("Status", lambda x: (x == "Closed Lost").sum()),
).reset_index().rename(columns={"PJ_clean": "PJ"}).sort_values("Total", ascending=False)

pj_summary_display = pj_summary.copy()
pj_summary_display["Conversion"] = (pj_summary_display["Won"] / pj_summary_display["Total"] * 100).fillna(0).round(1)

# Rename kolom untuk tampilan
pj_summary_display = pj_summary_display.rename(columns={
    "Total": "Total Mitra",
    "Won": "Won",
    "Proposal": "Proposal",
    "Contacted": "Contacted",
    "Lost": "Lost",
    "Conversion": "Conv. Rate",
    "PJ": "PJ Handling"
})

# Terapkan Pandas Styler dan konversi ke HTML agar warna header benar-benar terekskusi (Streamlit dataframe memblokir CSS header)
styled_pj = (
    pj_summary_display.style
    .set_table_styles([
        {'selector': 'table', 'props': [('width', '100%'), ('border-collapse', 'collapse'), ('font-size', '13px'), ('margin-top', '10px')]},
        {'selector': 'th', 'props': [('background-color', '#EA5C1F'), ('color', 'white'), ('padding', '12px 10px'), ('font-weight', '700'), ('text-align', 'left')]},
        {'selector': 'td', 'props': [('padding', '10px'), ('border-bottom', '1px solid #f0f2f6')]},
        {'selector': 'tbody tr:hover td', 'props': [('background-color', '#fff7ed !important')]}
    ])
    .background_gradient(subset=['Total Mitra'], cmap='Blues')
    .bar(subset=['Conv. Rate'], color='rgba(234, 92, 31, 0.6)', vmin=0, vmax=100)
    .format({'Conv. Rate': '{:.1f}%'})
    .hide(axis="index")
)

col_pj1, col_pj2 = st.columns([1, 1])

with col_pj1:
    st.markdown(styled_pj.to_html(), unsafe_allow_html=True)

with col_pj2:
    pj_summary_numeric = pj_summary.copy()
    pj_summary_numeric["Conversion Rate (%)"] = pj_summary_numeric["Won"] / pj_summary_numeric["Total"] * 100
    
    fig_pj = px.scatter(
        pj_summary_numeric, 
        x="Total", 
        y="Conversion Rate (%)", 
        size="Total", 
        color="PJ", 
        text="PJ",
        size_max=30, 
        hover_name="PJ"
    )
    fig_pj.update_traces(textposition='top center')
    fig_pj.update_layout(
        height=300, 
        margin=dict(l=10, r=10, t=10, b=10), 
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor="#e2e8f0", title="Beban Kerja (Total Mitra)"),
        yaxis=dict(showgrid=True, gridcolor="#e2e8f0", title="Conversion Rate (%)"),
        font=dict(family="Inter")
    )
    st.plotly_chart(fig_pj, use_container_width=True, config={"displayModeBar": False})

st.markdown("---")

# ─── AGING BOARD ─────────────────────────────────────────────────────────────
st.markdown('<div class="sec-title">⏳ Aging Board (Need Attention)</div>', unsafe_allow_html=True)

def is_vague_followup(text):
    text = str(text).lower()
    if not text.strip() or text.strip() == "-" or text.strip() == "nan":
        return True
    
    # Deteksi regex sederhana untuk tanggal (misal: 25 april, 10/05, 12-10)
    date_pattern = r'\b(\d{1,2})[/\s-]*(jan|feb|mar|apr|mei|jun|jul|agu|sep|okt|nov|des|\d{1,2})\b'
    if not re.search(date_pattern, text):
        return True
    return False

def extract_followup_date(text):
    text = str(text).lower()
    bulan_dict = {
        'jan': 1, 'januari': 1, 'feb': 2, 'februari': 2, 'mar': 3, 'maret': 3,
        'apr': 4, 'april': 4, 'mei': 5, 'jun': 6, 'juni': 6,
        'jul': 7, 'juli': 7, 'agu': 8, 'agustus': 8, 'sep': 9, 'september': 9,
        'okt': 10, 'oktober': 10, 'nov': 11, 'november': 11, 'des': 12, 'desember': 12
    }
    date_pattern = r'\b(\d{1,2})[/\s-]*(januari|februari|maret|april|mei|juni|juli|agustus|september|oktober|november|desember|jan|feb|mar|apr|mei|jun|jul|agu|sep|okt|nov|des|\d{1,2})\b'
    match = re.search(date_pattern, text)
    if match:
        day_str = match.group(1)
        month_str = match.group(2)
        day = int(day_str)
        month = None
        if month_str.isdigit():
            month = int(month_str)
        else:
            for k, v in bulan_dict.items():
                if k in month_str:
                    month = v
                    break
        if month and 1 <= month <= 12 and 1 <= day <= 31:
            try:
                return datetime(2026, month, day)
            except ValueError:
                pass
    return pd.NaT

filtered["FollowUp_Date"] = filtered["Next_FollowUp"].apply(extract_followup_date)

# Filter mitra berstatus Leads/Contacted yang tidak punya kejelasan tanggal follow up
aging_mask = filtered["Status"].isin(["Leads", "Contacted"]) & filtered["Next_FollowUp"].apply(is_vague_followup)
aging_df = filtered[aging_mask].copy()

if len(aging_df) > 0:
    st.warning(f"⚠️ Terdapat **{len(aging_df)} mitra** berstatus Leads/Contacted dengan target Follow Up yang tidak jelas (tanpa tanggal valid)!")
    aging_display = aging_df[["Nama", "Status", "PJ", "Next_FollowUp"]].reset_index(drop=True)
    aging_display = aging_display.rename(columns={
        "Nama": "Calon Mitra",
        "Status": "Status",
        "PJ": "PJ",
        "Next_FollowUp": "Catatan Follow Up saat ini"
    })
    styled_aging = (
        aging_display.style
        .set_table_styles([
            {'selector': 'table', 'props': [('width', '100%'), ('border-collapse', 'collapse'), ('font-size', '13px'), ('margin-top', '10px')]},
            {'selector': 'th', 'props': [('background-color', '#EA5C1F'), ('color', 'white'), ('padding', '12px 10px'), ('font-weight', '700'), ('text-align', 'left'), ('position', 'sticky'), ('top', '0'), ('z-index', '1')]},
            {'selector': 'td', 'props': [('padding', '10px'), ('border-bottom', '1px solid #f0f2f6')]},
            {'selector': 'tbody tr:hover td', 'props': [('background-color', '#fff7ed !important')]}
        ])
        .hide(axis="index")
    )
    st.markdown(f'<div style="max-height: 250px; overflow-y: auto; border-radius: 12px; border: 1px solid #e8ecf2;">{styled_aging.to_html()}</div>', unsafe_allow_html=True)
else:
    st.success("✅ Semua mitra Leads & Contacted telah memiliki target Follow Up (dengan tanggal) yang jelas.")

st.markdown("---")

# ─── TIMELINE & AGENDA FOLLOW UP ─────────────────────────────────────────────
st.markdown('<div class="sec-title">Timeline & Agenda Follow Up</div>', unsafe_allow_html=True)

agenda_df = filtered[filtered["FollowUp_Date"].notna()].copy()
agenda_df = agenda_df.sort_values("FollowUp_Date")

if len(agenda_df) > 0:
    col_ag1, col_ag2 = st.columns([3, 2])
    
    with col_ag1:
        # Scatter Plot Timeline
        fig_agenda = px.scatter(
            agenda_df,
            x="FollowUp_Date",
            y="PJ",
            color="Status",
            hover_name="Nama",
            hover_data={"PJ": False, "FollowUp_Date": False, "Next_FollowUp": True},
            title="Sebaran Jadwal Follow Up",
        )
        fig_agenda.update_traces(marker=dict(size=12, line=dict(width=1, color='#ffffff')))
        fig_agenda.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=30, b=0),
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=True, gridcolor="#e2e8f0", title=""),
            yaxis=dict(showgrid=True, gridcolor="#e2e8f0", title=""),
            font=dict(family="Inter"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_agenda, use_container_width=True, config={"displayModeBar": False})
        
    with col_ag2:
        st.markdown("<div style='font-size:14px; font-weight:600; color:#1a1c2e; margin-bottom:10px;'>Jadwal Terdekat</div>", unsafe_allow_html=True)
        display_agenda = agenda_df[["FollowUp_Date", "Nama", "PJ", "Next_FollowUp"]].copy()
        display_agenda["Tanggal"] = display_agenda["FollowUp_Date"].dt.strftime("%d %b")
        display_agenda = display_agenda[["Tanggal", "Nama", "PJ", "Next_FollowUp"]].rename(columns={
            "Next_FollowUp": "Catatan"
        })
        
        styled_agenda = (
            display_agenda.style
            .set_table_styles([
                {'selector': 'table', 'props': [('width', '100%'), ('border-collapse', 'collapse'), ('font-size', '12px')]},
                {'selector': 'th', 'props': [('background-color', '#252842'), ('color', 'white'), ('padding', '10px 8px'), ('font-weight', '600'), ('text-align', 'left'), ('position', 'sticky'), ('top', '0'), ('z-index', '1')]},
                {'selector': 'td', 'props': [('padding', '8px'), ('border-bottom', '1px solid #f0f2f6')]},
                {'selector': 'tbody tr:hover td', 'props': [('background-color', '#fff7ed !important')]}
            ])
            .hide(axis="index")
        )
        st.markdown(f'<div style="max-height: 270px; overflow-y: auto; border: 1px solid #e8ecf2; border-radius: 8px;">{styled_agenda.to_html()}</div>', unsafe_allow_html=True)
else:
    st.info("Belum ada jadwal follow-up dengan format tanggal yang dikenali.")

st.markdown("---")

# ─── MAIN DATA TABLE - DENGAN HEADER WARNA ORANGE ───────────────────────────
st.markdown(
    f'<div class="sec-title">Data Mitra Pipeline '
    f'<span style="background:#EA5C1F;color:#fff;border-radius:20px;padding:2px 12px;font-size:12px;font-weight:600;">'
    f'{len(filtered)} dari {len(df)} hasil</span></div>',
    unsafe_allow_html=True
)

# Siapkan data untuk ditampilkan
display_df = filtered[[
    "Nama", "Type", "Kecamatan", "PIC_Name", "Status", "PJ", "Next_FollowUp", "WA_Link"
]].copy()
display_df = display_df.reset_index(drop=True)
display_df.index = display_df.index + 1  # Nomor urut mulai dari 1

# Format WA_Link agar bisa di-klik di dalam HTML
display_df["WA_Link"] = display_df["WA_Link"].apply(lambda x: f'<a href="{x}" target="_blank" style="color: #3b82f6; text-decoration: none; font-weight: 600;">Chat WA</a>' if str(x).startswith("http") else "-")

display_df = display_df.rename(columns={
    "Nama": "Calon Mitra",
    "Type": "Tipe",
    "Kecamatan": "Kecamatan",
    "PIC_Name": "PIC Name",
    "Status": "Status",
    "PJ": "PJ Handling",
    "Next_FollowUp": "Next Follow Up",
    "WA_Link": "WA Quick-Contact"
})

# Paginasi Setup
ITEMS_PER_PAGE = 5
total_items = len(display_df)
total_pages = (total_items - 1) // ITEMS_PER_PAGE + 1 if total_items > 0 else 1

if "current_page" not in st.session_state:
    st.session_state.current_page = 1

# Reset halaman jika filter berubah drastis
if st.session_state.current_page > total_pages:
    st.session_state.current_page = 1

start_idx = (st.session_state.current_page - 1) * ITEMS_PER_PAGE
end_idx = start_idx + ITEMS_PER_PAGE
paginated_df = display_df.iloc[start_idx:end_idx]

styled_main = (
    paginated_df.style
    .set_table_styles([
        {'selector': 'table', 'props': [('width', '100%'), ('border-collapse', 'collapse'), ('font-size', '13px')]},
        {'selector': 'th', 'props': [('background-color', '#EA5C1F'), ('color', 'white'), ('padding', '14px 16px'), ('font-weight', '700'), ('text-align', 'left')]},
        {'selector': 'td', 'props': [('padding', '12px 16px'), ('border-bottom', '1px solid #f0f2f6')]},
        {'selector': 'tbody tr:hover td', 'props': [('background-color', '#fff7ed !important')]}
    ])
    .hide(axis="index")
)

st.markdown(f'<div style="min-height: 400px; border-radius: 16px; border: 1px solid #e8ecf2; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 15px;">{styled_main.to_html(escape=False)}</div>', unsafe_allow_html=True)

# Kontrol Paginasi
col_p1, col_p2, col_p3 = st.columns([1, 2, 1])
with col_p1:
    if st.button("Sebelumnya", disabled=st.session_state.current_page <= 1, use_container_width=True):
        st.session_state.current_page -= 1
        st.rerun()

with col_p2:
    st.markdown(f"<div style='text-align:center; padding-top:8px; font-weight:600; color:#1a1c2e;'>Halaman {st.session_state.current_page} dari {total_pages}</div>", unsafe_allow_html=True)

with col_p3:
    if st.button("Selanjutnya", disabled=st.session_state.current_page >= total_pages, use_container_width=True):
        st.session_state.current_page += 1
        st.rerun()

# ─── NOTES EXPANDER ─────────────────────────────────────────────────────────
with st.expander("Lihat Notes & History"):
    if "Notes" in filtered.columns:
        note_df = filtered[["Nama", "Status", "PJ", "Next_FollowUp", "Notes"]].copy()
        # Filter notes yang benar-benar ada isinya
        note_df = note_df[note_df["Notes"].astype(str).str.strip() != ""]
        note_df = note_df[note_df["Notes"].notna() & (note_df["Notes"] != "nan")]
        
        if len(note_df) > 0:
            NOTES_PER_PAGE = 6
            total_notes = len(note_df)
            total_note_pages = (total_notes - 1) // NOTES_PER_PAGE + 1
            
            if "note_page" not in st.session_state:
                st.session_state.note_page = 1
                
            if st.session_state.note_page > total_note_pages:
                st.session_state.note_page = 1
                
            start_idx = (st.session_state.note_page - 1) * NOTES_PER_PAGE
            end_idx = start_idx + NOTES_PER_PAGE
            paginated_notes = note_df.iloc[start_idx:end_idx]
            
            html_blocks = []
            html_blocks.append('<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; margin-bottom: 16px;">')
            
            for _, row in paginated_notes.iterrows():
                html_blocks.append(f"""<div style="background:#ffffff; border-radius:12px; padding:16px; border: 1px solid #e8ecf2; border-top: 4px solid #EA5C1F; box-shadow: 0 4px 10px rgba(0,0,0,0.03); display: flex; flex-direction: column;">
    <div style="display:flex; justify-content:space-between; margin-bottom:12px; border-bottom: 1px solid #e8ecf2; padding-bottom: 8px;">
        <span style="font-weight:700; color:#1a1c2e; font-size:14px;">{row['Nama']}</span>
        <span style="font-size:11px; color:#ffffff; background:#1a1c2e; padding: 2px 8px; border-radius: 12px; font-weight:600;">{row['Status']}</span>
    </div>
    <div style="font-size:12px; color:#64748b; margin-bottom:8px; font-weight:600;">PJ: {row['PJ']}</div>
    <div style="font-size:13px; color:#334155; margin-bottom:12px; line-height: 1.5; flex-grow: 1;">{str(row['Notes'])[:300]}</div>
    <div style="font-size:12px; color:#EA5C1F; font-weight:600; background:#fff7ed; padding: 6px 10px; border-radius: 6px; margin-top: auto;">Target Follow Up: {row['Next_FollowUp'] if row['Next_FollowUp'] else '-'}</div>
</div>""")
            html_blocks.append('</div>')
            st.markdown("".join(html_blocks), unsafe_allow_html=True)
            
            # Paginasi kontrol untuk notes
            if total_note_pages > 1:
                col_n1, col_n2, col_n3 = st.columns([1, 2, 1])
                with col_n1:
                    if st.button("Prev Notes", disabled=st.session_state.note_page <= 1, use_container_width=True, key="prev_note"):
                        st.session_state.note_page -= 1
                        st.rerun()
                with col_n2:
                    st.markdown(f"<div style='text-align:center; padding-top:8px; font-weight:600; color:#1a1c2e; font-size:13px;'>Halaman Notes {st.session_state.note_page} dari {total_note_pages}</div>", unsafe_allow_html=True)
                with col_n3:
                    if st.button("Next Notes", disabled=st.session_state.note_page >= total_note_pages, use_container_width=True, key="next_note"):
                        st.session_state.note_page += 1
                        st.rerun()
        else:
            st.info("Tidak ada notes yang tersedia")

# ─── DOWNLOAD BUTTON & FOOTER ───────────────────────────────────────────────
st.markdown("---")
col_dl1, col_dl2 = st.columns([1, 3])

with col_dl1:
    # Data untuk export
    export_df = filtered[["Nama", "Type", "Kecamatan", "PIC_Name", "Status", "PJ", "Next_FollowUp", "Notes"]].copy()
    csv_out = export_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📄 Download CSV",
        data=csv_out,
        file_name=f"pipeline_idul_adha_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True
    )

st.caption("🐄 Pipeline Idul Adha 1447H · Zakat Sukses · Data realtime dari Google Sheets · Refresh otomatis setiap 5 menit")