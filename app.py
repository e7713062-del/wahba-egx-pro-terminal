import streamlit as st
import google.generativeai as genai
import pandas as pd
import sqlite3
import json
import time
import ccxt
from datetime import datetime
from tradingview_ta import TA_Handler, Interval

# =================================================================
# 1. الأساسات والمفاتيح (The Foundation)
# =================================================================
GEMINI_API_KEY = "AIzaSyAHLshGDTIRhodR1CMAWGP_DH3622aADJQ" 
genai.configure(api_key=GEMINI_API_KEY)

API_KEY = "uOGPGtw8G18nxQIHKCWTn3TGfa1XoPzKbXUINnQmEZfNWGy9PabxbRXIJYKZ2w7n"
SECRET_KEY = "SFO6EXE1JGF7pfbPa1QKWbiAhU2tta0Bxsu1VDwytWyBnGbU1ji57ZRfEHn1MAxI"

# محرك الربط المباشر بمحفظة Spot
exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': SECRET_KEY,
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'} 
})

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config={"temperature": 0.3} # تقليل العشوائية لقرارات أدق
)

# =================================================================
# 2. محرك إدارة الثروة الحقيقي (Real-Time Wealth)
# =================================================================
class WahbaSovereignEngine:
    def __init__(self, db_name="wahba_wealth_master.db"):
        self.db_name = db_name
        self._setup_db()

    def _setup_db(self):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS ledger (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            time TEXT, symbol TEXT, school TEXT, 
                            logic TEXT, trade_amount REAL, balance_after REAL)""")

    def get_real_balance(self):
        try:
            # قراءة الرصيد الفعلي من بينانس
            bal = exchange.fetch_balance()
            return bal['total'].get('USDT', 0.0)
        except:
            return 0.0

    def record_trade(self, symbol, school, logic, amount, bal_after):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("""INSERT INTO ledger (time, symbol, school, logic, trade_amount, balance_after) 
                            VALUES (?,?,?,?,?,?)""",
                         (datetime.now().strftime("%H:%M:%S"), symbol, school, logic, amount, bal_after))

# =================================================================
# 3. واجهة التحكم والتنفيذ (The Master Floor)
# =================================================================
def main():
    st.set_page_config(page_title="Wahba Omni-Pulse", layout="wide", page_icon="🦅")
    engine = WahbaSovereignEngine()
    
    st.markdown("<h1 style='text-align:center; color:#f3ba2f;'>🦅 WAHBA OMNI-PULSE (REAL SYNC)</h1>", unsafe_allow_html=True)
    
    metrics_placeholder = st.empty()
    logs_placeholder = st.empty()

    while True:
        # 1. تحديث الرصيد الحقيقي من بينانس
        current_bal = engine.get_real_balance()
        
        with metrics_placeholder.container():
            c1, c2, c3 = st.columns(3)
            c1.metric("رصيد بينانس (USDT)", f"${current_bal:.2f}")
            c2.metric("الحماية على المنصة", "SL/TP ACTIVE")
            c3.metric("المدارس المدمجة", "SMC/ICT/Wyckoff/Elliott/VSA")

        # 2. طوبة التحليل والقرار (كل 12 ثانية)
        if int(time.time()) % 12 == 0:
            for sym in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
                pair = sym.replace("USDT", "/USDT")
                try:
                    handler = TA_Handler(symbol=sym, screener="crypto", exchange="BINANCE", interval=Interval.INTERVAL_1_MINUTE)
                    ta = handler.get_analysis()
                    price = ta.indicators['close']
                    
                    # التحليل الهجين بالذكاء الاصطناعي
                    prompt_text = f"""
                    Analyze {sym} at {price}. RSI={ta.indicators['RSI']}. Trend={ta.summary['RECOMMENDATION']}.
                    Use SMC, ICT, Wyckoff, Elliott Waves, and VSA. Choose the strategy that fits best now.
                    If market is sideways, wait or use Wyckoff accumulation. If trending, use Elliott/SMC.
                    Return JSON ONLY: {{"decision": "BUY", "school": "Selected School", "logic": "Specific Reason", "sl_pct": 0.8}} or WAIT.
                    """
                    
                    response = model.generate_content(prompt_text)
                    res_text = response.text.strip().replace('```json', '').replace('```', '')
                    res = json.loads(res_text)
                    
                    if res.get('decision') == "BUY":
                        # 3. التنفيذ الحقيقي (15 دولار لتخطي حد بينانس الأدنى)
                        trade_amount = 15.0 
                        
                        if current_bal >= trade_amount:
                            try:
                                # أمر الشراء
                                order = exchange.create_market_buy_order(pair, trade_amount)
                                entry_p = order.get('price', price)
                                
                                # حساب ووضع الاستوب لوز
                                sl_p = entry_p * (1 - (res.get('sl_pct', 0.8) / 100))
                                exchange.create_order(
                                    symbol=pair, type='STOP_LOSS_LIMIT', side='sell',
                                    amount=order['amount'], price=sl_p * 0.99,
                                    params={'stopPrice': sl_p}
                                )
                                
                                st.toast(f"🎯 تنفيذ ناجح: {res.get('school')} على {sym}")
                                
                                # تسجيل العملية
                                new_bal = engine.get_real_balance()
                                engine.record_trade(sym, res.get('school'), res.get('logic'), trade_amount, new_bal)
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"❌ بينانس رفضت الأوردر: {e}")
                except: 
                    continue

        # 4. السجل التاريخي للصفقات
        with logs_placeholder.container():
            st.divider()
            with sqlite3.connect(engine.db_name) as conn:
                df = pd.read_sql_query("SELECT * FROM ledger ORDER BY id DESC LIMIT 5", conn)
                if not df.empty:
                    st.write("📜 السجل السيادي للعمليات الحقيقية:")
                    st.table(df)

        time.sleep(2)

if __name__ == "__main__":
    main()
