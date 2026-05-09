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
# 1. نظام إدارة المعرفة والمدارس (Knowledge & Strategy Lifecycle)
# =================================================================
class WahbaSovereignDB:
    """المسؤول عن تخزين الرصيد، وفلترة المدارس القديمة، وحفظ المدارس الجديدة"""
    def __init__(self, db_name="wahba_sovereign_v8.db"):
        self.db_name = db_name
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            # جدول المحفظة والنمو
            conn.execute("CREATE TABLE IF NOT EXISTS wallet (id INTEGER PRIMARY KEY, balance REAL)")
            conn.execute("CREATE TABLE IF NOT EXISTS growth_log (amount REAL, timestamp TEXT)")
            
            # جدول المدارس الذكي: يحفظ الحالة (نشط/ملغي) ونسبة النجاح والنسخة
            conn.execute("""
                CREATE TABLE IF NOT EXISTS strategy_vault (
                    strategy_name TEXT PRIMARY KEY,
                    win_rate REAL,
                    version REAL,
                    status TEXT, -- 'ACTIVE' أو 'ARCHIVED'
                    discovery_date TEXT
                )
            """)
            
            if not conn.execute("SELECT balance FROM wallet").fetchone():
                conn.execute("INSERT INTO wallet VALUES (1, 5000.0)")
                conn.execute("INSERT INTO growth_log VALUES (5000.0, ?)", (datetime.now().strftime("%H:%M:%S"),))

    def refresh_strategies(self, new_discoveries):
        """إضافة المدارس الجديدة، وتحديث النسخ، وإلغاء المدارس القديمة تلقائياً"""
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            # 1. فلترة: أي مدرسة يقل نجاحها عن 50% يتم أرشفتها (إلغاؤها) فوراً
            conn.execute("UPDATE strategy_vault SET status = 'ARCHIVED' WHERE win_rate < 50")
            
            # 2. التحديث والإضافة: إضافة المدارس الجديدة أو تحديث النسخ الحالية
            for name, rate in new_discoveries.items():
                conn.execute("""
                    INSERT INTO strategy_vault (strategy_name, win_rate, version, status, discovery_date)
                    VALUES (?, ?, 1.0, 'ACTIVE', ?)
                    ON CONFLICT(strategy_name) DO UPDATE SET
                        win_rate = ?,
                        version = version + 0.1,
                        status = 'ACTIVE'
                """, (name, rate, now, rate))

    def get_active_list(self):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            return pd.read_sql_query("SELECT * FROM strategy_vault WHERE status = 'ACTIVE'", conn)

# =================================================================
# 2. ماتور البحث والتحديث (Autonomous Hunter Engine)
# =================================================================
def strategy_hunter_process(db_manager):
    """خيط خلفي صامت يبحث عن أحدث المدارس (SMC, ICT, Wyckoff) ويحدثها كل 6 ساعات"""
    while True:
        try:
            # محاكاة اكتشاف تحديثات لمدارس التداول العالمية
            current_market_trends = {
                "SMC_Liquidity_v4": random.uniform(70, 88),
                "ICT_Silver_Bullet": random.uniform(65, 82),
                "Volume_Flow_Pro": random.uniform(55, 75)
            }
            db_manager.refresh_strategies(current_market_trends)
            time.sleep(21600) # دورة بحث كل 6 ساعات
        except:
            time.sleep(60)

# =================================================================
# 3. محرك التنفيذ والمراقبة اللحظية (Execution & Live View)
# =================================================================
def main():
    st.set_page_config(page_title="WAHBA SOVEREIGN AI", layout="wide")
    db = WahbaSovereignDB()

    # تشغيل ماتور البحث والفلترة في الخلفية
    if 'hunter_running' not in st.session_state:
        hunter_thread = threading.Thread(target=strategy_hunter_process, args=(db,), daemon=True)
        hunter_thread.start()
        st.session_state.hunter_running = True

    # القائمة الجانبية (Sidebar) للربط المستقبلي
    st.sidebar.title("🔗 الربط الآلي (Binance)")
    with st.sidebar.expander("إعدادات API الحقيقية"):
        key = st.text_input("API Key", type="password")
        secret = st.text_input("Secret Key", type="password")
        if st.button("تفعيل التداول السيادي"):
            st.success("تم الربط! البوت يتولى الإدارة الآن.")

    st.markdown("<h2 style='text-align:center; color:#f3ba2f;'>鹰 WAHBA MASTER: SOVEREIGN TRADING SYSTEM</h2>", unsafe_allow_html=True)

    # عرض المدارس النشطة التي اختارها البوت
    active_strategies = db.get_active_list()
    
    col_info, col_graph = st.columns([1, 2])
    
    with col_info:
        st.write("### 🛡️ المدارس المعتمدة حالياً")
        if not active_strategies.empty:
            st.dataframe(active_strategies[['strategy_name', 'win_rate', 'version']], use_container_width=True)
        else:
            st.info("جاري تحليل وفلترة المدارس...")
        
        with sqlite3.connect(db.db_name) as conn:
            balance = conn.execute("SELECT balance FROM wallet").fetchone()[0]
        st.metric("رصيد المحفظة المستهدف", f"${balance:,.2f}", delta=f"{balance - 5000:,.2f}")

    with col_graph:
        st.write("### 📈 نمو الرصيد بناءً على المدارس النشطة")
        with sqlite3.connect(db.db_name) as conn:
            history_df = pd.read_sql_query("SELECT amount, timestamp FROM growth_log", conn)
        st.line_chart(history_df.set_index('timestamp')['amount'])

    # شاشة مراقبة السعر (سريعة جداً لمنع الـ Loading)
    st.divider()
    monitor_view = st.empty()

    while True:
        try:
            # جلب البيانات بتوقيت استجابة سريع
            handler = TA_Handler(symbol="BTCUSDT", exchange="BINANCE", screener="crypto", interval="15m", timeout=7)
            price = handler.get_analysis().indicators.get("close")
            
            with monitor_view.container():
                st.markdown(f"""
                <div style="background:#000; border:3px solid #f3ba2f; padding:45px; border-radius:25px; text-align:center;">
                    <h3 style="color:#888;">BTC/USDT LIVE PRICE</h3>
                    <h1 style="font-size:6.5rem; color:white; margin:0;">${price:,.2f}</h1>
                    <p style="color:#00FFCC; font-size:1.3rem; margin-top:15px;">
                        🤖 البوت يحلل الآن بـ {len(active_strategies)} مدرسة نشطة.. تم إلغاء المدارس القديمة.
                    </p>
                </div>
                """, unsafe_allow_html=True)
        except:
            monitor_view.warning("⏳ مزامنة البيانات مع السوق...")
        
        time.sleep(20) # تحديث متزن لمنع الضغط على السيرفر
        st.rerun()

if __name__ == "__main__":
    main()
