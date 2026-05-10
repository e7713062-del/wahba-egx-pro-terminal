import streamlit as st
import pandas as pd
import sqlite3
import threading
import time
from datetime import datetime
from binance.client import Client
from tradingview_ta import TA_Handler, Interval

# =================================================================
# 🛡️ إعدادات النظام الحاكمة
# =================================================================
DB_NAME = "wahba_master_system.db"
SYMBOL = "BTCUSDT"
SAFE_WALL = 190.0  # رقم الأمان (الفرامل)

# =================================================================
# 🧠 إدارة البيانات والصفقات (الذاكرة)
# =================================================================
class SystemMemory:
    @staticmethod
    def init_db():
        with sqlite3.connect(DB_NAME, check_same_thread=False) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS journal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    strategy TEXT,
                    action TEXT,
                    price REAL,
                    balance REAL
                )
            """)
            conn.commit()

    @staticmethod
    def log_trade(strategy, action, price, balance):
        with sqlite3.connect(DB_NAME, check_same_thread=False) as conn:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute("""
                INSERT INTO journal (timestamp, strategy, action, price, balance)
                VALUES (?, ?, ?, ?, ?)
            """, (now, strategy, action, price, balance))
            conn.commit()

# =================================================================
# ⚙️ محرك المتداول الذكي (العقل)
# =================================================================
def trading_brain(api_key, api_secret, testnet, name, interval, wait_time):
    client = Client(api_key, api_secret, testnet=testnet)
    SystemMemory.init_db()

    while True:
        try:
            # 1. جلب الرصيد اللحظي لدمج الأرباح
            asset = client.get_asset_balance(asset='USDT')
            curr_bal = float(asset['free']) if asset else 0.0

            # 🚨 صمام الأمان 190$
            if curr_bal <= SAFE_WALL:
                break

            # 2. تحليل المدارس (VSS + Technical Analysis)
            handler = TA_Handler(symbol=SYMBOL, exchange="BINANCE", screener="crypto", interval=interval, timeout=15)
            rec = handler.get_analysis().summary['RECOMMENDATION']
            price = float(client.get_symbol_ticker(symbol=SYMBOL)['price'])

            # 3. تنفيذ الصفقات
            if rec == "STRONG_BUY":
                client.create_order(symbol=SYMBOL, side='BUY', type='MARKET', quantity=0.001)
                SystemMemory.log_trade(name, "BUY", price, curr_bal)
            elif rec == "STRONG_SELL":
                client.create_order(symbol=SYMBOL, side='SELL', type='MARKET', quantity=0.001)
                SystemMemory.log_trade(name, "SELL", price, curr_bal)

        except Exception as e:
            print(f"Error in {name}: {e}")
        
        time.sleep(wait_time)

# =================================================================
# 🖥️ لوحة التحكم (الواجهة التي ستبحث فيها عن الفلوس)
# =================================================================
def main():
    st.set_page_config(page_title="Wahba Sovereign AI", layout="wide")
    SystemMemory.init_db()

    # العنوان الرئيسي
    st.markdown("<h1 style='text-align:center; color:#00FFCC;'>🦅 نظام وهبة السيادي - المحرك الذكي</h1>", unsafe_allow_html=True)
    st.divider()

    # القائمة الجانبية (Sidebar) - افتحها من السهم في هاتفك
    with st.sidebar:
        st.header("🔑 إعدادات الوصول")
        ak = st.text_input("API Key", type="password")
        as_key = st.text_input("Secret Key", type="password")
        is_live = st.toggle("تداول حقيقي (Live)", value=False)
        
        if st.button("🚀 تشغيل المتداول الآن"):
            if ak and as_key:
                # تشغيل 3 محركات في وقت واحد (سكالبينج، داي، سوينج)
                threading.Thread(target=trading_brain, args=(ak, as_key, not is_live, "Scalping", Interval.INTERVAL_1_MINUTE, 60), daemon=True).start()
                threading.Thread(target=trading_brain, args=(ak, as_key, not is_live, "Day Trade", Interval.INTERVAL_15_MINUTES, 300), daemon=True).start()
                threading.Thread(target=trading_brain, args=(ak, as_key, not is_live, "Swing", Interval.INTERVAL_4_HOURS, 3600), daemon=True).start()
                st.success("المتداول انطلق! انتظر ثواني لتظهر البيانات.")
            else:
                st.error("أدخل المفاتيح أولاً!")

    # --- عرض "الفلوس" والصفقات (Dashboard) ---
    if ak and as_key:
        client = Client(ak, as_key, testnet=not is_live)
        try:
            balance = float(client.get_asset_balance(asset='USDT')['free'])
        except: balance = 0.0

        # عدادات الأرباح والنمو
        c1, c2, c3 = st.columns(3)
        with col1:
            st.metric("💰 الرصيد الحالي", f"${balance:,.2f}", delta=f"{balance - SAFE_WALL:.2f}")
        with col2:
            st.metric("🛑 خط الأمان", "$190.00")
        with col3:
            st.metric("📊 حالة المحرك", "يعمل 24/7" if balance > 190 else "متوقف للحماية")

        # الرسم البياني وجدول الصفقات
        st.divider()
        st.subheader("📈 تتبع نمو المحفظة اللحظي")
        with sqlite3.connect(DB_NAME) as conn:
            df = pd.read_sql_query("SELECT * FROM journal ORDER BY id DESC LIMIT 100", conn)
            if not df.empty:
                st.line_chart(df.set_index('timestamp')['balance'])
                st.write("### 📜 عدد الصفقات المنفذة")
                st.dataframe(df, use_container_width=True)
                st.write(f"إجمالي العمليات المفتوحة والمغلقة: **{len(df)} صفقة**")
            else:
                st.info("المتداول يراقب المدارس الجديدة الآن.. ستظهر الصفقات والفلوس هنا فور التنفيذ.")

if __name__ == "__main__":
    main()
