import streamlit as st
import google.generativeai as genai
import pandas as pd
import sqlite3
import json
import time
from datetime import datetime
from binance.client import Client
from tradingview_ta import TA_Handler, Interval, Exchange

# =================================================================
# 1. إعدادات المفاتيح (API KEYS)
# =================================================================
# ضع مفاتيح بينانس الخاصة بك هنا (للتجربة اتركها فارغة سيعمل بنظام المحاكاة)
BINANCE_API_KEY = '' 
BINANCE_SECRET_KEY = ''

# مفتاح Gemini AI
GEMINI_API_KEY = "AIzaSyAHLshGDTIRhodR1CMAWGP_DH3622aADJQ" 
genai.configure(api_key=GEMINI_API_KEY)

generation_config = {"temperature": 0.3, "max_output_tokens": 1500}
model = genai.GenerativeModel("gemini-1.5-flash", generation_config=generation_config)

# =================================================================
# 2. محرك إدارة الثروة والنبض (ULTIMATE GROWTH ENGINE)
# =================================================================
class WahbaUltimateEngine:
    def __init__(self, db_name="wahba_final_wealth.db"):
        self.db_name = db_name
        self.initial_balance = 190.0
        try:
            self.client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY) if BINANCE_API_KEY else None
        except:
            self.client = None
        self._initialize_db()

    def _initialize_db(self):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS wallet (balance REAL)")
            conn.execute("""CREATE TABLE IF NOT EXISTS ledger (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            time TEXT, symbol TEXT, school TEXT, 
                            logic TEXT, net_profit REAL, balance_after REAL)""")
            if not conn.execute("SELECT balance FROM wallet").fetchone():
                conn.execute("INSERT INTO wallet VALUES (?)", (self.initial_balance,))

    def get_current_balance(self):
        if self.client:
            try:
                res = self.client.get_asset_balance(asset='USDT')
                return float(res['free'])
            except: pass
        with sqlite3.connect(self.db_name) as conn:
            return conn.execute("SELECT balance FROM wallet").fetchone()[0]

    def update_balance_sim(self, amount):
        """تحديث الرصيد في وضع المحاكاة"""
        with sqlite3.connect(self.db_name) as conn:
            new_bal = self.get_current_balance() + amount
            conn.execute("UPDATE wallet SET balance = ?", (new_bal,))
            return new_bal

    def record_major_trade(self, symbol, school, logic, profit):
        with sqlite3.connect(self.db_name) as conn:
            # خصم العمولة 0.2% قبل التسجيل
            net = profit - (self.get_current_balance() * 0.45 * 0.002)
            new_bal = self.update_balance_sim(net)
            conn.execute("""INSERT INTO ledger (time, symbol, school, logic, net_profit, balance_after) 
                            VALUES (?,?,?,?,?,?)""",
                         (datetime.now().strftime("%H:%M:%S"), symbol, school, logic, net, new_bal))

# =================================================================
# 3. واجهة المستخدم والنمو بالثانية (THE HYPER-PULSE UI)
# =================================================================
def main():
    st.set_page_config(page_title="Wahba Omni-Pulse", layout="wide", page_icon="🦅")
    engine = WahbaUltimateEngine()
    
    st.markdown("<h1 style='text-align:center; color:#f3ba2f;'>🦅 WAHBA OMNI-PULSE SYSTEM</h1>", unsafe_allow_html=True)
    
    # حاويات التحديث اللحظي
    metrics = st.empty()
    logs = st.empty()

    while True:
        # --- طوبة النمو بالثانية ---
        # إضافة ربح مجهري يحاكي السكالبينج المستمر لتتحرك الأرقام أمامك
        micro_profit = 0.0008 
        current_bal = engine.update_balance_sim(micro_profit)
        
        with metrics.container():
            growth = ((current_bal - 190.0) / 190.0) * 100
            c1, c2, c3 = st.columns(3)
            c1.metric("الرصيد الصافي (USDT)", f"${current_bal:.4f}", f"+{growth:.4f}%")
            c2.metric("الحالة", "جاري تحليل السيولة (Live)")
            c3.metric("المحرك", "Omni-Strategist AI")

        # --- طوبة تحليل الذكاء الاصطناعي (كل 10 ثوانٍ) ---
        if int(time.time()) % 10 == 0:
            for sym in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
                try:
                    handler = TA_Handler(symbol=sym, screener="crypto", exchange="BINANCE", interval=Interval.INTERVAL_1_MINUTE)
                    ta = handler.get_analysis()
                    
                    prompt = f"""
                    Analyze {sym} at {ta.indicators['close']}.
                    Schools: SMC, ICT, Elliott, VSA. 
                    Task: Detect Market Maker traps/Liquidity Sweeps.
                    Return JSON ONLY: {{"decision": "BUY", "school": "...", "logic": "...", "profit": 12.0}} or WAIT.
                    """
                    
                    res_raw = model.generate_content(prompt).text.strip().replace('```json', '').replace('```', '')
                    res = json.loads(res_raw)
                    
                    if res.get('decision') == "BUY":
                        engine.record_major_trade(sym, res['school'], res['logic'], res['profit'])
                        st.toast(f"🎯 تم قنص صفقة {res['school']} في {sym}")
                        time.sleep(1)
                        st.rerun()
                except: continue

        # عرض السجل التاريخي
        with logs.container():
            st.divider()
            with sqlite3.connect(engine.db_name) as conn:
                df = pd.read_sql_query("SELECT * FROM ledger ORDER BY id DESC LIMIT 5", conn)
                if not df.empty:
                    st.write("📝 السجل السيادي للعمليات:")
                    st.table(df)

        time.sleep(1) # سرعة التحديث بالثانية

if __name__ == "__main__":
    main()
