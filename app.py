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
        header_row = 1
    
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
        return val
    
    df["Status"] = df["Status"].apply(normalize_status)
    df["Type"] = df["Type"].fillna("-").astype(str).str.strip()
    df["Kecamatan"] = df["Kecamatan"].fillna("-").astype(str).str.strip()
    df["PJ"] = df["PJ"].fillna("").astype(str).str.strip()
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
    st.markdown('<div class="sec-title">📍 Top 5 Kecamatan</div>', unsafe_allow_html=True)
    top_kec = filtered[filtered["Kecamatan"] != "-"]["Kecamatan"].value_counts().head(5)
    
    fig3 = go.Figure(go.Pie(
        labels=top_kec.index,
        values=top_kec.values,
        hole=0.55,
        marker=dict(colors=px.colors.sequential.Oranges_r, line=dict(color="#ffffff", width=3)),
        textinfo="percent",
        textfont=dict(size=11, color="#1a1c2e")
    ))
    fig3.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=20, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(font=dict(size=10), orientation="v", x=1.02, y=0.5)
    )
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

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

pj_summary["Conversion"] = ((pj_summary["Won"] / pj_summary["Total"] * 100).round(1)).fillna(0).astype(str) + "%"

st.dataframe(
    pj_summary,
    use_container_width=True,
    hide_index=True,
    column_config={
        "PJ": st.column_config.TextColumn("PJ Handling", width="medium"),
        "Total": st.column_config.NumberColumn("Total Mitra", format="%d"),
        "Won": st.column_config.NumberColumn("✅ Won", format="%d"),
        "Proposal": st.column_config.NumberColumn("📄 Proposal", format="%d"),
        "Contacted": st.column_config.NumberColumn("📞 Contacted", format="%d"),
        "Lost": st.column_config.NumberColumn("❌ Lost", format="%d"),
        "Conversion": st.column_config.TextColumn("📈 Conv. Rate", width="small"),
    },
)

st.markdown("---")

# ─── MAIN DATA TABLE - DENGAN HEADER WARNA ORANGE ───────────────────────────
st.markdown(
    f'<div class="sec-title">📋 Data Mitra Pipeline '
    f'<span style="background:#EA5C1F;color:#fff;border-radius:20px;padding:2px 12px;font-size:12px;font-weight:600;">'
    f'{len(filtered)} dari {len(df)} hasil</span></div>',
    unsafe_allow_html=True
)

# Siapkan data untuk ditampilkan
display_df = filtered[[
    "Nama", "Type", "Kecamatan", "PIC_Name", "Status", "PJ", "Next_FollowUp"
]].copy()
display_df = display_df.reset_index(drop=True)
display_df.index = display_df.index + 1  # Nomor urut mulai dari 1

# Tampilkan dataframe dengan konfigurasi kolom
st.dataframe(
    display_df,
    use_container_width=True,
    height=550,
    column_config={
        "Nama": st.column_config.TextColumn("📌 Calon Mitra", width="large"),
        "Type": st.column_config.TextColumn("🏛️ Tipe", width="small"),
        "Kecamatan": st.column_config.TextColumn("📍 Kecamatan", width="medium"),
        "PIC_Name": st.column_config.TextColumn("👤 PIC Name", width="medium"),
        "Status": st.column_config.TextColumn("📊 Status", width="medium"),
        "PJ": st.column_config.TextColumn("👔 PJ Handling", width="small"),
        "Next_FollowUp": st.column_config.TextColumn("⏰ Next Follow Up", width="large"),
    },
)

# ─── NOTES EXPANDER ─────────────────────────────────────────────────────────
with st.expander("📝 Lihat Notes & History"):
    if "Notes" in filtered.columns:
        note_df = filtered[["Nama", "Status", "PJ", "Next_FollowUp", "Notes"]].copy()
        note_df = note_df[note_df["Notes"].astype(str).str.strip().notna()]
        
        if len(note_df) > 0:
            html_blocks = []
            for _, row in note_df.iterrows():
                html_blocks.append(f"""<div style="background:#f8f9fa; border-radius:12px; padding:12px 16px; margin-bottom:12px; border-left: 4px solid #EA5C1F;">
    <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
        <span style="font-weight:700; color:#1a1c2e;">🏫 {row['Nama']}</span>
        <span style="font-size:12px; color:#64748b;">👤 {row['PJ']} · {row['Status']}</span>
    </div>
    <div style="font-size:13px; color:#334155; margin-bottom:6px;">📝 {str(row['Notes'])[:300]}</div>
    <div style="font-size:12px; color:#EA5C1F;">⏰ Follow Up: {row['Next_FollowUp'] if row['Next_FollowUp'] else '-'}</div>
</div>""")
            # Optimasi: Render semua HTML sekaligus, bukan memanggil st.markdown berulang kali di dalam loop
            st.markdown("".join(html_blocks), unsafe_allow_html=True)
        else:
            st.info("ℹ️ Tidak ada notes yang tersedia")

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