import streamlit as st
import pandas as pd
import sqlite3
import threading
import time
import sys
from datetime import datetime
from binance.client import Client
from tradingview_ta import TA_Handler, Interval

# =================================================================
# 1. إعدادات الأمان الصارمة
# =================================================================
DB_NAME = "wahba_sovereign_pro.db"
SYMBOL = "BTCUSDT"
TRADE_AMOUNT_USDT = 50.0 
# الخط الأحمر: الرصيد الذي إذا وصل إليه البوت يغلق نفسه فوراً
STOP_LOSS_THRESHOLD = 170.0 

# =================================================================
# 2. إدارة البيانات
# =================================================================
class DatabaseManager:
    @staticmethod
    def init_db():
        with sqlite3.connect(DB_NAME, check_same_thread=False) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    time TEXT,
                    symbol TEXT,
                    side TEXT,
                    price REAL,
                    status TEXT
                )
            """)
            conn.commit()

    @staticmethod
    def log_trade(side, price):
        with sqlite3.connect(DB_NAME, check_same_thread=False) as conn:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute(
                "INSERT INTO trades (time, symbol, side, price, status) VALUES (?, ?, ?, ?, ?)",
                (now, SYMBOL, side, price, "EXECUTED")
            )
            conn.commit()

# =================================================================
# 3. محرك التداول (مع ميزة الفحص الذاتي)
# =================================================================
class TradingEngine:
    def __init__(self, api_key, api_secret, testnet=True):
        self.client = Client(api_key, api_secret, testnet=testnet)

    def get_actual_balance(self):
        """جلب الرصيد الحقيقي من بينانس"""
        try:
            asset = self.client.get_asset_balance(asset='USDT')
            return float(asset['free']) if asset else 0.0
        except:
            return 0.0

    def execute_trade(self, side):
        try:
            # فحص أمان إضافي قبل التنفيذ
            if self.get_actual_balance() <= STOP_LOSS_THRESHOLD:
                return False

            avg_price = float(self.client.get_avg_price(symbol=SYMBOL)['price'])
            quantity = round(TRADE_AMOUNT_USDT / avg_price, 6)
            
            self.client.create_order(symbol=SYMBOL, side=side, type='MARKET', quantity=quantity)
            DatabaseManager.log_trade(side, avg_price)
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

# =================================================================
# 4. العقل المدبر (The Brain - Auto Termination Logic)
# =================================================================
def brain_worker(api_key, api_secret, testnet):
    """هذا الجزء هو المسؤول عن إيقاف البوت لوحده"""
    engine = TradingEngine(api_key, api_secret, testnet)
    
    while True:
        # 🛡️ التحقق من صمام الأمان
        current_balance = engine.get_actual_balance()
        
        if current_balance <= STOP_LOSS_THRESHOLD:
            # تسجيل حالة التوقف الإجباري في القنصل والواجهة
            print(f"🚨🚨 إيقاف ذاتي! الرصيد الحالي {current_balance}$ وصل للحد الأدنى.")
            st.session_state.bot_running = False
            st.session_state.kill_message = f"تم إيقاف البوت ذاتياً لحماية الرصيد المتبقي ({current_balance}$)"
            break # الخروج من الحلقة يقتل هذا الخيط (Thread) نهائياً

        try:
            # تحليل السوق عبر TradingView
            handler = TA_Handler(
                symbol=SYMBOL, exchange="BINANCE", screener="crypto",
                interval=Interval.INTERVAL_15_MINUTES, timeout=10
            )
            analysis = handler.get_analysis().summary['RECOMMENDATION']

            if analysis == "STRONG_BUY":
                engine.execute_trade("BUY")
            elif analysis == "STRONG_SELL":
                engine.execute_trade("SELL")

        except Exception as e:
            print(f"Analysis Error: {e}")
        
        # الانتظار 5 دقائق قبل الدورة القادمة
        time.sleep(300)

# =================================================================
# 5. واجهة التحكم (Command Center)
# =================================================================
def main():
    st.set_page_config(page_title="Wahba Auto-Shield", layout="wide")
    DatabaseManager.init_db()

    if 'bot_running' not in st.session_state:
        st.session_state.bot_running = False

    st.markdown("<h1 style='text-align:center; color:#f3ba2f;'>🛡️ نظام وهبة السيادي (إيقاف ذاتي ذكي)</h1>", unsafe_allow_html=True)
    
    # رسالة التوقف الإجباري إذا حدثت
    if 'kill_message' in st.session_state:
        st.error(st.session_state.kill_message)

    with st.sidebar:
        st.header("🔑 إعدادات الحماية")
        api_key = st.text_input("API Key", type="password")
        api_secret = st.text_input("API Secret", type="password")
        mode = st.toggle("تداول حقيقي (Live)", value=False)
        
        if st.button("🚀 تشغيل البوت"):
            if api_key and api_secret:
                st.session_state.bot_running = True
                threading.Thread(target=brain_worker, args=(api_key, api_secret, not mode), daemon=True).start()
                st.success("البوت قيد العمل حالياً.. سيقوم بفصل نفسه عند الخطر.")

    # عرض البيانات
    if api_key and api_secret:
        engine = TradingEngine(api_key, api_secret, not mode)
        balance = engine.get_actual_balance()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("الرصيد الحي", f"${balance:,.2f}")
        c2.metric("حد الإيقاف الذاتي", f"${STOP_LOSS_THRESHOLD}")
        c3.status("حالة المحرك", state="running" if st.session_state.bot_running else "stopped")

        st.subheader("📝 سجل العمليات")
        with sqlite3.connect(DB_NAME) as conn:
            df = pd.read_sql_query("SELECT * FROM trades ORDER BY id DESC LIMIT 5", conn)
            st.table(df)

if __name__ == "__main__":
    main()
