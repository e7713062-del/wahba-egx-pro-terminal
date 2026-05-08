import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
from datetime import datetime
import pytz
import sqlite3
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# --- 1. CONFIGURATION & TIME ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)
today_date = now_egypt.strftime("%Y-%m-%d")

# --- 2. THE VAULT (نظام حفظ أعلى الإغلاقات اليومية) ---
class WahbaVault:
    @staticmethod
    def init_db():
        with sqlite3.connect("wahba_ultra_vault.db") as conn:
            # جدول لحفظ أعلى سعر إغلاق تم رصده لكل سهم على الإطلاق
            conn.execute('''CREATE TABLE IF NOT EXISTS high_closes 
                         (Symbol TEXT PRIMARY KEY, HighPrice REAL, Date TEXT)''')
            conn.commit()

    @staticmethod
    def update_high_closes(symbol, current_price):
        with sqlite3.connect("wahba_ultra_vault.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT HighPrice FROM high_closes WHERE Symbol=?", (symbol,))
            row = cursor.fetchone()
            
            if row is None:
                # لو السهم مش موجود، ضيفه كأعلى سعر حالي
                cursor.execute("INSERT INTO high_closes VALUES (?, ?, ?)", (symbol, current_price, today_date))
            else:
                # لو السعر الحالي أعلى من المتخزن، حدث البيانات
                if current_price > row[0]:
                    cursor.execute("UPDATE high_closes SET HighPrice=?, Date=? WHERE Symbol=?", 
                                 (current_price, today_date, symbol))
            conn.commit()

    @staticmethod
    def get_all_highs():
        with sqlite3.connect("wahba_ultra_vault.db") as conn:
            return pd.read_sql_query("SELECT * FROM high_closes ORDER BY HighPrice DESC", conn)

# --- 3. AI COMPLETE MODEL ---
class WahbaAIComplete:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=150, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False

    def train(self, df):
        if len(df) < 3: return
        X = df[['Price', 'Score', 'RSI']].values
        y = df['Price'].values * (1 + (df['Score'].values / 115))
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True

    def predict(self, price, score, rsi):
        if not self.is_trained: return round(price * (1 + (score/100)), 2)
        X_scaled = self.scaler.transform([[price, score, rsi]])
        return round(self.model.predict(X_scaled)[0], 2)

if 'ai_engine' not in st.session_state:
    st.session_state['ai_engine'] = WahbaAIComplete()

# --- 4. UI/UX DESIGN ---
st.set_page_config(page_title="WAHBA EGX ULTRA | Vault", layout="wide")
WahbaVault.init_db()

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * {{ font-family: 'Tajawal', sans-serif; }}
    .stApp {{ background-color: #000000; color: #ffffff; }}
    .nav-bar {{ text-align: center; padding: 40px; border-bottom: 3px solid #d4af37; background: #050505; margin-bottom: 40px; }}
    .logo {{ font-size: 50px; font-weight: 900; letter-spacing: 8px; }}
    .logo span {{ color: #d4af37; }}
    .elite-card {{ background: #0a0a0a; border: 1px solid #d4af37; border-radius: 25px; padding: 35px; margin-bottom: 25px; border-right: 8px solid #d4af37; }}
    .vault-table {{ background: #111; border-radius: 15px; padding: 20px; border: 1px solid #222; margin-top: 20px; }}
    </style>
    <div class="nav-bar">
        <div class="logo">WAHBA <span>EGX</span> ULTRA</div>
        <div style="color:#444; font-size:12px; letter-spacing:5px;">PREMIUM DATA ARCHIVE | {today_date}</div>
    </div>
""", unsafe_allow_html=True)

# --- 5. CORE LOGIC ---
@st.cache_data(ttl=3600)
def get_symbols():
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter":[], "markets":["egypt"], "columns":["name"]}).json()
        return [item['s'].split(':')[1] for item in res['data']]
    except: return ["COMI", "FWRY", "TMGH"]

if st.button('إطلاق المسح وتحديث الأرشيف التاريخي (SYNC VAULT)'):
    symbols = get_symbols()
    raw_results = []
    p_bar = st.progress(0)
    
    for i, sym in enumerate(symbols):
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY)
            analysis = handler.get_analysis()
            price = analysis.indicators["close"]
            
            # تحديث قاعدة البيانات بأعلى إغلاق
            WahbaVault.update_high_closes(sym, price)
            
            score = 5 if "BUY" in analysis.summary["RECOMMENDATION"] else 2
            if analysis.indicators["RSI"] < 70: score += 3
            
            raw_results.append({"Symbol": sym, "Price": price, "Score": score, "RSI": analysis.indicators["RSI"]})
        except: continue
        p_bar.progress((i + 1) / len(symbols))
    
    df = pd.DataFrame(raw_results)
    st.session_state.ai_engine.train(df)
    df['Target'] = df.apply(lambda x: st.session_state.ai_engine.predict(x['Price'], x['Score'], x['RSI']), axis=1)
    st.session_state['current_scan'] = df
    st.success("Vault Updated & AI Re-Trained!")

# --- 6. DISPLAY ---
tab1, tab2 = st.tabs(["Elite Selections", "Historical High-Closes"])

with tab1:
    if 'current_scan' in st.session_state:
        elite = st.session_state['current_scan'][st.session_state['current_scan']['Score'] >= 7]
        for _, row in elite.iterrows():
            st.markdown(f"""
            <div class="elite-card">
                <div style="display:flex; justify-content:space-between;">
                    <span style="font-size:30px; font-weight:900; color:#d4af37;">{row['Symbol']}</span>
                    <span style="font-size:24px; font-weight:bold;">{row['Price']} EGP</span>
                </div>
                <div style="color:#00ff00; margin-top:10px; font-weight:bold;">AI Target: {row['Target']}</div>
            </div>""", unsafe_allow_html=True)

with tab2:
    st.markdown("### سجل أعلى الإغلاقات التاريخية")
    highs_df = WahbaVault.get_all_highs()
    if not highs_df.empty:
        st.dataframe(highs_df, use_container_width=True)

# --- 7. LEGAL PROTECTION ---
st.markdown(f"""
    <div style="margin-top:100px; padding:40px; background:#110000; border:2px solid #ff0000; border-radius:20px;">
        <div style="color:#ff0000; font-size:22px; font-weight:900; text-align:center; margin-bottom:15px;">⚠️ إخلاء مسؤولية قانونية</div>
        <div style="color:#ccc; text-align:justify; direction:rtl; line-height:1.8;">
            هذه المنصة ملكية فكرية حصرية لـ <b>مصطفى تامر أحمد السيد</b>. 
            يتم أرشفة البيانات لأغراض إحصائية فقط. <b>المطور غير مسؤول عن أي خسائر مالية</b>. 
            التداول مسؤوليتك الشخصية بالكامل.
        </div>
    </div>
""", unsafe_allow_html=True)
