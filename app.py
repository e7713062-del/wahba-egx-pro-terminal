import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import time
from datetime import datetime
import pytz
import feedparser

# 1. إعدادات الوقت (إسكندرية - صيفي وشتوي)
egypt_tz = pytz.timezone('Africa/Cairo')
now_alex = datetime.now(egypt_tz)
today_key = now_alex.strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba EGX Intelligence", layout="wide")

# --- 2. التحذير القانوني (أول شيء يظهر) ---
st.error("⚠️ **تحذير قانوني وإخلاء مسؤولية:**")
st.caption("""
جميع البيانات والتحليلات الناتجة عن هذا التطبيق هي لغرض استرشادي وتعليمي فقط، ولا تعتبر بأي حال من الأحوال توصية مباشرة بالبيع أو الشراء. 
الاستثمار في الأوراق المالية ينطوي على مخاطر، والقرار النهائي يقع على عاتق المستخدم وحده. المصمم غير مسؤول عن أي خسائر مادية ناتجة عن استخدام هذه الأرقام.
""")

# 3. التنسيق والواجهة
st.markdown("""
    <style>
    .main-header { text-align: center; padding: 15px; border-bottom: 2px solid #00ff00; background: #0e0e0e; margin-bottom: 20px; }
    .elite-box { background: rgba(0, 255, 0, 0.05); border: 2px solid #00ff00; padding: 20px; border-radius: 15px; margin-bottom: 25px; }
    .index-card { padding:12px; border:1px solid #333; border-radius:10px; text-align:center; background: #111; }
    </style>
    <div class="main-header">
        <h1 style="margin:0; color:#00ff00;">WAHBA EGX INTELLIGENCE</h1>
        <div style="color: #888; font-size: 13px;">Advanced Professional Trading Terminal</div>
    </div>
""", unsafe_allow_html=True)

# 4. الدوال الذكية (Caching)
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

# 5. محرك المسح الذكي
def run_intelligent_scan():
    symbols = get_live_tickers()
    results = []
    idx30 = get_index_data("EGX30", today_key)
    _, macro_impact = get_macro_analysis(today_key)
    
    progress = st.progress(0)
    status = st.empty()

    for i, symbol in enumerate(symbols):
        try:
            status.text(f"🔍 تحليل الفرص: {symbol}")
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
                    "السهم": symbol, "إغلاق": round(analysis.indicators["close"], 2),
                    "RSI": round(rsi, 2), "أخبار السهم": news_status,
                    "التقييم": "⭐" * int(score), "score_val": score,
                    "التوصية": rec.replace("_", " ")
                })
            if (i + 1) % 5 == 0: time.sleep(0.3)
            progress.progress((i + 1) / len(symbols))
        except: continue
    status.empty(); progress.empty()
    return results

# --- واجهة العرض الرئيسية ---

# أ. المؤشرات والماكرو
c1, c2 = st.columns(2)
for c, s, n in zip([c1, c2], ["EGX30", "EGX70EWI"], ["EGX 30", "EGX 70 EWI"]):
    data = get_index_data(s, today_key)
    if data:
        clr = "#00ff00" if data['change'] >= 0 else "#ff4b4b"
        c.markdown(f"""<div class="index-card">
            <h4 style="margin:0;">{n}</h4>
            <h2 style="color:{clr}; margin:5px 0;">{data['price']:,.2f} ({data['change']:.2f}%)</h2>
        </div>""", unsafe_allow_html=True)

st.divider()

# ب. التشغيل
if 'final_results' not in st.session_state:
    st.session_state.final_results = None

st.write(f"🕒 **آخر تحديث:** {today_key} | توقيت إسكندرية")
if st.button('🚀 ابدأ تحليل السوق واكتشاف الفرص الذهبية', use_container_width=True):
    report = run_intelligent_scan()
    st.session_state.final_results = pd.DataFrame(report)

# ج. عرض النتائج المقسمة
if st.session_state.final_results is not None:
    df = st.session_state.final_results
    
    # --- القسم الأول: قائمة فرص النخبة (النجوم الكاملة) ---
    elite_df = df[df['score_val'] >= 4].sort_values(by="score_val", ascending=False)
    
    if not elite_df.empty:
        st.markdown("<div class='elite-box'><h3>🏆 قائمة فرص النخبة (أقوى إشارات شراء)</h3></div>", unsafe_allow_html=True)
        st.table(elite_df[['السهم', 'إغلاق', 'RSI', 'أخبار السهم', 'التقييم']])
    else:
        st.info("لم يتم العثور على أسهم بتقييم (النخبة) اليوم، يرجى مراجعة القائمة العامة.")

    st.divider()

    # --- القسم الثاني: قائمة الأسهم العامة (باقي الفرص) ---
    st.markdown("### 📊 القائمة العامة للأسهم الواعدة")
    general_df = df[df['score_val'] < 4].sort_values(by="score_val", ascending=False)
    st.dataframe(general_df[['السهم', 'إغلاق', 'RSI', 'التوصية', 'التقييم']], use_container_width=True)

# د. الأخبار في الأسفل
with st.expander("📰 نبض الاقتصاد (أخبار الدولة والحروب)"):
    news_list, impact_tags = get_macro_analysis(today_key)
    if impact_tags: st.warning(f"تنبيهات الماكرو: {' | '.join(impact_tags)}")
    for t in news_list: st.write(f"• {t}")
