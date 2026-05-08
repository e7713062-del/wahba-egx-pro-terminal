import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import sqlite3
import requests
from datetime import datetime

# ==========================================
# 1. DATABASE & AI BRAIN SETUP
# ==========================================
def init_db():
    with sqlite3.connect("wahba_ultra_brain.db") as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS market_memory 
                     (timestamp TEXT, price REAL, vol_eff REAL, rsi REAL, target_hit INTEGER)''')

class WahbaBrain:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100)
        self.is_trained = False

    def train(self):
        with sqlite3.connect("wahba_ultra_brain.db") as conn:
            df = pd.read_sql_query("SELECT * FROM market_memory", conn)
        if len(df) > 10: # يبدأ التعلم بعد أول 10 عمليات مسح
            X = df[['price', 'vol_eff', 'rsi']]
            y = df['target_hit']
            self.model.fit(X, y)
            self.is_trained = True

# ==========================================
# 2. CORE ENGINES (SMC, LIQUIDITY, DATA)
# ==========================================
def fetch_data():
    try:
        handler = TA_Handler(
            symbol="BTCUSDT", exchange="BINANCE", screener="crypto",
            interval=Interval.INTERVAL_15_MINUTES, timeout=15
        )
        return handler.get_analysis().indicators
    except: return None

def get_news():
    try:
        url = "https://min-api.cryptocompare.com/data/v2/news/?lang=EN"
        return requests.get(url).json()['Data'][:3]
    except: return []

# ==========================================
# 3. THE MASTER INTERFACE
# ==========================================
st.set_page_config(page_title="WAHBA AI ULTRA", layout="wide")
init_db()
brain = WahbaBrain()

st.markdown("""
<style>
    .stApp { background: #050505; color: white; font-family: 'Inter'; }
    .card { background: #0a0a0a; border: 1px solid #1a1a1a; padding: 20px; border-radius: 15px; border-top: 4px solid #D4AF37; }
    .news-card { background: #111; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-right: 3px solid #D4AF37; }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🦅 WAHBA MASTER AI: v17 ULTRA</h1>", unsafe_allow_html=True)
    st.divider()

    if st.button("🚀 EXECUTE FULL AI SCAN", use_container_width=True):
        ind = fetch_data()
        news = get_news()
        brain.train() # تحديث ذكاء البرنامج

        if ind:
            # Safe Data Extraction (Anti-KeyError)
            price = ind.get("close", 0)
            vol = ind.get("volume", 0)
            rsi = ind.get("RSI", 50)
            p_vol = ind.get("volume.1", vol)
            vol_eff = round((vol/p_vol)*100, 1) if p_vol != 0 else 100
            
            # SMC & Liquidity Logic
            is_swing = ind.get("high", 0) > ind.get("high.1", 0) and price < ind.get("high.1", 0)
            status = "🚨 LIQUIDITY SWEEP (SELL)" if is_swing else "⚖️ STRUCTURE STABLE"
            color = "#FF3131" if is_swing else "#D4AF37"
            if ind.get("low", 0) < ind.get("low.1", 0) and price > ind.get("low.1", 0):
                status = "🔥 LIQUIDITY SWING (BUY)"
                color = "#00FFCC"

            # AI Prediction
            ai_pred = "COLLECTING DATA..."
            if brain.is_trained:
                pred = brain.model.predict([[price, vol_eff, rsi]])[0]
                ai_pred = "HIGH PROBABILITY UP" if pred == 1 else "CAUTION: DOWNWARD TREND"

            # UI Display
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"""
                <div class="card" style="border-color:{color}; text-align:center;">
                    <h3 style="color:gray;">AI LIQUIDITY STATUS</h3>
                    <h1 style="color:{color}; font-size:2.5rem;">{status}</h1>
                    <hr style="opacity:0.1">
                    <p>AI PREDICTION: <b style="color:#D4AF37;">{ai_pred}</b></p>
                    <h2 style="color:white;">BTC: ${price:,.2f}</h2>
                </div>
                """, unsafe_allow_html=True)
                
                st.write("")
                c_tp, c_sl = st.columns(2)
                c_tp.success(f"🎯 TARGET (SMC): ${ind.get('Pivot.M.Classic.R1', 0):,.2f}")
                c_sl.error(f"🛑 STOP LOSS: ${ind.get('Pivot.M.Classic.S1', 0):,.2f}")

            with col2:
                st.markdown("### 📰 SMART NEWS FEED")
                for n in news:
                    st.markdown(f"""<div class="news-card"><a href="{n['url']}" style="color:white; text-decoration:none; font-size:0.8rem;">{n['title']}</a></div>""", unsafe_allow_html=True)
                
                # Manual Training Feed
                st.write("---")
                if st.button("✅ Hit Target (Teach AI)"):
                    with sqlite3.connect("wahba_ultra_brain.db") as conn:
                        conn.execute("INSERT INTO market_memory VALUES (?,?,?,?,?)", 
                                    (datetime.now(), price, vol_eff, rsi, 1))
                    st.success("AI Learned: Pattern was Successful!")

if __name__ == "__main__":
    main()
