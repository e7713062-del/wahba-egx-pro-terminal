import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import time
from datetime import datetime
import pytz
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import xml.etree.ElementTree as ET

# ==========================================
# 1. الإعدادات والوقت والذكاء الاصطناعي
# ==========================================
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)
today_key = now_egypt.strftime("%Y-%m-%d")

# كلمات مفتاحية لتحليل الأخبار (Sentiment)
POS_KEYWORDS = ['أرباح', 'نمو', 'استحواذ', 'صعود', 'توسع', 'إيجابي', 'ارتفاع', 'توزيعات', 'فائض']
NEG_KEYWORDS = ['خسارة', 'تراجع', 'انخفاض', 'هبوط', 'غرامة', 'سلبي', 'ديون', 'عجز']

class WahbaUltraAI:
    """محرك الذكاء الاصطناعي الهجين - يحلل الأرقام والمشاعر"""
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()

    def process_and_predict(self, df):
        if len(df) < 3:
            df['Target'] = df['Price'] * 1.05
            return df
        try:
            # تدريب الموديل على (السعر، السكور، RSI، ونقطة الارتكاز)
            X = df[['Price', 'Score', 'RSI', 'P']].values
            y = df['Price'] * (1 + (df['Score'] / 100))
            self.scaler.fit(X)
            X_scaled = self.scaler.transform(X)
            self.model.fit(X_scaled, y)
            df['Target'] = self.model.predict(X_scaled)
        except:
            df['Target'] = df['Price']
        return df

# تهيئة الجلسة
if 'wahba_ai' not in st.session_state:
    st.session_state.wahba_ai = WahbaUltraAI()
if 'market_data' not in st.session_state:
    st.session_state.market_data = None

# ==========================================
# 2. تصميم الواجهة الاحترافي (CSS)
# ==========================================
st.set_page_config(page_title="WAHBA AI | PRO TERMINAL", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background-color: #000; color: #fff; }
    
    .header-box { text-align: center; padding: 20px; border-bottom: 2px solid #d4af37; margin-bottom: 30px; }
    .gold-card {
        background: linear-gradient(145deg, #0a0a0a 0%, #151515 100%);
        border: 1px solid #d4af37; border-radius: 15px; padding: 25px; margin-bottom: 25px;
    }
    .news-box {
        background: rgba(212, 175, 55, 0.05); border-right: 3px solid #d4af37;
        padding: 12px; margin-top: 15px; border-radius: 5px;
    }
    .news-link { color: #aaa; text-decoration: none; font-size: 13px; display: block; margin-bottom: 5px; }
    .news-link:hover { color: #d4af37; }
    .price-tag { background: #d4af37; color: #000; padding: 4px 10px; border-radius: 5px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="header-box">
        <h1 style="color:#fff; margin:0;">WAHBA <span style="color:#d4af37;">INTELLIGENCE</span></h1>
        <p style="color:#555;">منصة التحليل الهجين بالذكاء الاصطناعي | {today_key}</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 3. وظائف جلب البيانات والأخبار
# ==========================================

@st.cache_data(ttl=3600)
def fetch_news(symbol):
    """جلب وتحليل مشاعر الأخبار لكل سهم"""
    try:
        query = f"سهم {symbol} البورصة المصرية"
        url = f"https://news.google.com/rss/search?q={query}&hl=ar&gl=EG&ceid=EG:ar"
        res = requests.get(url, timeout=10)
        root = ET.fromstring(res.content)
        items = []
        sentiment_score = 0
        
        for item in root.findall('.//item')[:3]:
            title = item.find('title').text
            link = item.find('link').text
            items.append({"title": title, "link": link})
            
            # تحليل المشاعر
            if any(w in title for w in POS_KEYWORDS): sentiment_score += 1.5
            if any(w in title for w in NEG_KEYWORDS): sentiment_score -= 2.0
            
        return items, sentiment_score
    except:
        return [], 0

@st.cache_data(ttl=86400)
def get_all_symbols():
    """سحب قائمة الأسهم أوتوماتيكياً"""
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}
        res = requests.post(url, json=payload, timeout=15).json()
        return [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except:
        return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO"]

def run_scanner():
    symbols = get_all_symbols()
    final_list = []
    progress = st.progress(0)
    status = st.empty()
    
    for i, sym in enumerate(symbols):
        try:
            status.text(f"جاري فحص {sym} وتحليل الأخبار...")
            if i % 5 == 0: time.sleep(0.5) # حماية من الحظر
            
            # 1. التحليل الفني
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            
            score = 0
            rec = analysis.summary["RECOMMENDATION"]
            if "STRONG_BUY" in rec: score += 5
            elif "BUY" in rec: score += 3
            
            rsi = ind.get("RSI", 50)
            if 45 <= rsi <= 65: score += 3
            
            # 2. التحليل الأساسي (الأخبار)
            news, news_bonus = fetch_news(sym)
            score += news_bonus
            
            final_list.append({
                "Symbol": sym, "Price": round(ind.get("close"), 2), "Score": score,
                "RSI": round(rsi, 2), "P": round(ind.get("Pivot.M.Classic.Middle", 0), 2),
                "S1": round(ind.get("Pivot.M.Classic.S1", 0), 2), "R1": round(ind.get("Pivot.M.Classic.R1", 0), 2),
                "News": news
            })
        except: continue
        progress.progress((i + 1) / len(symbols))
        
    if final_list:
        df = pd.DataFrame(final_list)
        df = st.session_state.wahba_ai.process_and_predict(df)
        st.session_state.market_data = df
        status.success("تم تحديث النظام بالكامل!")
    else:
        status.error("فشل سحب البيانات، جرب مرة أخرى.")

# ==========================================
# 4. العرض النهائي (UI)
# ==========================================

if st.button("🚀 تشغيل محرك الذكاء الاصطناعي (تحليل هجين)"):
    run_scanner()

if st.session_state.market_data is not None:
    df = st.session_state.market_data
    
    # القسم الذهبي
    st.markdown("### 🏆 ترشيحات الذكاء الاصطناعي (نخبة النخبة)")
    gold = df[df['Score'] >= 8.5].sort_values(by='Score', ascending=False)
    
    for _, row in gold.iterrows():
        news_html = "".join([f'<a href="{n["link"]}" class="news-link" target="_blank">• {n["title"]}</a>' for n in row['News']])
        
        st.markdown(f"""
            <div class="gold-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span style="font-size:32px; font-weight:900; color:#d4af37;">{row['Symbol']}</span>
                        <div style="margin-top:5px;"><span class="price-tag">{row['Price']} EGP</span></div>
                    </div>
                    <div style="text-align:left;">
                        <small style="color:#888;">الهدف المتوقع (AI):</small><br>
                        <span style="font-size:24px; color:#d4af37; font-weight:bold;">{round(row['Target'], 2)}</span>
                    </div>
                </div>
                
                <div class="news-box">
                    <b style="color:#d4af37; font-size:14px;">📡 نبض الأخبار والمشاعر:</b><br>
                    {news_html if news_html else "لا توجد أخبار مؤثرة حالياً."}
                </div>
                
                <div style="display:flex; justify-content:space-between; margin-top:20px; font-size:12px; color:#555;">
                    <span>الدعم (S1): {row['S1']}</span>
                    <span>الارتكاز (P): {row['P']}</span>
                    <span>المقاومة (R1): {row['R1']}</span>
                    <span>قوة السكور: {row['Score']}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # القسم الفضي
    st.markdown("<br>### 🥈 فرص ثانوية (Silver Tier)")
    silver = df[(df['Score'] >= 6) & (df['Score'] < 8.5)]
    cols = st.columns(3)
    for i, (_, row) in enumerate(silver.iterrows()):
        with cols[i % 3]:
            st.markdown(f"""
                <div style="background:#0a0a0a; border:1px solid #222; padding:15px; border-radius:10px; margin-bottom:15px;">
                    <b style="color:#d4af37;">{row['Symbol']}</b> | <small>{row['Price']} EGP</small><br>
                    <small style="color:#555;">الهدف: {round(row['Target'], 2)}</small>
                </div>
            """, unsafe_allow_html=True)

# تذييل المنصة
st.markdown(f"""
    <div style="text-align:center; margin-top:50px; padding:20px; border-top:1px solid #111; color:#333;">
        <small>Wahba Intelligence System v3.0 | تطوير مصطفى تامر أحمد السيد</small><br>
        <small>إخلاء مسؤولية: هذا النظام استرشادي وقرار البيع والشراء مسؤوليتك.</small>
    </div>
""", unsafe_allow_html=True)
