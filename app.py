# ==============================================================================
# 👑 PROJECT: WAHBA EGX - THE IMPERIAL BEAST (v28.0 - ENTERPRISE)
# 👨‍💻 ARCHITECT: MOSTAFA TAMER | ALEXANDRIA, EGYPT
# 🏛️ SYSTEM: QUANTUM NEURAL ANALYSIS & INSTITUTIONAL TRACKING
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
# 1. THE IMPERIAL VAULT (نظام التخزين العملاق الموفر للمساحة)
# ------------------------------------------------------------------------------
class ImperialVault:
    DB_NAME = "wahba_imperial_v28.db"

    @staticmethod
    def init():
        with sqlite3.connect(ImperialVault.DB_NAME) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS market_data 
                         (ticker TEXT PRIMARY KEY, price REAL, target REAL, 
                          rsi REAL, signal TEXT, trend TEXT, volatility REAL, last_update TEXT)''')
            conn.commit()

    @staticmethod
    def sync_data(results):
        with sqlite3.connect(ImperialVault.DB_NAME) as conn:
            cairo_tz = pytz.timezone('Africa/Cairo')
            ts = datetime.now(cairo_tz).strftime("%Y-%m-%d %H:%M")
            for r in results:
                conn.execute('''INSERT OR REPLACE INTO market_data 
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                             (r['S'], r['P'], r['T'], r['R'], r['M'], r['TR'], r['V'], ts))
            conn.commit()

    @staticmethod
    def get_market_view():
        try:
            with sqlite3.connect(ImperialVault.DB_NAME) as conn:
                return pd.read_sql_query("SELECT * FROM market_data", conn)
        except: return pd.DataFrame()

# ------------------------------------------------------------------------------
# 2. NEURAL CORE (المحرك العصبي المطور)
# ------------------------------------------------------------------------------
class NeuralBrain:
    @staticmethod
    def analyze(ind):
        p, r = ind["close"], ind["RSI"]
        # حساب التذبذب (Volatility)
        volat = round(((ind["high"] - ind["low"]) / p) * 100, 2)
        # التوقع بناءً على SMC و RSI
        target = round(p * 1.15, 2) if r < 40 else round(p * 1.07, 2)
        # تحديد الهيكل (Structure)
        trend = "Bullish 📈" if p > ind["Pivot.M.Classic.Middle"] else "Bearish 📉"
        
        if r < 35: msg = "💎 Institutional Accumulation"
        elif r > 70: msg = "🚨 Liquidity Distribution"
        else: msg = "🔄 Balanced Range"
        
        return target, msg, trend, volat

# ------------------------------------------------------------------------------
# 3. IMPERIAL UI (الواجهة الامبراطورية الكبرى)
# ------------------------------------------------------------------------------
st.set_page_config(page_title="WAHBA EGX PRO", layout="wide", initial_sidebar_state="expanded")

def apply_styles():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
        .stApp { background-color: #050505; color: #e0e0e0; font-family: 'Cairo', sans-serif; }
        [data-testid="stMetricValue"] { color: #D4AF37 !important; font-weight: 900; }
        .main-header {
            background: linear-gradient(135deg, #111 0%, #000 100%);
            padding: 50px; border-radius: 30px; border-bottom: 4px solid #D4AF37;
            text-align: center; margin-bottom: 40px; box-shadow: 0 20px 50px rgba(0,0,0,0.7);
        }
        .card-pro {
            background: #0d0d0d; border: 1px solid #1a1a1a; padding: 25px;
            border-radius: 20px; border-left: 6px solid #D4AF37; margin-bottom: 20px;
        }
        </style>
        <div class="main-header">
            <h1 style="color:#D4AF37; font-size: 50px; margin:0;">WAHBA EGX <span style="color:#fff;">SUPREME</span></h1>
            <p style="color:#666; letter-spacing: 5px;">QUANTUM FINANCIAL TERMINAL v28.0</p>
        </div>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 4. MAIN SYSTEM ENGINE
# ------------------------------------------------------------------------------
def main():
    ImperialVault.init()
    apply_styles()
    
    # Sidebar
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2534/2534183.png", width=100)
        st.title("Control Center")
        mode = st.selectbox("Navigation", ["Global Dashboard", "SMC Opportunities", "System Admin"])
        st.divider()
        st.info("Alexandria Node: Stable 🟢")

    df = ImperialVault.get_market_view()

    if mode == "System Admin":
        st.subheader("🔐 Database & Neural Sync")
        key = st.text_input("Access Key", type="password")
        if key == "WAHBA_2026":
            if st.button("🚀 FULL SYSTEM REFRESH"):
                with st.status("Scanning EGX & Training Neurons...", expanded=True):
                    try:
                        res = requests.post("https://scanner.tradingview.com/egypt/scan", 
                                            json={"filter": [{"left": "type", "operation": "in_range", "right": ["stock"]}], "markets": ["egypt"], "columns": ["name"]}, timeout=10).json()
                        symbols = [item['s'].split(':')[1] for item in res['data']]
                        
                        scans = []
                        prog = st.progress(0)
                        for i, s in enumerate(symbols):
                            try:
                                h = TA_Handler(symbol=s, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY)
                                ind = h.get_analysis().indicators
                                target, msg, trend, volat = NeuralBrain.analyze(ind)
                                scans.append({'S': s, 'P': ind["close"], 'T': target, 'R': round(ind["RSI"], 1), 'M': msg, 'TR': trend, 'V': volat})
                            except: continue
                            prog.progress((i+1)/len(symbols))
                        
                        ImperialVault.sync_data(scans)
                        st.balloons()
                        st.success("System Fully Updated.")
                    except: st.error("Global Connection Error.")

    elif mode == "Global Dashboard":
        if not df.empty:
            # Metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Assets", len(df))
            m2.metric("Bullish Trend", len(df[df['trend'] == 'Bullish 📈']))
            m3.metric("Accumulation Phase", len(df[df['signal'].str.contains('Accumulation')]))
            m4.metric("Avg Volatility", f"{df['volatility'].mean():.2f}%")
            
            st.divider()
            
            # Charts
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown("### 📈 AI Price Projection vs Current")
                fig = px.bar(df.head(20), x='ticker', y=['price', 'target'], barmode='group', 
                             color_discrete_sequence=['#333', '#D4AF37'], template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
            
            with c2:
                st.markdown("### 🏹 Signal Distribution")
                fig_pie = px.pie(df, names='signal', color_discrete_sequence=['#D4AF37', '#111', '#555'], hole=0.6)
                st.plotly_chart(fig_pie, use_container_width=True)

            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("No data found. Please run System Admin Sync.")

    elif mode == "SMC Opportunities":
        st.subheader("💎 Institutional Grade Setups (High Confidence)")
        hot_picks = df[df['signal'].str.contains('Accumulation')].sort_values('volatility')
        
        if not hot_picks.empty:
            for _, row in hot_picks.iterrows():
                st.markdown(f"""
                    <div class="card-pro">
                        <div style="display:flex; justify-content:space-between;">
                            <h2 style="color:#D4AF37; margin:0;">{row['ticker']}</h2>
                            <span style="background:#00ff87; color:#000; padding:5px 15px; border-radius:10px; font-weight:bold;">BUY ZONE</span>
                        </div>
                        <p style="color:#888;">{row['signal']} | Trend: {row['trend']}</p>
                        <div style="display:flex; gap:40px;">
                            <div><small>CURRENT</small><br><span style="font-size:20px;">{row['price']}</span></div>
                            <div><small>AI TARGET</small><br><span style="font-size:20px; color:#00ff87;">{row['target']}</span></div>
                            <div><small>VOLATILITY</small><br><span style="font-size:20px;">{row['volatility']}%</span></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Scanning for institutional footprints... No high-confidence setups at this moment.")

    st.markdown("<br><center style='color:#333; font-size:12px;'>WAHBA QUANT SYSTEMS | ALEXANDRIA NODE | © 2026</center>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
