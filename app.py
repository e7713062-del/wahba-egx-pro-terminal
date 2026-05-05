import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
from datetime import datetime
import pytz

# --- 1. إعدادات الوقت (القاهرة أوتوماتيك) ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)
today_key = now_egypt.strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba Intelligence", layout="wide")

# --- 2. التصميم المؤسسي (بدون f-string لمنع أخطاء التحميل) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif; }
    .stApp { background-color: #000000; color: #ffffff; }
    
    /* الهيدر */
    .nav-bar {
        text-align: center; padding: 30px; background: #000;
        border-bottom: 2px solid #d4af37; margin-bottom: 20px;
    }
    .logo-text { font-size: 30px; font-weight: 900; color: #fff; letter-spacing: 2px; }
    .logo-text span { color: #d4af37; }

    /* التصنيفات */
    .section-header {
        color: #d4af37; border-right: 5px solid #d4af37;
        padding-right: 15px; margin: 40px 0 20px 0; font-size: 24px; font-weight: bold;
    }

    /* كروت الأسهم الذهبية */
    .stock-card {
        background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 15px;
        padding: 25px; margin-bottom: 20px; border-top: 3px solid #d4af37;
    }
    .symbol-name { font-size: 28px; font-weight: 900; color: #d4af37; }
    .price-val { font-size: 24px; font-weight: bold; color: #fff; }
    
    /* مستويات الدعم والمقاومة */
    .levels-grid {
        display: flex; justify-content: space-between; margin-top: 20px;
        background: #000; padding: 10px; border-radius: 8px; border: 1px solid #111;
    }
    .level-item { text-align: center; }
    .label { font-size: 10px; color: #555; display: block; }
    .num { font-size: 14px; font-weight: bold; color: #d4af37; font-family: monospace; }

    /* زر التشغيل */
    .stButton>button {
        background: #d4af37 !important; color: #000 !important;
        font-weight: 900 !important; border-radius: 10px !important;
        height: 60px !important; width: 100% !important; border: none !important;
    }
    
    /* التذييل */
    .footer-box {
        margin-top: 80px; padding: 40px; text-align: center;
        border-top: 1px solid #1a1a1a; color: #444; font-size: 12px;
    }
    </style>
    
    <div class="nav-bar">
        <div class="logo-text">WAHBA <span>INTELLIGENCE</span></div>
        <p style="color:#444; font-size:10px;">INSTITUTIONAL GRADE TERMINAL</p>
    </div>
""", unsafe_allow_html=True)

# --- 3. محرك البيانات (أرشفة كاملة لليوم) ---

@st.cache_data(ttl=86400)
def fetch_egx_list(date_key):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=15).json()
        return [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except: return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK"]

@st.cache_data(ttl=86400, show_spinner=False)
def run_strategic_scan(date_key):
    symbols = fetch_egx_list(date_key)
    results = []
    p_bar = st.progress(0)
    
    for i, sym in enumerate(symbols):
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=10)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            rec = analysis.summary["RECOMMENDATION"]
            
            score = 0
            if "STRONG_BUY" in rec: score += 5
            elif "BUY" in rec: score += 3
            if ind.get("RSI") and 50 <= ind.get("RSI") <= 68: score += 3
            if ind.get("close") > ind.get("Pivot.M.Classic.Middle"): score += 2

            results.append({
                "Symbol": sym, "Price": round(ind.get("close"), 2), "Score": score,
                "S1": round(ind.get("Pivot.M.Classic.S1"), 2),
                "P": round(ind.get("Pivot.M.Classic.Middle"), 2),
                "R1": round(ind.get("Pivot.M.Classic.R1"), 2),
                "Signal": rec
            })
        except: continue
        p_bar.progress((i + 1) / len(symbols))
    
    p_bar.empty()
    return pd.DataFrame(results)

# --- 4. واجهة التحكم والعرض ---

st.write(f"توقيت التقرير: {now_egypt.strftime('%H:%M')} | {today_key}")

if st.button('إصدار التقرير الذهبي لليوم'):
    st.session_state.final_report = run_strategic_scan(today_key)

if 'final_report' not in st.session_state:
    st.session_state.final_report = None

data = st.session_state.final_report

if data is not None and not data.empty:
    
    # تصنيف 1: نخبة النخبة الذهبية
    t1 = data[data['Score'] >= 9]
    if not t1.empty:
        st.markdown('<div class="section-header">⚜️ نخبـة نخبـة الصعـود</div>', unsafe_allow_html=True)
        for _, row in t1.iterrows():
            st.markdown(f"""
            <div class="stock-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="symbol-name">{row['Symbol']}</span>
                    <span style="color:#d4af37; font-weight:bold;">{row['Signal']}</span>
                </div>
                <div class="price-val">{row['Price']} <small style="font-size:12px; color:#444;">EGP</small></div>
                <div class="levels-grid">
                    <div class="level-item"><span class="label">S1 (دعم)</span><span class="num">{row['S1']}</span></div>
                    <div class="level-item"><span class="label">PIVOT (ارتكاز)</span><span class="num">{row['P']}</span></div>
                    <div class="level-item"><span class="label">R1 (مقاومة)</span><span class="num">{row['R1']}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # تصنيف 2: النخبة الصاعدة
    t2 = data[(data['Score'] >= 6) & (data['Score'] < 9)]
    if not t2.empty:
        st.markdown('<div class="section-header">💎 نخبـة الصعـود</div>', unsafe_allow_html=True)
        cols = st.columns(2)
        for idx, row in t2.reset_index().iterrows():
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="stock-card" style="border-top: 1px solid #d4af37;">
                    <div style="font-size:20px; font-weight:900;">{row['Symbol']}</div>
                    <div style="color:#d4af37; font-size:18px;">{row['Price']} EGP</div>
                    <div style="font-size:11px; color:#444; margin-top:10px;">R1: {row['R1']} | S1: {row['S1']}</div>
                </div>
                """, unsafe_allow_html=True)

# --- 5. التذييل الفاخر ---
st.markdown("""
    <div class="footer-box">
        <p style="font-weight:bold; color:#d4af37;">WAHBA INTELLIGENCE • INSTITUTIONAL DIVISION</p>
        <p>التقرير مؤرشف لليوم لضمان الثبات الكامل. جميع الحقوق محفوظة 2026</p>
    </div>
""", unsafe_allow_html=True)
