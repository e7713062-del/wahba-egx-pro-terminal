import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import time
from datetime import datetime
import pytz
import feedparser
import urllib.parse

# --- 1. إعدادات الوقت الذكية (توقيت مصر الصيفي/الشتوي) ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)
today_key = now_egypt.strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba Intelligence V5.0", layout="wide")

# --- 2. التصميم الفاخر (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    .main-header { 
        text-align: center; padding: 30px; border-bottom: 3px solid #00ff00; 
        background: linear-gradient(180deg, #111 0%, #050505 100%);
        margin-bottom: 30px; border-radius: 0 0 25px 25px;
    }
    .gold-box { 
        background: linear-gradient(90deg, rgba(255,215,0,0.1) 0%, rgba(0,255,0,0.05) 100%);
        border: 1px solid #ffd700; padding: 20px; border-radius: 15px; margin-bottom: 20px;
    }
    .news-card {
        background: #111; padding: 10px; border-radius: 10px; border-right: 3px solid #00ff00;
        margin-bottom: 10px; font-size: 13px;
    }
    </style>
    <div class="main-header">
        <div style="color: #00ff00; font-family: monospace; letter-spacing: 2px;">SYSTEM V5.0 | NEWS INTEGRATED</div>
        <h1 style="margin:10px 0; color:#ffffff;">WAHBA <span style="color:#00ff00;">EGX</span> INTELLIGENCE</h1>
        <div style="color: #888;">التحليل الفني المتقدم القائم على الإغلاق وأخبار السوق</div>
    </div>
""", unsafe_allow_html=True)

# --- 3. الدوال الذكية ---

@st.cache_data(ttl=86400)
def get_stock_news(symbol):
    """جلب آخر الأخبار المتعلقة بالسهم من مصادر إخبارية"""
    try:
        query = urllib.parse.quote(f"سهم {symbol} البورصة المصرية")
        url = f"https://news.google.com/rss/search?q={query}&hl=ar&gl=EG&ceid=EG:ar"
        feed = feedparser.parse(url)
        news_items = []
        for entry in feed.entries[:2]: # جلب آخر خبرين فقط للاختصار
            news_items.append(f"📰 {entry.title}")
        return news_items if news_items else ["لا توجد أخبار حديثة مؤكدة"]
    except:
        return ["تعذر جلب الأخبار حالياً"]

@st.cache_data(ttl=86400)
def get_live_tickers():
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}
        res = requests.post(url, json=payload, timeout=15).json()
        return sorted(list(set([item['s'].split(':')[1] for item in res['data']])))
    except:
        return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ETEL"]

@st.cache_data(ttl=86400)
def run_full_analysis(date_key):
    symbols = get_live_tickers()
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, symbol in enumerate(symbols):
        try:
            status_text.text(f"🚀 جاري تحليل السهم والأخبار: {symbol}")
            handler = TA_Handler(
                symbol=symbol, screener="egypt", exchange="EGX", 
                interval=Interval.INTERVAL_1_DAY, timeout=10
            )
            analysis = handler.get_analysis()
            rec = analysis.summary["RECOMMENDATION"]
            
            if "BUY" in rec:
                rsi = analysis.indicators.get("RSI")
                close = analysis.indicators.get("close")
                
                if rsi and close:
                    score = 2
                    if "STRONG" in rec: score += 1
                    if 45 <= rsi <= 65: score += 2
                    
                    # دمج الأخبار في التحليل
                    news = get_stock_news(symbol)
                    
                    results.append({
                        "السهم": symbol,
                        "الإغلاق": round(close, 2),
                        "التقييم": score,
                        "النجوم": "⭐" * min(score, 5),
                        "أهم الأخبار": news
                    })
            
            progress_bar.progress((i + 1) / len(symbols))
            time.sleep(0.05)
        except: continue
        
    status_text.empty()
    progress_bar.empty()
    return pd.DataFrame(results).sort_values(by="التقييم", ascending=False) if results else pd.DataFrame()

# --- 4. واجهة العرض ---

col_a, col_b = st.columns([4, 1])
with col_a:
    if st.button('🎯 استخراج التقرير الفني والإخباري الشامل', use_container_width=True):
        st.session_state.final_report = run_full_analysis(today_key)
with col_b:
    if st.button('🔄 تحديث'):
        st.cache_data.clear()
        st.rerun()

if 'final_report' in st.session_state and not st.session_state.final_report.empty:
    df = st.session_state.final_report
    
    # عرض أفضل سهمين بكروت كبيرة
    st.markdown("### 🏆 ترشيحات النخبة بناءً على الإغلاق والأخبار")
    top_cols = st.columns(2)
    for idx, col in enumerate(top_cols):
        row = df.iloc[idx]
        with col:
            st.markdown(f"""
                <div class="gold-box">
                    <h2 style="margin:0; color:#00ff00;">{row['السهم']}</h2>
                    <div style="font-size:20px;">{row['الإغلاق']} ج.م | {row['النجوم']}</div>
                </div>
            """, unsafe_allow_html=True)
            for n in row['أهم الأخبار']:
                st.markdown(f'<div class="news-card">{n}</div>', unsafe_allow_html=True)

    st.divider()
    
    # الجدول الكامل
    st.markdown("### 📋 تفاصيل القائمة كاملة")
    # تحويل قائمة الأخبار لنص لعرضها في الجدول
    df_display = df.copy()
    df_display['أهم الأخبار'] = df_display['أهم الأخبار'].apply(lambda x: " | ".join(x))
    st.dataframe(df_display[['السهم', 'الإغلاق', 'النجوم', 'أهم الأخبار']], use_container_width=True, hide_index=True)

st.markdown(f"<div style='text-align:center; color:#444; font-size:10px; padding:20px;'>Wahba Intelligence V5.0 | البيانات تعتمد على إغلاق الجلسة | {now_egypt.strftime('%Y-%m-%d')}</div>", unsafe_allow_html=True)
