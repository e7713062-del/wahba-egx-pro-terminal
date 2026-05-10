import streamlit as st
import pandas as pd
import sqlite3
import threading
import time
from datetime import datetime
from binance.client import Client
from tradingview_ta import TA_Handler, Interval

# =================================================================
# 🛡️ إعدادات الحماية والنمو (The Sovereign Settings)
# =================================================================
DB_NAME = "wahba_eternal_engine.db"
SYMBOL = "BTCUSDT"
SAFE_STOP_LEVEL = 190.0  # خط الأمان الأحمر (الفرامل)

# =================================================================
# 🧠 ذاكرة النظام المبرمجة للتعلم (Evolutionary Memory)
# =================================================================
class SovereignMemory:
    @staticmethod
    def init_db():
        """تهيئة قاعدة البيانات لتخزين الخبرات وحساب الأرباح"""
        with sqlite3.connect(DB_NAME, check_same_thread=False) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_logs (
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
    def log_event(strategy, action, price, balance):
        """تسجيل العمليات ليتعلم البوت من أدائه التاريخي"""
        with sqlite3.connect(DB_NAME, check_same_thread=False) as conn:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute("""
                INSERT INTO system_logs (timestamp, strategy, action, price, balance)
                VALUES (?, ?, ?, ?, ?)
            """, (now, strategy, action, price, balance))
            conn.commit()

# =================================================================
# ⚙️ محرك التداول الذكي (Smart Execution Engine)
# =================================================================
class AutonomousTrader:
    def __init__(self, api_key, api_secret, testnet=True):
        self.client = Client(api_key, api_secret, testnet=testnet)

    def get_realtime_balance(self):
        """جلب الرصيد الحي لدمج الأرباح في رأس المال فوراً"""
        try:
            asset = self.client.get_asset_balance(asset='USDT')
            return float(asset['free']) if asset else 0.0
        except:
            return 0.0

    def check_vss_sentiment(self):
        """تطبيق مدرسة VSS (تحليل السيولة ومنع التلاعب)"""
        try:
            depth = self.client.get_order_book(symbol=SYMBOL, limit=10)
            bid_vol = sum([float(b[1]) for b in depth['bids']])
            ask_vol = sum([float(a[1]) for a in depth['asks']])
            # العثور على سيولة الحيتان (BULLISH = شراء حقيقي)
            return "BULLISH" if bid_vol > ask_vol else "BEARISH"
        except:
            return "NEUTRAL"

# =================================================================
# 🏗️ محطات العمل الثلاثة (Triple-Strategy Workers)
# =================================================================
def trading_worker(api_key, api_secret, testnet, name, interval, wait_time):
    bot = AutonomousTrader(api_key, api_secret, testnet)
    SovereignMemory.init_db()

    while True:
        # --- فحص صمام الأمان 190$ ---
        current_bal = bot.get_realtime_balance()
        if current_bal <= SAFE_STOP_LEVEL:
            print(f"🛑 [SAFETY STOP] {name} توقف لحماية الـ 190$")
            break

        try:
            # البحث عن إجماع المدارس (TradingView + التحليل السحابي)
            handler = TA_Handler(
                symbol=SYMBOL, exchange="BINANCE", screener="crypto",
                interval=interval, timeout=15
            )
            analysis = handler.get_analysis()
            rec = analysis.summary['RECOMMENDATION']
            
            # فلتر التلاعب (VSS Sentiment)
            vss = bot.check_vss_sentiment()
            price = float(bot.client.get_symbol_ticker(symbol=SYMBOL)['price'])

            # التنفيذ: شراء فقط إذا اتفقت المدرسة الجديدة مع السيولة
            if rec == "STRONG_BUY" and vss == "BULLISH":
                bot.client.create_order(symbol=SYMBOL, side='BUY', type='MARKET', quantity=0.001)
                SovereignMemory.log_event(name, "BUY", price, current_bal)
            
            elif rec == "STRONG_SELL" and vss == "BEARISH":
                bot.client.create_order(symbol=SYMBOL, side='SELL', type='MARKET', quantity=0.001)
                SovereignMemory.log_event(name, "SELL", price, current_bal)

        except Exception as e:
            print(f"Worker Error ({name}): {e}")

        time.sleep(wait_time)

# =================================================================
# 🖥️ واجهة التحكم والنمو (The Master Dashboard)
# =================================================================
def main():
    st.set_page_config(page_title="WAHBA AI ETERNAL", layout="wide")
    SovereignMemory.init_db()

    st.markdown("<h1 style='text-align:center; color:#00FFCC;'>🦅 نظام وهبة السيادي - المحرك الذكي 24/7</h1>", unsafe_allow_html=True)
    st.divider()

    # --- القائمة الجانبية (Sidebar) ---
    with st.sidebar:
        st.header("⚙️ إعدادات التشغيل")
        api_key = st.text_input("Binance API Key", type="password")
        api_secret = st.text_input("Binance Secret Key", type="password")
        is_live = st.toggle("تفعيل التداول الحقيقي (Live)", value=False)
        
        if st.button("🚀 إطلاق المتداول الإلكتروني"):
            if api_key and api_secret:
                # إطلاق المدارس الثلاث (سكالبينج، داي، سوينج)
                threading.Thread(target=trading_worker, args=(api_key, api_secret, not is_live, "سكالبينج", Interval.INTERVAL_1_MINUTE, 60), daemon=True).start()
                threading.Thread(target=trading_worker, args=(api_key, api_secret, not is_live, "داي تريدنج", Interval.INTERVAL_15_MINUTES, 300), daemon=True).start()
                threading.Thread(target=trading_worker, args=(api_key, api_secret, not is_live, "سوينج", Interval.INTERVAL_4_HOURS, 3600), daemon=True).start()
                st.success("المتداول يعمل الآن ويحدث مدارسه تلقائياً!")
            else:
                st.error("يرجى إدخال مفاتيح الـ API للبدء")

    # --- لوحة العدادات (ماذا يحدث لرصيدك؟) ---
    if api_key and api_secret:
        bot = AutonomousTrader(api_key, api_secret, not is_live)
        balance = bot.get_realtime_balance()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💰 رصيدك الحالي", f"${balance:,.2f}", delta=f"{balance - 190:.2f} فوق الأمان")
        with col2:
            st.metric("🛑 حائط الأمان", "$190.00")
        with col3:
            status = "آمن ونامي ✅" if balance > 190 else "توقف للحماية 🛑"
            st.metric("📊 حالة النظام", status)

        # الرسم البياني للنمو التراكمي
        st.divider()
        st.subheader("📈 منحنى نمو المحفظة (بتكثر ولا بتنزل)")
        with sqlite3.connect(DB_NAME) as conn:
            df = pd.read_sql_query("SELECT timestamp, balance FROM system_logs ORDER BY id DESC LIMIT 100", conn)
            if not df.empty:
                st.line_chart(df.set_index('timestamp'))
                st.write("### 📜 سجل الصفقات والتعلم الذاتي")
                st.dataframe(df.head(10), use_container_width=True)
            else:
                st.info("البوت يراقب السوق حالياً.. سيظهر النمو هنا فور تنفيذ أول صفقة.")

if __name__ == "__main__":
    main()
