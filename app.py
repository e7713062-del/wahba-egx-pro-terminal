import streamlit as st
import google.generativeai as genai
import pandas as pd
import sqlite3
import json
import time
from datetime import datetime
from tradingview_ta import TA_Handler, Interval

# =================================================================
# 1. إعدادات العقل المفكر (AI Brain)
# =================================================================
GEMINI_API_KEY = "AIzaSyAHLshGDTIRhodR1CMAWGP_DH3622aADJQ" 
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# =================================================================
# 2. مخرك تخزين التوصيات (The Ledger)
# =================================================================
class WahbaSovereignEngine:
    def __init__(self, db_name="wahba_pro_signals.db"):
        self.db_name = db_name
        self._setup_db()

    def _setup_db(self):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS signals (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            time TEXT, symbol TEXT, type TEXT, school TEXT, 
                            logic TEXT, entry REAL, sl REAL, tp REAL)""")

    def record_signal(self, symbol, s_type, school, logic, entry, sl, tp):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("""INSERT INTO signals (time, symbol, type, school, logic, entry, sl, tp) 
                            VALUES (?,?,?,?,?,?,?,?)""",
                         (datetime.now().strftime("%Y-%m-%d %H:%M"), symbol, s_type, school, logic, entry, sl, tp))

# =================================================================
# 3. واجهة التحكم (The Command Center)
# =================================================================
def main():
    st.set_page_config(page_title="Wahba Pro Signals", layout="wide", page_icon="🦅")
    engine = WahbaSovereignEngine()
    
    st.markdown("<h1 style='text-align:center; color:#f3ba2f;'>🦅 WAHBA PRO: DAY & SWING MASTER</h1>", unsafe_allow_html=True)
    st.sidebar.markdown("### 🛠️ حالة الضبط:")
    st.sidebar.warning("🚫 Scalping: DISABLED")
    st.sidebar.success("✅ Day Trading: ACTIVE")
    st.sidebar.success("✅ Swing Trading: ACTIVE")

    metrics_placeholder = st.empty()
    signals_placeholder = st.empty()

    while True:
        with metrics_placeholder.container():
            c1, c2, c3 = st.columns(3)
            c1.metric("الوضع الحالي", "Trend Hunting")
            c2.metric("المدارس", "Wyckoff / Elliott / VSA")
            c3.metric("الفريمات", "15m / 1h / 4h")

        # مراقبة العملات القوية للسوينج والداي
        for sym in ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "ADAUSDT"]:
            try:
                # التحليل بيتم على فريمات أكبر (15 دقيقة وساعة) لضمان جودة التوصية
                handler = TA_Handler(symbol=sym, screener="crypto", exchange="BINANCE", interval=Interval.INTERVAL_15_MINUTES)
                ta = handler.get_analysis()
                price = ta.indicators['close']
                
                # البرومبت الموجه للـ Day & Swing فقط
                prompt_text = f"""
                Analyze {sym} at price {price}. RSI={ta.indicators['RSI']}.
                Ignore all Scalping opportunities.
                Focus ONLY on:
                1. Day Trading setups (15m-1h) using Order Blocks & VSA.
                2. Swing Trading setups (1h-4h) using Wyckoff Accumulation/Distribution or Elliott Wave (3 or 5).
                
                Return JSON ONLY:
                {{
                    "status": "SIGNAL",
                    "type": "DAY or SWING",
                    "school": "...",
                    "logic": "...",
                    "entry": {price},
                    "sl": "Calculation based on structure",
                    "tp": "Calculation based on Next Resistance"
                }} or {{"status": "WAIT"}}
                """
                
                response = model.generate_content(prompt_text)
                res = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
                
                if res.get('status') == "SIGNAL":
                    st.toast(f"🚨 فرصة {res['type']} مكتشفة على {sym}")
                    engine.record_signal(sym, res['type'], res['school'], res['logic'], res['entry'], res['sl'], res['tp'])
                    st.balloons() # احتفال بسيط بالفرصة الكبيرة
            except:
                continue

        # عرض جدول الإشارات الحية
        with signals_placeholder.container():
            st.divider()
            with sqlite3.connect(engine.db_name) as conn:
                df = pd.read_sql_query("SELECT * FROM signals ORDER BY id DESC LIMIT 10", conn)
                if not df.empty:
                    st.write("### 📜 توصيات القناص (Day & Swing):")
                    # تلوين الجدول لتمييز السوينج عن الداي
                    def color_type(val):
                        color = '#1f77b4' if val == 'SWING' else '#2ca02c'
                        return f'background-color: {color}; color: white'
                    
                    st.dataframe(df.style.applymap(color_type, subset=['type']))

        # تحديث كل دقيقة لأن السوينج والداي مش محتاجين سرعة السكالبينج
        time.sleep(60)

if __name__ == "__main__":
    main()
