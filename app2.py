# dashboard_whatsapp.py
# Mockup Dashboard Analisis Percakapan WhatsApp - LAZ Zakat Sukses

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re

import importlib

WordCloud = None
try:
    _wordcloud_mod = importlib.import_module("wordcloud")
    WordCloud = getattr(_wordcloud_mod, "WordCloud", None)
except Exception:
    WordCloud = None

reportlab_canvas = None
A4_PAGE = None
try:
    _pagesizes = importlib.import_module("reportlab.lib.pagesizes")
    _canvas_mod = importlib.import_module("reportlab.pdfgen.canvas")
    reportlab_canvas = _canvas_mod
    A4_PAGE = getattr(_pagesizes, "A4", None)
except Exception:
    reportlab_canvas = None
    A4_PAGE = None

SHEET_ID = "1IkTPYjIZp_FEJWFaVGgC_EzeU1UuwC3o"
SHEET_GID = "1795788289"
DEFAULT_SHEET_CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={SHEET_GID}"
)

# ==================== KONFIGURASI HALAMAN ====================
st.set_page_config(
    page_title="Dashboard WhatsApp - LAZ Zakat Sukses",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== UI STYLE (CSS) ====================
st.markdown(
        """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    * { font-family: 'Inter', sans-serif; }

    .stApp {
        background: linear-gradient(135deg, #f5f7fc 0%, #ffffff 100%);
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1119 0%, #1a1c2e 100%) !important;
        border-right: 1px solid #2d3047 !important;
    }
    [data-testid="stSidebar"] * { color: #e2e4f0 !important; }
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stDateInput label,
    [data-testid="stSidebar"] .stSelectbox label {
        font-size: 11px;
        font-weight: 700;
        color: #8b92b0 !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    [data-testid="stSidebar"] .stMultiSelect > div,
    [data-testid="stSidebar"] .stDateInput > div,
    [data-testid="stSidebar"] .stSelectbox > div {
        border-radius: 10px !important;
    }
    [data-testid="stSidebar"] hr { border-color: #3d405b !important; }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        border: 1px solid #e8ecf2;
        border-radius: 16px;
        padding: 16px 18px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    [data-testid="metric-container"] label {
        font-size: 11px !important;
        font-weight: 800 !important;
        color: #6b7280 !important;
        text-transform: uppercase;
        letter-spacing: 0.7px;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 900 !important;
        color: #111827 !important;
    }

    /* DataFrame styling */
    div[data-testid="stDataFrame"] {
        border-radius: 16px !important;
        overflow: hidden !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    }
    div[data-testid="stDataFrame"] thead tr th {
        background: linear-gradient(135deg, #EA5C1F 0%, #c2410c 100%) !important;
        color: white !important;
        font-weight: 800 !important;
        font-size: 12px !important;
        border: none !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="stDataFrame"] tbody tr td {
        font-size: 13px !important;
        color: #0f172a !important;
        border-bottom: 1px solid #f0f2f6 !important;
        background: #ffffff !important;
    }
    div[data-testid="stDataFrame"] tbody tr:nth-child(even) td {
        background: #fafafa !important;
    }
    div[data-testid="stDataFrame"] tbody tr:hover td {
        background: #fff7ed !important;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 700 !important;
    }
    .stDownloadButton > button {
        border-radius: 10px !important;
        font-weight: 700 !important;
    }
</style>
""",
        unsafe_allow_html=True,
)

# ==================== JUDUL ====================
st.title("📊 Dashboard Analisis Percakapan Zaskia")
st.caption("LAZ Zakat Sukses | Periode: 5–18 Mei 2026")


def _clean_text_for_nlp(text: str) -> str:
    text = str(text)
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"[^0-9A-Za-zÀ-ÿ\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


_ID_STOPWORDS = {
    "yang", "dan", "di", "ke", "dari", "untuk", "pada", "dengan", "atau", "ini", "itu",
    "saya", "kamu", "anda", "kita", "kami", "mereka", "dia", "kami", "nya", "ya", "y",
    "mohon", "maaf", "terima", "kasih", "baik", "sahabat", "tolong", "bisa", "tidak", "udah",
    "sudah", "belum", "lagi", "banget", "aja", "dong", "nih", "lah", "kok", "juga", "agar",
}


_POS_WORDS = {
    "baik", "bagus", "mantap", "senang", "puas", "cepat", "jelas", "membantu", "terbantu",
    "terimakasih", "makasih", "alhamdulillah", "sip", "oke", "ok", "recommended",
}

_NEG_WORDS = {
    "buruk", "jelek", "kecewa", "lambat", "lama", "parah", "ribet", "susah", "sulit", "gagal",
    "error", "salah", "bohong", "mahal", "kesal", "marah",
}


def _sentiment_label(text: str) -> str:
    cleaned = _clean_text_for_nlp(text)
    tokens = [t for t in cleaned.split(" ") if t and t not in _ID_STOPWORDS]
    if not tokens:
        return "neutral"
    score = 0
    for t in tokens:
        if t in _POS_WORDS:
            score += 1
        if t in _NEG_WORDS:
            score -= 1
    if score > 0:
        return "positive"
    if score < 0:
        return "negative"
    return "neutral"


def _make_pdf_report(df_filtered: pd.DataFrame) -> bytes:
    if reportlab_canvas is None or A4_PAGE is None:
        raise RuntimeError("PDF export membutuhkan package 'reportlab'.")

    import io

    out = io.BytesIO()
    c = reportlab_canvas.Canvas(out, pagesize=A4_PAGE)

    width, height = A4_PAGE
    x = 40
    y = height - 50

    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, "Dashboard WhatsApp - LAZ Zakat Sukses")
    y -= 18
    c.setFont("Helvetica", 10)
    c.drawString(x, y, f"Export time: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M:%S')}")
    y -= 22

    total = len(df_filtered)
    unik = int(df_filtered["phone"].nunique()) if not df_filtered.empty and "phone" in df_filtered.columns else 0
    read_rate = 0
    if total > 0 and "status" in df_filtered.columns:
        read_rate = (df_filtered[df_filtered["status"] == "read"].shape[0] / total) * 100

    c.setFont("Helvetica-Bold", 11)
    c.drawString(x, y, "Ringkasan")
    y -= 14
    c.setFont("Helvetica", 10)
    c.drawString(x, y, f"Total pesan: {total}")
    y -= 12
    c.drawString(x, y, f"Kontak unik: {unik}")
    y -= 12
    c.drawString(x, y, f"Read rate: {read_rate:.0f}%")
    y -= 18

    if not df_filtered.empty and "Sentiment" in df_filtered.columns:
        sent_counts = df_filtered["Sentiment"].value_counts()
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x, y, "Sentiment")
        y -= 14
        c.setFont("Helvetica", 10)
        for label in ["positive", "neutral", "negative"]:
            if label in sent_counts.index:
                c.drawString(x, y, f"{label.title()}: {int(sent_counts[label])}")
                y -= 12
        y -= 8

    c.setFont("Helvetica-Bold", 11)
    c.drawString(x, y, "Contoh pesan (maks 15 baris)")
    y -= 14
    c.setFont("Helvetica", 9)

    cols = [cname for cname in ["Date_time", "name", "phone", "status", "Topic", "text"] if cname in df_filtered.columns]
    sample = df_filtered[cols].head(15) if cols else df_filtered.head(15)
    for _, row in sample.iterrows():
        line = " | ".join(
            [
                str(row.get("Date_time", ""))[:19],
                str(row.get("name", ""))[:20],
                str(row.get("phone", ""))[:15],
                str(row.get("status", ""))[:8],
                str(row.get("Topic", ""))[:12],
                str(row.get("text", "")).replace("\n", " ")[:70],
            ]
        )
        c.drawString(x, y, line)
        y -= 11
        if y < 60:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 9)

    c.save()
    return out.getvalue()

# ==================== FUNGSI KLASIFIKASI TOPIK ====================
def classify_topic(text):
    text_lower = str(text).lower()
    if re.search(r'qurban|kambing|sapi|hewan|kurban', text_lower):
        return 'Qurban'
    elif re.search(r'zakat|maal|fitrah|nisab|haul', text_lower):
        return 'Zakat'
    elif re.search(r'infak|sedekah|infaq|donasi|daging', text_lower):
        return 'Infak/Sedekah'
    elif re.search(r'pemberdayaan|gerobak|beasiswa|sudaya|air bersih', text_lower):
        return 'Program Pemberdayaan'
    elif re.search(r'ambulance|ambulan|layanan medis', text_lower):
        return 'Ambulance'
    elif re.search(r'mitra|kerjasama|partnership|proposal|lowongan', text_lower):
        return 'Partnership/CS'
    else:
        return 'Lainnya'

def need_cs_followup(text):
    text_lower = str(text).lower()
    keywords = ['customer service', 'fallback', 'belum memiliki informasi', 
                'arahkan ke admin', 'belum ada data', 'belum menemukan informasi']
    return any(keyword in text_lower for keyword in keywords)

# ==================== LOAD DATA ====================
@st.cache_data
def load_data():
    def _norm(s: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", str(s).strip().lower())

    def _pick_col(df_: pd.DataFrame, candidates: list[str]) -> str | None:
        candidates_norm = {_norm(c) for c in candidates}
        for col in df_.columns:
            if _norm(col) in candidates_norm:
                return col
        return None

    csv_url = DEFAULT_SHEET_CSV_URL
    try:
        csv_url = st.secrets["SHEET_CSV_URL"]
    except Exception:
        csv_url = DEFAULT_SHEET_CSV_URL

    try:
        df = pd.read_csv(csv_url)
    except Exception as e:
        raise RuntimeError(
            "Gagal mengambil data Google Sheet. Pastikan Sheet bisa diakses publik (Anyone with the link) "
            "atau set `SHEET_CSV_URL` di Streamlit secrets. "
            f"Detail: {e}"
        )

    df.columns = [str(c).strip() for c in df.columns]

    # Flexible column mapping (supports Indonesian/English variants)
    mapping: dict[str, str] = {}
    col_id = _pick_col(df, ["id", "no", "nomor", "index"])
    col_jid = _pick_col(df, ["jid", "chatjid", "whatsappjid", "wa_jid"])
    col_name = _pick_col(df, ["name", "nama", "contact", "kontak", "sendername"])
    col_status = _pick_col(df, ["status", "msgstatus", "message_status"])
    col_text = _pick_col(df, ["text", "pesan", "message", "chat", "body", "content"])
    col_phone = _pick_col(df, ["phone", "nohp", "nomorhp", "nomorwa", "msisdn", "number"])
    col_dt = _pick_col(df, ["date_time", "datetime", "date", "tanggal", "waktu", "timestamp", "created_at"])

    if col_id:
        mapping[col_id] = "id"
    if col_jid:
        mapping[col_jid] = "jid"
    if col_name:
        mapping[col_name] = "name"
    if col_status:
        mapping[col_status] = "status"
    if col_text:
        mapping[col_text] = "text"
    if col_phone:
        mapping[col_phone] = "phone"
    if col_dt:
        mapping[col_dt] = "Date_time"

    df = df.rename(columns=mapping)

    # Ensure required columns exist
    if "text" not in df.columns:
        df["text"] = ""
    if "status" not in df.columns:
        df["status"] = ""
    if "name" not in df.columns:
        df["name"] = ""
    if "phone" not in df.columns:
        df["phone"] = ""
    if "jid" not in df.columns:
        df["jid"] = ""
    if "Date_time" not in df.columns:
        df["Date_time"] = ""
    if "id" not in df.columns:
        df["id"] = range(1, len(df) + 1)

    # Clean types
    df["status"] = df["status"].astype(str).str.strip().str.lower()
    df["text"] = df["text"].astype(str)
    df["name"] = df["name"].astype(str)
    df["phone"] = df["phone"].astype(str)
    df["jid"] = df["jid"].astype(str)

    # Parse datetime flexibly (supports dd/mm/yyyy or ISO)
    dt = pd.to_datetime(df["Date_time"], errors="coerce", dayfirst=True)
    if dt.isna().all():
        # try one more time without dayfirst (some exports use yyyy-mm-dd)
        dt = pd.to_datetime(df["Date_time"], errors="coerce", dayfirst=False)
    df["Date_time"] = dt
    
    # Tambahkan kolom analitik
    df['Topic'] = df['text'].apply(classify_topic)
    df['Need_CS'] = df['text'].apply(need_cs_followup)
    df['Date'] = df['Date_time'].dt.date
    df['Hour'] = df['Date_time'].dt.hour
    
    return df

df = load_data()

# ==================== SIDEBAR FILTER ====================
st.sidebar.header("🔍 Filter Data")

with st.sidebar:
    st.caption("Gunakan filter di bawah untuk memperbarui semua grafik & tabel.")
    st.divider()

# Status filter
status_filter = st.sidebar.multiselect(
    "Status Pesan",
    options=df['status'].unique(),
    default=df['status'].unique()
)

status_filter_effective = status_filter if len(status_filter) > 0 else list(df['status'].unique())
if len(status_filter) == 0:
    st.sidebar.info("Status kosong → menampilkan semua status.")

# Topic filter
topic_filter = st.sidebar.multiselect(
    "Topik Percakapan",
    options=df['Topic'].unique(),
    default=df['Topic'].unique()
)

topic_filter_effective = topic_filter if len(topic_filter) > 0 else list(df['Topic'].unique())
if len(topic_filter) == 0:
    st.sidebar.info("Topik kosong → menampilkan semua topik.")

# Date range filter
min_date = df['Date'].min()
max_date = df['Date'].max()
date_range = st.sidebar.date_input(
    "Rentang Tanggal",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, (tuple, list)):
    if len(date_range) == 2:
        start_date, end_date = date_range
    elif len(date_range) == 1:
        start_date = end_date = date_range[0]
    else:
        start_date, end_date = min_date, max_date
else:
    start_date = end_date = date_range

# Apply filters
df_filtered = df[
    (df['status'].isin(status_filter_effective)) &
    (df['Topic'].isin(topic_filter_effective)) &
    (df['Date'] >= pd.to_datetime(start_date).date()) &
    (df['Date'] <= pd.to_datetime(end_date).date())
]

# Urutkan data dari yang tertinggi/terbaru
sort_cols = [c for c in ['Date_time', 'id'] if c in df_filtered.columns]
if sort_cols:
    ascending = [False] * len(sort_cols)
    df_filtered = df_filtered.sort_values(by=sort_cols, ascending=ascending, na_position='last')

if not df_filtered.empty and 'text' in df_filtered.columns:
    df_filtered = df_filtered.copy()
    df_filtered['Sentiment'] = df_filtered['text'].apply(_sentiment_label)

# ==================== METRIK UTAMA ====================
st.markdown("### 📈 Ringkasan Metrik")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Percakapan", f"{len(df_filtered):,}")
with col2:
    st.metric("Kontak Unik", f"{df_filtered['phone'].nunique():,}")
with col3:
    read_pct = (df_filtered[df_filtered['status'] == 'read'].shape[0] / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
    st.metric("Read Rate", f"{read_pct:.0f}%")
with col4:
    cs_needed = df_filtered['Need_CS'].sum()
    st.metric("Perlu Follow-up CS", f"{cs_needed}")
with col5:
    top_topic = df_filtered['Topic'].mode().iloc[0] if not df_filtered.empty else "-"
    st.metric("Topik Dominan", top_topic)

# ==================== VISUALISASI ====================
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Status Pesan")
    if df_filtered.empty:
        st.info("Tidak ada data untuk ditampilkan (cek filter).")
    else:
        status_counts = df_filtered['status'].value_counts()
        if status_counts.empty:
            st.info("Tidak ada status untuk ditampilkan.")
        else:
            status_df = status_counts.reset_index()
            status_df.columns = ["status", "count"]
            fig_status = px.pie(
                status_df,
                values="count",
                names="status",
                color="status",
                color_discrete_map={'read': '#4CAF50', 'sent': '#FF9800'},
                hole=0.4
            )
            fig_status.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_status, use_container_width=True)

with col2:
    st.subheader("🏷️ Topik Percakapan")
    if df_filtered.empty:
        st.info("Tidak ada data untuk ditampilkan (cek filter).")
    else:
        topic_counts = df_filtered['Topic'].value_counts().head(6)
        if topic_counts.empty:
            st.info("Tidak ada topik untuk ditampilkan.")
        else:
            topic_df = topic_counts.reset_index()
            topic_df.columns = ["Topic", "count"]
            fig_topic = px.bar(
                topic_df,
                x="count",
                y="Topic",
                orientation='h',
                color="count",
                color_continuous_scale='Blues',
                labels={'count': 'Jumlah Pesan', 'Topic': 'Topik'}
            )
            fig_topic.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_topic, use_container_width=True)

# ==================== GRAFIK TREND ====================
st.markdown("### 📅 Tren Percakapan per Hari")
daily_counts = df_filtered.groupby('Date').size().reset_index(name='count')
fig_trend = px.line(
    daily_counts,
    x='Date',
    y='count',
    markers=True,
    labels={'Date': 'Tanggal', 'count': 'Jumlah Pesan'}
)
fig_trend.update_layout(hovermode='x unified')
st.plotly_chart(fig_trend, use_container_width=True)

# ==================== KONTAK TERAKTIF ====================
col1, col2 = st.columns(2)

with col1:
    st.subheader("👥 Top 10 Kontak Paling Aktif")
    if df_filtered.empty:
        st.info("Tidak ada data untuk ditampilkan (cek filter).")
    else:
        contact_counts = df_filtered['name'].value_counts().head(10)
        if contact_counts.empty:
            st.info("Tidak ada kontak untuk ditampilkan.")
        else:
            contact_df = contact_counts.reset_index()
            contact_df.columns = ["name", "count"]
            fig_contact = px.bar(
                contact_df,
                x="count",
                y="name",
                orientation='h',
                color="count",
                color_continuous_scale='Oranges',
                labels={'count': 'Jumlah Pesan', 'name': 'Nama Kontak'}
            )
            fig_contact.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_contact, use_container_width=True)

with col2:
    st.subheader("⏰ Distribusi Pesan per Jam")
    hourly_counts = df_filtered.groupby('Hour').size().reset_index(name='count')
    fig_hourly = px.bar(
        hourly_counts,
        x='Hour',
        y='count',
        color='count',
        color_continuous_scale='Teal',
        labels={'Hour': 'Jam (24h)', 'count': 'Jumlah Pesan'}
    )
    st.plotly_chart(fig_hourly, use_container_width=True)

# ==================== ANALISIS TEKS ====================
st.markdown("### 🧾 Analisis Teks")

tab_wc, tab_sent = st.tabs(["☁️ Word Cloud", "😊 Sentiment"])

with tab_wc:
    st.caption("Berdasarkan pesan terfilter.")
    if df_filtered.empty:
        st.info("Tidak ada data untuk ditampilkan.")
    elif WordCloud is None:
        st.info("Word Cloud membutuhkan package `wordcloud`. Install: `pip install wordcloud`.")
    else:
        try:
            texts = " ".join(_clean_text_for_nlp(t) for t in df_filtered["text"].astype(str).tolist())
            tokens = [t for t in texts.split(" ") if t and t not in _ID_STOPWORDS and len(t) > 2]
            wc_text = " ".join(tokens).strip()

            if not wc_text:
                st.info("Teks terlalu sedikit setelah dibersihkan (stopwords/karakter).")
            else:
                wc = WordCloud(
                    width=1400,
                    height=600,
                    background_color="white",
                    collocations=False,
                ).generate(wc_text)
                st.image(wc.to_array(), use_container_width=True)
        except Exception as e:
            st.warning(f"Gagal membuat word cloud: {e}")

with tab_sent:
    st.caption("Rule-based sentiment (positive/neutral/negative) dari pesan terfilter.")
    if df_filtered.empty or "Sentiment" not in df_filtered.columns:
        st.info("Tidak ada data untuk dianalisis.")
    else:
        col_pie, col_trend = st.columns([1, 2])

        with col_pie:
            sent_counts = (
                df_filtered["Sentiment"].value_counts()
                .reindex(["positive", "neutral", "negative"])
                .fillna(0)
                .astype(int)
            )

            fig_sent = px.pie(
                values=sent_counts.values,
                names=[s.title() for s in sent_counts.index.tolist()],
                hole=0.55,
            )
            fig_sent.update_traces(textposition='inside', textinfo='percent+label')
            fig_sent.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_sent, use_container_width=True)

        with col_trend:
            sent_daily = (
                df_filtered.groupby(["Date", "Sentiment"]).size().reset_index(name="count")
                if "Date" in df_filtered.columns else pd.DataFrame(columns=["Date", "Sentiment", "count"])
            )
            if sent_daily.empty:
                st.info("Belum ada tren sentiment (kolom tanggal kosong).")
            else:
                fig_sent_trend = px.line(
                    sent_daily,
                    x="Date",
                    y="count",
                    color="Sentiment",
                    markers=True,
                    labels={"Date": "Tanggal", "count": "Jumlah Pesan"},
                )
                fig_sent_trend.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_sent_trend, use_container_width=True)

# ==================== EXPORT PDF ====================
st.markdown("### 📄 Export")
if reportlab_canvas is None:
    st.info("Export PDF membutuhkan package `reportlab`. Install: `pip install reportlab`.")
else:
    col_pdf_1, col_pdf_2 = st.columns([1, 3])
    with col_pdf_1:
        generate_pdf = st.button("Generate PDF")
    with col_pdf_2:
        st.caption("PDF berisi ringkasan + contoh 15 pesan dari data terfilter.")

    if generate_pdf:
        try:
            pdf_bytes = _make_pdf_report(df_filtered)
            st.download_button(
                label="⬇️ Download PDF (hasil generate)",
                data=pdf_bytes,
                file_name="dashboard_whatsapp_report.pdf",
                mime="application/pdf",
            )
        except Exception as e:
            st.warning(f"Gagal generate PDF: {e}")

# ==================== TABEL PERLU FOLLOW-UP ====================
st.subheader("⚠️ Percakapan yang Perlu Follow-up (Customer Service)")

cs_df = df_filtered[df_filtered['Need_CS'] == True][['Date_time', 'name', 'phone', 'status', 'text']]
if not cs_df.empty and "Date_time" in cs_df.columns:
    cs_df = cs_df.copy()
    cs_df["Date_time"] = pd.to_datetime(cs_df["Date_time"], errors="coerce").dt.strftime("%d/%m/%Y %H:%M")
cs_df = cs_df.rename(columns={
    'Date_time': 'Tanggal/Jam',
    'name': 'Nama',
    'phone': 'Nomor WA',
    'status': 'Status',
    'text': 'Pesan'
})

if not cs_df.empty:
    st.dataframe(cs_df, use_container_width=True, height=300)
    
    # Export button
    csv = cs_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Daftar Follow-up (CSV)",
        data=csv,
        file_name="followup_cs.csv",
        mime="text/csv"
    )
else:
    st.info("✅ Tidak ada percakapan yang memerlukan follow-up CS.")

# ==================== TABEL DATA LENGKAP ====================
with st.expander("📋 Lihat Seluruh Data Percakapan"):
    full_df = df_filtered[['Date_time', 'name', 'phone', 'status', 'Topic', 'Need_CS', 'Sentiment', 'text']].copy() if 'Sentiment' in df_filtered.columns else df_filtered[['Date_time', 'name', 'phone', 'status', 'Topic', 'Need_CS', 'text']].copy()
    if "Date_time" in full_df.columns:
        full_df["Date_time"] = pd.to_datetime(full_df["Date_time"], errors="coerce").dt.strftime("%d/%m/%Y %H:%M")
    st.dataframe(
        full_df.head(100),
        use_container_width=True,
        height=400
    )

# ==================== FOOTER ====================
st.divider()
st.caption("Dashboard ini dibuat untuk monitoring percakapan WhatsApp LAZ Zakat Sukses.")
st.caption(f"Terakhir diperbarui: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M:%S')} | Data: {len(df_filtered)} percakapan dari {df['Date'].nunique()} hari")