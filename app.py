# ==============================================================================
# 👑 PROJECT: WAHBA EGX - THE IMPERIAL FOUNDATION (v27.0)
# 👨‍💻 ARCHITECT: MOSTAFA TAMER | ALEXANDRIA, EGYPT
# 🏛️ SYSTEM: NEURAL QUANTUM ANALYSIS & SMC TRACKING
# ==============================================================================

import streamlit as st
import pandas as pd
import sqlite3
import pytz
import requests
import plotly.express as px
from datetime import datetime
from tradingview_ta import TA_Handler, Interval

# ------------------------------------------------------------------------------
# 1. THE DATA FORTRESS
# ------------------------------------------------------------------------------
class DataFortress:
    DB_NAME = "wahba_egx_v27.db"

    @staticmethod
    def init():
        with sqlite3.connect(DataFortress.DB_NAME) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS market_data 
                         (ticker TEXT PRIMARY KEY, price REAL, target REAL, 
                          rsi REAL, signal TEXT, trend TEXT, volatility REAL, 
                          ma_state TEXT, last_update TEXT)''')
            conn.commit()

    @staticmethod
    def sync(results):
        with sqlite3.connect(DataFortress.DB_NAME) as conn:
            cairo_tz = pytz.timezone('Africa/Cairo')
            ts = datetime.now(cairo_tz).strftime("%Y-%m-%d %H:%M")
            for r in results:
                conn.execute('''INSERT OR REPLACE INTO market_data 
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                             (r['S'], r['P'], r['T'], r['R'], r['M'], r['TR'], r['V'], r['MA'], ts))
            conn.commit()

    @staticmethod
    def fetch():
        try:
            with sqlite3.connect(DataFortress.DB_NAME) as conn:
                return pd.read_sql_query("SELECT * FROM market_data ORDER BY ticker ASC", conn)
        except: return pd.DataFrame()

# ------------------------------------------------------------------------------
# 2. NEURAL INTELLIGENCE
# ------------------------------------------------------------------------------
class NeuralCore:
    @staticmethod
    def process(ind):
        p, r = ind["close"], ind["RSI"]
        volat = round(((ind["high"] - ind["low"]) / p) * 100, 2)
        target = round(p * 1.18, 2) if r < 35 else round(p * 1.08, 2)
        trend = "Bullish 📈" if p > ind["Pivot.M.Classic.Middle"] else "Bearish 📉"
        ma_state = "Above MA200" if p > ind["SMA200"] else "Below MA200"
        
        if r < 35: msg = "💎 Institutional Accumulation"
        elif r > 75: msg = "🚨 Liquidity Distribution"
        else: msg = "🔄 Balanced Market"
        
        return target, msg, trend, volat, ma_state

# ------------------------------------------------------------------------------
# 3. PREMIUM UI ENGINE
# ------------------------------------------------------------------------------
st.set_page_config(page_title="WAHBA EGX v27.0", layout="wide")

def apply_design():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
        .stApp { background-color: #030303; color: #f0f0f0; font-family: 'Cairo', sans-serif; }
        
        .hero-header {
            background: linear-gradient(135deg, #0f0f0f 0%, #000 100%);
            padding: 60px; border-radius: 40px; border: 1px solid #1a1a1a;
            border-bottom: 5px solid #D4AF37; text-align: center;
            margin-bottom: 50px; box-shadow: 0 30px 60px rgba(0,0,0,0.8);
        }
        
        .tactical-card {
            background: #0a0a0a; border: 1px solid #151515; padding: 30px;
            border-radius: 25px; border-left: 8px solid #D4AF37;
            margin-bottom: 25px; transition: 0.4s ease;
        }
        
        .legal-box {
            background: #050505; padding: 40px; border: 1px solid #111;
            margin-top: 100px; border-radius: 20px; font-size: 11px;
        }
        </style>
        <div class="hero-header">
            <h1 style="color:#D4AF37; font-size: 60px; font-weight:900; margin:0;">WAHBA <span style="color:#fff;">EGX</span></h1>
            <p style="color:#666; font-size:14px; letter-spacing: 8px; margin-top:10px;">PROPRIETARY QUANTUM TRADING TERMINAL v27.0</p>
            <div style="margin-top:20px;"><span style="background:#D4AF37; color:#000; padding:4px 12px; border-radius:5px; font-weight:900;">ALEXANDRIA QUANT NODE</span></div>
        </div>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 4. MAIN APPLICATION
# ------------------------------------------------------------------------------
def main():
    DataFortress.init()
    apply_design()
    
    with st.sidebar:
        st.markdown("<h2 style='color:#D4AF37;'>COMMAND</h2>", unsafe_allow_html=True)
        nav = st.radio("Navigation", ["🛰️ Market Overview", "🏹 SMC Scanner", "🛠️ System Authority"])
        st.divider()
        st.caption("Server: Active 🟢")

    df = DataFortress.fetch()

    if nav == "🛠️ System Authority":
        st.subheader("System Synchronization")
        key = st.text_input("Authority Key", type="password")
        if key == "WAHBA_2026":
            if st.button("RUN DEEP MARKET SCAN"):
                try:
                    res = requests.post("https://scanner.tradingview.com/egypt/scan", 
                                        json={"filter": [{"left": "type", "operation": "in_range", "right": ["stock"]}], "markets": ["egypt"], "columns": ["name"]}, timeout=10).json()
                    symbols = [item['s'].split(':')[1] for item in res['data']]
                    
                    all_data = []
                    p_bar = st.progress(0)
                    for i, s in enumerate(symbols):
                        try:
                            h = TA_Handler(symbol=s, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY)
                            ind = h.get_analysis().indicators
                            target, msg, trend, volat, ma = NeuralCore.process(ind)
                            all_data.append({'S': s, 'P': ind["close"], 'T': target, 'R': round(ind["RSI"], 1), 
                                            'M': msg, 'TR': trend, 'V': volat, 'MA': ma})
                        except: continue
                        p_bar.progress((i+1)/len(symbols))
                    
                    DataFortress.sync(all_data)
                    st.success("Global Node Synchronized.")
                    st.balloons()
                except: st.error("Connection Failure.")

    elif nav == "🛰️ Market Overview":
        if not df.empty:
            col1, col2, col3 = st.columns(3)
            col1.metric("Assets Analyzed", len(df))
            col2.metric("Bullish Trend", len(df[df['trend'].str.contains('Bullish')]))
            col3.metric("Avg Volatility", f"{df['volatility'].mean():.2f}%")
            
            st.divider()
            fig = px.bar(df.head(20), x='ticker', y=['price', 'target'], barmode='group', 
                         color_discrete_sequence=['#333', '#D4AF37'], template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("System offline. Admin sync required.")

    elif nav == "🏹 SMC Scanner":
        st.subheader("Institutional Footprint Analysis")
        setups = df[df['signal'].str.contains('Accumulation')]
        if not setups.empty:
            for _, row in setups.iterrows():
                st.markdown(f"""
                    <div class="tactical-card">
                        <h2 style="color:#D4AF37; margin:0;">{row['ticker']}</h2>
                        <p style="color:#777;">{row['signal']} | {row['ma_state']}</p>
                        <div style="display:flex; gap:50px; margin-top:20px;">
                            <div><small>PRICE</small><br><b style="font-size:24px;">{row['price']}</b></div>
                            <div><small style="color:#00ff87;">TARGET</small><br><b style="font-size:24px; color:#00ff87;">{row['target']}</b></div>
                            <div><small>RSI</small><br><b style="font-size:24px;">{row['rsi']}</b></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    # --- LEGAL DISCLAIMER ---
    st.markdown("""
        <div class="legal-box">
            <h4 style="color:#D4AF37;">LEGAL NOTICE & DISCLAIMER</h4>
            This terminal and its neural algorithms are the property of Mostafa Tamer Ahmed El-Sayed. 
            Information provided is for analytical purposes only. Trading involves risk. 
            Verify all data through official EGX sources.
            <hr style="border:0.5px solid #111; margin:20px 0;">
            <center>© 2026 WAHBA QUANTUM LABS | ALEXANDRIA, EGYPT | ALL RIGHTS RESERVED</center>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
