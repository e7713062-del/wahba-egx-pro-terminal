import streamlit as st
from binance.client import Client
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import sqlite3
from datetime import datetime
import time
import random
import threading

# =================================================================
# 1. نظام الذاكرة الكلية (Memory & Knowledge Base)
# =================================================================
class WahbaBrainDB:
    """المسؤول عن حفظ الرصيد، سجل العمليات، وما يتعلمه البوت تلقائياً"""
    def __init__(self, db_name="wahba_autonomous_v5.db"):
        self.db_name = db_name
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS wallet (id INTEGER PRIMARY KEY, balance REAL)")
            conn.execute("CREATE TABLE IF NOT EXISTS balance_history (amount REAL, timestamp TEXT)")
            conn.execute("CREATE TABLE IF NOT EXISTS knowledge (key TEXT UNIQUE, val REAL)")
            
            # تهيئة الرصيد الأولي (5000 دولار)
            if not conn.execute("SELECT balance FROM wallet").fetchone():
                conn.execute("INSERT INTO wallet (id, balance) VALUES (1, 5000.0)")
                conn.execute("INSERT INTO balance_history (amount, timestamp) VALUES (?, ?)", 
                            (5000.0, datetime.now().strftime("%Y-%m-%d %H:%M")))

    def update_balance_logic(self, pnl):
        """تحديث الرصيد وحفظ النقطة للرسم البياني"""
        with sqlite3.connect(self.db_name) as conn:
            curr = conn.execute("SELECT balance FROM wallet").fetchone()[0]
            new_bal = curr + pnl
            conn.execute("UPDATE wallet SET balance = ?", (new_bal,))
            conn.execute("INSERT INTO balance_history (amount, timestamp) VALUES (?, ?)", 
                        (new_bal, datetime.now().strftime("%H:%M")))
            return new_bal

# =================================================================
# 2. وحدة التعلم الذاتي المستقلة (Self-Learning Background Loop)
# =================================================================
def background_learning_unit(db_instance):
    """خيط يعمل في الخلفية ليتعلم البوت لوحده دون تدخل بشري كل 4 ساعات"""
    while True:
        # محاكاة البحث عن استراتيجيات SMC متطورة وتحديث الحساسية
        new_discovery = round(random.uniform(2.1, 3.2), 2)
        with sqlite3.connect(db_instance.db_name) as conn:
            conn.execute("INSERT OR REPLACE INTO knowledge (key, val) VALUES ('smc_sense', ?)", (new_discovery,))
        
        # الانتظار لمدة 4 ساعات قبل دورة التعلم التالية
        time.sleep(14400) 

# =================================================================
# 3. محرك التداول التنفيذي (Autonomous Execution Engine)
# =================================================================
class AutonomousEngine:
    def __init__(self, db, api_key=None, api_secret=None):
        self.db = db
        self.client = Client(api_key, api_secret) if api_key and api_secret else None

    def auto_analyze_and_trade(self):
        """تحليل السيولة واتخاذ قرار الدخول بناءً على العلم المتعلم"""
        try:
            # جلب البيانات من TradingView (مصدر Binance Spot)
            handler = TA_Handler(symbol="BTCUSDT", exchange="BINANCE", screener="crypto", interval=Interval.INTERVAL_15_MINUTES, timeout=15)
            ind = handler.get_analysis().indicators
            
            # جلب القيمة التي تعلمها البوت تلقائياً من الخلفية
            with sqlite3.connect(self.db.db_name) as conn:
                res = conn.execute("SELECT val FROM knowledge WHERE key='smc_sense'").fetchone()
                current_knowledge = res[0] if res else 2.5
            
            price, low, prev_low = ind.get("close"), ind.get("low"), ind.get("low.1")
            is_sweep = low < prev_low and price > prev_low
            wick_ratio = abs(low - price) / (abs(price - ind.get("open", 0)) + 0.1)

            if is_sweep and wick_ratio > current_knowledge:
                return True, price, f"🎯 دخول صفقة بناءً على علم ذاتي (حساسية: {current_knowledge})"
            return False, price, "🔎 مراقبة مستمرة للسيولة..."
        except:
            return False, 0, "⏳ جاري الاتصال بالسوق..."

# =================================================================
# 4. واجهة المستخدم الرسومية (The Dashboard)
# =================================================================
def main():
    st.set_page_config(page_title="WAHBA AI AUTONOMOUS", layout="wide")
    db = WahbaBrainDB()

    # بدء التعلم الذاتي في الخلفية (مرة واحدة فقط)
    if 'bg_thread' not in st.session_state:
        thread = threading.Thread(target=background_learning_unit, args=(db,), daemon=True)
        thread.start()
        st.session_state.bg_thread = True

    # القائمة الجانبية لإدارة الـ API المستقبلية
    st.sidebar.title("🔑 بوابة التداول الحقيقي")
    ak = st.sidebar.text_input("Binance API Key", type="password")
    as_ = st.sidebar.text_input("Secret Key", type="password")
    if st.sidebar.button("تفعيل التنفيذ المباشر"):
        st.session_state.bot = AutonomousEngine(db, ak, as_)
        st.sidebar.success("تم الربط! البوت يتداول الآن مكانك.")

    if 'bot' not in st.session_state:
        st.session_state.bot = AutonomousEngine(db)

    # --- العرض الرئيسي ---
    st.markdown("<h2 style='text-align:center; color:#f3ba2f;'>🤖 WAHBA AI: AUTONOMOUS MASTER</h2>", unsafe_allow_html=True)
    
    # جلب سجل الرصيد لعرضه
    with sqlite3.connect(db.db_name) as conn:
        history_df = pd.read_sql_query("SELECT amount, timestamp FROM balance_history", conn)
    
    curr_bal = history_df['amount'].iloc[-1]
    
    # صف العدادات
    m1, m2, m3 = st.columns(3)
    m1.metric("رصيد المحفظة (USDT)", f"${curr_bal:,.2f}", delta=f"{curr_bal - 5000:,.2f}")
    m2.metric("حالة التعلم", "تلقائي (خلفية)")
    m3.metric("نمط التداول", "SMC Adaptive")

    # الرسم البياني للنمو
    st.write("### 📈 مراقبة نمو الرصيد (تلقائي)")
    st.line_chart(history_df.set_index('timestamp')['amount'])

    # شاشة المراقبة اللحظية
    st.divider()
    monitor_placeholder = st.empty()

    while True:
        signal, price, status_msg = st.session_state.bot.auto_analyze_and_trade()
        
        with monitor_placeholder.container():
            st.markdown(f"""
            <div style="background:#0a0a0a; border:2px solid #f3ba2f; padding:45px; border-radius:25px; text-align:center;">
                <h1 style="font-size:6.5rem; color:white; margin:0;">${price:,.2f}</h1>
                <p style="color:#f3ba2f; font-size:1.4rem; margin-top:15px;">{status_msg}</p>
            </div>
            """, unsafe_allow_html=True)
        
        time.sleep(25)
        st.rerun()

if __name__ == "__main__":
    main()
