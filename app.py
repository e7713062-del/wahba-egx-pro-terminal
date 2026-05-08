# ==============================================================================
# 👑 PROJECT: WAHBA EGX - THE IMPERIAL SUPREME (v32.0)
# 👨‍💻 ARCHITECT: MOSTAFA TAMER | ALEXANDRIA, EGYPT
# 🏛️ SYSTEM: NEURAL QUANTUM ANALYSIS & HORIZONTAL LEGAL COMPLIANCE
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
# 1. THE DATA FORTRESS (إدارة التخزين الذكي)
# ------------------------------------------------------------------------------
class DataFortress:
    DB_NAME = "wahba_egx_v32.db"

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
# 2. NEURAL CORE (محرك التحليل العصبي)
# ------------------------------------------------------------------------------
class NeuralCore:
    @staticmethod
    def process(ind):
        p, r = ind["close"], ind["RSI"]
        volat = round(((ind["high"] - ind["low"]) / p) * 100, 2)
        target = round(p * 1.18, 2) if r < 35 else round(p * 1.08, 2)
        trend = "Bullish Structure 📈" if p > ind["Pivot.M.Classic.Middle"] else "Bearish Structure 📉"
        ma_state = "Above MA200" if p > ind["SMA200"] else "Below MA200"
        
        if r < 35: msg = "💎 Institutional Accumulation"
        elif r > 75: msg = "🚨 Liquidity Distribution"
        else: msg = "🔄 Balanced Market"
        
        return target, msg, trend, volat, ma_state

# ------------------------------------------------------------------------------
# 3. ULTRA-PREMIUM UI ENGINE (محرك التصميم)
# ------------------------------------------------------------------------------
st.set_page_config(page_title="WAHBA EGX v32.0", layout="wide")

def apply_design():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
        .stApp { background-color: #010101; color: #f0f0f0; font-family: 'Cairo', sans-serif; }
        
        /* Progress Bar Custom Color */
        .stProgress > div > div > div > div { background-image: linear-gradient(to right, #D4AF37, #FFD700); }
        
        /* Hero Header */
        .hero-header {
            background: linear-gradient(135deg, #0a0a0a 0%, #000 100%);
            padding: 70px 40px; border-radius: 40px; border-bottom: 6px solid #D4AF37;
            text-align: center; margin-bottom: 50px; box-shadow: 0 30px 60px rgba(0,0,0,1);
        }
        
        /* Tactical Cards */
        .tactical-card-pro {
            background: #080808; border: 1px solid #111; padding: 30px;
            border-radius: 25px; border-left: 10px solid #D4AF37;
            margin-bottom: 25px; transition: 0.3s;
        }
        
        /* Horizontal Legal Fortress */
        .horizontal-legal {
            background: #050505; border: 1px solid #111; padding: 50px;
            margin-top: 100px; border-radius: 25px; width: 100%;
        }
        .legal-section { margin-bottom: 30px; line-height: 1.8; font-size: 13px; }
        </style>
        
        <div class="hero-header">
            <h1 style="color:#D4AF37; font-size: 65px; font-weight:900; margin:0;">WAHBA <span style="color:#fff;">EGX</span></h1>
            <p style="color:#555; font-size:15px; letter-spacing: 12px; margin-top:10px;">QUANTUM FINANCIAL TERMINAL v32.0</p>
        </div>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 4. MISSION CONTROL (الإدارة والتشغيل)
# ------------------------------------------------------------------------------
def main():
    DataFortress.init()
    apply_design()
    
    with st.sidebar:
        st.markdown("<h2 style='color:#D4AF37;'>WAHBA COMMAND</h2>", unsafe_allow_html=True)
        nav = st.radio("Navigation", ["🛰️ Market Overview", "🏹 SMC Scanner", "🛠️ System Admin"])
        st.divider()
        st.caption("Alexandria Node: ACTIVE 🟢")

    df = DataFortress.fetch()

    if nav == "🛠️ System Admin":
        st.subheader("⚙️ Global Neural Synchronization")
        key = st.text_input("Sovereign Admin Key", type="password")
        if key == "WAHBA_2026":
            if st.button("EXECUTE DEEP SYNC"):
                try:
                    res = requests.post("https://scanner.tradingview.com/egypt/scan", 
                                        json={"filter": [{"left": "type", "operation": "in_range", "right": ["stock"]}], "markets": ["egypt"], "columns": ["name"]}, timeout=10).json()
                    symbols = [item['s'].split(':')[1] for item in res['data']]
                    
                    # --- شريط التحميل الاحترافي ---
                    st.write("🛰️ **Scanning Global Node & Propagating Neurons...**")
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    all_results = []
                    total = len(symbols)
                    
                    for i, s in enumerate(symbols):
                        try:
                            # تحديث شريط التحميل
                            progress_bar.progress((i + 1) / total)
                            status_text.text(f"Processing Neural Signature: {s} ({i+1}/{total})")
                            
                            h = TA_Handler(symbol=s, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY)
                            ind = h.get_analysis().indicators
                            target, msg, trend, volat, ma = NeuralCore.process(ind)
                            all_results.append({'S': s, 'P': ind["close"], 'T': target, 'R': round(ind["RSI"], 1), 
                                               'M': msg, 'TR': trend, 'V': volat, 'MA': ma})
                        except: continue
                    
                    DataFortress.sync(all_results)
                    status_text.success(f"Successfully Synchronized {len(all_results)} Assets.")
                    st.balloons()
                except: st.error("Node Connection Failure.")

    elif nav == "🛰️ Market Overview":
        if not df.empty:
            st.caption(f"Last Imperial Sync: {df['last_update'].iloc[0]}")
            m1, m2, m3 = st.columns(3)
            m1.metric("Assets Analyzed", len(df))
            m2.metric("Bullish Trend", len(df[df['trend'].str.contains('Bullish')]))
            m3.metric("Avg Market Risk", f"{df['volatility'].mean():.2f}%")
            
            st.divider()
            st.markdown("### 📊 Market Projection Map")
            fig = px.bar(df.head(20), x='ticker', y=['price', 'target'], barmode='group', 
                         color_discrete_sequence=['#333', '#D4AF37'], template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("System offline. Please perform Admin Sync.")

    elif nav == "🏹 SMC Scanner":
        st.subheader("🏹 Institutional Footprint Tracker")
        hot_picks = df[df['signal'].str.contains('Accumulation')]
        if not hot_picks.empty:
            for _, row in hot_picks.iterrows():
                st.markdown(f"""
                    <div class="tactical-card-pro">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h2 style="color:#D4AF37; margin:0;">{row['ticker']}</h2>
                            <span style="color:#00ff87; font-weight:bold;">SMC CONFIRMED</span>
                        </div>
                        <p style="color:#555;">{row['signal']} | {row['ma_state']}</p>
                        <div style="display:flex; gap:60px; margin-top:20px;">
                            <div><small>CURRENT</small><br><b style="font-size:26px;">{row['price']}</b></div>
                            <div><small style="color:#00ff87;">AI TARGET</small><br><b style="font-size:26px; color:#00ff87;">{row['target']}</b></div>
                            <div><small>RSI</small><br><b style="font-size:26px;">{row['rsi']}</b></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No institutional footprints detected in the current session.")

    # --- ⚖️ HORIZONTAL BILINGUAL LEGAL FORTRESS ---
    st.markdown(f"""
        <div class="horizontal-legal">
            <div class="legal-section" style="direction: ltr; text-align: left; border-bottom: 1px solid #111; padding-bottom: 25px;">
                <h4 style="color:#D4AF37; margin-bottom:15px;">⚖️ LEGAL NOTICE & TERMS OF USE (ENGLISH)</h4>
                <b>1. PROPRIETARY TECHNOLOGY:</b> This terminal ("WAHBA EGX") and its underlying neural algorithms are the sole intellectual property of <b>Mostafa Tamer Ahmed El-Sayed</b>, Alexandria, Egypt. Unauthorized reproduction or redistribution is strictly prohibited.<br>
                <b>2. NO FINANCIAL ADVICE:</b> Information provided is for analytical purposes only and does not constitute financial advice. Trading in the Egyptian Exchange (EGX) involves high risk. Mostafa Tamer is not liable for any financial losses.<br>
                <b>3. DATA ACCURACY:</b> We do not guarantee 100% accuracy of market data. Users must verify through official exchange sources.
            </div>
            <div class="legal-section" style="direction: rtl; text-align: right; padding-top: 10px;">
                <h4 style="color:#D4AF37; margin-bottom:15px;">⚖️ إخلاء مسؤولية وشروط الاستخدام (العربية)</h4>
                <b>١. الملكية الفكرية:</b> هذه المنصة ("WAHBA EGX") وخوارزمياتها العصبية هي ملكية حصرية لـ <b>مصطفى تامر أحمد السيد</b>، الإسكندرية، مصر. يُمنع منعاً باتاً إعادة الإنتاج أو التوزيع غير المصرح به.<br>
                <b>٢. لا نصيحة مالية:</b> المعلومات المقدمة هي لأغراض تحليلية فقط ولا تعتبر نصيحة استثمارية. التداول في البورصة المصرية ينطوي على مخاطر عالية، ومصطفى تامر غير مسؤول عن أي خسائر مالية.<br>
                <b>٣. دقة البيانات:</b> لا نضمن دقة بيانات السوق بنسبة ١٠٠٪؛ لذا يجب على المستخدمين التحقق من المصادر الرسمية للبورصة.
            </div>
            <hr style="border:0.5px solid #111; margin:30px 0;">
            <center style="color:#333; font-size:11px;">© 2026 WAHBA QUANTUM LABS | DEVELOPED IN ALEXANDRIA, EGYPT | ALL RIGHTS RESERVED TO MOSTAFA TAMER</center>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
