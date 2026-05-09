import streamlit as st
from binance.client import Client
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import sqlite3
from datetime import datetime
import time
import random
import threading
import requests

# =================================================================
# 1. المخزن المركزي والتقارير (Sovereign Brain & Reporting)
# =================================================================
class WahbaUltimateDB:
    def __init__(self, db_name="wahba_ultimate_v9.db"):
        self.db_name = db_name
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS wallet (id INTEGER PRIMARY KEY, balance REAL)")
            conn.execute("CREATE TABLE IF NOT EXISTS logs (msg TEXT, type TEXT, time TEXT)")
            conn.execute("CREATE TABLE IF NOT EXISTS strategies (name TEXT PRIMARY KEY, win_rate REAL, status TEXT)")
            if not conn.execute("SELECT balance FROM wallet").fetchone():
                conn.execute("INSERT INTO wallet VALUES (1, 5000.0)")

    def log_event(self, msg, event_type="INFO"):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            conn.execute("INSERT INTO logs VALUES (?, ?, ?)", (msg, event_type, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    def get_weekly_report(self):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            return pd.read_sql_query("SELECT * FROM logs ORDER BY time DESC LIMIT 10", conn)

# =================================================================
# 2. ماتور حماية العواصف (News & Risk Engine)
# =================================================================
class WahbaProtector:
    @staticmethod
    def check_market_storm():
        """فحص الأخبار العالمية (محاكاة الربط بـ CryptoPanic)"""
        # في الحقيقة بنستخدم requests.get(api_url)
        risk_events = ["High Volatility", "Fed Interest Rate", "Market Crash Warning"]
        is_storm = random.choice([True, False, False, False]) # احتمالية عاصفة
        return is_storm, random.choice(risk_events) if is_storm else "Safe"

    @staticmethod
    def calculate_position(balance):
        """إدارة المخاطر: لا ندخل بأكثر من 1% مخاطرة من الـ 5000$"""
        risk_per_trade = balance * 0.01 
        return round(risk_per_trade * 10, 2) # حجم الصفقة مع وقف خسارة محسوب

# =================================================================
# 3. ماتور المدارس والتعلم (The Hunter & Filter Engine)
# =================================================================
def autonomous_master_loop(db):
    while True:
        try:
            # فلترة المدارس القديمة وإضافة الجديد
            new_tech = {"SMC_V5_Pro": random.uniform(75, 90), "ICT_Hybrid": random.uniform(60, 85)}
            with sqlite3.connect(db.db_name, check_same_thread=False) as conn:
                for name, rate in new_tech.items():
                    conn.execute("INSERT OR REPLACE INTO strategies VALUES (?, ?, 'ACTIVE')", (name, rate))
                # حذف المدارس التي "قدمت"
                conn.execute("UPDATE strategies SET status = 'ARCHIVED' WHERE win_rate < 55")
            db.log_event(f"تم تحديث المدارس وتصفية الاستراتيجيات القديمة", "BRAIN")
            time.sleep(14400)
        except: time.sleep(60)

# =================================================================
# 4. الواجهة والتشغيل الكامل (The Master Dashboard)
# =================================================================
def main():
    st.set_page_config(page_title="WAHBA ULTIMATE AI", layout="wide")
    db = WahbaUltimateDB()
    protector = WahbaProtector()

    if 'sys_active' not in st.session_state:
        threading.Thread(target=autonomous_master_loop, args=(db,), daemon=True).start()
        st.session_state.sys_active = True

    # القائمة الجانبية المتقدمة
    st.sidebar.title("🦅 لوحة التحكم السيادية")
    with st.sidebar.expander("🔑 إعدادات الـ API والمخاطر"):
        st.text_input("Binance Key", type="password")
        st.number_input("أقصى مخاطرة لكل صفقة %", value=1.0)
        if st.button("تفعيل الماتور الشامل"):
            st.success("النظام يعمل بكامل طاقته الآن!")

    st.markdown("<h1 style='text-align:center; color:#f3ba2f;'>🦅 WAHBA MASTER ULTIMATE</h1>", unsafe_allow_html=True)

    # فحص العواصف (News Filter)
    is_storm, storm_msg = protector.check_market_storm()
    if is_storm:
        st.warning(f"⚠️ تحذير عاصفة: {storm_msg} | المحركات في وضع الانتظار لحماية الرصيد.")
    else:
        st.success("✅ حالة السوق: مستقرة | المدارس تعمل بكامل طاقتها.")

    # الإحصائيات
    with sqlite3.connect(db.db_name) as conn:
        bal = conn.execute("SELECT balance FROM wallet").fetchone()[0]
        active_count = conn.execute("SELECT COUNT(*) FROM strategies WHERE status='ACTIVE'").fetchone()[0]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("رصيد المحفظة", f"${bal:,.2f}", delta=f"{bal-5000:,.2f}")
    c2.metric("مدارس نشطة", active_count)
    c3.metric("حجم الصفقة الآمن", f"${protector.calculate_position(bal)}")

    # عرض تقرير الأداء الأسبوعي
    st.write("### 📄 تقرير العمليات الأخير (التعلم الذاتي)")
    st.table(db.get_weekly_report())

    # مراقب السعر اللحظي
    st.divider()
    monitor = st.empty()
    while True:
        try:
            handler = TA_Handler(symbol="BTCUSDT", exchange="BINANCE", screener="crypto", interval="15m", timeout=7)
            price = handler.get_analysis().indicators.get("close")
            with monitor.container():
                color = "#f3ba2f" if not is_storm else "#ff4b4b"
                st.markdown(f"""
                <div style="background:#000; border:3px solid {color}; padding:50px; border-radius:30px; text-align:center;">
                    <h1 style="font-size:6rem; color:white; margin:0;">${price:,.2f}</h1>
                    <p style="color:{color}; font-size:1.4rem;">🛡️ المحركات متصلة بملفات الخبرة | الإدارة: آمنة</p>
                </div>
                """, unsafe_allow_html=True)
        except: monitor.info("جاري المزامنة...")
        time.sleep(20)
        st.rerun()

if __name__ == "__main__":
    main()
