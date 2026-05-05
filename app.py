import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
from datetime import datetime
import pytz

# --- 1. محرك التوقيت الذكي ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)
today_key = now_egypt.strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba Intelligence Terminal", layout="wide", initial_sidebar_state="collapsed")

# --- 2. الهندسة البصرية (Professional Web UI) ---
# تم استخدام علامة {{}} للـ CSS لتجنب خطأ f-string SyntaxError
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    
    * {{ font-family: 'Tajawal', sans-serif; }}
    .stApp {{ background-color: #030303; color: #ffffff; }}
    
    .nav-bar {{
        display: flex; justify-content: space-between; align-items: center;
        padding: 20px 40px; background: rgba(0,0,0,0.8);
        border-bottom: 1px solid #1a1a1a; position: sticky; top: 0; z-index: 999;
    }}
    .logo {{ font-size: 28px; font-weight: 900; letter-spacing: -1px; }}
    .logo span {{ color: #00ff00; }}
    .time-badge {{ background: #111; padding: 5px 15px; border-radius: 20px; font-size: 12px; border: 1px solid #222; }}

    .section-title {{
        margin: 40px 0 20px 0; padding-right: 15px; border-right: 4px solid #00ff00;
        font-size: 22px; font-weight: 800; color: #fff;
    }}

    .stock-card {{
        background: rgba(15, 15, 15, 0.6); backdrop-filter: blur(10px);
        border: 1px solid #222; border-radius: 20px; padding: 25px;
        transition: 0.4s ease-weight; margin-bottom: 20px;
    }}
    .stock-card:hover {{ border-color: #00ff00; transform: translateY(-5px); }}

    .price-tag {{ font-size: 32px; font-weight: 900; margin: 10px 0; color: #fff; }}
    
    .level-pill {{
        background: #000; border: 1px solid #1a1a1a; border-radius: 10px;
        padding: 12px; margin-top: 15px; display: flex; justify-content: space-around;
    }}
    .val-item {{ text-align: center; }}
    .val-label {{ font-size: 9px; color: #555; display: block; }}
    .val-num {{ font-size: 14px; font-weight: bold; font-family: monospace; }}

    .stButton>button {{
        background: linear-gradient(90deg, #00ff00 0%, #008800 100%) !important;
        color: #000 !important; font-weight: 900 !important; font-size: 18px !important;
        border-radius: 15px !important; border: none !important; height: 60px !important;
        width: 100% !important; cursor: pointer;
    }}

    .footer {{
        background: #000; padding: 50px 20px; margin-top: 80px;
        border-top: 1px solid #111; color: #444; text-align: center; font-size: 12px;
    }}
    </style>
    
    <div class="nav-bar">
        <div class="logo">WAHBA <span>INTELLIGENCE</span></div>
        <div class="time-badge">توقيت القاهرة: {now_egypt.strftime('%H:%M')}</div>
    </div>
""", unsafe_allow_html=True)

# --- 3. المحرك التقني المستقر ---

@st.cache_data(ttl=86400)
def get_market_tickers(date_key):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={{"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}}, timeout=20).json()
        return [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except: return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK"]

@st.cache_data(ttl=86400, show_spinner=False)
def generate_web_report(date_key):
    symbols = get_market_tickers(date_key)
    scanned = []
    p_bar = st.progress(0)
    
    for i, sym in enumerate(symbols):
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=12)
            analysis = handler.get_analysis()
            ind, rec = analysis.indicators, analysis.summary["RECOMMENDATION"]
            
            score = 0
            if "STRONG_BUY" in rec: score += 5
            elif "BUY" in rec: score += 3
            if ind.get("RSI") and 50 <= ind.get("RSI") <= 68: score += 3
            if ind.get("close") > ind.get("Pivot.M.Classic.Middle"): score += 2

            scanned.append({{
                "Symbol": sym, "Price": round(ind.get("close"), 2), "Score": score,
                "S1": round(ind.get("Pivot.M.Classic.S1"), 2),
                "P": round(ind.get("Pivot.M.Classic.Middle"), 2),
                "R1": round(ind.get("Pivot.M.Classic.R1"), 2),
                "Signal": rec
            }})
        except: continue
        p_bar.progress((i + 1) / len(symbols))
    
    p_bar.empty()
    return pd.DataFrame(scanned)

# --- 4. واجهة العرض والتشغيل ---

st.write("")
if st.button('تحديث البيانات وإصدار التقرير الاستراتيجي'):
    st.session_state.web_db = generate_web_report(today_key)

if 'web_db' not in st.session_state:
    st.session_state.web_db = None

db = st.session_state.web_db

if db is not None and not db.empty:
    # 1. نخبة نخبة الصعود (Score >= 9)
    t1 = db[db['Score'] >= 9]
    if not t1.empty:
        st.markdown('<div class="section-title">🏆 نخبـة نخبـة الصعـود</div>', unsafe_allow_html=True)
        cols = st.columns(2)
        for idx, row in t1.reset_index().iterrows():
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="stock-card" style="border-top: 4px solid #00ff00;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:10px; color:#555;">PREMIUM SELECTION</span>
                        <span style="color:#00ff00; font-size:11px; font-weight:bold;">{row['Signal']}</span>
                    </div>
                    <div class="price-tag">{row['Symbol']} <small style="font-size:14px; color:#444;">{row['Price']} EGP</small></div>
                    <div class="level-pill">
                        <div class="val-item"><span class="val-label">دعم</span><span class="val-num" style="color:#00ff00;">{row['S1']}</span></div>
                        <div class="val-item"><span class="val-label">ارتكاز</span><span class="val-num">{row['P']}</span></div>
                        <div class="val-item"><span class="val-label">مقاومة</span><span class="val-num" style="color:#ff4b4b;">{row['R1']}</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # 2. نخبة الصعود (Score 6-8)
    t2 = db[(db['Score'] >= 6) & (db['Score'] < 9)]
    if not t2.empty:
        st.markdown('<div class="section-title">💎 نخبـة الصعـود</div>', unsafe_allow_html=True)
        cols = st.columns(3)
        for idx, row in t2.reset_index().iterrows():
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="stock-card">
                    <div style="font-weight:bold; font-size:18px; color:#00ff00;">{row['Symbol']}</div>
                    <div style="font-size:22px; font-weight:900; margin:5px 0;">{row['Price']} <small style="font-size:10px; color:#444;">EGP</small></div>
                    <div style="font-size:10px; color:#555; margin-top:10px; border-top:1px solid #1a1a1a; padding-top:5px;">
                        R1: {row['R1']} | S1: {row['S1']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# --- 5. التذييل المؤسسي ---
st.markdown(f"""
    <div class="footer">
        <p style="font-size:14px; color:#fff; font-weight:bold;">WAHBA INTELLIGENCE TERMINAL</p>
        <p>جميع البيانات مؤرشفة لليوم لضمان استقرار التقرير. الاستثمار مسؤوليتك الشخصية.</p>
        <p>© 2026 Wahba Intelligence. All Rights Reserved.</p>
    </div>
""", unsafe_allow_html=True)
