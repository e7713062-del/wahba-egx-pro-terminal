import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import sqlite3
import requests
from datetime import datetime
import time

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
        try:
            with sqlite3.connect("wahba_ultra_brain.db") as conn:
                df = pd.read_sql_query("SELECT * FROM market_memory", conn)
            if len(df) > 5: # تقليل الحد الأدنى للتعلم ليبدأ أسرع
                X = df[['price', 'vol_eff', 'rsi']]
                y = df['target_hit']
                self.model.fit(X, y)
                self.is_trained = True
        except:
            pass

# ==========================================
# 2. DATA ENGINES
# ==========================================
def fetch_data():
    try:
        handler = TA_Handler(
            symbol="BTCUSDT", exchange="BINANCE", screener="crypto",
            interval=Interval.INTERVAL_15_MINUTES, timeout=15
        )
        return handler.get_analysis().indicators
    except Exception as e:
        return None

def get_news():
    try:
        url = "https://min-api.cryptocompare.com/data/v2/news/?lang=EN"
        return requests.get(url).json()['Data'][:4]
    except:
        return []

# ==========================================
# 3. INTERFACE DESIGN
# ==========================================
st.set_page_config(page_title="WAHBA AI ULTRA", layout="wide", page_icon="🦅")

# CSS لإعطاء مظهر التطبيقات الاحترافية
st.markdown("""
<style>
    .stApp { background: #050505; color: white; }
    .main-card { 
        background: #0d0d0d; 
        border: 1px solid #1f1f1f; 
        padding: 30px; 
        border-radius: 20px; 
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }
    .metric-box {
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        font-weight: bold;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .target-box { background-color: rgba(0, 255, 128, 0.1); border: 1px solid #00ff80; color: #00ff80; }
    .stop-box { background-color: rgba(255, 49, 49, 0.1); border: 1px solid #ff3131; color: #ff3131; }
    .news-card { 
        background: #111; 
        padding: 12px; 
        border-radius: 8px; 
        margin-bottom: 8px; 
        border-left: 4px solid #D4AF37;
        transition: 0.3s;
    }
    .news-card:hover { background: #1a1a1a; }
</style>
""", unsafe_allow_html=True)

def main():
    init_db()
    brain = WahbaBrain()
    brain.train()

    # Title
    st.markdown("<h1 style='text-align:center; color:#D4AF37; font-size: 2.2rem;'>🦅 WAHBA MASTER AI <span style='font-size:0.8rem; color:gray;'>v17 ULTRA</span></h1>", unsafe_allow_html=True)
    
    # Auto-Refresh Logic (Refresh every 60 seconds)
    # st.empty() يستخدم لتحديث البيانات في مكانها
    placeholder = st.empty()

    while True:
        ind = fetch_data()
        news = get_news()
        
        with placeholder.container():
            if ind:
                price = ind.get("close", 0)
                vol = ind.get("volume", 0)
                rsi = ind.get("RSI", 50)
                p_vol = ind.get("volume.1", vol)
                vol_eff = round((vol/p_vol)*100, 1) if p_vol != 0 else 100
                
                # SMC Logic
                is_swing = ind.get("high", 0) > ind.get("high.1", 0) and price < ind.get("high.1", 0)
                status = "⚖️ STRUCTURE STABLE"
                color = "#D4AF37"
                
                if is_swing:
                    status = "🚨 LIQUIDITY SWEEP (SELL)"
                    color = "#FF3131"
                elif ind.get("low", 0) < ind.get("low.1", 0) and price > ind.get("low.1", 0):
                    status = "🔥 LIQUIDITY SWING (BUY)"
                    color = "#00FFCC"

                # AI Prediction
                ai_pred = "COLLECTING DATA..."
                ai_color = "#888"
                if brain.is_trained:
                    pred = brain.model.predict([[price, vol_eff, rsi]])[0]
                    ai_pred = "HIGH PROBABILITY UP" if pred == 1 else "CAUTION: DOWNWARD TREND"
                    ai_color = "#00FFCC" if pred == 1 else "#FF3131"

                # UI Layout
                col1, col2 = st.columns([1.5, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="main-card" style="border-top: 5px solid {color};">
                        <h2 style="color: {color}; margin-bottom:0;">{status}</h2>
                        <p style="color: gray; font-size: 0.9rem;">AI PREDICTION: <span style="color:{ai_color};">{ai_pred}</span></p>
                        <h1 style="font-size: 3.5rem; margin: 20px 0;">BTC: ${price:,.2f}</h1>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Target & Stop Loss Buttons (Styled)
                    target_val = ind.get('Pivot.M.Classic.R1', price * 1.01)
                    stop_val = ind.get('Pivot.M.Classic.S1', price * 0.99)
                    
                    st.markdown(f"""
                    <div class="metric-box target-box">
                        <span>🎯 TARGET (SMC)</span>
                        <span>${target_val:,.2f}</span>
                    </div>
                    <div class="metric-box stop-box">
                        <span>🛑 STOP LOSS</span>
                        <span>${stop_val:,.2f}</span>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown("### 📰 SMART NEWS FEED")
                    for n in news:
                        st.markdown(f"""<div class="news-card"><a href="{n['url']}" target="_blank" style="color:white; text-decoration:none; font-size:0.85rem;">{n['title']}</a></div>""", unsafe_allow_html=True)
                    
                    st.divider()
                    st.markdown("### 🧠 AI TEACHING")
                    t_col1, t_col2 = st.columns(2)
                    if t_col1.button("✅ Hit Target"):
                        with sqlite3.connect("wahba_ultra_brain.db") as conn:
                            conn.execute("INSERT INTO market_memory VALUES (?,?,?,?,?)", (datetime.now(), price, vol_eff, rsi, 1))
                        st.success("Learned: Success!")
                    
                    if t_col2.button("❌ Hit Stoploss"):
                        with sqlite3.connect("wahba_ultra_brain.db") as conn:
                            conn.execute("INSERT INTO market_memory VALUES (?,?,?,?,?)", (datetime.now(), price, vol_eff, rsi, 0))
                        st.error("Learned: Failure")

            else:
                st.warning("🔄 Connecting to Binance/TradingView Streams...")
        
        time.sleep(60) # تحديث كل دقيقة
        st.rerun()

if __name__ == "__main__":
    main()
