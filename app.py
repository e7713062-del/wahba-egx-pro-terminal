import streamlit as st
import google.generativeai as genai
import pandas as pd
import sqlite3
import json
import time
from datetime import datetime
from tradingview_ta import TA_Handler, Interval

# =================================================================
# 1. إعدادات العقل المفكر (AI Setup)
# =================================================================
GEMINI_API_KEY = "AIzaSyAHLshGDTIRhodR1CMAWGP_DH3622aADJQ" 
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# =================================================================
# 2. محرك تخزين الصفقات (Sovereign Ledger)
# =================================================================
class WahbaSovereignEngine:
    def __init__(self, db_name="wahba_final_signals.db"):
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
                         (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), symbol, s_type, school, logic, entry, sl, tp))

# =================================================================
# 3. واجهة التحكم (The Master Dashboard)
# =================================================================
def main():
    st.set_page_config(page_title="Wahba Sovereign Master", layout="wide", page_icon="🦅")
    engine = WahbaSovereignEngine()
    
    st.markdown("<h1 style='text-align:center; color:#f3ba2f;'>🦅 WAHBA SOVEREIGN MASTER</h1>", unsafe_allow_html=True)
    
    # شريط الحالة الجانبي عشان تطمن إن الكود شغال
    st.sidebar.header("📡 مراقب الأنظمة")
    status_box = st.sidebar.empty()
    price_box = st.sidebar.empty()
    st.sidebar.divider()
    st.sidebar.info("الوضع: Day & Swing (Scalping Disabled)")

    metrics_placeholder = st.empty()
    signals_placeholder = st.empty()

    while True:
        # تحديث لوحة التحكم
        with metrics_placeholder.container():
            c1, c2, c3 = st.columns(3)
            c1.metric("وضع الرادار", "Day / Swing Only")
            c2.metric("المدارس النشطة", "Wyckoff + Elliott")
            c3.metric("توقيت النظام", datetime.now().strftime("%H:%M:%S"))

        # فحص العملات القيادية
        for sym in ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]:
            try:
                # تحديث الحالة للمستخدم
                status_box.warning(f"🔍 يتم تحليل: {sym}...")
                
                # التحليل على فريم الـ 15 دقيقة (بداية الداي تريدنج)
                handler = TA_Handler(symbol=sym, screener="crypto", exchange="BINANCE", interval=Interval.INTERVAL_15_MINUTES)
                ta = handler.get_analysis()
                price = ta.indicators['close']
                
                price_box.success(f"💰 سعر {sym} الحالي: {price}")

                # برومبت القناص الصبور
                prompt_text = f"""
                Analyze {sym} at {price}. RSI={ta.indicators['RSI']}.
                Ignore noise. Look for:
                - Day Trade (15m/1h): Order Blocks or VSA confirmation.
                - Swing Trade (1h/4h): Wyckoff Accumulation/Spring or Elliott Wave 3.
                Return JSON ONLY:
                {{
                    "status": "SIGNAL",
                    "type": "DAY or SWING",
                    "school": "Specific School",
                    "logic": "Detailed explanation",
                    "entry": {price},
                    "sl": "price minus structural support",
                    "tp": "price plus next resistance"
                }} or {{"status": "WAIT"}}
                """
                
                response = model.generate_content(prompt_text)
                res = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
                
                if res.get('status') == "SIGNAL":
                    engine.record_signal(sym, res['type'], res['school'], res['logic'], res['entry'], res['sl'], res['tp'])
                    st.toast(f"🚨 فرصة {res['type']} مكتشفة!")
                    st.balloons()
            except:
                continue

        # عرض التوصيات
        with signals_placeholder.container():
            st.divider()
            st.subheader("📜 سجل الصيد الثمين (توصيات حية)")
            with sqlite3.connect(engine.db_name) as conn:
                df = pd.read_sql_query("SELECT * FROM signals ORDER BY id DESC LIMIT 10", conn)
                if df.empty:
                    st.info("النظام يبحث عن فرص قوية حالياً... الصبر هو مفتاح الأرباح في السوينج.")
                else:
                    st.table(df)

        time.sleep(30) # تحديث كل نصف دقيقة لضمان دقة التحليل

if __name__ == "__main__":
    main()
