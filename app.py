import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import time
from datetime import datetime
import pytz
import feedparser

# 1. إعدادات الوقت (التكيف مع التوقيت الصيفي والشتوي في إسكندرية)
egypt_tz = pytz.timezone('Africa/Cairo')
now_alex = datetime.now(egypt_tz)
today_key = now_alex.strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba EGX Intelligence", layout="wide")

# 2. الواجهة الاحترافية (CSS)
st.markdown("""
    <style>
    .main-header { text-align: center; padding: 20px; border-bottom: 2px solid #00ff00; background: #0e0e0e; }
    .index-card { padding:15px; border:1px solid #333; border-radius:10px; text-align:center; background: #111; }
    .macro-box { background: rgba(255, 75, 75, 0.1); border: 1px solid #ff4b4b; padding: 15px; border-radius: 10px; margin: 10px 0; }
    .star-rating { color: #ffd700; font-size: 18px; }
    </style>
    <div class="main-header">
        <h1 style="margin:0; color:#00ff00;">WAHBA EGX INTELLIGENCE</h1>
        <div style="color: #888; font-size: 13px;">Advanced Technical & Macro Analysis System</div>
    </div>
""", unsafe_allow_html=True)

# 3. محرك البحث والذاكرة (Caching)

@st.cache_data(ttl=None) # حفظ المؤشرات طول اليوم
def get_index_data(symbol, date_key):
    try:
        handler = TA_Handler(symbol=symbol, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=5)
        analysis = handler.get_analysis()
        return {"price": analysis.indicators["close"], "change": analysis.indicators["change"], "rec": analysis.summary["RECOMMENDATION"]}
    except: return None

@st.cache_data(ttl=None) # جلب أخبار الدولة والعالم (الماكرو)
def get_macro_analysis(date_key):
    try:
        urls = ["https://www.mubasher.info/rss/countries/eg/news", "https://www.skynewsarabia.com/rss/v1/business.xml"]
        news_titles = []
        for url in urls:
            feed = feedparser.parse(url)
            news_titles.extend([e.title for e in feed.entries[:4]])
        
        # تحليل الكلمات المفتاحية للحروب والاقتصاد
        impact_keywords = ['حرب', 'فائدة', 'تضخم', 'صندوق', 'أزمة', 'دولار', 'استحواذ']
        impact_found = [word for word in impact_keywords if any(word in title for title in news_titles)]
        return news_titles, impact_found
    except: return [], []

@st.cache_data(ttl=None) # أخبار السهم المحددة
def get_stock_news_status(symbol, date_key):
    try:
        feed = feedparser.parse(f"https://www.mubasher.info/rss/stocks/{symbol}/news")
        return ("🟢 إيجابي حديث" if len(feed.entries) > 0 else "⚪ هادئ"), (1 if len(feed.entries) > 0 else 0)
    except: return "⚪ لا يوجد", 0

@st.cache_data(ttl=86400) # سحب كل الأسهم المدرجة جديداً أوتوماتيك
def get_live_tickers():
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {"filter": [], "options": {"lang": "en"}, "markets": ["egypt"], "symbols": {"query": {"types": []}, "tickers": []}, "columns": ["name"]}
        res = requests.post(url, json=payload, timeout=15).json()
        return sorted(list(set([item['s'].split(':')[1] for item in res['data']])))
    except: return ["COMI", "FWRY", "TMGH", "SWDY", "ANFI"]

# 4. محرك المسح الذكي (Scoring Engine)
def run_wahba_intelligence_scan():
    symbols = get_live_tickers()
    results = []
    idx30 = get_index_data("EGX30", today_key)
    _, macro_impact = get_macro_analysis(today_key)
    
    progress = st.progress(0)
    status = st.empty()

    for i, symbol in enumerate(symbols):
        try:
            status.text(f"🔍 فحص ذكي: {symbol}")
            handler = TA_Handler(symbol=symbol, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=7)
            analysis = handler.get_analysis()
            rec = analysis.summary["RECOMMENDATION"]
            
            if "BUY" in rec:
                rsi = analysis.indicators["RSI"]
                news_status, news_pts = get_stock_news_status(symbol, today_key)
                
                # حساب نقاط القوة
                score = 1
                if "STRONG" in rec: score += 1
                if 30 < rsi < 60: score += 1
                score += news_pts
                if idx30 and idx30['change'] > 0: score += 1 # قوة السوق العام
                
                results.append({
                    "السهم": symbol,
                    "إغلاق": round(analysis.indicators["close"], 2),
                    "RSI": round(rsi, 2),
                    "أخبار السهم": news_status,
                    "التقييم": "⭐" * int(score),
                    "قوة": score,
                    "التوصية": rec.replace("_", " ")
                })
            
            if (i + 1) % 5 == 0: time.sleep(0.3)
            progress.progress((i + 1) / len(symbols))
        except: continue
    
    status.empty()
    progress.empty()
    return results

# --- واجهة العرض الرئيسية ---

# أ. المؤشرات
st.markdown("### 📊 المؤشرات القيادية")
col1, col2 = st.columns(2)
for c, s, n in zip([col1, col2], ["EGX30", "EGX70EWI"], ["EGX 30", "EGX 70 EWI"]):
    data = get_index_data(s, today_key)
    if data:
        clr = "#00ff00" if data['change'] >= 0 else "#ff4b4b"
        c.markdown(f"""<div class="index-card">
            <h3 style="margin:0;">{n}</h3>
            <h2 style="color:{clr}; margin:5px 0;">{data['price']:,.2f} ({data['change']:.2f}%)</h2>
            <small>الاتجاه: {data['rec']}</small>
        </div>""", unsafe_allow_html=True)

# ب. تحليل المخاطر (الماكرو والحروب)
news_list, impact_tags = get_macro_analysis(today_key)
if impact_tags:
    with st.container():
        st.markdown(f"""<div class="macro-box">
            <b>⚠️ تنبيه مخاطر اقتصادية/سياسية:</b> تم رصد تأثيرات ( {' | '.join(impact_tags)} ) قد تؤثر على حركة السيولة.
        </div>""", unsafe_allow_html=True)

# ج. التشغيل والنتائج
st.write(f"📅 **الجلسة:** {today_key} | 🕒 **توقيت إسكندرية:** {now_alex.strftime('%I:%M %p')}")

if 'final_results' not in st.session_state:
    st.session_state.final_results = None

if st.button('🚀 تشغيل الرادار الذكي (فني + ماكرو + أخبار)', use_container_width=True):
    report = run_wahba_intelligence_scan()
    st.session_state.final_results = pd.DataFrame(report)

if st.session_state.final_results is not None:
    df = st.session_state.final_results
    st.markdown("### 🏆 ترتيب الفرص (من الأقوى تقييماً)")
    # عرض الجدول مرتباً من 5 نجوم لأسفل
    st.dataframe(df.sort_values(by="قوة", ascending=False)[['السهم', 'إغلاق', 'RSI', 'التوصية', 'أخبار السهم', 'التقييم']], use_container_width=True)

st.divider()
with st.expander("📰 نبض الأخبار العاجلة"):
    for t in news_list: st.write(f"• {t}")
