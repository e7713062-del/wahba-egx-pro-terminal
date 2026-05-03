import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import time
from datetime import datetime
import pytz
import feedparser

# --- 1. إعدادات الوقت (إسكندرية - مصطفى وهبة) ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_alex = datetime.now(egypt_tz)
today_key = now_alex.strftime("%Y-%m-%d")

# إعداد الصفحة وتصميم الهوية
st.set_page_config(page_title="Wahba Intelligence | Mostafa Wahba", layout="wide")

# --- 2. التصميم الاحترافي (CSS) ---
st.markdown("""
    <style>
    /* خلفية التطبيق وتنسيق الخطوط */
    .stApp { background-color: #050505; color: #e0e0e0; }
    
    /* الهيدر الرئيسي باسم مصطفى وهبة */
    .main-header { 
        text-align: center; 
        padding: 30px; 
        border-bottom: 3px solid #00ff00; 
        background: linear-gradient(180deg, #111 0%, #050505 100%);
        margin-bottom: 30px;
        border-radius: 0 0 25px 25px;
        box-shadow: 0 10px 30px rgba(0, 255, 0, 0.1);
    }
    .dev-name { 
        color: #00ff00; 
        font-family: 'Courier New', monospace; 
        letter-spacing: 3px; 
        font-size: 14px;
        font-weight: bold;
    }
    
    /* صناديق التميز */
    .elite-box { 
        background: rgba(0, 255, 0, 0.03); 
        border: 1px solid #00ff00; 
        padding: 25px; 
        border-radius: 15px; 
        margin-bottom: 25px;
        box-shadow: inset 0 0 15px rgba(0, 255, 0, 0.05);
    }
    
    /* كروت المؤشرات */
    .index-card { 
        padding: 20px; 
        border: 1px solid #333; 
        border-radius: 15px; 
        text-align: center; 
        background: #0f0f0f;
        transition: 0.3s;
    }
    .index-card:hover { border-color: #00ff00; transform: translateY(-5px); }
    
    /* الجداول */
    .styled-table { width: 100%; border-radius: 10px; overflow: hidden; }
    </style>
    
    <div class="main-header">
        <div class="dev-name">ENGINEERED BY MOSTAFA WAHBA</div>
        <h1 style="margin:10px 0; color:#ffffff; font-size: 40px;">WAHBA <span style="color:#00ff00;">EGX</span> INTELLIGENCE</h1>
        <div style="color: #888; font-size: 15px;">Advanced Quantitative Trading Terminal v2.0</div>
    </div>
""", unsafe_allow_html=True)

# --- 3. التحذير القانوني ---
with st.expander("⚖️ إخلاء المسؤولية القانونية"):
    st.caption("""
    جميع البيانات والتحليلات الناتجة عن هذا التطبيق هي لغرض استرشادي وتعليمي فقط، ولا تعتبر بأي حال من الأحوال توصية مباشرة بالبيع أو الشراء. 
    الاستثمار في الأوراق المالية ينطوي على مخاطر، والقرار النهائي يقع على عاتق المستخدم وحده. المصمم (مصطفى وهبة) غير مسؤول عن أي خسائر مادية.
    """)

# --- 4. الدوال الذكية (تظل كما هي بدون تغيير في المنطق) ---
@st.cache_data(ttl=None)
def get_index_data(symbol, date_key):
    try:
        handler = TA_Handler(symbol=symbol, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=5)
        analysis = handler.get_analysis()
        return {"price": analysis.indicators["close"], "change": analysis.indicators["change"], "rec": analysis.summary["RECOMMENDATION"]}
    except: return None

@st.cache_data(ttl=None)
def get_macro_analysis(date_key):
    try:
        urls = ["https://www.mubasher.info/rss/countries/eg/news", "https://www.skynewsarabia.com/rss/v1/business.xml"]
        news_titles = []
        for url in urls:
            feed = feedparser.parse(url)
            news_titles.extend([e.title for e in feed.entries[:4]])
        impact_keywords = ['حرب', 'فائدة', 'تضخم', 'صندوق', 'أزمة', 'دولار']
        impact_found = [word for word in impact_keywords if any(word in title for title in news_titles)]
        return news_titles, impact_found
    except: return [], []

@st.cache_data(ttl=None)
def get_stock_news_status(symbol, date_key):
    try:
        feed = feedparser.parse(f"https://www.mubasher.info/rss/stocks/{symbol}/news")
        return ("🟢 إيجابي حديث" if len(feed.entries) > 0 else "⚪ هادئ"), (1 if len(feed.entries) > 0 else 0)
    except: return "⚪ لا يوجد", 0

@st.cache_data(ttl=86400)
def get_live_tickers():
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {"filter": [], "options": {"lang": "en"}, "markets": ["egypt"], "symbols": {"query": {"types": []}, "tickers": []}, "columns": ["name"]}
        res = requests.post(url, json=payload, timeout=15).json()
        return sorted(list(set([item['s'].split(':')[1] for item in res['data']])))
    except: return ["COMI", "FWRY", "TMGH", "SWDY", "ANFI"]

def run_intelligent_scan():
    symbols = get_live_tickers()
    results = []
    idx30 = get_index_data("EGX30", today_key)
    progress = st.progress(0)
    status = st.empty()

    for i, symbol in enumerate(symbols):
        try:
            status.text(f"🚀 جاري فحص: {symbol}")
            handler = TA_Handler(symbol=symbol, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=7)
            analysis = handler.get_analysis()
            rec = analysis.summary["RECOMMENDATION"]
            
            if "BUY" in rec:
                rsi = analysis.indicators["RSI"]
                news_status, news_pts = get_stock_news_status(symbol, today_key)
                score = 1
                if "STRONG" in rec: score += 1
                if 30 < rsi < 60: score += 1
                score += news_pts
                if idx30 and idx30['change'] > 0: score += 1
                
                results.append({
                    "السهم": symbol, "السعر": round(analysis.indicators["close"], 2),
                    "RSI": round(rsi, 2), "حالة الخبر": news_status,
                    "القوة": "⭐" * int(score), "score_val": score,
                    "التوصية": rec.replace("_", " ")
                })
            progress.progress((i + 1) / len(symbols))
        except: continue
    status.empty(); progress.empty()
    return results

# --- 5. واجهة العرض الرئيسية ---

# عرض المؤشرات بشكل جمالي
c1, c2 = st.columns(2)
for c, s, n in zip([c1, c2], ["EGX30", "EGX70EWI"], ["مؤشر EGX 30", "مؤشر EGX 70"]):
    data = get_index_data(s, today_key)
    if data:
        clr = "#00ff00" if data['change'] >= 0 else "#ff4b4b"
        c.markdown(f"""<div class="index-card">
            <div style="font-size:14px; color:#888;">{n}</div>
            <div style="color:{clr}; font-size:28px; font-weight:bold;">{data['price']:,.2f}</div>
            <div style="color:{clr}; font-size:14px;">{data['change']:.2f}%</div>
        </div>""", unsafe_allow_html=True)

st.write("") 

# زر التشغيل
if 'final_results' not in st.session_state:
    st.session_state.final_results = None

col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    if st.button('🎯 تحليل السوق الآن', use_container_width=True):
        report = run_intelligent_scan()
        st.session_state.final_results = pd.DataFrame(report)

# عرض النتائج
if st.session_state.final_results is not None:
    df = st.session_state.final_results
    
    # فرص النخبة
    elite_df = df[df['score_val'] >= 4].sort_values(by="score_val", ascending=False)
    if not elite_df.empty:
        st.markdown("<div class='elite-box'><h3 style='margin:0; color:#00ff00;'>🏆 أقوى فرص الشراء (Elite Picks)</h3></div>", unsafe_allow_html=True)
        st.dataframe(elite_df[['السهم', 'السعر', 'RSI', 'حالة الخبر', 'القوة']], use_container_width=True, hide_index=True)
    
    # القائمة العامة
    st.markdown("### 📊 تقرير السوق العام")
    general_df = df[df['score_val'] < 4].sort_values(by="score_val", ascending=False)
    st.dataframe(general_df[['السهم', 'السعر', 'RSI', 'التوصية', 'القوة']], use_container_width=True, hide_index=True)

# تذييل الصفحة بالأخبار
st.divider()
with st.expander("🌐 موجز الأنباء الاقتصادية"):
    news_list, impact_tags = get_macro_analysis(today_key)
    if impact_tags: st.warning(f"⚠️ الكلمات الأكثر تأثيراً اليوم: {' | '.join(impact_tags)}")
    for t in news_list: st.write(f"• {t}")

st.markdown(f"<div style='text-align:center; color:#555; font-size:12px; padding:20px;'>تم التحديث في: {now_alex.strftime('%Y-%m-%d %H:%M:%S')} (Alexandria Time) <br> All rights reserved © Wahba Intelligence </div>", unsafe_allow_html=True)
