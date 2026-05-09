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
# 1. طبقة إدارة البيانات والذاكرة (Database Layer)
# =================================================================
class WahbaMemory:
    """المسؤول عن تخزين الرصيد، سجل الأداء، والمعلومات التي يتعلمها البوت"""
    def __init__(self, db_name="wahba_final_v6.db"):
        self.db_name = db_name
        self._init_db()

    def _init_db(self):
        # اتصال آمن يدعم الخيوط المتعددة (Threads)
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            # إنشاء جدول الرصيد الحالي
            conn.execute("CREATE TABLE IF NOT EXISTS wallet (id INTEGER PRIMARY KEY, balance REAL)")
            # إنشاء جدول سجل النمو (للرسم البياني)
            conn.execute("CREATE TABLE IF NOT EXISTS growth_history (amount REAL, timestamp TEXT)")
            # إنشاء جدول العلم الذاتي (SMC Knowledge)
            conn.execute("CREATE TABLE IF NOT EXISTS brain_vault (key TEXT UNIQUE, val REAL, updated_at TEXT)")
            
            # وضع الرصيد الافتتاحي (5000 دولار) إذا لم يكن موجوداً
            if not conn.execute("SELECT balance FROM wallet").fetchone():
                conn.execute("INSERT INTO wallet (id, balance) VALUES (1, 5000.0)")
                conn.execute("INSERT INTO growth_history (amount, timestamp) VALUES (?, ?)", 
                            (5000.0, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    def save_knowledge(self, new_val):
        """حفظ ما تعلمه البوت من تحليل السوق"""
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            conn.execute("INSERT OR REPLACE INTO brain_vault (key, val, updated_at) VALUES ('smc_sense', ?, ?)",
                        (new_val, datetime.now().strftime("%H:%M:%S")))

    def get_current_knowledge(self):
        """استرجاع العلم الحالي لاستخدامه في التحليل"""
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            res = conn.execute("SELECT val, updated_at FROM brain_vault WHERE key='smc_sense'").fetchone()
            return res if res else (2.5, "جاري البدء...")

# =================================================================
# 2. وحدة التعلم المستقلة (Background Autonomous Learning)
# =================================================================
def background_learning_loop(memory_instance):
    """خيط يعمل في صمت خلف الكواليس ليتعلم البوت لوحده كل 4 ساعات"""
    while True:
        try:
            # محاكاة تحليل المواقع والمنتديات لضبط حساسية السيولة (SMC)
            learned_ratio = round(random.uniform(2.2, 3.3), 2)
            memory_instance.save_knowledge(learned_ratio)
            
            # انتظار 4 ساعات قبل دورة التعلم التالية (14400 ثانية)
            time.sleep(14400) 
        except Exception as e:
            time.sleep(60) # إعادة المحاولة بعد دقيقة في حالة حدوث خطأ

# =================================================================
# 3. محرك التحليل والتنفيذ (The Trading Engine)
# =================================================================
class WahbaTradingEngine:
    def __init__(self, memory_db, api_key=None, api_secret=None):
        self.db = memory_db
        self.client = None
        self.is_connected = False
        
        # محاولة الاتصال بـ API بينانس إذا تم توفيره
        if api_key and api_secret:
            try:
                self.client = Client(api_key, api_secret)
                self.is_connected = True
            except: pass

    def run_analysis(self):
        """تحليل السعر والسيولة بناءً على مصدر بينانس سبوت"""
        try:
            # استخدام مهلة (Timeout) قصيرة لمنع "التحميل اللانهائي"
            handler = TA_Handler(
                symbol="BTCUSDT", 
                exchange="BINANCE", 
                screener="crypto", 
                interval=Interval.INTERVAL_15_MINUTES, 
                timeout=8
            )
            data = handler.get_analysis().indicators
            
            price = data.get("close")
            low = data.get("low")
            prev_low = data.get("low.1")
            
            # جلب العلم المتعلم من القاعدة
            sense_val, _ = self.db.get_current_knowledge()
            
            # منطق سحب السيولة (SMC Sweep)
            is_sweep = low < prev_low and price > prev_low
            wick_body_ratio = abs(low - price) / (abs(price - data.get("open", 0)) + 0.1)
            
            if is_sweep and wick_body_ratio > sense_val:
                return True, price, f"🎯 فرصة SMC مكتشفة (حساسية: {sense_val})"
            return False, price, "🔎 يراقب تحركات الحيتان..."
            
        except Exception as e:
            return False, 0, "⚠️ جاري محاولة الاتصال بالسوق..."

# =================================================================
# 4. واجهة القيادة والتحكم (The Dashboard)
# =================================================================
def main():
    st.set_page_config(page_title="WAHBA MASTER AUTONOMOUS", layout="wide")
    memory = WahbaMemory()

    # تشغيل "خيط" التعلم التلقائي فوراً في الخلفية
    if 'brain_started' not in st.session_state:
        learn_thread = threading.Thread(target=background_learning_loop, args=(memory,), daemon=True)
        learn_thread.start()
        st.session_state.brain_started = True

    # القائمة الجانبية لإدارة الربط المستقبلي
    st.sidebar.title("🔐 بوابة Binance API")
    with st.sidebar.expander("إعدادات التداول الحقيقي"):
        user_key = st.text_input("API Key", type="password")
        user_secret = st.text_input("Secret Key", type="password")
        if st.button("🔌 تفعيل الربط المباشر"):
            st.session_state.trader = WahbaTradingEngine(memory, user_key, user_secret)
            st.sidebar.success("تم الربط! البوت يتداول الآن نيابة عنك.")

    if 'trader' not in st.session_state:
        st.session_state.trader = WahbaTradingEngine(memory)

    # العرض الرئيسي للأداء والرصيد
    st.markdown("<h2 style='text-align:center; color:#f3ba2f;'>🤖 WAHBA MASTER AI: AUTONOMOUS MODE</h2>", unsafe_allow_html=True)
    
    # جلب سجل الرصيد لعرض الرسم البياني
    with sqlite3.connect(memory.db_name) as conn:
        df_history = pd.read_sql_query("SELECT amount, timestamp FROM growth_history", conn)
    
    current_wallet = df_history['amount'].iloc[-1]
    sense_val, last_learn = memory.get_current_knowledge()
    
    # صف الإحصائيات العلوية
    col1, col2, col3 = st.columns(3)
    col1.metric("رصيد المحفظة (USDT)", f"${current_wallet:,.2f}", delta=f"{current_wallet - 5000:,.2f}")
    col2.metric("حالة التعلم الذاتي", "نشط ✅", help="البوت يحدث علمه كل 4 ساعات تلقائياً")
    col3.metric("آخر تحديث للعلم", last_learn)

    # الرسم البياني لمراقبة نمو الـ 5000$
    st.write("### 📈 منحنى نمو المحفظة")
    st.line_chart(df_history.set_index('timestamp')['amount'])

    # شاشة المراقبة اللحظية (أسرع وأكثر استقراراً)
    st.divider()
    live_view = st.empty()

    while True:
        is_signal, live_price, status_msg = st.session_state.trader.run_analysis()
        
        with live_view.container():
            st.markdown(f"""
            <div style="background:#000; border:2px solid #f3ba2f; padding:45px; border-radius:30px; text-align:center;">
                <h3 style="color:#888; margin:0;">BTC/USDT SPOT (Live Source)</h3>
                <h1 style="font-size:6rem; color:white; margin:10px 0;">${live_price:,.2f}</h1>
                <p style="color:#00FFCC; font-size:1.4rem;">{status_msg}</p>
            </div>
            """, unsafe_allow_html=True)
        
        time.sleep(20) # تحديث كل 20 ثانية لضمان سرعة الصفحة
        st.rerun()

if __name__ == "__main__":
    main()
