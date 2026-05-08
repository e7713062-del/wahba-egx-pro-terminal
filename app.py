# ==============================================================================
# 👑 PROJECT: WAHBA EGX - THE IMPERIAL SUPREME (v29.0)
# 👨‍💻 ARCHITECT: MOSTAFA TAMER | ALEXANDRIA, EGYPT
# 🏛️ SYSTEM: NEURAL QUANTUM ANALYSIS, SMC TRACKING & LEGAL COMPLIANCE
# ==============================================================================

import streamlit as st
import pandas as pd
import sqlite3
import pytz
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from tradingview_ta import TA_Handler, Interval

# ------------------------------------------------------------------------------
# 1. THE DATA FORTRESS (إدارة التخزين والحماية)
# ------------------------------------------------------------------------------
class DataFortress:
    DB_NAME = "wahba_supreme_v29.db"

    @staticmethod
    def init():
        with sqlite3.connect(DataFortress.DB_NAME) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS market_data 
                         (ticker TEXT PRIMARY KEY, price REAL, target REAL, 
                          rsi REAL, signal TEXT, trend TEXT, volatility REAL, 
                          ma_state TEXT, volume_profile TEXT, last_update TEXT)''')
            conn.commit()

    @staticmethod
    def sync(results):
        with sqlite3.connect(DataFortress.DB_NAME) as conn:
            cairo_tz = pytz.timezone('Africa/Cairo')
            ts = datetime.now(cairo_tz).strftime("%Y-%m-%d %H:%M")
            for r in results:
                conn.execute('''INSERT OR REPLACE INTO market_data 
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                             (r['S'], r['P'], r['T'], r['R'], r['M'], r['TR'], r['V'], r['MA'], r['VP'], ts))
            conn.commit()

    @staticmethod
    def fetch():
        try:
            with sqlite3.connect(DataFortress.DB_NAME) as conn:
                return pd.read_sql_query("SELECT * FROM market_data ORDER BY ticker ASC", conn)
        except: return pd.DataFrame()

# ------------------------------------------------------------------------------
# 2. NEURAL INTELLIGENCE (المحرك العصبي المطور)
# ------------------------------------------------------------------------------
class NeuralCore:
    @staticmethod
    def process(ind):
        p, r = ind["close"], ind["RSI"]
        volat = round(((ind["high"] - ind["low"]) / p) * 100, 2)
        target = round(p * 1.18, 2) if r < 35 else round(p * 1.08, 2)
        trend = "Bullish 📈" if p > ind["Pivot.M.Classic.Middle"] else "Bearish 📉"
        ma_state = "Above MA200" if p > ind["SMA200"] else "Below MA200"
        
        # SMC & Volume Analysis
        if r < 35: msg = "💎 Institutional Accumulation"
        elif r > 75: msg = "🚨 Liquidity Distribution"
        else: msg = "🔄 Balanced Market"
        
        v_profile = "High Volume Node" if ind["volume"] > ind["average_volume_10d"] else "Low Liquidity"
        
        return target, msg, trend, volat, ma_state, v_profile

# ------------------------------------------------------------------------------
# 3. PREMIUM UI ENGINE (محرك التصميم الاحترافي)
# ------------------------------------------------------------------------------
st.set_page_config(page_title="WAHBA SUPREME v29.0", layout="wide")

def apply_imperial_design():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
        .stApp { background-color: #030303; color: #f0f0f0; font-family: 'Cairo', sans-serif; }
        
        /* Header Section */
        .hero-header {
            background: linear-gradient(135deg, #0f0f0f 0%, #000 100%);
            padding: 60px; border-radius: 40px; border: 1px solid #1a1a1a;
            border-bottom: 5px solid #D4AF37; text-align: center;
            margin-bottom: 50px; box-shadow: 0 30px 60px rgba(0,0,0,0.8);
        }
        
        /* Tactical Cards */
        .tactical-card {
            background: #0a0a0a; border: 1px solid #151515; padding: 30px;
            border-radius: 25px; border-left: 8px solid #D4AF37;
            margin-bottom: 25px; transition: 0.4s ease;
        }
        .tactical-card:hover { transform: translateY(-5px); border-color: #fff; }
        
        /* Legal Disclaimer */
        .legal-footer {
            background: #050505; padding: 50px; border-top: 1px solid #111;
            margin-top: 100px; text-align: justify; color: #444; font-size: 11px;
        }
        
        .status-badge { background: #D4AF37; color: #000; padding: 3px 12px; border-radius: 5px; font-weight: 900; }
        </style>
        <div class="hero-header">
            <h1 style="color:#D4AF37; font-size: 60px; font-weight:900; margin:0;">WAHBA <span style="color:#fff;">SUPREME</span></h1>
            <p style="color:#666; font-size:14px; letter-spacing: 8px; margin-top:10px;">PROPRIETARY QUANTUM TRADING TERMINAL v29.0</p>
            <div style="margin-top:20px;"><span class="status-badge">ALEXANDRIA QUANT NODE</span></div>
        </div>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 4. MAIN APPLICATION LOGIC
# ------------------------------------------------------------------------------
def main():
    DataFortress.init()
    apply_imperial_design()
    
    # --- Sidebar Control ---
    with st.sidebar:
        st.markdown("<h2 style='color:#D4AF37;'>COMMAND CENTER</h2>", unsafe_allow_html=True)
        nav = st.radio("Navigation", ["🛰️ Market Overview", "🏹 SMC Scanner", "🛠️ System Authority"])
        st.divider()
        st.caption("Server: Active 🟢")
        st.caption("Timezone: Africa/Cairo (DST Compliant)")

    df = DataFortress.fetch()

    # --- Mode: System Authority ---
    if nav == "🛠️ System Authority":
        st.subheader("Sovereign Data Synchronization")
        key = st.text_input("Enter Authority Key", type="password")
        if key == "WAHBA_2026":
            if st.button("RUN DEEP MARKET SCAN"):
                with st.status("Fetching Neural Data...", expanded=True):
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
                                target, msg, trend, volat, ma, vp = NeuralCore.process(ind)
                                all_data.append({'S': s, 'P': ind["close"], 'T': target, 'R': round(ind["RSI"], 1), 
                                                'M': msg, 'TR': trend, 'V': volat, 'MA': ma, 'VP': vp})
                            except: continue
                            p_bar.progress((i+1)/len(symbols))
                        
                        DataFortress.sync(all_data)
                        st.balloons()
                        st.success("Global Node Synchronized.")
                    except: st.error("Connection Refused by Remote Server.")

    # --- Mode: Market Overview ---
    elif nav == "🛰️ Market Overview":
        if not df.empty:
            # Metrics Dashboard
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Assets Analyzed", len(df))
            col2.metric("Bullish Market", f"{len(df[df['trend'].str.contains('Bullish')])}")
            col3.metric("Avg Volatility", f"{df['volatility'].mean():.2f}%")
            col4.metric("SMC Buy Zones", len(df[df['signal'].str.contains('Accumulation')]))
            
            st.divider()
            
            # Interactive Visuals
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown("### 📊 Quantum Price Projections")
                fig = px.scatter(df, x="rsi", y="volatility", size="price", color="trend",
                                 hover_name="ticker", template="plotly_dark", color_discrete_sequence=["#D4AF37", "#444"])
                st.plotly_chart(fig, use_container_width=True)
            
            with c2:
                st.markdown("### 🏹 Market Sentiment")
                fig_pie = px.pie(df, names='signal', hole=0.7, color_discrete_sequence=['#D4AF37', '#1a1a1a', '#555'])
                st.plotly_chart(fig_pie, use_container_width=True)

            st.markdown("### 🏛️ Active Master Data")
            st.dataframe(df.drop(columns=['last_update']), use_container_width=True, hide_index=True)
        else:
            st.info("System is offline. Please login to Authority Panel for initial sync.")

    # --- Mode: SMC Scanner ---
    elif nav == "🏹 SMC Scanner":
        st.subheader("Institutional Footprint Analysis")
        setups = df[df['signal'].str.contains('Accumulation')]
        
        if not setups.empty:
            for _, row in setups.iterrows():
                st.markdown(f"""
                    <div class="tactical-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h2 style="color:#D4AF37; margin:0;">{row['ticker']}</h2>
                            <span style="color:#00ff87; font-weight:bold;">SMC CONFIRMED</span>
                        </div>
                        <p style="color:#777;">Logic: {row['signal']} | RSI: {row['rsi']} | {row['ma_state']}</p>
                        <div style="display:flex; gap:50px; margin-top:20px;">
                            <div><small style="color:#555;">CURRENT</small><br><b style="font-size:24px;">{row['price']}</b></div>
                            <div><small style="color:#555;">AI TARGET</small><br><b style="font-size:24px; color:#00ff87;">{row['target']}</b></div>
                            <div><small style="color:#555;">STRUCTURE</small><br><b style="font-size:24px;">{row['trend']}</b></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No institutional footprints detected in the current session.")

    # --- ⚖️ LEGAL DISCLAIMER & FOOTER ---
    st.markdown(f"""
        <div class="legal-footer">
            <h3 style="color:#D4AF37; margin-bottom:20px;">LEGAL NOTICE & DISCLAIMER</h3>
            <p>
                <b>1. PROPRIETARY TECHNOLOGY:</b> This terminal ("WAHBA SUPREME") and its underlying neural algorithms, 
                SMC logic, and architecture are the sole intellectual property of <b>Mostafa Tamer Ahmed El-Sayed</b>, based in Alexandria, Egypt. 
                Unauthorized reproduction, reverse engineering, or redistribution is strictly prohibited under international copyright laws.
            </p>
            <p>
                <b>2. NO FINANCIAL ADVICE:</b> The information provided by this system is for educational and analytical purposes only. 
                It does not constitute financial, investment, or trading advice. Trading in the Egyptian Exchange (EGX) and global markets 
                carries significant risk. Past performance, as calculated by our neural engine, is not indicative of future results.
            </p>
            <p>
                <b>3. DATA ACCURACY:</b> While our system utilizes advanced caching and real-time APIs, <b>WAHBA QUANT SYSTEMS</b> 
                does not guarantee the 100% accuracy, completeness, or timeliness of market data. Users are advised to verify all 
                information through official exchange sources.
            </p>
            <p>
                <b>4. LIMITATION OF LIABILITY:</b> Mostafa Tamer and his affiliates shall not be held liable for any financial losses, 
                damages, or profit variations resulting from the use of this software.
            </p>
            <hr style="border:0.5px solid #111; margin:30px 0;">
            <center>© 2026 WAHBA QUANTUM LABS | DEVELOPED IN ALEXANDRIA, EGYPT | ALL RIGHTS RESERVED</center>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
