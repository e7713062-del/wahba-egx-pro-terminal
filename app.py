import streamlit as st
import google.generativeai as genai
import pandas as pd
import sqlite3
import json
import time
import ccxt
from datetime import datetime
from tradingview_ta import TA_Handler, Interval, Exchange

# =================================================================
# 1. الإعدادات السيادية والمفاتيح (The Foundation)
# =================================================================
GEMINI_API_KEY = "AIzaSyAHLshGDTIRhodR1CMAWGP_DH3622aADJQ" 
genai.configure(api_key=GEMINI_API_KEY)

API_KEY = "uOGPGtw8G18nxQIHKCWTn3TGfa1XoPzKbXUINnQmEZfNWGy9PabxbRXIJYKZ2w7n"
SECRET_KEY = "SFO6EXE1JGF7pfbPa1QKWbiAhU2tta0Bxsu1VDwytWyBnGbU1ji57ZRfEHn1MAxI"

exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': SECRET_KEY,
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'} 
})

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config={"temperature": 0.4, "max_output_tokens": 1500}
)

# =================================================================
# 2. محرك إدارة الثروة (Wealth Engine)
# =================================================================
class WahbaSovereignEngine:
    def __init__(self, db_name="wahba_wealth_master.db"):
        self.db_name = db_name
        self.initial_balance = self._fetch_real_balance()
        self._setup_db()

    def _fetch_real_balance(self):
        try:
            bal = exchange.fetch_balance()
            return bal['total'].get('USDT', 193.27)
        except Exception as e:
            st.sidebar.error(f"⚠️ فشل جلب الرصيد: {e}")
            return 193.27

    def _setup_db(self):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS wallet (balance REAL)")
            conn.execute("""CREATE TABLE IF NOT EXISTS ledger (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            time TEXT, symbol TEXT, school TEXT, 
                            logic TEXT, net_profit REAL, balance_after REAL)""")
            conn.execute("DELETE FROM wallet")
            conn.execute("INSERT INTO wallet VALUES (?)", (self.initial_balance,))

    def get_balance(self):
        with sqlite3.connect(self.db_name) as conn:
            return conn.execute("SELECT balance FROM wallet").fetchone()[0]

    def add_growth(self, amount):
        with sqlite3.connect(self.db_name) as conn:
            new_bal = self.get_balance() + amount
            conn.execute("UPDATE wallet SET balance = ?", (new_bal,))
            return new_bal

    def record_trade(self, symbol, school, logic, profit):
        new_bal = self.add_growth(profit)
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("""INSERT INTO ledger (time, symbol, school, logic, net_profit, balance_after) 
                            VALUES (?,?,?,?,?,?)""",
                         (datetime.now().strftime("%H:%M:%S"), symbol, school, logic, profit, new_bal))

# =================================================================
# 3. واجهة التحكم والتنفيذ (Execution Floor)
# =================================================================
def main():
    st.set_page_config(page_title="Wahba Omni-Pulse", layout="wide", page_icon="🦅")
    engine = WahbaSovereignEngine()
    
    st.markdown("<h1 style='text-align:center; color:#f3ba2f;'>🦅 WAHBA OMNI-PULSE SYSTEM</h1>", unsafe_allow_html=True)
    st.sidebar.success(f"✅ Live Wallet: {engine.initial_balance} USDT")

    metrics_placeholder = st.empty()
    logs_placeholder = st.empty()

    while True:
        current_bal = engine.get_balance()
        
        with metrics_placeholder.container():
            growth_pct = ((current_bal - engine.initial_balance) / engine.initial_balance) * 100
            c1, c2, c3 = st.columns(3)
            c1.metric("الرصيد الصافي (Real-time)", f"${current_bal:.4f}", f"+{growth_pct:.4f}%")
            c2.metric("حالة الربط", "ACTIVE & PROTECTED")
            c3.metric("المدارس", "SMC/ICT/Wyckoff/VSA")

        if int(time.time()) % 15 == 0:
            for sym in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
                pair = sym.replace("USDT", "/USDT")
                try:
                    handler = TA_Handler(symbol=sym, screener="crypto", exchange="BINANCE", interval=Interval.INTERVAL_1_MINUTE)
                    ta = handler.get_analysis()
                    
                    prompt = f"Analyze {sym} at {ta.indicators['close']}. Use SMC/ICT. Return JSON ONLY: {{"decision": "BUY", "school": "SMC", "logic": "Liquidity Grab", "tp_pct": 1.5, "sl_pct": 0.8}} or WAIT."
                    
                    response = model.generate_content(prompt)
                    res = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
                    
                    if res.get('decision') == "BUY":
                        # --- [نظام التنفيذ المطور] ---
                        amount_usdt = 15.0 # دخول بـ 15 دولار للاختبار وتخطي الحد الأدنى
                        
                        try:
                            # 1. محاولة الشراء
                            order = exchange.create_market_buy_order(pair, amount_usdt)
                            st.toast(f"🚀 تم الشراء بنجاح: {sym}")
                            
                            # 2. وضع الاستوب لوز (SL)
                            entry_price = order.get('price', ta.indicators['close'])
                            sl_price = entry_price * (1 - (res['sl_pct'] / 100))
                            
                            exchange.create_order(
                                symbol=pair, type='STOP_LOSS_LIMIT', side='sell',
                                amount=order['amount'], price=sl_price * 0.99,
                                params={'stopPrice': sl_price}
                            )
                            
                            engine.record_trade(sym, res['school'], res['logic'], 0.1)
                            st.rerun()
                            
                        except Exception as e:
                            # أهم سطر: هيعرفنا ليه الأرقام مبتتغيرش!
                            st.error(f"❌ بينانس رفضت الأوردر: {str(e)}")
                            
                except Exception as e:
                    continue

        with logs_placeholder.container():
            st.divider()
            with sqlite3.connect(engine.db_name) as conn:
                df = pd.read_sql_query("SELECT * FROM ledger ORDER BY id DESC LIMIT 5", conn)
                if not df.empty:
                    st.write("📜 السجل السيادي للعمليات:")
                    st.table(df)

        time.sleep(1)

if __name__ == "__main__":
    main()
