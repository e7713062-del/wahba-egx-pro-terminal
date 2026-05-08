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
# 1. إعدادات الوقت والمحرك الذكي
# ==========================================
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)
today_key = now_egypt.strftime("%Y-%m-%d")

class WahbaUltraAI:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()

    def process_and_predict(self, df):
        if len(df) < 3:
            df['Target'] = df['Price'] * 1.05
            return df
        try:
            X = df[['Price', 'Score', 'RSI', 'P']].values
            y = df['Price'] * (1 + (df['Score'] / 100))
            self.scaler.fit(X)
            X_scaled = self.scaler.transform(X)
            self.model.fit(X_scaled, y)
            df['Target'] = self.model.predict(X_scaled)
        except:
            df['Target'] = df['Price']
        return df

if 'wahba_ai' not in st.session_state:
    st.session_state.wahba_ai = WahbaUltraAI()
if 'market_data' not in st.session_state:
    st.session_state.market_data = None

# ==========================================
# 2. تصميم الواجهة الـ Formal (Premium Dark Mode)
# ==========================================
st.set_page_config(page_title="WAHBA INTEL | AI TERMINAL", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=Tajawal:wght@400;700;900&display=swap');
    
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background-color: #050505; color: #e0e0e0; }

    /* هيدر احترافي */
    .header-container {
        text-align: center; padding: 40px 20px;
        background: linear-gradient(180deg, #000 0%, #050505 100%);
        border-bottom: 1px solid #1a1a1a; margin-bottom: 40px;
    }
    .logo { font-size: 42px; font-weight: 900; letter-spacing: -1px; color: #fff; }
    .logo span { color: #d4af37; text-shadow: 0 0 20px rgba(212, 175, 55, 0.3); }

    /* كارت السهم الذهبي */
    .premium-card {
        background: #0d0d0d;
        border: 1px solid #1a1a1a;
        border-right: 4px solid #d4af37;
        border-radius: 12px;
        padding: 30px;
        margin-bottom: 25px;
        transition: all 0.3s ease;
    }
    .premium-card:hover { border-color: #d4af37; transform: translateY(-5px); box-shadow: 0 10px 30px rgba(0,0,0,0.5); }

    .symbol-title { font-size: 32px; font-weight: 900; color: #fff; margin: 0; }
    .target-box { background: rgba(212, 175, 55, 0.1); padding: 15px; border-radius: 8px; text-align: center; min-width: 150px; }
    .target-val { font-size: 28px; font-weight: 900; color: #d4af37; display: block; }
    
    /* صندوق الأخبار */
    .news-wrapper { background: #080808; border-radius: 8px; padding: 15px; margin: 20px 0; border: 1px solid #111; }
    .news-item { 
        color: #888; text-decoration: none; font-size: 14px; 
        display: block; padding: 8px 0; border-bottom: 1px solid #151515;
    }
    .news-item:last-child { border: none; }
    .news-item:hover { color: #d4af37; padding-right: 5px; }

    /* شبكة المستويات الرقمية */
    .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-top: 20px; }
    .stat-box { background: #000; padding: 10px; border-radius: 6px; text-align: center; border: 1px solid #151515; }
    .stat-label { font-size: 11px; color: #444; display: block; margin-bottom: 5px; text-transform: uppercase; }
    .stat-value { font-size: 14px; font-weight: bold; color: #fff; font-family: 'Inter', sans-serif; }

    /* زر الأكشن */
    .stButton > button {
        background: #d4af37 !important; color: #000 !important;
        font-weight: 900 !important; border: none !important;
        border-radius: 8px !important; height: 55px !important; width: 100%;
        transition: 0.3s;
    }
    .stButton > button:hover { opacity: 0.9; box-shadow: 0 0 20px rgba(212, 175, 55, 0.4); }
    </style>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="header-container">
        <div class="logo">WAHBA <span>INTEL</span></div>
        <div style="color:#444; font-size:12px; margin-top:10px;">INSTITUTIONAL AI TERMINAL • {today_key}</div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 3. محرك جلب البيانات والأخبار (بدون أخطاء عرض)
# ==========================================

@st.cache_data(ttl=3600)
def fetch_news_clean(symbol):
    try:
        query = f"سهم {symbol} البورصة المصرية"
        url = f"https://news.google.com/rss/search?q={query}&hl=ar&gl=EG&ceid=EG:ar"
        res = requests.get(url, timeout=7)
        root = ET.fromstring(res.content)
        items = []
        for item in root.findall('.//item')[:3]:
            items.append({"title": item.find('title').text, "link": item.find('link').text})
        return items
    except:
        return []

@st.cache_data(ttl=86400)
def get_symbols():
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}
        res = requests.post(url, json=payload, timeout=10).json()
        return [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except:
        return ["COMI", "FWRY", "TMGH", "SWDY"]

def start_scanning():
    symbols = get_symbols()
    data_list = []
    p_bar = st.progress(0)
    status = st.empty()
    
    for i, sym in enumerate(symbols):
        try:
            status.text(f"Scanning Asset: {sym}...")
            if i % 4 == 0: time.sleep(0.3)
            
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY)
            ind = handler.get_analysis().indicators
            
            # سكور بسيط للمثال
            score = 5
            if "BUY" in handler.get_analysis().summary["RECOMMENDATION"]: score += 3
            if 40 < ind.get("RSI", 50) < 65: score += 2

            data_list.append({
                "Symbol": sym, "Price": round(ind.get("close"), 2), "Score": score,
                "RSI": round(ind.get("RSI", 50), 2), "P": round(ind.get("Pivot.M.Classic.Middle", 0), 2),
                "S1": round(ind.get("Pivot.M.Classic.S1", 0), 2), "R1": round(ind.get("Pivot.M.Classic.R1", 0), 2)
            })
        except: continue
        p_bar.progress((i + 1) / len(symbols))
    
    if data_list:
        df = pd.DataFrame(data_list)
        st.session_state.market_data = st.session_state.wahba_ai.process_and_predict(df)
        status.success("Terminal Updated Successfully.")
        p_bar.empty()

# ==========================================
# 4. العرض الرسمي (The Premium Dashboard)
# ==========================================

col1, col2 = st.columns([1, 3])
with col1:
    if st.button("RUN AI ENGINE"):
        start_scanning()

if st.session_state.market_data is not None:
    df = st.session_state.market_data
    
    # فلترة نخبة النخبة
    gold_df = df[df['Score'] >= 8].sort_values(by='Score', ascending=False)
    
    st.markdown("### 🏛️ HIGH-CONVICTION OPPORTUNITIES")
    
    for _, row in gold_df.iterrows():
        # جلب أخبار السهم
        news_data = fetch_news_clean(row['Symbol'])
        
        # بناء قائمة الأخبار بـ HTML سليم
        news_html = ""
        if news_data:
            for n in news_data:
                news_html += f'<a href="{n["link"]}" class="news-item" target="_blank">• {n["title"]}</a>'
        else:
            news_html = '<div style="color:#333; font-size:12px;">No urgent news detected for this asset.</div>'

        st.markdown(f"""
            <div class="premium-card">
                <div style="display:flex; justify-content:space-between; align-items:start;">
                    <div>
                        <div class="symbol-title">{row['Symbol']}</div>
                        <div style="color:#d4af37; font-weight:bold; margin-top:5px;">CURRENT: {row['Price']} EGP</div>
                    </div>
                    <div class="target-box">
                        <small style="color:#666; font-size:10px;">PREDICTED TARGET (AI)</small>
                        <span class="target-val">{round(row['Target'], 2)}</span>
                    </div>
                </div>
                
                <div class="news-wrapper">
                    <div style="font-size:12px; font-weight:bold; color:#444; margin-bottom:10px;">MARKET SENTIMENT & NEWS</div>
                    {news_html}
                </div>
                
                <div class="stats-grid">
                    <div class="stat-box"><span class="stat-label">Support S1</span><span class="stat-value">{row['S1']}</span></div>
                    <div class="stat-box"><span class="stat-label">Pivot P</span><span class="stat-value">{row['P']}</span></div>
                    <div class="stat-box"><span class="stat-label">Resist R1</span><span class="stat-value">{row['R1']}</span></div>
                    <div class="stat-box"><span class="stat-label">AI Score</span><span class="stat-value" style="color:#d4af37;">{row['Score']}/10</span></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<br><div style='text-align:center; color:#222; font-size:10px;'>WAHBA INTEL • INSTITUTIONAL GRADE SOLUTIONS</div>", unsafe_allow_html=True)
