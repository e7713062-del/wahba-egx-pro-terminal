# ==============================================================================
# 👑 PROJECT: WAHBA EGX - THE GOLDEN IMPERIAL (v35.0)
# 👨‍💻 ARCHITECT: MOSTAFA TAMER | ALEXANDRIA, EGYPT
# 🏛️ STRATEGY: HYBRID (CLASSIC, PRICE ACTION, MATH, VOLUME)
# ⚖️ LEGAL: BILINGUAL HORIZONTAL FORTRESS
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
# 1. DATABASE SYSTEM
# ------------------------------------------------------------------------------
class DataVault:
    DB_NAME = "wahba_egx_golden.db"

    @staticmethod
    def init():
        with sqlite3.connect(DataVault.DB_NAME) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS market_data 
                         (ticker TEXT PRIMARY KEY, price REAL, target REAL, 
                          rsi REAL, signal TEXT, trend TEXT, strategy TEXT, 
                          ma_state TEXT, last_update TEXT)''')
            conn.commit()

    @staticmethod
    def sync(results):
        with sqlite3.connect(DataVault.DB_NAME) as conn:
            ts = datetime.now(pytz.timezone('Africa/Cairo')).strftime("%Y-%m-%d %H:%M")
            for r in results:
                conn.execute('''INSERT OR REPLACE INTO market_data 
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                             (r['S'], r['P'], r['T'], r['R'], r['M'], r['TR'], r['ST'], r['MA'], ts))
            conn.commit()

    @staticmethod
    def fetch():
        try:
            with sqlite3.connect(DataVault.DB_NAME) as conn:
                return pd.read_sql_query("SELECT * FROM market_data ORDER BY ticker ASC", conn)
        except: return pd.DataFrame()

# ------------------------------------------------------------------------------
# 2. HYBRID ANALYTICAL ENGINE (المعادلات الرياضية والبرايس أكشن)
# ------------------------------------------------------------------------------
class HybridEngine:
    @staticmethod
    def analyze(ind):
        p, r, v = ind["close"], ind["RSI"], ind["volume"]
        ma50, ma200 = ind["SMA50"], ind["SMA200"]
        
        # تحليل الاتجاه الكلاسيكي والمتوسطات
        ma_status = "Golden Cross 🚀" if ma50 > ma200 else "Death Cross ⚠️"
        trend = "Bullish Empire 📈" if p > ma200 else "Bearish Zone 📉"
        
        # معادلة رياضية للتوقع (Target Projection)
        target = round(p * 1.15, 2) if p > ma50 else round(p * 1.07, 2)
        
        # منطق البرايس أكشن والفوليوم
        if v > ind["average_volume_10d"] and p > ind["open"]:
            strat = "Price Action + Volume"
            msg = "High Momentum Detected"
        elif r < 30:
            strat = "Mathematical Bounce"
            msg = "Oversold - Potential Target"
        else:
            strat = "Classic Structure"
            msg = "Stable Market Node"
            
        return target, msg, trend, strat, ma_status

# ------------------------------------------------------------------------------
# 3. PRESERVED IMPERIAL DESIGN (نفس الشكل اللي حبيته)
# ------------------------------------------------------------------------------
st.set_page_config(page_title="WAHBA EGX Golden v35.0", layout="wide")

def apply_golden_ui():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
        .stApp { background-color: #050505; color: #f0f0f0; font-family: 'Cairo', sans-serif; }
        
        /* Progress Bar Color */
        .stProgress > div > div > div > div { background-color: #D4AF37; }
        
        /* Hero Header */
        .hero-header {
            background: linear-gradient(135deg, #111 0%, #000 100%);
            padding: 60px; border-radius: 35px; border-bottom: 5px solid #D4AF37;
            text-align: center; margin-bottom: 50px; box-shadow: 0 25px 50px rgba(0,0,0,0.9);
        }
        
        /* Tactical Cards */
        .tactical-card {
            background: #080808; border: 1px solid #151515; padding: 25px;
            border-radius: 20px; border-left: 10px solid #D4AF37;
            margin-bottom: 20px; transition: 0.3s ease-in-out;
        }
        .tactical-card:hover { transform: scale(1.01); border-color: #D4AF37; }

        /* Legal Horizontal Footer */
        .legal-horizontal {
            background: #020202; border: 1px solid #111; padding: 45px;
            margin-top: 100px; border-radius: 20px; font-size: 13px; width: 100%;
        }
        </style>
        
        <div class="hero-header">
            <h1 style="color:#D4AF37; font-size: 65px; font-weight:900; margin:0;">WAHBA <span style="color:#fff;">EGX</span></h1>
            <p style="color:#666; font-size:15px; letter-spacing: 10px; margin-top:10px;">GOLDEN ANALYTICAL TERMINAL v35.0</p>
            <div style="margin-top:20px;"><span style="background:#D4AF37; color:#000; padding:5px 15px; border-radius:5px; font-weight:900;">ALEXANDRIA QUANT NODE</span></div>
        </div>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 4. MISSION CONTROL
# ------------------------------------------------------------------------------
def main():
    DataVault.init()
    apply_golden_ui()
    
    with st.sidebar:
        st.markdown("<h2 style='color:#D4AF37;'>COMMAND</h2>", unsafe_allow_html=True)
        nav = st.radio("Navigation", ["🛰️ Dashboard", "🏹 Strategy Scanner", "🛠️ Admin Control"])
        st.divider()
        st.caption("Status: Secure 🟢")

    df = DataVault.fetch()

    if nav == "🛠️ Admin Control":
        st.subheader("⚙️ Global Synchronization")
        key = st.text_input("Sovereign Key", type="password")
        if key == "WAHBA_2026":
            if st.button("RUN FULL MARKET SCAN"):
                try:
                    res = requests.post("https://scanner.tradingview.com/egypt/scan", 
                                        json={"filter": [{"left": "type", "operation": "in_range", "right": ["stock"]}], "markets": ["egypt"], "columns": ["name"]}, timeout=10).json()
                    symbols = [item['s'].split(':')[1] for item in res['data']]
                    
                    st.write("🔄 **Processing Multi-Strategy Analysis...**")
                    prog_bar = st.progress(0)
                    status_lbl = st.empty()
                    
                    results = []
                    total = len(symbols)
                    for i, s in enumerate(symbols):
                        try:
                            prog_bar.progress((i + 1) / total)
                            status_lbl.text(f"Analyzing Node: {s} ({i+1}/{total})")
                            
                            h = TA_Handler(symbol=s, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY)
                            ind = h.get_analysis().indicators
                            target, msg, trend, strat, ma = HybridEngine.analyze(ind)
                            results.append({'S': s, 'P': ind["close"], 'T': target, 'R': round(ind["RSI"], 1), 
                                           'M': msg, 'TR': trend, 'ST': strat, 'MA': ma})
                        except: continue
                    
                    DataVault.sync(results)
                    status_lbl.success("Synchronization Complete.")
                    st.balloons()
                except: st.error("Link Failure.")

    elif nav == "🛰️ Dashboard":
        if not df.empty:
            m1, m2, m3 = st.columns(3)
            m1.metric("Assets Analyzed", len(df))
            m2.metric("Bullish Trend", len(df[df['trend'].str.contains('Bullish')]))
            m3.metric("Last Sync", df['last_update'].iloc[0].split(' ')[1])
            
            st.divider()
            st.plotly_chart(px.bar(df.head(20), x='ticker', y=['price', 'target'], barmode='group', 
                                   color_discrete_sequence=['#333', '#D4AF37'], template="plotly_dark"), use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("System offline. Please run Admin Sync.")

    elif nav == "🏹 Strategy Scanner":
        st.subheader("🏹 High-Probability Setups")
        picks = df[df['MA'].str.contains('Golden') | df['ST'].str.contains('Volume')]
        if not picks.empty:
            for _, row in picks.iterrows():
                st.markdown(f"""
                    <div class="tactical-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h2 style="color:#D4AF37; margin:0;">{row['ticker']}</h2>
                            <span style="color:#666; font-size:12px;">{row['ST']}</span>
                        </div>
                        <p style="color:#888; margin:5px 0;">{row['M']} | {row['MA']}</p>
                        <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:20px; margin-top:20px; text-align:center;">
                            <div><small>PRICE</small><br><b style="font-size:24px;">{row['price']}</b></div>
                            <div><small style="color:#00ff87;">TARGET</small><br><b style="font-size:24px; color:#00ff87;">{row['target']}</b></div>
                            <div><small>TREND</small><br><b style="font-size:24px;">{row['trend'].split(' ')[0]}</b></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    # --- ⚖️ BILINGUAL HORIZONTAL LEGAL FORTRESS (WIDE) ---
    st.markdown("""
        <div class="legal-horizontal">
            <div style="border-bottom: 1px solid #111; padding-bottom: 25px; margin-bottom: 25px;">
                <h4 style="color:#D4AF37; margin-top:0;">⚖️ LEGAL DISCLAIMER (EN)</h4>
                This terminal ("WAHBA EGX") and its proprietary neural algorithms are the sole intellectual property of <b>Mostafa Tamer Ahmed El-Sayed</b>. Information provided is for analytical purposes only and does not constitute financial advice. Trading involves substantial risk; always verify data through official EGX sources.
            </div>
            <div style="direction: rtl; text-align: right;">
                <h4 style="color:#D4AF37; margin-top:0;">⚖️ إخلاء مسؤولية قانوني (AR)</h4>
                هذه المنصة ("WAHBA EGX") وخوارزمياتها العصبية هي ملكية حصرية لـ <b>مصطفى تامر أحمد السيد</b>. المعلومات المقدمة هي لأغراض تحليلية فقط ولا تعتبر نصيحة مالية. التداول ينطوي على مخاطر كبيرة؛ يرجى التحقق من البيانات عبر المصادر الرسمية للبورصة المصرية.
            </div>
            <hr style="border:0.5px solid #111; margin:25px 0;">
            <center style="color:#222; font-size:11px;">© 2026 WAHBA QUANTUM LABS | DEVELOPED IN ALEXANDRIA, EGYPT | ALL RIGHTS RESERVED TO MOSTAFA TAMER</center>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
