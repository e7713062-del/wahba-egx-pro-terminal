import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import sqlite3
from datetime import datetime
import time
import threading
import ccxt # المكتبة المسؤولة عن التنفيذ الفعلي على Binance

# =================================================================
# 1. نظام الذاكرة والإدارة المالية (Sovereign Memory)
# =================================================================
class WahbaSovereignMemory:
    def __init__(self, db_name="wahba_sovereign_v2.db"):
        self.db_name = db_name
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS wallet (id INTEGER PRIMARY KEY, balance REAL)")
            conn.execute("CREATE TABLE IF NOT EXISTS trade_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, style TEXT, pnl REAL, time TEXT, status TEXT)")
            # تعديل البداية لـ 190 دولار
            if not conn.execute("SELECT balance FROM wallet").fetchone():
                conn.execute("INSERT INTO wallet VALUES (1, 190.0)")

    def get_balance(self):
        with sqlite3.connect(self.db_name) as conn:
            return conn.execute("SELECT balance FROM wallet").fetchone()[0]

    def update_balance(self, pnl, style, status):
        with sqlite3.connect(self.db_name) as conn:
            curr = self.get_balance()
            new_bal = curr + pnl
            conn.execute("UPDATE wallet SET balance = ?", (new_bal,))
            conn.execute("INSERT INTO trade_logs (style, pnl, time, status) VALUES (?, ?, ?, ?)",
                         (style, pnl, datetime.now().strftime("%H:%M:%S"), status))

# =================================================================
# 2. محرك التداول المباشر (Live Trading Engine)
# =================================================================
class WahbaBot:
    def __init__(self, memory, api_key=None, secret_key=None):
        self.memory = memory
        # إعداد الاتصال بالمنصة (Binance)
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret_key,
            'enableRateLimit': True,
        })
        self.stop_limit = 160.0 # حد التوقف الذي طلبته

    def check_stop_loss(self):
        """التأكد من أن الرصيد لم يكسر حاجز الـ 160"""
        if self.memory.get_balance() <= self.stop_limit:
            return False
        return True

    def fetch_price(self, symbol="BTC/USDT"):
        ticker = self.exchange.fetch_ticker(symbol)
        return ticker['last']

    def trade_logic(self, interval_str, style_name):
        if not self.check_stop_loss():
            return "STOPPED"

        try:
            handler = TA_Handler(symbol="BTCUSDT", exchange="BINANCE", screener="crypto", interval=interval_str, timeout=5)
            rec = handler.get_analysis().summary['RECOMMENDATION']

            # إذا كانت التوصية شراء قوي
            if rec == "STRONG_BUY":
                # هنا يتم وضع أمر شراء حقيقي، حالياً يحاكي الربح/الخسارة لتجربة الكود
                pnl = 2.5  # مثال لربح
                self.memory.update_balance(pnl, style_name, "SUCCESS")
                return "TRADED"
            return "SCANNING"
        except Exception as e:
            return f"ERROR: {str(e)}"

# =================================================================
# 3. الواجهة الرسومية (Streamlit Dashboard)
# =================================================================
def main():
    st.set_page_config(page_title="WAHBA SOVEREIGN", layout="wide")
    memory = WahbaSovereignMemory()
    
    # واجهة إدخال الـ API في الجانب
    st.sidebar.title("🔐 إعدادات Binance API")
    key = st.sidebar.text_input("API Key", type="password")
    secret = st.sidebar.text_input("Secret Key", type="password")
    
    bot = WahbaBot(memory, key, secret)

    # الهيدر
    st.markdown("<h1 style='text-align:center; color:#f3ba2f;'>🦅 WAHBA SOVEREIGN AI</h1>", unsafe_allow_html=True)
    
    # شاشة التوقف التحذيرية
    bal = memory.get_balance()
    if bal <= 160:
        st.error(f"🚨 تم إيقاف النظام فورياً! الرصيد الحالي {bal}$ وصل لحد التوقف (160$)")
        st.button("إعادة تشغيل النظام (تحذير)")
    
    # عرض العدادات
    c1, c2, c3 = st.columns(3)
    c1.metric("الرصيد الحالي", f"${bal:.2f}", delta=f"{bal-190:.2f}")
    c2.metric("حالة الأمان", "آمن" if bal > 160 else "مخاطرة عالية")
    c3.metric("الهدف القادم", "$250.00")

    # تشغيل البوت في الخلفية (عند الضغط على زر التفعيل)
    if st.sidebar.button("تشغيل البوت الآن"):
        st.sidebar.success("تم تفعيل المحرك الثلاثي")
        # تشغيل العمليات
        status = bot.trade_logic(Interval.INTERVAL_1_MINUTE, "SCALPING")
        st.write(f"العملية الحالية: {status}")

    # عرض البيانات
    with sqlite3.connect(memory.db_name) as conn:
        df = pd.read_sql_query("SELECT * FROM trade_logs ORDER BY id DESC LIMIT 5", conn)
    
    st.subheader("📊 سجل آخر العمليات")
    st.table(df)

    # مراقب السعر المباشر
    st.divider()
    try:
        price = bot.fetch_price()
        st.markdown(f"""
            <div style="background:#000; padding:30px; border-radius:15px; text-align:center; border: 2px solid #f3ba2f">
                <h2 style="color:white">BTC/USDT LIVE</h2>
                <h1 style="color:#00ffcc; font-size:50px">${price:,.2f}</h1>
                <p style="color:gray">نظام وهبة السيادي - مراقبة لحظية</p>
            </div>
        """, unsafe_allow_html=True)
    except:
        st.warning("يرجى إدخال API Key صحيح للاتصال بالمنصة")

    time.sleep(5)
    st.rerun()

if __name__ == "__main__":
    main()
