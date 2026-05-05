import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
from datetime import datetime
import pytz

# --- 1. إعدادات الوقت والثبات ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)
today_key = now_egypt.strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba Intelligence | Elite-X", layout="wide")

# --- 2. التصميم المؤسسي الثلاثي ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ffffff; }
    .header-box { text-align: center; padding: 40px; border-bottom: 1px solid #1a1a1a; }
    .tier-header { padding: 15px; border-radius: 10px; margin: 20px 0; text-align: center; font-weight: bold; }
    
    /* ألوان التصنيفات */
    .t1 { background: linear-gradient(90deg, #00ff00 0%, #004400 100%); color: #000; font-size: 20px; } /* سوبر نخبة */
    .t2 { background: #111; border: 1px solid #00ff00; color: #00ff00; } /* نخبة الصعود */
    .t3 { background: #111; border: 1px solid #444; color: #eee; } /* صاعد */

    .asset-card { background: #0a0a0a; border: 1px solid #222; border-radius: 12px; padding: 20px; margin-bottom: 15px; }
    .level-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-top: 10px; font-size: 11px; text-align: center; }
    .sup { color: #00ff00; } .piv { color: #aaa; } .res { color: #ff4b4b; }
    </style>
    
    <div class="header-box">
        <h1 style="margin:0;">WAHBA <span style="color:#00ff00;">INTELLIGENCE</span></h1>
        <p style="color:#444; font-size:10px; letter-spacing:3px;">ELITE TRIPLE-CLASSIFICATION SYSTEM</p>
    </div>
""", unsafe_allow_html=True)

# --- 3. المحرك التقني (The Elite Engine) ---

@st.cache_data(ttl=86400)
def get_egx_symbols(date_key):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=20).json()
        return [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except: return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO"]

@st.cache_data(ttl=86400, show_spinner=False)
def run_triple_elite_scan(date_key):
    symbols = get_egx_symbols(date_key)
    results = []
    p_bar = st.progress(0)
    
    for i, sym in enumerate(symbols):
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=12)
            analysis = handler.get_analysis()
            ind, rec = analysis.indicators, analysis.summary["RECOMMENDATION"]
            
            # حساب القوة الفنية (0 إلى 10)
            power_score = 0
            if "STRONG_BUY" in rec: power_score += 5
            elif "BUY" in rec: power_score += 3
            
            rsi = ind.get("RSI")
            if rsi and 50 <= rsi <= 70: power_score += 3 # زخم مثالي
            if ind.get("close") > ind.get("Pivot.M.Classic.Middle"): power_score += 2 # فوق الارتكاز

            results.append({
                "Symbol": sym, "Price": round(ind.get("close"), 2), "Power": power_score,
                "S1": round(ind.get("Pivot.M.Classic.S1"), 2),
                "P": round(ind.get("Pivot.M.Classic.Middle"), 2),
                "R1": round(ind.get("Pivot.M.Classic.R1"), 2),
                "Signal": rec
            })
        except: continue
        p_bar.progress((i + 1) / len(symbols))
    
    p_bar.empty()
    df = pd.DataFrame(results)
    return df

# --- 4. عرض النتائج بالتصنيفات ---

if 'elite_db' not in st.session_state:
    st.session_state.elite_db = None

if st.button('إصدار تقرير تصنيفات النخبة'):
    st.session_state.elite_db = run_triple_elite_scan(today_key)

db = st.session_state.elite_db
if db is not None and not db.empty:
    
    # 1. نخبة نخبة الصعود (Power >= 9)
    t1 = db[db['Power'] >= 9]
    if not t1.empty:
        st.markdown('<div class="tier-header t1">🏆 نخبة نخبة الصعود (Super Elite)</div>', unsafe_allow_html=True)
        for _, row in t1.iterrows():
            st.markdown(f"""
            <div class="asset-card" style="border-left: 5px solid #00ff00;">
                <div style="display:flex; justify-content:space-between;"><b>{row['Symbol']}</b> <span style="color:#00ff00;">{row['Price']} EGP</span></div>
                <div class="level-grid">
                    <div class="sup">دعم: {row['S1']}</div> <div class="piv">ارتكاز: {row['P']}</div> <div class="res">مقاومة: {row['R1']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 2. نخبة الصعود (Power 6-8)
    t2 = db[(db['Power'] >= 6) & (db['Power'] < 9)]
    if not t2.empty:
        st.markdown('<div class="tier-header t2">💎 نخبة الصعود (Elite)</div>', unsafe_allow_html=True)
        for _, row in t2.iterrows():
            st.markdown(f"""
            <div class="asset-card">
                <div style="display:flex; justify-content:space-between;"><b>{row['Symbol']}</b> <span>{row['Price']} EGP</span></div>
                <div class="level-grid">
                    <div class="sup">دعم: {row['S1']}</div> <div class="piv">ارتكاز: {row['P']}</div> <div class="res">مقاومة: {row['R1']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 3. تصنيف صاعد (Power 3-5)
    t3 = db[(db['Power'] >= 3) & (db['Power'] < 6)]
    if not t3.empty:
        st.markdown('<div class="tier-header t3">📈 تصنيف صاعد (Trending)</div>', unsafe_allow_html=True)
        for _, row in t3.iterrows():
            st.markdown(f"**{row['Symbol']}** | السعر: {row['Price']} | المقاومة: {row['R1']}")

# --- 5. إخلاء المسؤولية ---
st.markdown("<div style='margin-top:50px; color:#333; font-size:10px; text-align:center;'>جميع البيانات مؤرشفة لليوم لضمان الثبات. القرار الاستثماري مسؤوليتك. © 2026 Wahba Intelligence</div>", unsafe_allow_html=True)
