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

# --- إعدادات الوقت ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)

# --- كلاس الـ AI ---
class WahbaAI:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
    def predict(self, df):
        if len(df) < 3: 
            df['Target'] = df['Price'] * 1.05
            return df
        X = df[['Price', 'Score', 'RSI', 'P']].values
        y = df['Price'] * (1 + (df['Score'] / 100))
        self.scaler.fit(X)
        df['Target'] = self.model.fit(self.scaler.transform(X), y).predict(self.scaler.transform(X))
        return df

if 'ai' not in st.session_state: st.session_state.ai = WahbaAI()
if 'results' not in st.session_state: st.session_state.results = None

# --- التصميم الفورمال (تم الإصلاح لضمان الرندر) ---
st.set_page_config(page_title="WAHBA INTEL", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif; }
    .stApp { background-color: #050505; color: #fff; }
    
    .card {
        background: #0d0d0d; border: 1px solid #1a1a1a;
        border-right: 5px solid #d4af37; border-radius: 10px;
        padding: 25px; margin-bottom: 20px;
    }
    .symbol { font-size: 28px; font-weight: 900; color: #fff; }
    .target-box { background: rgba(212, 175, 55, 0.1); padding: 10px; border-radius: 5px; text-align: center; }
    .target-val { font-size: 24px; font-weight: 900; color: #d4af37; display: block; }
    
    .news-tag { background: #111; padding: 10px; border-radius: 5px; margin: 15px 0; border: 1px solid #222; }
    .news-link { color: #888; text-decoration: none; display: block; font-size: 13px; padding: 5px 0; border-bottom: 1px solid #1a1a1a; }
    
    .grid { display: flex; justify-content: space-between; margin-top: 15px; background: #000; padding: 10px; border-radius: 5px; }
    .unit { text-align: center; flex: 1; }
    .lbl { font-size: 10px; color: #444; display: block; }
    .val { font-size: 13px; font-weight: bold; color: #fff; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:#d4af37;'>WAHBA <span style='color:#fff;'>INTELLIGENCE</span></h1>", unsafe_allow_html=True)

# --- سحب البيانات ---
@st.cache_data(ttl=3600)
def get_news(sym):
    try:
        r = requests.get(f"https://news.google.com/rss/search?q=سهم+{sym}+البورصة+المصرية&hl=ar&gl=EG&ceid=EG:ar", timeout=5)
        root = ET.fromstring(r.content)
        return [{"t": i.find('title').text, "l": i.find('link').text} for i in root.findall('.//item')[:2]]
    except: return []

if st.button("🚀 تحديث رادار AI اللحظي"):
    with st.spinner("حل بيانات السوق..."):
        try:
            url = "https://scanner.tradingview.com/egypt/scan"
            payload = {"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}
            symbols = [item['s'].split(':')[1] for item in requests.post(url, json=payload).json()['data'] if not item['s'].split(':')[1].isdigit()]
            
            temp = []
            for i, s in enumerate(symbols[:20]): # اختصار للتجربة
                try:
                    handler = TA_Handler(symbol=s, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY)
                    ind = handler.get_analysis().indicators
                    score = 7 if "BUY" in handler.get_analysis().summary["RECOMMENDATION"] else 4
                    temp.append({
                        "Symbol": s, "Price": round(ind['close'], 2), "Score": score,
                        "RSI": round(ind['RSI'], 2), "P": round(ind['Pivot.M.Classic.Middle'], 2),
                        "S1": round(ind['Pivot.M.Classic.S1'], 2), "R1": round(ind['Pivot.M.Classic.R1'], 2)
                    })
                except: continue
            
            df = pd.DataFrame(temp)
            st.session_state.results = st.session_state.ai.predict(df)
        except Exception as e: st.error(f"Error: {e}")

# --- العرض الرسمي المصحح ---
if st.session_state.results is not None:
    for _, row in st.session_state.results.sort_values(by='Score', ascending=False).iterrows():
        news = get_news(row['Symbol'])
        news_html = "".join([f'<a href="{n["l"]}" class="news-link" target="_blank">• {n["t"]}</a>' for n in news]) if news else "لا يوجد أخبار حالياً."
        
        # استخدام f-string واحدة نظيفة لكل كارت
        card_html = f"""
        <div class="card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div class="symbol">{row['Symbol']}</div>
                    <div style="color:#d4af37; font-weight:bold;">{row['Price']} EGP</div>
                </div>
                <div class="target-box">
                    <span style="font-size:10px; color:#555;">AI TARGET</span>
                    <span class="target-val">{round(row['Target'], 2)}</span>
                </div>
            </div>
            <div class="news-tag">
                <div style="font-size:11px; color:#d4af37; margin-bottom:5px; font-weight:bold;">نبض السوق:</div>
                {news_html}
            </div>
            <div class="grid">
                <div class="unit"><span class="lbl">S1</span><span class="val">{row['S1']}</span></div>
                <div class="unit"><span class="lbl">PIVOT</span><span class="val">{row['P']}</span></div>
                <div class="unit"><span class="lbl">R1</span><span class="val">{row['R1']}</span></div>
                <div class="unit"><span class="lbl">SCORE</span><span class="val" style="color:#d4af37;">{row['Score']}/10</span></div>
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
