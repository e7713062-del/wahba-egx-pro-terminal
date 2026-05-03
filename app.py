import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import time
from datetime import datetime
import pytz
import feedparser

# --- 1. إعدادات الوقت (إسكندرية) ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_alex = datetime.now(egypt_tz)
today_key = now_alex.strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba Intelligence | Mostafa Wahba", layout="wide")

# --- 2. التصميم الاحترافي (نفس التصميم السابق مع لمسات الفخامة) ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    .main-header { 
        text-align: center; padding: 30px; border-bottom: 3px solid #00ff00; 
        background: linear-gradient(180deg, #111 0%, #050505 100%);
        margin-bottom: 30px; border-radius: 0 0 25px 25px;
    }
    .dev-name { color: #00ff00; font-family: 'Courier New', monospace; letter-spacing: 3px; font-size: 14px; font-weight: bold; }
    .elite-box { 
        background: rgba(0, 255, 0, 0.03); border: 1px solid #00ff00; 
        padding: 25px; border-radius: 15px; margin-bottom: 25px;
    }
    .index-card { 
        padding: 20px; border: 1px solid #333; border-radius: 15px; 
        text-align: center; background: #0f0f0f;
    }
    </style>
    <div class="main-header">
        <div class="dev-name">ENGINEERED BY MOSTAFA WAHBA</div>
        <h1 style="margin:10px 0; color:#ffffff; font-size: 40px;">WAHBA <span style="color:#00ff00;">EGX</span> INTELLIGENCE</h1>
        <div style="color: #888; font-size: 15px;">Global Enterprise Trading Terminal v3.0</div>
    </div>
""", unsafe_allow_html=True)

# --- 3. الدوال الذكية مع "الذاكرة المشتركة" (Global Cache) ---

# حفظ بيانات المؤشرات لمدة ساعة (توفيراً للطلبات)
@st.cache_data(ttl=3600)
def get_index_data(symbol, date_key):
    try:
        handler = TA_Handler(symbol=symbol, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=5)
        analysis = handler.get_analysis()
        return {"price": analysis.indicators["close"], "change": analysis.indicators["change"]}
    except: return None

# حفظ الأخبار العالمية لمدة ساعتين
@st.cache_data(ttl=7200)
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

# حفظ قائمة الأسهم المتاحة لمدة يوم كامل (مهم جداً للتسويق)
@st.cache_data(ttl=86400)
def get_live_tickers():
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {"filter": [], "options": {"lang": "en"}, "markets": ["egypt"], "symbols": {"query": {"types": []}, "tickers": []}, "columns": ["name"]}
        res = requests.post(url, json=payload, timeout=15).json()
        return sorted(list(set([item['s'].split(':')[1] for item in res['data']])))
    except: return ["COMI", "FWRY", "TMGH", "SWDY", "ANFI"]

# حفظ نتائج الفحص الكامل لمدة 4 ساعات (هذا هو المفتاح لمنع الهجمات)
# أي مستخدم يطلب الفحص خلال 4 ساعات سيحصل على نفس النتيجة فوراً
@st.cache_data(ttl=14400)
def run_intelligent_scan(date_key):
    symbols = get_live_tickers()
    results = []
    idx30 = get_index_data("EGX30", date_key)
    
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, symbol in enumerate(symbols):
        try:
            status_text.text(f"🔍 فحص السهم {i+1}/{len(symbols)}: {symbol}")
            handler = TA_Handler(symbol=symbol, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=7)
            analysis = handler.get_analysis()
            rec = analysis.summary["RECOMMENDATION"]
            
            if "BUY" in rec:
                rsi = analysis.indicators["RSI"]
                score = 1
                if "STRONG" in rec: score += 1
                if 30 < rsi < 60: score += 1
                if idx30 and idx30['change'] > 0: score += 1
                
                results.append({
                    "السهم": symbol, "السعر": round(analysis.indicators["close"], 2),
                    "RSI": round(rsi, 2), "التقييم": "⭐" * int(score),
                    "score_val": score, "التوصية": rec.replace("_", " ")
                })
            progress_bar.progress((i + 1) / len(symbols))
            time.sleep(0.1) # تأخير بسيط لتجنب الضغط على السيرفر
        except: continue
        
    status_text.empty()
    progress_bar.empty()
    return results

# --- 4. واجهة العرض الرئيسية ---

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

# زر الفحص مع خاصية الذاكرة المشتركة
if st.button('🚀 تشغيل الماسح الذكي (نتائج الجلسة)', use_container_width=True):
    # بمجرد ضغط أول مستخدم، يتم حفظ النتيجة للجميع لمدة 4 ساعات
    report_data = run_intelligent_scan(today_key)
    st.session_state.final_results = pd.DataFrame(report_data)

if 'final_results' in st.session_state and st.session_state.final_results is not None:
    df = st.session_state.final_results
    
    # قسم النخبة
    elite = df[df['score_val'] >= 3].sort_values(by="score_val", ascending=False)
    if not elite.empty:
        st.markdown("<div class='elite-box'><h3 style='margin:0; color:#00ff00;'>🏆 فرص النخبة المكتشفة</h3></div>", unsafe_allow_html=True)
        st.table(elite[['السهم', 'السعر', 'RSI', 'التقييم']])
    
    # القائمة العامة
    st.markdown("### 📊 القائمة العامة للأسهم")
    st.dataframe(df[['السهم', 'السعر', 'RSI', 'التوصية', 'التقييم']], use_container_width=True, hide_index=True)

# تذييل الصفحة
st.divider()
with st.expander("📰 نبض السوق والأخبار"):
    news, tags = get_macro_analysis(today_key)
    for n in news: st.write(f"• {n}")

st.markdown(f"<div style='text-align:center; color:#555; font-size:11px; padding:20px;'>حقوق الملكية محفوظة © مصطفى وهبة | Wahba Intelligence <br> التحديثات تتم بشكل دوري لضمان استقرار الخدمة</div>", unsafe_allow_html=True)
