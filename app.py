import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
from datetime import datetime
import pytz

# --- 1. إعدادات الوقت والهوية الرقمية ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)
today_key = now_egypt.strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba Intelligence | Enterprise Terminal", layout="wide")

# --- 2. الواجهة المؤسسية (Corporate UI Design) ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ffffff; }
    
    /* هيدر المنصة */
    .terminal-header {
        text-align: center; padding: 50px 20px; 
        background: linear-gradient(180deg, #000 0%, #050505 100%);
        border-bottom: 1px solid #1a1a1a; margin-bottom: 30px;
    }
    .brand-logo { font-size: 45px; font-weight: 900; letter-spacing: -2px; margin: 0; }
    .accent { color: #00ff00; text-shadow: 0 0 20px rgba(0, 255, 0, 0.3); }
    .sub-brand { color: #444; font-size: 10px; letter-spacing: 5px; text-transform: uppercase; margin-top: 10px; }

    /* كروت مستويات التداول */
    .level-container { display: flex; gap: 10px; margin-top: 15px; }
    .level-tag {
        flex: 1; padding: 10px; border-radius: 6px; text-align: center;
        font-size: 12px; font-weight: bold; font-family: monospace;
    }
    .sup-tag { background: rgba(0, 255, 0, 0.05); color: #00ff00; border: 1px solid #00ff0033; }
    .piv-tag { background: rgba(255, 255, 255, 0.05); color: #ffffff; border: 1px solid #ffffff22; }
    .res-tag { background: rgba(255, 0, 0, 0.05); color: #ff4b4b; border: 1px solid #ff4b4b33; }

    /* بطاقة السهم الرئيسية */
    .asset-card {
        background: #0a0a0a; border: 1px solid #222; border-radius: 16px;
        padding: 25px; margin-bottom: 20px; transition: 0.3s ease;
    }
    .asset-card:hover { border-color: #00ff00; transform: translateY(-3px); }
    
    /* الأزرار */
    .stButton>button {
        background: #00ff00 !important; color: #000 !important; font-weight: 800 !important;
        border-radius: 10px !important; border: none !important; height: 50px !important;
        width: 100%; transition: 0.3s !important;
    }
    .stButton>button:hover { transform: scale(1.01); box-shadow: 0 5px 20px rgba(0,255,0,0.2); }

    /* التذييل القانوني */
    .legal-box {
        background: #000; border-top: 1px solid #111; padding: 40px;
        margin-top: 60px; color: #444; font-size: 12px; line-height: 1.8; text-align: justify;
    }
    </style>
    
    <div class="terminal-header">
        <h1 class="brand-logo">WAHBA <span class="accent">INTELLIGENCE</span></h1>
        <p class="sub-brand">Institutional Asset Scanner & Trading Levels</p>
    </div>
""", unsafe_allow_html=True)

# --- 3. المحرك التقني المستقر (The Vault Engine) ---

@st.cache_data(ttl=86400) # أرشفة قائمة الأسهم يومياً
def get_automated_symbols(date_key):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=20).json()
        return [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except: return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK"]

@st.cache_data(ttl=86400, show_spinner=False) # أرشفة التحليل لليوم بالكامل لضمان الثبات
def run_stable_pro_scan(date_key):
    symbols = get_automated_symbols(date_key)
    scanned_data = []
    p_bar = st.progress(0)
    
    for i, sym in enumerate(symbols):
        try:
            # الاعتماد على الإغلاق اليومي (1-Day) لثبات الإشارات
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=12)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            rec = analysis.summary["RECOMMENDATION"]
            
            # حساب مستويات الدعم والمقاومة (Pivot Classic)
            r1 = ind.get("Pivot.M.Classic.R1")
            s1 = ind.get("Pivot.M.Classic.S1")
            pivot = ind.get("Pivot.M.Classic.Middle")
            
            # خوارزمية التقييم
            score = 0
            if "STRONG_BUY" in rec: score += 3
            elif "BUY" in rec: score += 2
            elif "NEUTRAL" in rec: score += 1
            if ind.get("RSI") and 45 <= ind.get("RSI") <= 68: score += 1

            scanned_data.append({
                "Symbol": sym, "Price": round(ind.get("close"), 2), "Score": score,
                "RSI": round(ind.get("RSI"), 1) if ind.get("RSI") else 0,
                "Support": round(s1, 2) if s1 else 0,
                "Pivot": round(pivot, 2) if pivot else 0,
                "Resistance": round(r1, 2) if r1 else 0,
                "Stars": "⭐" * min(score, 5), "Signal": rec
            })
        except: continue
        p_bar.progress((i + 1) / len(symbols))
    
    p_bar.empty()
    if not scanned_data: return pd.DataFrame(), "Neutral"
    
    # تحديد حساسية الفلتر بناءً على حالة السوق الإجمالية
    avg_score = sum(d['Score'] for d in scanned_data) / len(scanned_data)
    threshold = 4 if avg_score > 1.8 else (3 if avg_score > 1.1 else 2)
    m_status = "BULLISH 🚀" if avg_score > 1.8 else ("STABLE ⚖️" if avg_score > 1.1 else "ADAPTIVE 😴")
    
    final_df = pd.DataFrame([d for d in scanned_data if d['Score'] >= threshold])
    return final_df.sort_values(by="Score", ascending=False), m_status

# --- 4. العرض والتشغيل ---

st.markdown(f"""
    <div style="display:flex; justify-content:space-between; padding:0 10px; color:#444; font-size:10px; font-family:monospace; margin-bottom:20px;">
        <span>SYSTEM_STATUS: ONLINE</span>
        <span>SESSION_DATE: {today_key}</span>
        <span>CAIRO_TIME: {now_egypt.strftime('%H:%M:%S')}</span>
    </div>
""", unsafe_allow_html=True)

# استرجاع البيانات المؤرشفة من الـ Session State
if 'stable_db' not in st.session_state:
    st.session_state.stable_db = None

if st.button('GENERATE INSTITUTIONAL MARKET REPORT'):
    with st.spinner("ARCHIVING DATA & CALCULATING LEVELS..."):
        df, status = run_stable_pro_scan(today_key)
        st.session_state.stable_db = df
        st.session_state.m_status = status

db = st.session_state.stable_db
if db is not None and not db.empty:
    st.markdown(f"### 💎 نخبـة السـوق المصـري | <span style='color:#00ff00'>{st.session_state.m_status}</span>", unsafe_allow_html=True)
    
    # عرض الأسهم كبطاقات احترافية
    for _, row in db.iterrows():
        st.markdown(f"""
        <div class="asset-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h2 style="margin:0; color:#00ff00;">{row['Symbol']}</h2>
                <span style="color:#666; font-size:12px;">{row['Signal']}</span>
            </div>
            <p style="font-size:28px; font-weight:bold; margin:10px 0;">{row['Price']} <small style="color:#444;">EGP</small></p>
            <div style="margin-bottom:15px;">{row['Stars']} | RSI: {row['RSI']}</div>
            
            <div class="level-container">
                <div class="level-tag sup-tag">دعم (S1): {row['Support']}</div>
                <div class="level-tag piv-tag">ارتكاز (P): {row['Pivot']}</div>
                <div class="level-tag res-tag">مقاومة (R1): {row['Resistance']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # الجدول التفصيلي للبيانات
    st.write("")
    st.markdown("#### 📋 مـلخص البيـانات الفنيـة")
    st.dataframe(db[['Symbol', 'Price', 'Stars', 'Support', 'Pivot', 'Resistance']], use_container_width=True, hide_index=True)

# --- 5. إخلاء المسؤولية القانوني (The Disclaimer) ---
st.markdown(f"""
    <div class="legal-box">
        <b>إخلاء مسؤولية قانوني (Institutional Disclaimer):</b><br>
        تعد منصة <b>WAHBA INTELLIGENCE</b> أداة فنية مؤتمتة تقوم بتحليل إحصائي لإغلاقات الجلسات اليومية في البورصة المصرية. 
        النتائج الواردة، بما في ذلك مستويات الدعم والمقاومة، هي بيانات مؤرشفة بناءً على مؤشرات تقنية رياضية ولا تعد توصيات مباشرة بالشراء أو البيع. 
        <br><br>
        الاستثمار في الأوراق المالية ينطوي على مخاطر عالية، وقرار التداول هو مسؤولية المستخدم الفردية بالكامل. 
        لا تتحمل المنصة أو مطورها أي مسؤولية عن أي خسائر مالية ناتجة عن استخدام هذه البيانات. 
        يُنصح دائماً بمراجعة مستشار مالي مرخص قبل اتخاذ أي خطوة استثمارية. جميع الحقوق محفوظة © 2026.
    </div>
""", unsafe_allow_html=True)
