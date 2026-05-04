import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import time
from datetime import datetime
import pytz

# --- 1. إعدادات التوقيت والأتمتة ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)
today_key = now_egypt.strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba Intelligence | Official Terminal", layout="wide")

# --- 2. التصميم المؤسسي الفاخر (Corporate Branding) ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ffffff; }
    
    /* هيدر المنصة الرئيسي */
    .corporate-header {
        text-align: center; padding: 60px 20px; 
        background: linear-gradient(180deg, #000 0%, #050505 100%);
        border-bottom: 1px solid #1a1a1a; margin-bottom: 40px;
    }
    .brand-name { font-size: 48px; font-weight: 900; letter-spacing: -2px; margin: 0; color: #fff; }
    .brand-accent { color: #00ff00; text-shadow: 0 0 15px rgba(0,255,0,0.2); }
    .sub-text { color: #555; font-size: 11px; letter-spacing: 5px; text-transform: uppercase; margin-top: 10px; }

    /* بطاقات النخبة */
    .asset-card {
        background: #0a0a0a; border: 1px solid #222; border-radius: 16px;
        padding: 30px; position: relative; transition: 0.4s ease;
    }
    .asset-card:hover { border-color: #00ff00; background: #0f0f0f; }
    .tier-badge {
        position: absolute; top: 20px; right: 20px; font-size: 9px; font-weight: bold;
        background: rgba(0,255,0,0.1); color: #00ff00; padding: 5px 12px; border-radius: 4px;
    }

    /* التذييل القانوني */
    .legal-footer {
        background: #000; border-top: 1px solid #111; padding: 50px 30px;
        margin-top: 80px; color: #444; font-size: 12px; line-height: 1.8; text-align: justify;
    }
    
    /* الأزرار المؤسسية */
    .stButton>button {
        background: #00ff00 !important; color: #000 !important; font-weight: 800 !important;
        border-radius: 12px !important; border: none !important; height: 55px !important;
        transition: 0.3s !important; text-transform: uppercase;
    }
    .stButton>button:hover { transform: scale(1.01); box-shadow: 0 5px 20px rgba(0,255,0,0.2); }
    </style>
    
    <div class="corporate-header">
        <h1 class="brand-name">WAHBA <span class="brand-accent">INTELLIGENCE</span></h1>
        <p class="sub-text">Institutional Grade Egyptian Stock Scanner</p>
    </div>
""", unsafe_allow_html=True)

# --- 3. محرك الأرشفة والذكاء التكيفي (The Vault Logic) ---

@st.cache_data(ttl=86400) # جلب القائمة آلياً مرة واحدة يومياً
def get_automated_market_list(date_key):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=25).json()
        return [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except: return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK", "ORAS"]

@st.cache_data(ttl=86400, show_spinner=False) # أرشفة النتائج لليوم بالكامل
def run_immutable_analysis(date_key):
    symbols = get_automated_market_list(date_key)
    scanned_results = []
    p_bar = st.progress(0)
    
    for i, sym in enumerate(symbols):
        try:
            # الاعتماد حصراً على إغلاق اليوم (1-Day Interval) لثبات النتائج
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=12)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            rec = analysis.summary["RECOMMENDATION"]
            
            # خوارزمية التقييم الاحترافية
            score = 0
            if "STRONG_BUY" in rec: score += 3
            elif "BUY" in rec: score += 2
            elif "NEUTRAL" in rec: score += 1
            
            rsi = ind.get("RSI")
            if rsi and 45 <= rsi <= 68: score += 1
            if ind.get("ADX") and ind.get("ADX") > 18: score += 1

            scanned_results.append({
                "Symbol": sym, "Price": round(ind.get("close"), 2), "Score": score,
                "RSI": round(rsi, 1) if rsi else 0, "Stars": "⭐" * min(score, 5), "Rec": rec
            })
        except: continue
        p_bar.progress((i + 1) / len(symbols))
    
    p_bar.empty()
    if not scanned_results: return pd.DataFrame(), "Neutral"

    # --- منطق التكيف التلقائي مع السوق ---
    avg_score = sum(d['Score'] for d in scanned_results) / len(scanned_results)
    threshold = 4 if avg_score > 1.8 else (3 if avg_score > 1.1 else 2)
    m_status = "BULLISH 🚀" if avg_score > 1.8 else ("STABLE ⚖️" if avg_score > 1.1 else "QUIET/ADAPTIVE 😴")

    final_df = pd.DataFrame([d for d in scanned_results if d['Score'] >= threshold])
    return final_df.sort_values(by="Score", ascending=False), m_status

# --- 4. واجهة التشغيل والعرض ---

st.markdown(f"""
    <div style="display:flex; justify-content:space-between; padding:0 10px; color:#444; font-size:10px; font-family:monospace; margin-bottom:20px;">
        <span>TERMINAL ID: WAHBA-PRO-V13</span>
        <span>MARKET DATE: {today_key}</span>
        <span>CAIRO: {now_egypt.strftime('%H:%M:%S')}</span>
    </div>
""", unsafe_allow_html=True)

# التأكد من ثبات البيانات في الـ Session
if 'archived_report' not in st.session_state:
    st.session_state.archived_report = None

if st.button('GENERATE OFFICIAL MARKET REPORT'):
    with st.spinner("SCANNING EGX DATABASE & ARCHIVING RESULTS..."):
        df, status = run_immutable_analysis(today_key)
        st.session_state.archived_report = df
        st.session_state.m_status = status

# عرض التقارير المؤرشفة
db = st.session_state.archived_report
if db is not None and not db.empty:
    
    st.markdown(f"### ⚡ نخبـة السـوق المصـري | <span style='color:#00ff00'>{st.session_state.m_status}</span>", unsafe_allow_html=True)
    
    # عرض أول سهمين كفرص استثمارية كبرى (VIP)
    top_picks = db.head(2)
    cols = st.columns(2)
    for idx, col in enumerate(cols):
        if idx < len(top_picks):
            row = top_picks.iloc[idx]
            with col:
                st.markdown(f"""
                <div class="asset-card">
                    <div class="tier-badge">INSTITUTIONAL PICK</div>
                    <h1 style="margin:0; color:#00ff00;">{row['Symbol']}</h1>
                    <p style="font-size:32px; font-weight:bold; margin:15px 0;">{row['Price']} <span style="font-size:14px; color:#444;">EGP</span></p>
                    <div style="letter-spacing:5px;">{row['Stars']}</div>
                </div>
                """, unsafe_allow_html=True)

    # عرض الجدول الكامل لبقية القائمة المفلترة
    st.write("")
    st.markdown("#### 📋 القائمة المفلترة بالكامل")
    st.dataframe(db[['Symbol', 'Price', 'Stars', 'RSI', 'Rec']], use_container_width=True, hide_index=True)

# --- 5. إخلاء المسؤولية القانوني (Institutional Disclaimer) ---
st.markdown(f"""
    <div class="legal-footer">
        <b>إخلاء مسؤولية قانوني (Official Disclaimer):</b><br>
        تعد منصة <b>WAHBA INTELLIGENCE</b> أداة فنية مؤتمتة تقوم بتحليل إحصائي لإغلاقات الجلسات اليومية في البورصة المصرية. 
        النتائج الواردة في هذا التقرير هي بيانات مؤرشفة بناءً على مؤشرات تقنية (Technical Indicators) ولا تعد توصيات مباشرة بالشراء أو البيع. 
        <br><br>
        الاستثمار في الأوراق المالية ينطوي على مخاطر تقلبات الأسعار، وقرار التداول هو مسؤولية المستخدم الفردية بالكامل. 
        لا تتحمل المنصة أو مطورها أي مسؤولية عن أي خسائر مالية ناتجة عن استخدام هذه البيانات. 
        نوصي دائماً بالرجوع إلى مستشار مالي مرخص قبل اتخاذ أي خطوة استثمارية.
        <br><br>
        <b>© 2026 Wahba Intelligence Terminal - Institutional Grade Scanner. All Rights Reserved.</b>
    </div>
""", unsafe_allow_html=True)
