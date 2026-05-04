import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import time
from datetime import datetime
import pytz
import feedparser
import urllib.parse

# --- 1. إعدادات الوقت والمنطقة الزمنية ---
def get_egypt_now():
    return datetime.now(pytz.timezone('Africa/Cairo'))

now_egypt = get_egypt_now()
today_key = now_egypt.strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba EGX | Elite System", layout="wide")

# --- 2. التصميم الاحترافي (UI) ---
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
        <div style="color: #888; font-size: 14px;">Elite & Super-Elite Classification v8.5</div>
    </div>
""", unsafe_allow_html=True)

# --- 3. الدوال الأساسية ---

@st.cache_data(ttl=86400)
def get_stable_tickers(date_key):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}
        res = requests.post(url, json=payload, timeout=20).json()
        return [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except:
        return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ETEL", "ABUK"]

@st.cache_data(ttl=86400)
def fetch_news_stable(symbol, date_key):
    try:
        query = urllib.parse.quote(f"سهم {symbol} البورصة المصرية")
        url = f"https://news.google.com/rss/search?q={query}&hl=ar&gl=EG&ceid=EG:ar"
        feed = feedparser.parse(url)
        return [e.title.split(" - ")[0] for e in feed.entries[:2]] if feed.entries else ["لا توجد أخبار جوهرية."]
    except: return ["الأخبار غير متاحة."]

@st.cache_data(ttl=86400, show_spinner=False)
def perform_stable_scan(date_key):
    symbols = get_stable_tickers(date_key)
    results = []
    progress_bar = st.progress(0)

    for i, symbol in enumerate(symbols):
        try:
            handler = TA_Handler(symbol=symbol, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=12)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            rec = analysis.summary["RECOMMENDATION"]
            
            if "BUY" in rec:
                rsi, close, adx = ind.get("RSI"), ind.get("close"), ind.get("ADX")
                if all(v is not None for v in [rsi, close, adx]):
                    score = 0
                    if "STRONG" in rec: score += 3
                    if 45 <= rsi <= 60: score += 2
                    if adx > 22: score += 1
                    
                    if score >= 4: # حد أدنى للنخبة
                        news = fetch_news_stable(symbol, date_key)
                        results.append({
                            "السهم": symbol, "الإغلاق": round(close, 2),
                            "التقييم": score, "النجوم": "⭐" * min(score, 5),
                            "ADX": round(adx, 1), "أخبار": news
                        })
            time.sleep(0.05)
            progress_bar.progress((i + 1) / len(symbols))
        except: continue
        
    progress_bar.empty()
    return pd.DataFrame(results).sort_values(by=["التقييم", "ADX"], ascending=[False, False]) if results else pd.DataFrame()

# --- 4. عرض النتائج بتصنيف (نخبة النخبة) و (نخبة) ---

with st.spinner("جاري استحضار النخبة..."):
    final_db = perform_stable_scan(today_key)

if not final_db.empty:
    # 1. نخبة النخبة (أعلى تقييم وأعلى ADX - أول سهمين أو تلاتة)
    st.markdown('<div class="elite-header">✨ نخبة النخبة (أقوى فرص السوق)</div>', unsafe_allow_html=True)
    super_elite = final_db.head(2) 
    
    se_cols = st.columns(2)
    for idx, col in enumerate(se_cols):
        if idx < len(super_elite):
            row = super_elite.iloc[idx]
            with col:
                st.markdown(f"""
                <div class="gold-box">
                    <h2 style="color:#ffd700; margin:0;">{row['السهم']}</h2>
                    <p style="font-size:22px; margin:5px 0; color:white;">{row['الإغلاق']} EGP | {row['النجوم']}</p>
                    <div style="font-size:12px; color:#888;">قوة الاتجاه الحالية: {row['ADX']}</div>
                    <hr style="border:0.2px solid #333;">
                    {"".join([f'<div style="font-size:12px; color:#ccc; margin-bottom:4px;">🔥 {n}</div>' for n in row['أخبار']])}
                </div>
                """, unsafe_allow_html=True)

    st.write("")
    
    # 2. قائمة النخبة (باقي الأسهم الحاصلة على 4 نجوم)
    st.markdown('### 🟢 قائمة النخبة (فرص مؤكدة)')
    other_elite = final_db.iloc[2:] # باقي الجدول
    
    if not other_elite.empty:
        for _, row in other_elite.iterrows():
            st.markdown(f"""
            <div class="standard-elite">
                <span style="font-size:18px; color:#00ff00; font-weight:bold;">{row['السهم']}</span> | 
                <span style="color:white;">السعر: {row['الإغلاق']} EGP</span> | 
                <span style="color:#ffd700;">{row['النجوم']}</span> | 
                <span style="font-size:12px; color:#666;">الزخم: {row['ADX']}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("نخبة النخبة هم المتاحون حالياً.")

else:
    st.warning("لا يوجد أسهم في منطقة النخبة حالياً. انتظر إغلاق اليوم للفحص الجديد.")

st.markdown(f"<div style='text-align:center; padding:30px; color:#333; font-size:10px;'>Wahba EGX v8.5 | Updated: {today_key}</div>", unsafe_allow_html=True)
