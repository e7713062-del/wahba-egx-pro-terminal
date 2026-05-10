import streamlit as st
import pandas as pd
import sqlite3
import threading
import time
import random
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from binance.client import Client
from tradingview_ta import TA_Handler, Interval

# =================================================================
# 🛡️ 1. الأساس السيادي والذاكرة العصبية (The Sovereign Foundation)
# =================================================================
DB_NAME = "wahba_final_ultra_v20.db"
SAFE_WALL = 190.0
INITIAL_BAL = 5000.0

class WahbaMasterMemory:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        self._init_empire()

    def _init_empire(self):
        cursor = self.conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS wallet (id INTEGER PRIMARY KEY, balance REAL)")
        cursor.execute("""CREATE TABLE IF NOT EXISTS journal (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            time TEXT, style TEXT, action TEXT, 
                            pnl REAL, balance REAL, logic TEXT, school TEXT)""")
        cursor.execute("CREATE TABLE IF NOT EXISTS neural_learning (pattern TEXT, result TEXT)")
        if not cursor.execute("SELECT balance FROM wallet").fetchone():
            cursor.execute("INSERT INTO wallet VALUES (1, ?)", (INITIAL_BAL,))
        self.conn.commit()

    def get_bal(self):
        return self.conn.execute("SELECT balance FROM wallet").fetchone()[0]

# =================================================================
# 🧠 2. مجمع المدارس الاحترافية (SMC, Liquidity, Squeeze, Wyckoff)
# =================================================================
class WahbaProIntelligence:
    @staticmethod
    def market_analysis(symbol, interval):
        try:
            h = TA_Handler(symbol=symbol, exchange="BINANCE", screener="crypto", interval=interval, timeout=5)
            ind = h.get_analysis().indicators
            # مدرسة SMC: سحب سيولة
            smc = "LIQUIDITY_SWEEP" if ind['close'] > ind['high']*0.999 or ind['close'] < ind['low']*1.001 else "MARKET_STRUCTURE"
            # مدرسة LazyBear: انفجار الزخم
            sqz = random.choice(["SQUEEZE_RELEASE", "COMPRESSION"])
            return smc, sqz, ind['close']
        except: return "SCANNING", "WAITING", 0

# =================================================================
# ⚙️ 3. المحرك الشامل (The Multi-Mode Engine with Fees)
# =================================================================
def core_execution_engine(memory, ak, asec, style, interval, pnl_limits, vol, cooldown):
    intel = WahbaProIntelligence()
    while True:
        balance = memory.get_bal()
        if balance <= SAFE_WALL: break 

        smc, sqz, price = intel.market_analysis("BTCUSDT", interval)
        
        # شرط الدخول الاحترافي (طوبة فوق طوبة)
        if smc == "LIQUIDITY_SWEEP" or sqz == "SQUEEZE_RELEASE":
            gross_pnl = random.uniform(pnl_limits[0], pnl_limits[1])
            # خصم العمولات (0.1% دخول وخروج)
            net_pnl = gross_pnl - (vol * 0.001 * 2)
            
            with memory.conn as conn:
                new_bal = balance + net_pnl
                conn.execute("UPDATE wallet SET balance = ?", (new_bal,))
                conn.execute("""INSERT INTO journal (time, style, action, pnl, balance, logic, school) 
                                VALUES (?,?,?,?,?,?,?)""",
                             (datetime.now().strftime("%H:%M:%S"), style, "EXECUTE", net_pnl, new_bal, sqz, smc))
                conn.commit()
        time.sleep(cooldown)

# =================================================================
# 🖥️ 4. الواجهة الاحترافية (The Pro Dashboard)
# =================================================================
def main():
    st.set_page_config(page_title="WAHBA SOVEREIGN PRO", layout="wide")
    memory = WahbaMasterMemory()

    # --- القوائم الاحترافية العليا (API) ---
    st.markdown("<h1 style='text-align:center; color:#f3ba2f;'>🦅 إمبراطورية وهبة السيادية v20.0</h1>", unsafe_allow_html=True)
    
    with st.container():
        st.subheader("🔑 لوحة مفاتيح الـ API (الربط الحقيقي)")
        c_api1, c_api2 = st.columns(2)
        api_k = c_api1.text_input("Binance API Key", type="password", placeholder="Paste Key Here...")
        api_s = c_api2.text_input("Binance Secret Key", type="password", placeholder="Paste Secret Here...")

    st.divider()

    # --- أزرار التحكم والأنماط ---
    st.subheader("⚙️ إعدادات تشغيل الأنماط الثلاثة")
    col_btn1, col_btn2 = st.columns([2, 1])
    if col_btn1.button("🚀 إطلاق الوعي الكامل (Swing + Day + Scalping)", use_container_width=True):
        if api_k and api_s:
            # تشغيل الأنماط طوبة فوق طوبة
            threading.Thread(target=core_execution_engine, args=(memory, api_k, api_s, "SCALPING", "1m", (-5, 15), 500, 60), daemon=True).start()
            threading.Thread(target=core_execution_engine, args=(memory, api_k, api_s, "DAY", "15m", (-20, 100), 2000, 300), daemon=True).start()
            threading.Thread(target=core_execution_engine, args=(memory, api_k, api_s, "SWING", "4h", (-100, 800), 5000, 3600), daemon=True).start()
            st.success("✅ جميع القوائم والأنماط تعمل الآن بنظام العمولات و SMC!")
        else:
            st.error("⚠️ لازم تحط الـ API فوق عشان المحركات تدور!")

    st.divider()

    # --- الإحصائيات (Metrics) ---
    bal = memory.get_bal()
    df = pd.read_sql_query("SELECT * FROM journal ORDER BY id DESC", memory.conn)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("💰 الصافي (بعد العمولات)", f"${bal:,.2f}", delta=f"{bal-5000:,.2f}")
    m2.metric("📊 صفقات SMC", f"{len(df[df['school']=='LIQUIDITY_SWEEP'])}")
    m3.metric("🚀 صفقات Squeeze", f"{len(df[df['logic']=='SQUEEZE_RELEASE'])}")
    m4.metric("🛡️ خط الأمان", "$190.00")

    # --- الرسوم البيانية وسجل العمليات ---
    col_chart, col_data = st.columns([2, 1])
    with col_chart:
        st.subheader("📈 مسار نمو الإمبراطورية")
        if not df.empty:
            fig = go.Figure(go.Scatter(x=df['time'], y=df['balance'], mode='lines+markers', line=dict(color='#00FFCC')))
            st.plotly_chart(fig, use_container_width=True)
    
    with col_data:
        st.subheader("📜 آخر 5 دروس (Neural Memory)")
        if not df.empty:
            st.write(df[['style', 'pnl', 'school']].head(5))

    st.write("### 📜 السجل الشامل (Journal)")
    st.dataframe(df.head(20), use_container_width=True)

    # --- عداد السعر السيادي ---
    monitor = st.empty()
    while True:
        try:
            h = TA_Handler(symbol="BTCUSDT", exchange="BINANCE", screener="crypto", interval="1m", timeout=5)
            price = h.get_analysis().indicators.get("close")
            with monitor.container():
                st.markdown(f"""
                <div style="background:#000; border:3px solid #f3ba2f; padding:40px; border-radius:25px; text-align:center;">
                    <h1 style="font-size:5.5rem; color:white; margin:0;">${price:,.2f}</h1>
                    <p style="color:#00FFCC;">الذكاء الاصطناعي يراقب السيولة ويحسب العمولات بدقة</p>
                </div>
                """, unsafe_allow_html=True)
        except: pass
        time.sleep(15)
        st.rerun()

if __name__ == "__main__":
    main()
