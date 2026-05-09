import streamlit as st
from binance.client import Client
import pandas as pd
import sqlite3
from datetime import datetime
import time
import random
import threading

# =================================================================
# 1. نظام إدارة المعرفة والمدارس (Knowledge & SMC Vault)
# =================================================================
class WahbaSovereignDB:
    """المسؤول عن تخزين الرصيد، وفلترة المدارس بناءً على منطق السيولة (SMC)"""
    def __init__(self, db_name="wahba_sovereign_smc.db"):
        self.db_name = db_name
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            # جداول المحفظة والنمو والصفقات
            conn.execute("CREATE TABLE IF NOT EXISTS wallet (id INTEGER PRIMARY KEY, balance REAL)")
            conn.execute("CREATE TABLE IF NOT EXISTS growth_log (amount REAL, timestamp TEXT)")
            conn.execute("CREATE TABLE IF NOT EXISTS trades (id INTEGER PRIMARY KEY AUTOINCREMENT, side TEXT, entry REAL, status TEXT, pnl REAL, time TEXT)")
            
            # جدول المدارس (SMC/ICT/Volume Flow)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS strategy_vault (
                    strategy_name TEXT PRIMARY KEY,
                    win_rate REAL,
                    version REAL,
                    status TEXT, 
                    discovery_date TEXT
                )
            """)
            
            if not conn.execute("SELECT balance FROM wallet").fetchone():
                conn.execute("INSERT INTO wallet VALUES (1, 5000.0)")
                conn.execute("INSERT INTO growth_log VALUES (5000.0, ?)", (datetime.now().strftime("%H:%M:%S"),))

    def refresh_strategies(self, new_discoveries):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            conn.execute("UPDATE strategy_vault SET status = 'ARCHIVED' WHERE win_rate < 55")
            for name, rate in new_discoveries.items():
                conn.execute("""
                    INSERT INTO strategy_vault (strategy_name, win_rate, version, status, discovery_date)
                    VALUES (?, ?, 1.0, 'ACTIVE', ?)
                    ON CONFLICT(strategy_name) DO UPDATE SET
                        win_rate = ?, version = version + 0.1, status = 'ACTIVE'
                """, (name, rate, now, rate))

    def get_active_list(self):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            return pd.read_sql_query("SELECT * FROM strategy_vault WHERE status = 'ACTIVE'", conn)

# =================================================================
# 2. محرك البحث الذكي (Hunter Engine) - الجزء القديم المطور
# =================================================================
def strategy_hunter_process(db_manager):
    """يبحث صامتاً عن تحديثات مدارس SMC و ICT كل 6 ساعات"""
    while True:
        try:
            # محاكاة اكتشاف تحديثات لمفاهيم السيولة
            current_trends = {
                "SMC_OrderBlock_v2": random.uniform(75, 90),
                "ICT_Silver_Bullet": random.uniform(70, 85),
                "Liquidity_Void_Scanner": random.uniform(60, 78)
            }
            db_manager.refresh_strategies(current_trends)
            time.sleep(21600) 
        except:
            time.sleep(60)

# =================================================================
# 3. محرك التنفيذ بمنطق السيولة (SMC Execution Engine) - الزيادة الجديدة
# =================================================================
def smc_execution_process(db_manager):
    """المحرك الفعلي الذي يحلل الشموع بحثاً عن الـ FVG والسيولة"""
    client = Client() # بدون API للبيانات العامة فقط
    symbol = "BTCUSDT"

    while True:
        try:
            # جلب البيانات الخام (15 دقيقة)
            bars = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_15MINUTE, limit=50)
            df = pd.DataFrame(bars, columns=['time','open','high','low','close','vol','ct','qv','tr','tb','tq','ig'])
            df[['high', 'low', 'close']] = df[['high', 'low', 'close']].astype(float)

            # تحليل FVG (Fair Value Gap)
            last_3 = df.tail(3)
            c1_high, c1_low = last_3.iloc[0]['high'], last_3.iloc[0]['low']
            c3_high, c3_low = last_3.iloc[2]['high'], last_3.iloc[2]['low']
            price = last_3.iloc[2]['close']

            with sqlite3.connect(db_manager.db_name) as conn:
                active_trade = conn.execute("SELECT * FROM trades WHERE status = 'OPEN'").fetchone()

                if not active_trade:
                    # Bullish FVG: (High of Candle 1 < Low of Candle 3)
                    if c3_low > c1_high:
                        conn.execute("INSERT INTO trades (side, entry, status, pnl, time) VALUES (?,?,?,?,?)",
                                     ("BUY (SMC)", price, "OPEN", 0, datetime.now().strftime("%H:%M")))
                
                elif active_trade:
                    entry_price = active_trade[2]
                    pnl = price - entry_price if "BUY" in active_trade[1] else entry_price - price
                    
                    # إغلاق ذكي (Target 1.5% أو Stop 0.7%)
                    if pnl > (entry_price * 0.015) or pnl < -(entry_price * 0.007):
                        conn.execute("UPDATE trades SET status='CLOSED', pnl=? WHERE id=?", (pnl, active_trade[0]))
                        conn.execute("UPDATE wallet SET balance = balance + ?", (pnl * 5,)) # Leverage 5x
            
            time.sleep(30)
        except Exception as e:
            time.sleep(20)

# =================================================================
# 4. الواجهة الرئيسية (Sovereign Live View)
# =================================================================
def main():
    st.set_page_config(page_title="WAHBA SOVEREIGN SMC", layout="wide")
    db = WahbaSovereignDB()

    # تشغيل المحركات في الخلفية
    if 'engines_initialized' not in st.session_state:
        threading.Thread(target=strategy_hunter_process, args=(db,), daemon=True).start()
        threading.Thread(target=smc_execution_process, args=(db,), daemon=True).start()
        st.session_state.engines_initialized = True

    st.markdown("<h2 style='text-align:center; color:#f3ba2f;'>🦅 WAHBA MASTER: SOVEREIGN V8 (SMC)</h2>", unsafe_allow_html=True)

    # عرض البيانات
    active_strategies = db.get_active_list()
    col_info, col_graph = st.columns([1, 2])
    
    with col_info:
        st.write("### 🛡️ المدارس السيادية النشطة")
        st.dataframe(active_strategies[['strategy_name', 'win_rate', 'version']], use_container_width=True)
        
        with sqlite3.connect(db.db_name) as conn:
            balance = conn.execute("SELECT balance FROM wallet").fetchone()[0]
            current_trade = pd.read_sql_query("SELECT * FROM trades WHERE status = 'OPEN'", conn)
        
        st.metric("رصيد المحفظة المستهدف", f"${balance:,.2f}")
        if not current_trade.empty:
            st.warning(f"جاري تنفيذ عملية: {current_trade['side'].iloc[0]} من سعر {current_trade['entry'].iloc[0]}")

    with col_graph:
        st.write("### 📈 منحنى نمو السيولة الذكية")
        with sqlite3.connect(db.db_name) as conn:
            history_df = pd.read_sql_query("SELECT amount, timestamp FROM growth_log", conn)
        if not history_df.empty:
            st.line_chart(history_df.set_index('timestamp')['amount'])

    # شاشة مراقبة السعر اللحظي (Refresh Loop)
    st.divider()
    monitor_view = st.empty()

    while True:
        try:
            client = Client()
            p = float(client.get_symbol_ticker(symbol="BTCUSDT")['price'])
            with monitor_view.container():
                st.markdown(f"""
                <div style="background:#000; border:2px solid #f3ba2f; padding:40px; border-radius:20px; text-align:center;">
                    <h3 style="color:#888;">BTC/USDT LIVE MARKET STRUCTURE</h3>
                    <h1 style="font-size:6rem; color:white; margin:0;">${p:,.2f}</h1>
                    <p style="color:#00FFCC; font-size:1.2rem; margin-top:10px;">
                        🤖 المحرك يلاحق سيولة المؤسسات الآن.. تم تفعيل منطق FVG وإلغاء الكلاسيك.
                    </p>
                </div>
                """, unsafe_allow_html=True)
        except:
            monitor_view.warning("⏳ مزامنة مع السيرفر...")
        
        time.sleep(15)
        st.rerun()

if __name__ == "__main__":
    main()
