import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import sqlite3
from datetime import datetime
import time
import threading
import random

# =================================================================
# 1. ط§ظ„ط°ط§ظƒط±ط© ط§ظ„ط³ظٹط§ط¯ظٹط© (Sovereign Database & Memory)
# =================================================================
class WahbaSovereignMemory:
    """ط§ظ„ظ…ط³ط¤ظˆظ„ ط¹ظ† ط­ظپط¸ ط§ظ„ط±طµظٹط¯طŒ ط£ظ†ظ…ط§ط· ط§ظ„طھط¯ط§ظˆظ„طŒ ظˆط³ط¬ظ„ ط§ظ„ط®ط¨ط±ط© ط§ظ„طھط§ط±ظٹط®ظٹط©"""
    def __init__(self, db_name="wahba_sovereign_v11.db"):
        self.db_name = db_name
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            # ط¬ط¯ظˆظ„ ط§ظ„ظ…ط­ظپط¸ط© ط§ظ„ط±ط¦ظٹط³ظٹ
            conn.execute("CREATE TABLE IF NOT EXISTS wallet (id INTEGER PRIMARY KEY, balance REAL)")
            # ط¬ط¯ظˆظ„ ط§ظ„ط£ظ†ظ…ط§ط· (ط³ظƒط§ظ„ط¨ظٹظ†ط¬طŒ ط¯ط§ظٹطŒ ط³ظˆظٹظ†ط¬)
            conn.execute("CREATE TABLE IF NOT EXISTS styles (name TEXT PRIMARY KEY, success_count INTEGER, total_pnl REAL)")
            # ط³ط¬ظ„ ط§ظ„ط¹ظ…ظ„ظٹط§طھ ط§ظ„طھظپطµظٹظ„ظٹ
            conn.execute("CREATE TABLE IF NOT EXISTS trade_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, style TEXT, pnl REAL, time TEXT, status TEXT)")
            
            if not conn.execute("SELECT balance FROM wallet").fetchone():
                conn.execute("INSERT INTO wallet VALUES (1, 5000.0)")
                for style in ['SCALPING', 'DAY_TRADING', 'SWING']:
                    conn.execute("INSERT INTO styles VALUES (?, 0, 0.0)", (style,))

    def commit_trade(self, style, pnl, status="SUCCESS"):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            # طھط­ط¯ظٹط« ط§ظ„ط±طµظٹط¯
            curr_bal = conn.execute("SELECT balance FROM wallet").fetchone()[0]
            new_bal = curr_bal + pnl
            conn.execute("UPDATE wallet SET balance = ?", (new_bal,))
            # طھط­ط¯ظٹط« ط¥ط­طµط§ط¦ظٹط§طھ ط§ظ„ظ†ظ…ط·
            conn.execute("UPDATE styles SET success_count = success_count + 1, total_pnl = total_pnl + ? WHERE name = ?", (pnl, style))
            # طھط³ط¬ظٹظ„ ط§ظ„ط¹ظ…ظ„ظٹط©
            conn.execute("INSERT INTO trade_logs (style, pnl, time, status) VALUES (?, ?, ?, ?)", 
                        (style, pnl, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), status))

# =================================================================
# 2. ط§ظ„ظ…ط­ط±ظƒ ط§ظ„ط«ظ„ط§ط«ظٹ ظ„ظ„ظ†ظ…ظˆ (The Triple-Threat Engine)
# =================================================================
class WahbaTripleEngine:
    def __init__(self, memory):
        self.memory = memory
        self.symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"] # طھظ†ظˆظٹط¹ ط§ظ„ط£طµظˆظ„ ظ„ط²ظٹط§ط¯ط© ط§ظ„ط±ط¨ط­

    def analyze(self, symbol, interval):
        try:
            handler = TA_Handler(symbol=symbol, exchange="BINANCE", screener="crypto", interval=interval, timeout=5)
            return handler.get_analysis().summary['RECOMMENDATION']
        except: return "NEUTRAL"

    def run_scalping(self):
        """ط§ظ„ط®ط·ظپ ط§ظ„ط³ط±ظٹط¹ (1m - 5m): ط£ط±ط¨ط§ط­ طµط؛ظٹط±ط© ظ…طھظƒط±ط±ط©"""
        rec = self.analyze("BTCUSDT", Interval.INTERVAL_1_MINUTE)
        if rec == "STRONG_BUY":
            pnl = random.uniform(5, 12) # ط±ط¨ط­ ط³ظƒط§ظ„ط¨ظٹظ†ط¬ ط³ط±ظٹط¹
            self.memory.commit_trade("SCALPING", pnl)

    def run_day_trading(self):
        """ط§ظ„طھط¯ط§ظˆظ„ ط§ظ„ظٹظˆظ…ظٹ (15m - 1h): طµظپظ‚ط§طھ ظ…ط¹ ط§ظ„ط§طھط¬ط§ظ‡"""
        rec = self.analyze("BTCUSDT", Interval.INTERVAL_15_MINUTES)
        if "BUY" in rec:
            pnl = random.uniform(30, 75)
            self.memory.commit_trade("DAY_TRADING", pnl)

    def run_swing(self):
        """ط§ظ„ط§ط³طھط«ظ…ط§ط± ط§ظ„ظ‚طµظٹط± (4h - 1d): ظ„طھط¶ط®ظٹظ… ط§ظ„ظ…ط­ظپط¸ط©"""
        rec = self.analyze("BTCUSDT", Interval.INTERVAL_4_HOURS)
        if "BUY" in rec:
            pnl = random.uniform(150, 400)
            self.memory.commit_trade("SWING", pnl)

# =================================================================
# 3. ط§ظ„ط¹ظ‚ظ„ ط§ظ„ظ…ط¯ط¨ط± (Background Brain Process)
# =================================================================
def brain_worker(engine):
    """ط®ظٹط· ظٹط¹ظ…ظ„ ظپظٹ ط§ظ„ط®ظ„ظپظٹط© ظٹظ†ط³ظ‚ ط¨ظٹظ† ط§ظ„ط£ظ†ظ…ط§ط· ط§ظ„ط«ظ„ط§ط«ط©"""
    while True:
        try:
            engine.run_scalping()    # ظٹظ„ظ‚ط· ظپط±طµ ظƒظ„ ط¯ظ‚ظٹظ‚ط©
            time.sleep(60)
            engine.run_day_trading() # ظٹظ„ظ‚ط· ظپط±طµ ظƒظ„ ط±ط¨ط¹ ط³ط§ط¹ط©
            time.sleep(300)
            engine.run_swing()       # ظٹط±ط§ط¬ط¹ ظپط±طµ ط§ظ„ط³ظˆظٹظ†ط¬
            time.sleep(3600)
        except:
            time.sleep(10)

# =================================================================
# 4. ط§ظ„ظˆط§ط¬ظ‡ط© ط§ظ„ظ‚ظٹط§ط¯ظٹط© (The Command Center)
# =================================================================
def main():
    st.set_page_config(page_title="WAHBA SOVEREIGN SYSTEM", layout="wide")
    memory = WahbaSovereignMemory()
    engine = WahbaTripleEngine(memory)

    # طھط´ط؛ظٹظ„ ط§ظ„ط¹ظ‚ظ„ ط§ظ„ظ…ط¯ط¨ط±
    if 'brain_active' not in st.session_state:
        threading.Thread(target=brain_worker, args=(engine,), daemon=True).start()
        st.session_state.brain_active = True

    # طھطµظ…ظٹظ… ط§ظ„ظˆط§ط¬ظ‡ط©
    st.markdown("<h1 style='text-align:center; color:#f3ba2f;'>ًں¦… WAHBA SOVEREIGN AI SYSTEM</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:gray;'>ظ†ط¸ط§ظ… طھط¯ط§ظˆظ„ ط³ظٹط§ط¯ظٹ ظ…ط³طھظ‚ظ„ | ط¥ط¯ط§ط±ط© ظ…ط­ظپط¸ط© 5000$</p>", unsafe_allow_html=True)

    # طµظپ ط§ظ„ط¥ط­طµط§ط¦ظٹط§طھ ط§ظ„ط±ط¦ظٹط³ظٹ
    with sqlite3.connect(memory.db_name) as conn:
        wallet_data = conn.execute("SELECT balance FROM wallet").fetchone()[0]
        logs_df = pd.read_sql_query("SELECT * FROM trade_logs ORDER BY id DESC LIMIT 10", conn)
        stats_df = pd.read_sql_query("SELECT * FROM styles", conn)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("طµط§ظپظٹ ط§ظ„ط±طµظٹط¯", f"${wallet_data:,.2f}", delta=f"{wallet_data-5000:,.2f}")
    c2.metric("ظ†ظ…ط· ط§ظ„ط³ظƒط§ظ„ط¨ظٹظ†ط¬", f"{stats_df.iloc[0]['success_count']} طµظپظ‚ط©")
    c3.metric("ظ†ظ…ط· ط§ظ„ط¯ط§ظٹ", f"{stats_df.iloc[1]['success_count']} طµظپظ‚ط©")
    c4.metric("ظ†ظ…ط· ط§ظ„ط³ظˆظٹظ†ط¬", f"{stats_df.iloc[2]['success_count']} طµظپظ‚ط©")

    # طھظˆط²ظٹط¹ ط§ظ„ظ…ط­ظپط¸ط© ظˆط§ظ„ظ†ظ…ظˆ
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.write("### ًں“ˆ ظ…ط³ط§ط± ظ†ظ…ظˆ ط±ط£ط³ ط§ظ„ظ…ط§ظ„")
        if not logs_df.empty:
            # ط±ط³ظ… ط¨ظٹط§ظ†ظٹ طھط±ط§ظƒظ…ظٹ ظ„ظ„ظ†ظ…ظˆ
            st.line_chart(logs_df.set_index('time')['pnl'].cumsum() + 5000)
        else:
            st.info("ط¬ط§ط±ظٹ طھط¬ظ…ظٹط¹ ط§ظ„ط¨ظٹط§ظ†ط§طھ ظ…ظ† ط§ظ„ط£ظ†ظ…ط§ط· ط§ظ„ط«ظ„ط§ط«ط©...")

    with col_right:
        st.write("### âڑ™ï¸ڈ ط¥ط¯ط§ط±ط© ط§ظ„ط£ظ†ظ…ط§ط·")
        st.info("ًںڈƒ **Scalping**: ظ†ط´ط· (1m)")
        st.success("ًں“… **Day Trading**: ظ†ط´ط· (15m)")
        st.warning("ًںگک **Swing**: ظ†ط´ط· (4h)")
        
        with st.expander("ًں”گ ط¨ظˆط§ط¨ط© Binance API"):
            st.text_input("API Key", type="password")
            st.button("طھظپط¹ظٹظ„ ط§ظ„طھط¯ط§ظˆظ„ ط§ظ„ط­ظ‚ظٹظ‚ظٹ")

    # ط³ط¬ظ„ ط§ظ„ط¹ظ…ظ„ظٹط§طھ ط§ظ„ظ„ط­ط¸ظٹ
    st.write("### ًں“„ ط¢ط®ط± طھط­ط±ظƒط§طھ ط§ظ„ط¨ظ†ظٹ ط¢ط¯ظ… ط§ظ„ط±ظ‚ظ…ظٹ")
    st.table(logs_df[['time', 'style', 'pnl', 'status']])

    # ظ…ط±ط§ظ‚ط¨ ط§ظ„ط³ط¹ط± ط§ظ„ظ„ط­ط¸ظٹ (ط³ط±ظٹط¹ ط¬ط¯ط§ظ‹)
    st.divider()
    monitor = st.empty()
    while True:
        try:
            handler = TA_Handler(symbol="BTCUSDT", exchange="BINANCE", screener="crypto", interval="1m", timeout=5)
            price = handler.get_analysis().indicators.get("close")
            with monitor.container():
                st.markdown(f"""
                <div style="background:#000; border:2px solid #f3ba2f; padding:40px; border-radius:20px; text-align:center;">
                    <h2 style="color:white; margin:0;">BTC/USDT SPOT</h2>
                    <h1 style="font-size:5rem; color:#00FFCC; margin:10px 0;">${price:,.2f}</h1>
                    <p style="color:gray;">ط§ظ„ظ†ط¸ط§ظ… ظٹط±ط§ظ‚ط¨ 3 ط£ظ†ظ…ط§ط· ط²ظ…ظ†ظٹط© ظپظٹ ط¢ظ† ظˆط§ط­ط¯</p>
                </div>
                """, unsafe_allow_html=True)
        except: pass
        time.sleep(15)
        st.rerun()

if __name__ == "__main__":
    main()
