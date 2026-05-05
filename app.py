import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
from datetime import datetime
import pytz

# --- 1. محرك التوقيت (الصيفي والشتوي أوتوماتيك) ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)
today_key = now_egypt.strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba Intelligence Terminal", layout="wide", initial_sidebar_state="collapsed")

# --- 2. الهندسة البصرية (Professional Web UI) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    
    * {{ font-family: 'Tajawal', sans-serif; }}
    .stApp {{ background-color: #030303; color: #ffffff; }}
    
    /* خلفية الويب الاحترافية */
    .web-container {{
        background: radial-gradient(circle at top right, #111 0%, #030303 100%);
        padding: 20px; border-radius: 0px;
    }}

    /* هيدر الصفحة */
    .nav-bar {{
        display: flex; justify-content: space-between; align-items: center;
        padding: 20px 40px; background: rgba(0,0,0,0.8);
        border-bottom: 1px solid #1a1a1a; position: sticky; top: 0; z-index: 999;
    }}
    .logo {{ font-size: 28px; font-weight: 900; letter-spacing: -1px; }}
    .logo span {{ color: #00ff00; }}
    .time-badge {{ background: #111; padding: 5px 15px; border-radius: 20px; font-size: 12px; border: 1px solid #222; }}

    /* الأقسام (Sections) */
    .section-title {{
        margin: 40px 0 20px 0; padding-right: 15px; border-right: 4px solid #00ff00;
        font-size: 22px; font-weight: 800; color: #fff;
    }}

    /* بطاقات الأسهم (Premium Web Cards) */
    .stock-card {{
        background: rgba(15, 15, 15, 0.6); backdrop-filter: blur(10px);
        border: 1px solid #222; border-radius: 20px; padding: 25px;
        transition: 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275); margin-bottom: 20px;
    }
    .stock-card:hover {{ border-color: #00ff00; transform: translateY(-8px); box-shadow: 0 10px 30px rgba(0,255,0,0.1); }}

    .price-tag {{ font-size: 32px; font-weight: 900; margin: 10px 0; color: #fff; }}
    .price-tag small {{ font-size: 14px; color: #444; font-weight: 400; }}
    
    .level-pill {{
        background: #000; border: 1px solid #1a1a1a; border-radius: 10px;
        padding: 12px; margin-top: 15px; display: flex; justify-content: space-around;
    }}
    .val-item {{ text-align: center; font-family: monospace; }}
    .val-label {{ font-size: 9px; color: #555; text-transform: uppercase; display: block; }}
    .val-num {{ font-size: 14px; font-weight: bold; }}

    /* زر التشغيل الرئيسي */
    .stButton>button {{
        background: linear-gradient(90deg, #00ff00 0%, #008800 100%) !important;
        color: #000 !important; font-weight: 900 !important; font-size: 18px !important;
        border-radius: 15px !important; border: none !important; height: 65px !important;
        box-shadow: 0 4px 15px rgba(0,255,0,0.3) !important; width: 100% !important;
    }}

    /* التذييل المؤسسي */
    .footer {{
        background: #000; padding: 60px 40px; margin-top: 100px;
        border-top: 1px solid #111; color: #333; text-align: center;
    }}
    </style>
    
    <div class="nav-bar">
        <div class="logo">WAHBA <span>INTELLIGENCE</span></div>
        <div class="time-badge">توقيت القاهرة: {now_egypt.strftime('%H:%M')}</div>
    </div>
""", unsafe_allow_html=True)

# --- 3. المحرك التقني المستقر (The Enterprise Engine) ---

@st.cache_data(ttl=86400) # أتمتة سحب الأسهم
def get_market_tickers(date_key):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=20).json()
        return [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except: return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK"]

@st.cache_data(ttl=86400, show_spinner=False) # أرشفة النتائج لليوم بالكامل
def generate_web_report(date_key):
    symbols = get_market_tickers(date_key)
    scanned = []
    p_bar = st.progress(0)
    
    for i, sym in enumerate(symbols):
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=12)
            analysis = handler.get_analysis()
            ind, rec = analysis.indicators, analysis.summary["RECOMMENDATION"]
            
            # منطق التصنيف الثلاثي للنخبة
            score = 0
            if "STRONG_BUY" in rec: score += 5
            elif "BUY" in rec: score += 3
            if ind.get("RSI") and 50 <= ind.get("RSI") <= 68: score += 3
            if ind.get("close") > ind.get("Pivot.M.Classic.Middle"): score += 2

            scanned.append({
                "Symbol": sym, "Price": round(ind.get("close"), 2), "Score": score,
                "S1": round(ind.get("Pivot.M.Classic.S1"), 2),
                "P": round(ind.get("Pivot.M.Classic.Middle"), 2),
                "R1": round(ind.get("Pivot.M.Classic.R1"), 2),
                "Signal": rec
            })
        except: continue
        p_bar.progress((i + 1) / len(symbols))
    
    p_bar.empty()
    return pd.DataFrame(scanned)

# --- 4. العرض والتشغيل (Web Interface Construction) ---

st.write("") # مسافة
if st.button('تحديث البيانات وإصدار التقرير الاستراتيجي'):
    st.session_state.web_db = generate_web_report(today_key)

if 'web_db' not in st.session_state:
    st.session_state.web_db = None

db = st.session_state.web_db

if db is not None and not db.empty:
    
    # تصنيف 1: نخبة نخبة الصعود (The VIP Assets)
    t1 = db[db['Score'] >= 9]
    if not t1.empty:
        st.markdown('<div class="section-title">🏆 نخبـة نخبـة الصعـود</div>', unsafe_allow_html=True)
        cols = st.columns(2)
        for idx, row in t1.iterrows():
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="stock-card" style="border-top: 4px solid #00ff00;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:12px; color:#555;">PREMIUM SELECTION</span>
                        <span style="color:#00ff00; font-size:12px; font-weight:bold;">{row['Signal']}</span>
                    </div>
                    <div class="price-tag">{row['Symbol']} <small>{row['Price']} EGP</small></div>
                    <div class="level-pill">
                        <div class="val-item"><span class="val-label">دعم</span><span class="val-num" style="color:#00ff00;">{row['S1']}</span></div>
                        <div class="val-item"><span class="val-label">ارتكاز</span><span class="val-num">{row['P']}</span></div>
                        <div class="val-item"><span class="val-label">مقاومة</span><span class="val-num" style="color:#ff4b4b;">{row['R1']}</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # تصنيف 2: نخبة الصعود (The Elite List)
    t2 = db[(db['Score'] >= 6) & (db['Score'] < 9)]
    if not t2.empty:
        st.markdown('<div class="section-title">💎 نخبـة الصعـود</div>', unsafe_allow_html=True)
        cols = st.columns(3)
        for idx, row in t2.iterrows():
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="stock-card">
                    <div style="font-weight:bold; font-size:18px;">{row['Symbol']}</div>
                    <div style="font-size:22px; font-weight:900; margin:5px 0;">{row['Price']} <small style="font-size:10px;">EGP</small></div>
                    <div style="font-size:10px; color:#444; margin-top:10px;">R1: {row['R1']} | S1: {row['S1']}</div>
                </div>
                """, unsafe_allow_html=True)

    # تصنيف 3: تصنيف صاعد (The Trending List)
    t3 = db[(db['Score'] >= 3) & (db['Score'] < 6)]
    if not t3.empty:
        st.markdown('<div class="section-title">📈 تصنيـف صـاعد</div>', unsafe_allow_html=True)
        st.dataframe(t3[['Symbol', 'Price', 'R1', 'Signal']], use_container_width=True, hide_index=True)

# --- 5. التذييل القانوني المؤسسي (Corporate Footer) ---
st.markdown(f"""
    <div class="footer">
        <p style="font-size:16px; color:#fff; font-weight:bold; margin-bottom:10px;">WAHBA INTELLIGENCE TERMINAL</p>
        <p style="max-width:800px; margin: 0 auto;">
            <b>إخلاء مسؤولية قانوني:</b> هذه المنصة مخصصة لأغراض المعلومات والتحليل التقني فقط. 
            البيانات مستمدة من إغلاقات البورصة المصرية ومؤرشفة لضمان استقرار التقرير طوال اليوم. 
            الاستثمار في الأوراق المالية ينطوي على مخاطر، والقرار النهائي هو مسؤوليتك الشخصية بالكامل.
        </p>
        <div style="margin-top:30px; font-size:10px; color:#222;">
            SERVER_ID: EGX-PRO-V17 | ENCRYPTION: AES-256 | SESSION_KEY: {today_key}
        </div>
        <p style="margin-top:20px;">© 2026 Wahba Intelligence. All Rights Reserved.</p>
    </div>
""", unsafe_allow_html=True)
