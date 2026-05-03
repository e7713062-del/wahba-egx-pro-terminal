import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import time
from datetime import datetime
import pytz
import feedparser

# 1. إعدادات الوقت والمنطقة (إسكندرية)
egypt_tz = pytz.timezone('Africa/Cairo')
now_alex = datetime.now(egypt_tz)
today_key = now_alex.strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba EGX | Intelligence Terminal", layout="wide")

# 2. واجهة المستخدم والتنسيق
st.markdown("""
    <style>
    .main-header { text-align: center; padding: 10px; border-bottom: 2px solid #1e1e1e; }
    .index-card { padding:15px; border:1px solid #333; border-radius:10px; text-align:center; background: #0e0e0e; }
    .pro-card { background: #0a0a0a; padding: 20px; border-radius: 12px; border: 1px solid #00ff00; margin-bottom: 20px; }
    .star-rating { color: #ffd700; font-weight: bold; }
    </style>
    <div class="main-header">
        <h1 style="margin:0; color:#00ff00;">WAHBA EGX INTELLIGENCE</h1>
        <div style="color: #888; font-size: 12px; letter-spacing: 2px;">TECHNICAL + FUNDAMENTAL SYNC</div>
    </div>
""", unsafe_allow_html=True)

# 3. الدوال الذكية مع الـ Caching اليومي

@st.cache_data(ttl=None)
def get_index_data(symbol, date_key):
    try:
        handler = TA_Handler(symbol=symbol, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=5)
        analysis = handler.get_analysis()
        return {"price": analysis.indicators["close"], "change": analysis.indicators["change"], "rec": analysis.summary["RECOMMENDATION"]}
    except: return None

@st.cache_data(ttl=None)
def get_general_news(date_key):
    try:
        feed = feedparser.parse("https://www.mubasher.info/rss/countries/eg/news")
        return [{"title": e.title, "link": e.link} for e in feed.entries[:5]]
    except: return []

@st.cache_data(ttl=None)
def get_stock_news_status(symbol, date_key):
    """التحقق من وجود أخبار حديثة للسهم لتقوية التوصية"""
    try:
        # البحث في أخبار السهم المحددة
        feed = feedparser.parse(f"https://www.mubasher.info/rss/stocks/{symbol}/news")
        if len(feed.entries) > 0:
            return "🟢 أخبار حديثة", 1 # نقطة إضافية للتقييم
        return "⚪ هادئ", 0
    except: return "⚪ لا يوجد", 0

@st.cache_data(ttl=86400)
def get_all_tickers():
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {"filter": [], "options": {"lang": "en"}, "markets": ["egypt"], "symbols": {"query": {"types": []}, "tickers": []}, "columns": ["name"]}
        res = requests.post(url, json=payload, timeout=15).json()
        return sorted(list(set([item['s'].split(':')[1] for item in res['data']])))
    except: return ["COMI", "FWRY", "TMGH", "SWDY"]

# 4. محرك المسح المتطور (التقييم بالنجوم)
def run_intelligent_scan():
    symbols = get_all_tickers()
    results = []
    progress_bar = st.progress(0)
    status_msg = st.empty()
    
    for i, symbol in enumerate(symbols):
        try:
            status_msg.markdown(f"🔍 تحليل ذكي للسهم: `{symbol}`")
            handler = TA_Handler(symbol=symbol, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=5)
            analysis = handler.get_analysis()
            rec = analysis.summary["RECOMMENDATION"]
            
            if "BUY" in rec:
                rsi = analysis.indicators["RSI"]
                news_status, news_points = get_stock_news_status(symbol, today_key)
                
                # نظام نقاط Wahba (نجمتين للفني + نجمة للـ RSI + نجمة للأخبار)
                score = 1 # نقطة أساسية للشراء
                if "STRONG" in rec: score += 1
                if 30 < rsi < 60: score += 1
                score += news_points
                
                results.append({
                    "السهم": symbol,
                    "إغلاق": round(analysis.indicators["close"], 2),
                    "RSI": round(rsi, 2),
                    "أخبار": news_status,
                    "التقييم": "⭐" * score,
                    "قوة_الترتيب": score
                })
            
            if (i + 1) % 5 == 0: time.sleep(0.4) # حماية السيرفر
            progress_bar.progress((i + 1) / len(symbols))
        except: continue
        
    status_msg.empty()
    progress_bar.empty()
    return results

# --- العرض (UI) ---

# أولاً: المؤشرات الرئيسية
st.markdown("### 📈 أداء المؤشرات العامة")
c1, c2 = st.columns(2)
for col, sym, name in zip([c1, c2], ["EGX30", "EGX70EWI"], ["EGX 30", "EGX 70 EWI"]):
    idx = get_index_data(sym, today_key)
    if idx:
        color = "#00ff00" if idx['change'] >= 0 else "#ff4b4b"
        col.markdown(f"""<div class="index-card">
            <h4 style="margin:0;">{name}</h4>
            <h2 style="margin:5px 0; color:{color};">{idx['price']:,.2f} ({idx['change']:.2f}%)</h2>
            <small>الحالة: {idx['rec']}</small>
        </div>""", unsafe_allow_html=True)

st.divider()

# ثانياً: شريط الأخبار
st.markdown("### 📰 نبض السوق")
gen_news = get_general_news(today_key)
news_text = " • ".join([f"[{n['title']}]({n['link']})" for n in gen_news])
st.caption(f"📢 {news_text}")

st.divider()

# ثالثاً: المسح والفرص
st.write(f"🕒 تحديث الجلسة: {today_key} | إسكندرية")
if 'intelligent_results' not in st.session_state:
    st.session_state.intelligent_results = None

if st.button('🚀 تشغيل التحليل الفني والإخباري الشامل', use_container_width=True):
    data = run_intelligent_scan()
    st.session_state.intelligent_results = pd.DataFrame(data)

if st.session_state.intelligent_results is not None:
    df = st.session_state.intelligent_results
    st.markdown("<div class='pro-card'>🏆 أقوى الفرص المختارة (بناءً على تلاقي السعر والأخبار)</div>", unsafe_allow_html=True)
    
    # عرض الـ Top Picks (الـ 4 نجوم فأكثر)
    top_picks = df[df['قوة_الترتيب'] >= 3].sort_values(by="قوة_الترتيب", ascending=False)
    st.dataframe(top_picks[['السهم', 'إغلاق', 'RSI', 'أخبار', 'التقييم']], use_container_width=True)
