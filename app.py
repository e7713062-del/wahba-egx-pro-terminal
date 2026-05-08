# ==============================================================================
# 👑 PROJECT: WAHBA EGX - THE IMPERIAL SUPREME (v31.0 - ULTRA-PREMIUM UI)
# 👨‍💻 ARCHITECT: MOSTAFA TAMER | ALEXANDRIA, EGYPT
# 🏛️ SYSTEM: NEURAL QUANTUM ANALYSIS & BILINGUAL LEGAL FORTRESS
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
# 1. THE DATA FORTRESS (إدارة التخزين والحماية - SQLite Lite)
# ------------------------------------------------------------------------------
class DataFortress:
    DB_NAME = "wahba_egx_v31.db"

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
# 2. NEURAL CORE (المحرك العصبي المطور)
# ------------------------------------------------------------------------------
class NeuralCore:
    @staticmethod
    def process(ind):
        p, r = ind["close"], ind["RSI"]
        volat = round(((ind["high"] - ind["low"]) / p) * 100, 2)
        # التوقع (AI Projection) بناءً على مستويات RSI التاريخية وسلوك البورصة المصرية
        target = round(p * 1.18, 2) if r < 35 else round(p * 1.08, 2)
        trend = "Bullish Structure 📈" if p > ind["Pivot.M.Classic.Middle"] else "Bearish Structure 📉"
        ma_state = "Trading Above MA200" if p > ind["SMA200"] else "Trading Below MA200"
        
        # منطق الـ SMC (Smart Money Concepts)
        if r < 35: msg = "💎 Institutional Accumulation"
        elif r > 75: msg = "🚨 Liquidity Distribution"
        else: msg = "🔄 Balanced Market"
        
        return target, msg, trend, volat, ma_state

# ------------------------------------------------------------------------------
# 3. ULTRA-PREMIUM UI ENGINE (محرك التصميم الامبراطوري الكهرماني)
# ------------------------------------------------------------------------------
st.set_page_config(page_title="WAHBA EGX Imperial v31.0", layout="wide")

def apply_imperial_design():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&family=JetBrains+Mono:wght@300&display=swap');
        
        :root { --gold: #D4AF37; --amber: #FFBF00; --bg: #030303; --card-bg: #080808; --border: #111; }
        
        .stApp { background-color: var(--bg); color: #f0f0f0; font-family: 'Cairo', sans-serif; }
        
        /* 1. Hero Header - Full Scale */
        .hero-header {
            background: linear-gradient(135deg, #0f0f0f 0%, #000 100%);
            padding: 80px 40px; border-radius: 40px; border: 1px solid var(--border);
            border-bottom: 5px solid var(--gold); text-align: center;
            margin-bottom: 60px; box-shadow: 0 40px 80px rgba(0,0,0,0.9);
        }
        
        /* 2. Tactical Cards - Neumorphism Style */
        .tactical-card-pro {
            background: var(--card-bg); border: 1px solid var(--border); padding: 35px;
            border-radius: 30px; border-left: 10px solid var(--gold);
            margin-bottom: 30px; transition: 0.4s ease;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        .tactical-card-pro:hover { transform: translateY(-10px); border-color: #fff; }
        
        /* 3. Dashboard Metrics - Glassmorphism */
        .glass-metric {
            background: rgba(10, 10, 10, 0.5); backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.05); padding: 25px;
            border-radius: 20px; text-align: center; margin-bottom: 20px;
        }
        
        /* 4. Text Utilities */
        .stat-label { font-size: 11px; color: #555; text-transform: uppercase; letter-spacing: 2px; }
        .stat-value { font-family: 'JetBrains Mono', monospace; font-size: 32px; font-weight: 300; color: #fff; }
        .target-value { color: #00ff87; }
        </style>
        
        <div class="hero-header">
            <h1 style="color:var(--gold); font-size: 70px; font-weight:900; margin:0;">WAHBA <span style="color:#fff;">EGX</span></h1>
            <p style="color:#666; font-size:16px; letter-spacing: 12px; margin-top:10px;">PROPRIETARY QUANTUM TERMINAL v31.0</p>
            <div style="margin-top:25px;"><span style="background:var(--gold); color:#000; padding:4px 15px; border-radius:5px; font-weight:900;">ALEXANDRIA QUANT NODE</span></div>
        </div>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 4. MAIN APPLICATION LOGIC
# ------------------------------------------------------------------------------
def main():
    DataFortress.init()
    apply_imperial_design()
    
    # --- Sidebar Command ---
    with st.sidebar:
        st.markdown("<h2 style='color:#D4AF37;'>COMMAND</h2>", unsafe_allow_html=True)
        nav = st.radio("Navigation", ["🛰️ Market Overview", "🏹 SMC Scanner", "🛠️ System Authority"])
        st.divider()
        st.caption("Node: ALEXANDRIA | Status: ACTIVE 🟢")
        st.caption("Timezone: Africa/Cairo (DST Compliant)")

    df = DataFortress.fetch()

    # --- Mode: System Authority ---
    if nav == "🛠️ System Authority":
        st.subheader("🛠️ Authority Synchronization")
        key = st.text_input("Enter Authority Key", type="password")
        if key == "WAHBA_TITAN_2026":
            if st.button("RUN GLOBAL CACHE REFRESH"):
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
                                target, msg, trend, volat, ma = NeuralCore.process(ind)
                                all_data.append({'S': s, 'P': ind["close"], 'T': target, 'R': round(ind["RSI"], 1), 
                                                'M': msg, 'TR': trend, 'V': volat, 'MA': ma})
                            except: continue
                            p_bar.progress((i+1)/len(symbols))
                        
                        DataFortress.sync(all_data)
                        st.balloons()
                        st.success("Global Cache Updated.")
                    except: st.error("Link Failure.")

    # --- Mode: Market Overview ---
    elif nav == "🛰️ Market Overview":
        if not df.empty:
            # Glass Metrics Dashboard
            m1, m2, m3, m4 = st.columns(4)
            with m1: st.markdown(f'<div class="glass-metric"><span class="stat-label">Analyzed</span><br><span class="stat-value">{len(df)}</span></div>', unsafe_allow_html=True)
            with m2: st.markdown(f'<div class="glass-metric"><span class="stat-label">Bullish</span><br><span class="stat-value">{len(df[df['trend'].str.contains('Bullish')])}</span></div>', unsafe_allow_html=True)
            with m3: st.markdown(f'<div class="glass-metric"><span class="stat-label">Buy Zone</span><br><span class="stat-value">{len(df[df['signal'].str.contains('Accumulation')])}</span></div>', unsafe_allow_html=True)
            with m4: st.markdown(f'<div class="glass-metric"><span class="stat-label">Avg Risk</span><br><span class="stat-value">{df['volatility'].mean():.1f}%</span></div>', unsafe_allow_html=True)
            
            st.divider()
            
            # Interactive Visuals
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown("### 📊 Quantum Price Projections")
                fig = px.bar(df.head(20), x='ticker', y=['price', 'target'], barmode='group', 
                             color_discrete_sequence=['#333', '#D4AF37'], template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
            
            with c2:
                st.markdown("### 🏹 Market Sentiment")
                fig_pie = px.pie(df, names='signal', hole=0.7, color_discrete_sequence=['#D4AF37', '#111', '#555'])
                st.plotly_chart(fig_pie, use_container_width=True)

            st.markdown("### 🏛️ Master Data Grid")
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("System offline. Admin sync required.")

    # --- Mode: SMC Scanner ---
    elif nav == "🏹 SMC Scanner":
        st.subheader("🏹 Institutional Footprint Tracker (SMC)")
        setups = df[df['signal'].str.contains('Accumulation')]
        
        if not setups.empty:
            for _, row in setups.iterrows():
                st.markdown(f"""
                    <div class="tactical-card-pro">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h2 style="color:var(--gold); margin:0; font-size:35px; font-weight:900;">{row['ticker']}</h2>
                            <span style="color:#00ff87; background: rgba(0,255,135,0.1); padding:5px 20px; border-radius:10px; font-weight:bold;">SMC TARGET</span>
                        </div>
                        <p style="color:#777; margin-top:5px; margin-bottom:20px;">Logic: {row['signal']} | {row['ma_state']}</p>
                        <div style="display:grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap:30px; text-align:center;">
                            <div><span class="stat-label">PRICE</span><br><b class="stat-value">{row['price']}</b></div>
                            <div><span class="stat-label">TARGET</span><br><b class="stat-value target-value">{row['target']}</b></div>
                            <div><span class="stat-label">RSI</span><br><b class="stat-value">{row['rsi']}</b></div>
                            <div><span class="stat-label">STRUCTURE</span><br><b class="stat-value" style="font-size:18px; color:var(--gold);">{row['trend'].split(' ')[0]}</b></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Searching for footprints...")

    # --- ⚖️ BILINGUAL LEGAL SECURED FOOTER ---
    st.markdown("""
        <div style="background: rgba(10, 10, 10, 0.5); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.05); padding: 50px; margin-top: 100px; border-radius: 20px; font-size: 12px; line-height: 1.6;">
            <div style="display: flex; gap: 50px; text-align: justify; direction: ltr;">
                <div style="flex: 1; border-right: 1px solid rgba(255, 255, 255, 0.05); padding-right: 25px;">
                    <h4 style="color:var(--gold); margin-bottom:15px;">LEGAL DISCLAIMER</h4>
                    <b>1. Ownership:</b> This terminal ("WAHBA EGX") and its underlying neural algorithms are the exclusive property of <b>Mostafa Tamer Ahmed El-Sayed</b>, based in Alexandria, Egypt. Authorized use is strictly prohibited.<br>
                    <b>2. No Advice:</b> Content is for informational purposes only. Trading involves risk. We are not liable for any financial losses.<br>
                    <b>3. Data:</b> Market data accuracy is not guaranteed. Verify with official EGX sources.
                </div>
                <div style="flex: 1; direction: rtl; text-align: right; padding-right: 15px;">
                    <h4 style="color:var(--gold); margin-bottom:15px;">إخلاء مسؤولية قانوني</h4>
                    <b>١. الملكية:</b> هذه المنصة ("WAHBA EGX") وخوارزمياتها ملكية حصرية لـ <b>مصطفى تامر أحمد السيد</b>، المقيم بالإسكندرية، مصر. يُحظر الاستخدام غير المصرح به.<br>
                    <b>٢. لا نصيحة مالية:</b> المحتوى للأغراض المعلوماتية فقط. التداول ينطوي على مخاطر، ونحن غير مسؤولين عن أي خسائر مالية.<br>
                    <b>٣. البيانات:</b> دقة بيانات السوق غير مضمونة؛ يرجى التحقق من المصادر الرسمية للبورصة المصرية.
                </div>
            </div>
            <hr style="border:0.5px solid rgba(255, 255, 255, 0.03); margin:35px 0;">
            <center style="color:#333;">© 2026 WAHBA QUANTUM LABS | DEVELOPED IN ALEXANDRIA, EGYPT | ALL RIGHTS RESERVED</center>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
