import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
from datetime import datetime
import pytz

# --- 1. محرك التوقيت الذكي (القاهرة) ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)
today_key = now_egypt.strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba Intelligence Terminal", layout="wide", initial_sidebar_state="collapsed")

# --- 2. التصميم المؤسسي الفاخر (Gold & Dark Edition) ---
# تم إصلاح أقواس الـ CSS لتجنب خطأ التحميل (f-string error)
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    
    * {{ font-family: 'Tajawal', sans-serif; }}
    .stApp {{ background-color: #050505; color: #e0e0e0; }}
    
    .nav-bar {{
        display: flex; justify-content: space-between; align-items: center;
        padding: 20px 40px; background: #000;
        border-bottom: 1px solid #1a1a1a; position: sticky; top: 0; z-index: 999;
    }}
    .logo {{ font-size: 26px; font-weight: 900; letter-spacing: 1px; color: #fff; }}
    .logo span {{ color: #d4af37; }} /* لون ذهبي */
    .time-badge {{ background: #111; padding: 5px 15px; border-radius: 5px; font-size: 12px; border: 1px solid #d4af37; color: #d4af37; }}

    .section-title {{
        margin: 40px 0 20px 0; padding-right: 15px; border-right: 4px solid #d4af37;
        font-size: 22px; font-weight: 800; color: #fff;
    }}

    .stock-card {{
        background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 12px; padding: 25px;
        transition: 0.3s; margin-bottom: 20px;
    }}
    .stock-card:hover {{ border-color: #d4af37; background: #0f0f0f; }}

    .price-tag {{ font-size: 30px; font-weight: 900; margin: 10px 0; color: #fff; }}
    .price-tag small {{ font-size: 14px; color: #666; }}
    
    .level-pill {{
        background: #000; border: 1px solid #1a1a1a; border-radius: 8px;
        padding: 12px; margin-top: 15px; display: flex; justify-content: space-around;
    }}
    .val-item {{ text-align: center; }}
    .val-label {{ font-size: 10px; color: #555; display: block; margin-bottom: 4px; }}
    .val-num {{ font-size: 14px; font-weight: bold; font-family: monospace; color: #d4af37; }}

    /* زر التشغيل - تصميم كلاسيكي فخم */
    .stButton>button {{
        background: #d4af37 !important;
        color: #000 !important; font-weight: 900 !important; font-size: 16px !important;
        border-radius: 8px !important; border: none !important; height: 55px !important;
        width: 100% !important; transition: 0.3s !important;
    }}
    .stButton>button:hover {{ background: #b8962e !important; box-shadow: 0 0 15px rgba(212,175,55,0.2) !important; }}

    .footer {{
        background: #000; padding: 40px; margin-top: 60px;
        border-top: 1px solid #1a1a1a; color: #444; text-align: center; font-size: 12px;
    }}
    </style>
    
    <div class="nav-bar">
        <div class="logo">WAHBA <span>INTELLIGENCE</span></div>
        <div class="time-badge">{now_egypt.strftime('%H:%M')} | CAIRO</div>
    </div>
""", unsafe_allow_html=True)

# --- 3. المحرك التقني المؤرشف ---

@st.cache_data(ttl=86400)
def get_tickers(date_key):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={{"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}}, timeout=15).json()
        return [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except: return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO"]

@st.cache_data(ttl=86400, show_spinner=False)
def generate_report(date_key):
    symbols = get_tickers(date_key)
    scanned = []
    p_bar = st.progress(0)
    for i, sym in enumerate(symbols):
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=10)
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

# --- 4. العرض التشغيلي ---

st.write("")
if st.button('إصدار التقرير الاستراتيجي لليوم'):
    st.session_state.master_db = generate_report(today_key)

if 'master_db' not in st.session_state:
    st.session_state.master_db = None

db = st.session_state.master_db

if db is not None and not db.empty:
    # الفئة الأولى: النخبة الذهبية
    t1 = db[db['Score'] >= 9]
    if not t1.empty:
        st.markdown('<div class="section-title">⚜️ نخبـة النخبـة الذهبية</div>', unsafe_allow_html=True)
        cols = st.columns(2)
        for idx, row in t1.reset_index().iterrows():
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="stock-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:10px; color:#555;">INSTITUTIONAL GRADE</span>
                        <span style="color:#d4af37; font-size:11px; font-weight:bold;">{row['Signal']}</span>
                    </div>
                    <div class="price-tag">{row['Symbol']} <small>{row['Price']} EGP</small></div>
                    <div class="level-pill">
                        <div class="val-item"><span class="val-label">SUPPORT</span><span class="val-num">{row['S1']}</span></div>
                        <div class="val-item"><span class="val-label">PIVOT</span><span class="val-num" style="color:#fff;">{row['P']}</span></div>
                        <div class="val-item"><span class="val-label">RESISTANCE</span><span class="val-num">{row['R1']}</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # الفئة الثانية: الأداء المتميز
    t2 = db[(db['Score'] >= 6) & (db['Score'] < 9)]
    if not t2.empty:
        st.markdown('<div class="section-title">📜 الأداء المتميز</div>', unsafe_allow_html=True)
        cols = st.columns(3)
        for idx, row in t2.reset_index().iterrows():
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="stock-card">
                    <div style="font-weight:bold; font-size:18px; color:#fff;">{row['Symbol']}</div>
                    <div style="font-size:20px; font-weight:bold; margin:5px 0; color:#d4af37;">{row['Price']} EGP</div>
                    <div style="font-size:10px; color:#444; border-top:1px solid #1a1a1a; padding-top:10px;">
                        R1: {row['R1']} | S1: {row['S1']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# --- 5. التذييل ---
st.markdown(f"""
    <div class="footer">
        <p style="color:#666; font-weight:bold;">WAHBA INTELLIGENCE • ASSET MANAGEMENT DIVISION</p>
        <p>© 2026 Institutional Data Report. All Rights Reserved.</p>
    </div>
""", unsafe_allow_html=True)
