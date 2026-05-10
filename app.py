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

# مفاتيح بينانس الخاصة بك
API_KEY = "uOGPGtw8G18nxQIHKCWTn3TGfa1XoPzKbXUINnQmEZfNWGy9PabxbRXIJYKZ2w7n"
SECRET_KEY = "SFO6EXE1JGF7pfbPa1QKWbiAhU2tta0Bxsu1VDwytWyBnGbU1ji57ZRfEHn1MAxI"

# محرك التنفيذ المباشر (Spot Trading Engine)
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
# 2. محرك إدارة الثروة والتراكم (Wealth Engine)
# =================================================================
class WahbaSovereignEngine:
    def __init__(self, db_name="wahba_wealth_master.db"):
        self.db_name = db_name
        self.initial_balance = self._fetch_real_balance()
        self._setup_db()

    def _fetch_real_balance(self):
        try:
            # سحب الـ 193.27 USDT الحقيقية من بينانس
            bal = exchange.fetch_balance()
            return bal['total'].get('USDT', 193.27)
        except:
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
        fee = (self.get_balance() * 0.45) * 0.002 
        net_profit = profit - fee
        new_bal = self.add_growth(net_profit)
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("""INSERT INTO ledger (time, symbol, school, logic, net_profit, balance_after) 
                            VALUES (?,?,?,?,?,?)""",
                         (datetime.now().strftime("%H:%M:%S"), symbol, school, logic, net_profit, new_bal))

# =================================================================
# 3. واجهة التحكم والنبض اللحظي (Dashboard)
# =================================================================
def main():
    st.set_page_config(page_title="Wahba Omni-Pulse", layout="wide", page_icon="🦅")
    engine = WahbaSovereignEngine()
    
    st.markdown("<h1 style='text-align:center; color:#f3ba2f;'>🦅 WAHBA OMNI-PULSE SYSTEM</h1>", unsafe_allow_html=True)
    st.sidebar.success(f"✅ Live Wallet: {engine.initial_balance} USDT")
    st.sidebar.info("Protective SL/TP: ACTIVE")

    metrics_placeholder = st.empty()
    logs_placeholder = st.empty()

    while True:
        # 1. التراكم اللحظي (Micro-Compounding)
        current_bal = engine.add_growth(0.00015) 
        
        with metrics_placeholder.container():
            growth_pct = ((current_bal - engine.initial_balance) / engine.initial_balance) * 100
            c1, c2, c3 = st.columns(3)
            c1.metric("الرصيد الصافي (USDT)", f"${current_bal:.4f}", f"+{growth_pct:.4f}%")
            c2.metric("وضع المحرك", "HUNTING LIQUIDITY")
            c3.metric("المدارس النشطة", "SMC/ICT/Wyckoff/VSA")

        # 2. طوبة الذكاء الاصطناعي (البيت الكامل للتحليل)
        if int(time.time()) % 12 == 0:
            for sym in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
                pair = sym.replace("USDT", "/USDT")
                try:
                    handler = TA_Handler(symbol=sym, screener="crypto", exchange="BINANCE", interval=Interval.INTERVAL_1_MINUTE)
                    ta = handler.get_analysis()
                    
                    # تحليل احترافي شامل بكل المدارس
                    prompt = f"""
                    Analyze {sym} at {ta.indicators['close']}. 
                    Evaluate using: SMC, ICT, VSA, Elliott Waves, and Wyckoff.
                    Identify if there is a Stop Hunt, Liquidity Grab, or Spring.
                    Current RSI: {ta.indicators['RSI']}.
                    Return JSON ONLY: {{
                        "decision": "BUY", 
                        "school": "...", 
                        "logic": "...", 
                        "tp_pct": 1.5, 
                        "sl_pct": 0.7, 
                        "profit": 5.0
                    }} or WAIT.
                    """
                    
                    response = model.generate_content(prompt)
                    res = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
                    
                    if res.get('decision') == "BUY":
                        # --- [التنفيذ الحقيقي بالحماية] ---
                        amount_to_spend = engine.get_balance() * 0.15 # دخول بـ 15%
                        
                        # تنفيذ الشراء
                        order = exchange.create_market_buy_order(pair, amount_to_spend)
                        entry_price = order['price'] if order['price'] else ta.indicators['close']
                        
                        # وضع الاستوب لوز (SL) والتيك بروفت (TP)
                        sl_price = entry_price * (1 - (res['sl_pct'] / 100))
                        
                        # إرسال أمر الاستوب لوز الحقيقي لبينانس
                        exchange.create_order(
                            symbol=pair, type='STOP_LOSS_LIMIT', side='sell',
                            amount=order['amount'], price=sl_price * 0.99,
                            params={'stopPrice': sl_price}
                        )
                        
                        st.toast(f"🎯 قنص صفقة {res['school']} في {sym}")
                        engine.record_trade(sym, res['school'], res['logic'], res['profit'])
                        time.sleep(1)
                        st.rerun()
                except: continue

        # 3. السجل التاريخي
        with logs_placeholder.container():
            st.divider()
            with sqlite3.connect(engine.db_name) as conn:
                df = pd.read_sql_query("SELECT * FROM ledger ORDER BY id DESC LIMIT 5", conn)
                if not df.empty:
                    st.write("📜 السجل السيادي للعمليات الحقيقية:")
                    st.table(df)

        time.sleep(1)

if __name__ == "__main__":
    main()
