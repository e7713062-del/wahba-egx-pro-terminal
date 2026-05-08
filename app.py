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

# --- 1. CONFIG ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)

# --- 2. AI BRAIN ---
class WahbaAI:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()

    def process(self, df):
        if len(df) < 2: return df
        X = df[['Price', 'Score', 'RSI']].values
        y = df['Price'] * (1 + (df['Score'] / 100))
        self.scaler.fit(X)
        self.model.fit(self.scaler.transform(X), y)
        df['Target'] = self.model.predict(self.scaler.transform(X))
        return df

if 'ai' not in st.session_state:
    st.session_state.ai = WahbaAI()
if 'market_results' not in st.session_state:
    st.session_state.market_results = None

# --- 3. UI STYLE ---
st.set_page_config(page_title="WAHBA EGX ULTRA", layout="wide")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background-color: #000; color: #fff; }
    .gold-card { background: #0a0a0a; border: 2px solid #d4af37; border-radius: 20px; padding: 25px; margin-bottom: 20px; }
    .silver-card { background: #0a0a0a; border: 1px solid #444; border-radius: 20px; padding: 20px; margin-bottom: 15px; }
    .price-text { color: #d4af37; font-weight: bold; font-size: 20px; }
    </style>
""", unsafe_allow_html=True)

st.title("WAHBA EGX | MARKETING TERMINAL")

# --- 4. SAFE SCANNER ---
@st.cache_data(ttl=3600)
def fetch_symbols():
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter":[], "markets":["egypt"], "columns":["name"]}).json()
        return [item['s'].split(':')[1] for item in res['data']]
    except: return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK"]

if st.button('🚀 إطلاق المسح الموحد (Anti-Block Scan)'):
    symbols = fetch_symbols()
    temp_data = []
    p_bar = st.progress(0)
    status = st.empty()
    
    for i, sym in enumerate(symbols):
        try:
            status.text(f"فحص آمن لـ: {sym}...")
            # حماية المنصة من الحظر: انتظار بسيط
            if i % 5 == 0: time.sleep(0.5) 
            
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY)
            analysis = handler.get_analysis()
            
            # حساب سكور النخبة
            score = 0
            rec = analysis.summary["RECOMMENDATION"]
            if "STRONG_BUY" in rec: score += 6
            elif "BUY" in rec: score += 3
            if 40 < analysis.indicators["RSI"] < 65: score += 4
            
            temp_data.append({
                "Symbol": sym, "Price": analysis.indicators["close"], 
                "Score": score, "RSI": analysis.indicators["RSI"]
            })
        except: continue
        p_bar.progress((i + 1) / len(symbols))
    
    if temp_data:
        df = pd.DataFrame(temp_data)
        df = st.session_state.ai.process(df)
        st.session_state.market_results = df
        status.success("تم تحديث البيانات بنجاح!")
    else:
        status.error("لم يتم العثور على بيانات، تأكد من الاتصال بالإنترنت.")

# --- 5. DISPLAY (نخبة النخبة والنخبة) ---
if st.session_state.market_results is not None:
    df = st.session_state.market_results
    
    # قسم نخبة النخبة (سكور 9 فأكثر)
    gold = df[df['Score'] >= 9].sort_values(by='Score', ascending=False)
    if not gold.empty:
        st.markdown("### 🏆 نخبة النخبة (Gold Tier)")
        for _, row in gold.iterrows():
            st.markdown(f"""
            <div class="gold-card">
                <div style="display:flex; justify-content:space-between;">
                    <span style="font-size:30px; font-weight:900;">{row['Symbol']}</span>
                    <span class="price-text">الهدف: {round(row['Target'], 2)}</span>
                </div>
                <div style="color:#888;">السعر الحالي: {row['Price']} EGP</div>
            </div>""", unsafe_allow_html=True)

    # قسم النخبة (سكور 7-8)
    silver = df[(df['Score'] >= 7) & (df['Score'] < 9)]
    if not silver.empty:
        st.markdown("### 🥈 النخبة (Silver Tier)")
        cols = st.columns(2)
        for idx, row in enumerate(silver.reset_index().iterrows()):
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="silver-card">
                    <div style="font-size:22px; font-weight:bold;">{row[1]['Symbol']}</div>
                    <div style="color:#d4af37;">الهدف المتوقع: {round(row[1]['Target'], 2)}</div>
                </div>""", unsafe_allow_html=True)

# --- 6. LEGAL ---
st.markdown(f"""
    <div style="margin-top:50px; padding:20px; border:1px solid red; border-radius:10px; text-align:center;">
        <small>تطوير: مصطفى تامر أحمد السيد - إخلاء مسؤولية: التداول مخاطرة وأنت المسؤول.</small>
    </div>
""", unsafe_allow_html=True)
