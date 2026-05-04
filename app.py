import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import time
from datetime import datetime
import pytz
import feedparser
import urllib.parse

# --- 1. المحرك الزمني (Cairo Time Automation) ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)
today_key = now_egypt.strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba Intelligence | Corporate Terminal", layout="wide")

# --- 2. الواجهة المؤسسية (Corporate UI Design) ---
st.markdown("""
    <style>
    .stApp { background-color: #080808; color: #ffffff; }
    
    /* هيدر المنصة */
    .terminal-header {
        text-align: center; padding: 50px 20px; 
        background: radial-gradient(circle at center, #111 0%, #080808 100%);
        border-bottom: 1px solid #1a1a1a; margin-bottom: 30px;
    }
    .main-logo { font-size: 42px; font-weight: 900; letter-spacing: -1px; margin: 0; color: #fff; }
    .accent { color: #00ff00; }
    
    /* بطاقات النخبة المتميزة */
    .premium-card {
        background: #111; border: 1px solid #222; border-radius: 16px;
        padding: 30px; position: relative; transition: 0.4s;
    }
    .premium-card:hover { border-color: #00ff00; transform: translateY(-5px); }
    .badge {
        position: absolute; top: 15px; right: 15px; font-size: 10px;
        background: rgba(0,255,0,0.1); color: #00ff00; padding: 4px 12px; border-radius: 4px;
    }

    /* شريط التذييل القانوني */
    .footer-legal {
        background: #000; border-top: 1px solid #111; padding: 40px;
        margin-top: 60px; color: #444; font-size: 11px; text-align: justify;
    }
    
    /* تخصيص الأزرار */
    .stButton>button {
        background: #00ff00 !important; color: #000 !important; font-weight: 800 !important;
        border-radius: 8px !important; border: none !important; height: 50px !important;
    }
    </style>
    
    <div class="terminal-header">
        <p style="color: #666; font-size: 10px; letter-spacing: 6px; margin-bottom: 10px;">INSTITUTIONAL GRADE TRADING TERMINAL</p>
        <h1 class="main-logo">WAHBA <span class="accent">INTELLIGENCE</span></h1>
    </div>
""", unsafe_allow_html=True)

# --- 3. المحرك التقني المؤتمت (Staple Logic) ---

@st.cache_data(ttl=86400) # جلب القائمة آلياً مرة كل 24 ساعة
def auto_fetch_tickers(date_key):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=25).json()
        return [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except: return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK"]

@st.cache_data(ttl=86400, show_spinner=False)
def institutional_engine(date_key):
    symbols = auto_fetch_tickers(date_key)
    database = []
    p_bar = st.progress(0)
    
    for i, sym in enumerate(symbols):
        try:
            # استخدام فريم اليوم لإشارات مؤسسية مستقرة
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=12)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            rec = analysis.summary["RECOMMENDATION"]
            
            # خوارزمية التقييم (Point-Based Scoring)
            score = 0
            if "STRONG_BUY" in rec: score += 3
            elif "BUY" in rec: score += 2
            elif "NEUTRAL" in rec: score += 1
            
            rsi = ind.get("RSI")
            if rsi and 45 <= rsi <= 68: score += 1
            if ind.get("ADX") and ind.get("ADX") > 18: score += 1

            database.append({
                "Symbol": sym, "Price": round(ind.get("close"), 2), "Score": score,
                "RSI": round(rsi, 1) if rsi else 0, "Stars": "⭐" * min(score, 5), "Rec": rec
            })
        except: continue
        p_bar.progress((i + 1) / len(symbols))
    
    p_bar.empty()
    if not database: return pd.DataFrame(), "Neutral"

    # --- الذكاء التكيفي (Adaptive Filter) ---
    avg_score = sum(d['Score'] for d in database) / len(database)
    # لو السوق ميت، الكود بيفك الفلتر تلقائياً (score >= 2)
    threshold = 4 if avg_score > 1.8 else (3 if avg_score > 1.1 else 2)
    status = "Active/Bullish" if avg_score > 1.8 else ("Stable" if avg_score > 1.1 else "Quiet/Adaptive")

    final_df = pd.DataFrame([d for d in database if d['Score'] >= threshold])
    return final_df.sort_values(by="Score", ascending=False), status

# --- 4. العرض التشغيلي ---

st.markdown(f"""
    <div style="display:flex; justify-content:space-between; padding:0 10px; color:#444; font-size:10px; font-family:monospace;">
        <span>SYSTEM: ONLINE</span>
        <span>MARKET: EGX</span>
        <span>CAIRO_TIME: {now_egypt.strftime('%H:%M:%S')}</span>
    </div>
""", unsafe_allow_html=True)

if 'final_db' not in st.session_state:
    st.session_state.final_db = None

if st.button('GENERATE INSTITUTIONAL DATA REPORT'):
    with st.spinner("EXECUTING ADAPTIVE SCAN..."):
        df, status = institutional_engine(today_key)
        st.session_state.final_db = df
        st.session_state.m_status = status

# عرض النتائج
res = st.session_state.final_db
if res is not None and not res.empty:
    
    st.markdown(f"### ⚡ تقرير الأداء العالي | <small style='color:#00ff00'>{st.session_state.m_status}</small>", unsafe_allow_html=True)
    
    # قسم الأولوية القصوى (نخبة النخبة)
    top_picks = res.head(2)
    cols = st.columns(2)
    for idx, col in enumerate(cols):
        if idx < len(top_picks):
            row = top_picks.iloc[idx]
            with col:
                st.markdown(f"""
                <div class="premium-card">
                    <div class="badge">HIGH CONVICTION</div>
                    <h1 style="margin:0; color:#00ff00;">{row['Symbol']}</h1>
                    <p style="font-size:28px; font-weight:bold; margin:10px 0;">{row['Price']} <span style="font-size:12px; color:#444;">EGP</span></p>
                    <div style="letter-spacing:3px;">{row['Stars']}</div>
                </div>
                """, unsafe_allow_html=True)

    # قائمة النخبة الكاملة
    st.write("")
    st.markdown("#### 🔍 تفاصيل القائمة المفلترة")
    st.dataframe(res[['Symbol', 'Price', 'Stars', 'RSI', 'Rec']], use_container_width=True, hide_index=True)

# --- 5. إخلاء المسؤولية القانونية (Standard Legal Disclaimer) ---
st.markdown(f"""
    <div class="footer-legal">
        <b>إخلاء مسؤولية قانوني (Legal Disclaimer):</b><br>
        هذا النظام عبارة عن أداة تحليلية مؤتمتة تعتمد على بيانات فنية مستمدة من مصادر خارجية. 
        لا تعتبر النتائج المعروضة "توصيات استثمارية" أو دعوة للبيع أو الشراء. التداول في البورصة المصرية ينطوي على مخاطر مالية كبيرة.
        إدارة <b>WAHBA INTELLIGENCE</b> والمطور غير مسؤولين عن أي قرارات مالية يتم اتخاذها بناءً على هذا التقرير. 
        يُنصح بمراجعة مستشار مالي معتمد قبل التنفيذ. جميع البيانات تعبر عن إغلاق الجلسة السابقة وقد تختلف مع حركة التداول اللحظية.
        <br><br>
        <b>© 2026 Wahba Intelligence - Institutional Assets Division.</b>
    </div>
""", unsafe_allow_html=True)
