import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import time
from datetime import datetime
import pytz
import feedparser
import urllib.parse

# --- 1. إعدادات الوقت والهوية ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)
today_key = now_egypt.strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba Intelligence | Professional", layout="wide")

# --- 2. التصميم الفاخر (UI) ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    .main-header { 
        text-align: center; padding: 25px; border-bottom: 2px solid #00ff00; 
        background: linear-gradient(180deg, #111 0%, #050505 100%);
        margin-bottom: 20px; border-radius: 0 0 25px 25px;
    }
    .elite-header {
        background: linear-gradient(90deg, #ffd700 0%, #b8860b 100%);
        color: black; padding: 10px; border-radius: 8px; text-align: center;
        font-weight: bold; font-size: 20px; margin-bottom: 15px;
    }
    .standard-elite {
        background: #111; border-left: 5px solid #00ff00; padding: 15px;
        border-radius: 10px; margin-bottom: 10px;
    }
    .gold-box { 
        background: #0f0f0f; border: 2px solid #ffd700; padding: 20px; 
        border-radius: 15px; margin-bottom: 15px; box-shadow: 0 0 20px rgba(255, 215, 0, 0.2);
    }
    </style>
    <div class="main-header">
        <h1 style="margin:0; color:#ffffff; font-size: 35px;">WAHBA <span style="color:#00ff00;">INTELLIGENCE</span></h1>
        <div style="color: #888; font-size: 14px;">Professional Daily Database Engine v9.0</div>
    </div>
""", unsafe_allow_html=True)

# --- 3. محرك جلب البيانات الذكي ---

@st.cache_data(ttl=86400)
def get_safe_tickers(date_key):
    """جلب الأسهم مع نظام حماية Headers"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}
        res = requests.post(url, json=payload, headers=headers, timeout=20).json()
        # تنقية الرموز من أي بيانات غير صحيحة
        return [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except:
        return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ETEL", "ABUK"]

@st.cache_data(ttl=86400)
def get_safe_news(symbol, date_key):
    """جلب الأخبار مع معالجة الأخطاء"""
    try:
        query = urllib.parse.quote(f"سهم {symbol} البورصة المصرية")
        url = f"https://news.google.com/rss/search?q={query}&hl=ar&gl=EG&ceid=EG:ar"
        feed = feedparser.parse(url)
        return [e.title.split(" - ")[0] for e in feed.entries[:2]] if feed.entries else ["لا توجد أخبار جوهرية حالياً."]
    except: return ["الأخبار غير متاحة."]

@st.cache_data(ttl=86400, show_spinner=False)
def perform_final_scan(date_key):
    symbols = get_safe_tickers(date_key)
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, symbol in enumerate(symbols):
        try:
            status_text.text(f"🔍 فحص السهم: {symbol}")
            handler = TA_Handler(symbol=symbol, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=10)
            analysis = handler.get_analysis()
            
            # الفلترة الذكية (نخبة 4 نجوم فما فوق)
            rec = analysis.summary["RECOMMENDATION"]
            if "BUY" in rec:
                rsi = analysis.indicators.get("RSI")
                adx = analysis.indicators.get("ADX")
                close = analysis.indicators.get("close")
                
                if all(v is not None for v in [rsi, adx, close]):
                    score = 0
                    if "STRONG" in rec: score += 3
                    if 45 <= rsi <= 60: score += 2
                    if adx > 22: score += 1
                    
                    if score >= 4:
                        news = get_safe_news(symbol, date_key)
                        results.append({
                            "السهم": symbol, "الإغلاق": round(close, 2),
                            "التقييم": score, "النجوم": "⭐" * min(score, 5),
                            "ADX": round(adx, 1), "أخبار": news
                        })
            progress_bar.progress((i + 1) / len(symbols))
            time.sleep(0.05)
        except: continue
        
    status_text.empty()
    progress_bar.empty()
    if results:
        df = pd.DataFrame(results)
        # الترتيب حسب التقييم ثم قوة الاتجاه (الزخم)
        return df.sort_values(by=["التقييم", "ADX"], ascending=[False, False])
    return pd.DataFrame()

# --- 4. واجهة العرض النهائية ---

st.info(f"📊 حالة النظام: متصل | بيانات الإغلاق محفوظة لليوم: {today_key}")

# التحديث التلقائي أو اليدوي
if 'final_data' not in st.session_state:
    st.session_state.final_data = None

if st.button('🚀 تحديث وأرشفة بيانات الجلسة كاملة', use_container_width=True):
    st.session_state.final_data = perform_final_scan(today_key)

# عرض النتائج
data = st.session_state.final_data
if data is not None and not data.empty:
    
    # 1. قسم نخبة النخبة
    st.markdown('<div class="elite-header">✨ نخبة النخبة (أعلى زخم شرائي)</div>', unsafe_allow_html=True)
    super_elite = data.head(2)
    se_cols = st.columns(2)
    for idx, col in enumerate(se_cols):
        if idx < len(super_elite):
            row = super_elite.iloc[idx]
            with col:
                st.markdown(f"""
                <div class="gold-box">
                    <h2 style="color:#ffd700; margin:0;">{row['السهم']}</h2>
                    <p style="font-size:22px; color:white;">{row['الإغلاق']} EGP | {row['النجوم']}</p>
                    <hr style="border:0.1px solid #333;">
                    {"".join([f'<div style="font-size:12px; color:#aaa; margin-bottom:5px;">🔥 {n}</div>' for n in row['أخبار']])}
                </div>
                """, unsafe_allow_html=True)

    # 2. قسم النخبة
    st.write("")
    st.markdown("### 🟢 قائمة النخبة (فرص قوية)")
    other_elite = data.iloc[2:]
    if not other_elite.empty:
        for _, row in other_elite.iterrows():
            st.markdown(f"""
            <div class="standard-elite">
                <span style="font-size:17px; color:#00ff00; font-weight:bold;">{row['السهم']}</span> | 
                <span style="color:white;">{row['الإغلاق']} EGP</span> | 
                <span style="color:#ffd700;">{row['النجوم']}</span> | 
                <span style="font-size:11px; color:#555;">الزخم: {row['ADX']}</span>
            </div>
            """, unsafe_allow_html=True)
else:
    if st.session_state.final_data is not None:
        st.warning("لم يتم العثور على أسهم مطابقة لمعايير النخبة في هذه الجلسة.")

st.markdown(f"<div style='text-align:center; color:#333; font-size:10px; padding:40px;'>Wahba Intelligence Stable-Engine v9.0 | Cairo Time: {now_egypt.strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)
