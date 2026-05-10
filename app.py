import streamlit as st
import pandas as pd
import sqlite3
import threading
import time
from datetime import datetime
from binance.client import Client
from tradingview_ta import TA_Handler, Interval

# =================================================================
# 🛡️ الإعدادات السيادية (ممنوع المساس بها)
# =================================================================
DB_NAME = "wahba_eternal_sovereign.db"
SYMBOL = "BTCUSDT"
SAFE_WALL = 190.0  # خط الأمان الأحمر

# =================================================================
# 🧠 الذاكرة الرقمية والتعلم (Eternal Memory)
# =================================================================
def init_db():
    with sqlite3.connect(DB_NAME, check_same_thread=False) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS eternal_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                strategy TEXT,
                action TEXT,
                price REAL,
                balance REAL
            )
        """)
        conn.commit()

init_db()

# =================================================================
# ⚙️ محرك التداول المتطور (VSS + مدارس جديدة + تعلم ذاتي)
# =================================================================
def sovereign_worker(api_key, api_secret, testnet, name, interval, wait_time):
    client = Client(api_key, api_secret, testnet=testnet)
    
    while True:
        try:
            # 1. جلب الرصيد لدمج الأرباح فوراً
            asset = client.get_asset_balance(asset='USDT')
            balance = float(asset['free']) if asset else 0.0
            
            # صمام الأمان 190$
            if balance <= SAFE_WALL: break

            # 2. البحث عن المدارس الجديدة وتطبيق VSS
            handler = TA_Handler(symbol=SYMBOL, exchange="BINANCE", screener="crypto", interval=interval, timeout=15)
            analysis = handler.get_analysis()
            rec = analysis.summary['RECOMMENDATION']
            
            # تحليل السيولة (VSS Sentiment)
            depth = client.get_order_book(symbol=SYMBOL, limit=5)
            bid_v = sum([float(b[1]) for b in depth['bids']])
            ask_v = sum([float(a[1]) for a in depth['asks']])
            vss_sentiment = "BULLISH" if bid_v > ask_v else "BEARISH"
            
            price = float(client.get_symbol_ticker(symbol=SYMBOL)['price'])

            # 3. اتخاذ القرار (دمج المدارس)
            if rec == "STRONG_BUY" and vss_sentiment == "BULLISH":
                client.create_order(symbol=SYMBOL, side='BUY', type='MARKET', quantity=0.001)
                with sqlite3.connect(DB_NAME) as conn:
                    conn.execute("INSERT INTO eternal_logs (timestamp, strategy, action, price, balance) VALUES (?,?,?,?,?)",
                                 (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), name, "BUY", price, balance))
            
            elif rec == "STRONG_SELL" and vss_sentiment == "BEARISH":
                client.create_order(symbol=SYMBOL, side='SELL', type='MARKET', quantity=0.001)
                with sqlite3.connect(DB_NAME) as conn:
                    conn.execute("INSERT INTO eternal_logs (timestamp, strategy, action, price, balance) VALUES (?,?,?,?,?)",
                                 (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), name, "SELL", price, balance))

        except: pass
        time.sleep(wait_time)

# =================================================================
# 🖥️ لوحة التحكم الاحترافية (نفس تصميم الصورة)
# =================================================================
def main():
    st.set_page_config(page_title="Wahba Sovereign AI", layout="centered")
    
    # تصميم رأس الصفحة (نفس الصورة)
    st.markdown("<h1 style='text-align:center; color:#f3ba2f;'>🦅 WAHBA SOVEREIGN AI SYSTEM</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#888;'>$نظام تداول سيادي مستقل | إدارة محفظة 5000</p>", unsafe_allow_html=True)
    st.divider()

    with st.sidebar:
        st.header("🔑 إعدادات الوصول")
        ak = st.text_input("API Key", type="password")
        sk = st.text_input("Secret Key", type="password")
        is_live = st.toggle("تداول حقيقي", value=False)
        if st.button("🚀 إطلاق المحرك الذكي"):
            # تشغيل المدارس الثلاثة دون حذف أي واحدة
            threading.Thread(target=sovereign_worker, args=(ak, sk, not is_live, "السكالبينج", Interval.INTERVAL_1_MINUTE, 60), daemon=True).start()
            threading.Thread(target=sovereign_worker, args=(ak, sk, not is_live, "الداي", Interval.INTERVAL_15_MINUTES, 300), daemon=True).start()
            threading.Thread(target=sovereign_worker, args=(ak, sk, not is_live, "السوينج", Interval.INTERVAL_4_HOURS, 3600), daemon=True).start()
            st.success("المحرك بدأ العمل والبحث في المدارس!")

    if ak and sk:
        client = Client(ak, sk, testnet=not is_live)
        try:
            balance = float(client.get_asset_balance(asset='USDT')['free'])
        except: balance = 0.0

        # --- قسم صافي الرصيد (تصميم الصورة) ---
        st.write("### صافي الرصيد")
        st.markdown(f"<h1 style='font-size:65px; font-weight:bold;'>${balance:,.2f}</h1>", unsafe_allow_html=True)
        # عرض الربح التراكمي
        profit = balance - 5000 if not is_live else 0.0
        color = "#00ff00" if profit >= 0 else "#ff0000"
        st.markdown(f"<p style='color:{color}; font-size:20px;'>▲ {profit:,.2f}</p>", unsafe_allow_html=True)

        st.divider()

        # --- قسم عدادات الصفقات لكل مدرسة ---
        with sqlite3.connect(DB_NAME) as conn:
            df = pd.read_sql_query("SELECT * FROM eternal_logs", conn)
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.write("**نمط السكالبينج**")
                st.markdown(f"<h2>صفقة {len(df[df['strategy'] == 'السكالبينج'])}</h2>", unsafe_allow_html=True)
            with c2:
                st.write("**نمط الداي**")
                st.markdown(f"<h2>صفقة {len(df[df['strategy'] == 'الداي'])}</h2>", unsafe_allow_html=True)
            with c3:
                st.write("**نمط السوينج**")
                st.markdown(f"<h2>صفقة {len(df[df['strategy'] == 'السوينج'])}</h2>", unsafe_allow_html=True)

        # الرسم البياني للنمو
        if not df.empty:
            st.divider()
            st.subheader("📈 تتبع نمو الأموال (تراكمي)")
            st.line_chart(df.set_index('timestamp')['balance'])
            
            # عرض "البحث عن مدارس جديدة" كإشعار
            st.info("🧠 النظام يقوم الآن بدمج المدارس الجديدة مع VSS لمنع التلاعب.")

if __name__ == "__main__":
    main()
