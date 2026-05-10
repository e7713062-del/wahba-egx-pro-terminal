import streamlit as st
import pandas as pd
import sqlite3
import threading
import time
from datetime import datetime
from binance.client import Client
from tradingview_ta import TA_Handler, Interval

# =================================================================
# إعدادات وضع "التعليم الذاتي" (Testnet Mode)
# =================================================================
DB_NAME = "wahba_learning_v1.db"
SYMBOL = "BTCUSDT"
# تفعيل وضع الاختبار عالمياً لضمان عدم سحب أموال حقيقية
IS_TESTNET = True 

# =================================================================
# 1. إدارة ذاكرة الخبرة (Learning Memory)
# =================================================================
class LearningMemory:
    @staticmethod
    def init_db():
        with sqlite3.connect(DB_NAME) as conn:
            # ننشئ جدولاً يسجل فيه البوت "خبراته" ليتعلم منها
            conn.execute("""
                CREATE TABLE IF NOT EXISTS experience (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    time TEXT,
                    signal TEXT,
                    price REAL,
                    result TEXT
                )
            """)
            conn.commit()

    @staticmethod
    def save_lesson(signal, price, result="PENDING"):
        with sqlite3.connect(DB_NAME) as conn:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute("INSERT INTO experience (time, signal, price, result) VALUES (?, ?, ?, ?)",
                         (now, signal, price, result))

# =================================================================
# 2. محرك التداول الوهمي (Paper Trading Engine)
# =================================================================
class VirtualTrader:
    def __init__(self, api_key, api_secret):
        # الربط مع سيرفرات الاختبار (Testnet) وليس السيرفر الحقيقي
        self.client = Client(api_key, api_secret, testnet=True)

    def get_virtual_balance(self):
        try:
            asset = self.client.get_asset_balance(asset='USDT')
            return float(asset['free']) if asset else 10000.0 # رصيد وهمي افتراضي
        except:
            return 10000.0

# =================================================================
# 3. العقل الذي يتعلم (The Learning Brain)
# =================================================================
def self_learning_process(api_key, api_secret):
    v_trader = VirtualTrader(api_key, api_secret)
    LearningMemory.init_db()

    while True:
        try:
            # تحليل السوق (هنا البوت يقرأ "الدروس" من السوق)
            handler = TA_Handler(symbol=SYMBOL, exchange="BINANCE", screener="crypto", 
                                interval=Interval.INTERVAL_15_MINUTES, timeout=10)
            analysis = handler.get_analysis().summary['RECOMMENDATION']
            price = float(v_trader.client.get_symbol_ticker(symbol=SYMBOL)['price'])

            # البوت يطبق ما تعلمه
            if "BUY" in analysis:
                LearningMemory.save_lesson("BUY_EXPERIMENT", price, "EXECUTED")
                # تنفيذ أمر شراء وهمي في الـ Testnet
                v_trader.client.create_test_order(symbol=SYMBOL, side='BUY', type='MARKET', quantity=0.001)
                
            elif "SELL" in analysis:
                LearningMemory.save_lesson("SELL_EXPERIMENT", price, "EXECUTED")
                v_trader.client.create_test_order(symbol=SYMBOL, side='SELL', type='MARKET', quantity=0.001)

        except Exception as e:
            print(f"Learning Error: {e}")
        
        time.sleep(300) # يكرر التجربة كل 5 دقائق

# =================================================================
# 4. واجهة التحكم في التعليم (Learning Dashboard)
# =================================================================
def main():
    st.set_page_config(page_title="Wahba AI Learner", layout="wide")
    st.title("🎓 أكاديمية وهبة للتداول الآلي (وضع التعليم الوهمي)")
    
    st.info("هذا النظام يعمل الآن بـ 'أموال وهمية' ليعلم نفسه كيفية التعامل مع حركة السوق الحقيقية.")

    with st.sidebar:
        st.header("🔑 إعدادات Testnet")
        st.write("استخدم مفاتيح Binance Testnet هنا")
        api_k = st.text_input("Testnet Key", type="password")
        api_s = st.text_input("Testnet Secret", type="password")
        
        if st.button("بدء عملية التعلم الذاتي"):
            threading.Thread(target=self_learning_process, args=(api_k, api_s), daemon=True).start()
            st.success("انطلق البوت ليتعلم من السوق!")

    # عرض الدروس المستفادة
    st.subheader("📊 سجل الخبرات المكتسبة (ماذا تعلم البوت؟)")
    try:
        with sqlite3.connect(DB_NAME) as conn:
            df = pd.read_sql_query("SELECT * FROM experience ORDER BY id DESC LIMIT 10", conn)
            st.table(df)
    except:
        st.write("في انتظار أول درس من السوق...")

if __name__ == "__main__":
    main()
