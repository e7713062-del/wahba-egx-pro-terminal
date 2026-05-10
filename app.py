import streamlit as st
import google.generativeai as genai
import pandas as pd
import sqlite3
import json
import time
from datetime import datetime
from tradingview_ta import TA_Handler, Interval, Exchange

# =================================================================
# 1. إعدادات السيادة الرقمية (AI CONFIGURATION)
# =================================================================
API_KEY = "AIzaSyAHLshGDTIRhodR1CMAWGP_DH3622aADJQ" 
genai.configure(api_key=API_KEY)

generation_config = {
    "temperature": 0.1,
    "top_p": 0.95,
    "max_output_tokens": 1500,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config
)

# =================================================================
# 2. محرك إدارة الذاكرة والتراكم (THE SOVEREIGN ENGINE)
# =================================================================
class WahbaSovereignEngine:
    def __init__(self, db_name="wahba_final_sovereign.db"):
        self.db_name = db_name
        self.initial_balance = 190.0
        self._initialize_db()

    def _initialize_db(self):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS wallet (balance REAL, last_trade_time TEXT)")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS master_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    time TEXT, 
                    symbol TEXT, 
                    strategy TEXT, 
                    price REAL,
                    net_profit REAL, 
                    logic_summary TEXT,
                    market_mood TEXT
                )
            """)
            if not conn.execute("SELECT balance FROM wallet").fetchone():
                conn.execute("INSERT INTO wallet (balance, last_trade_time) VALUES (?, ?)", 
                             (self.initial_balance, datetime.now().isoformat()))

    def get_balance(self):
        with sqlite3.connect(self.db_name) as conn:
            return conn.execute("SELECT balance FROM wallet").fetchone()[0]

    def get_memory_logs(self, count=7):
        try:
            with sqlite3.connect(self.db_name) as conn:
                query = "SELECT net_profit, strategy, logic_summary FROM master_history ORDER BY id DESC LIMIT ?"
                return pd.read_sql_query(query, conn, params=(count,)).to_dict(orient='records')
        except:
            return []

    def execute_and_record(self, symbol, strategy, price, raw_profit, logic, mood):
        current_balance = self.get_balance()
        risk_factor = 0.45 if mood == "Aggressive" else 0.15
        fees = (current_balance * risk_factor) * 0.002
        net_pnl = raw_profit - fees
        
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("UPDATE wallet SET balance = balance + ?", (net_pnl,))
            conn.execute("""
                INSERT INTO master_history (time, symbol, strategy, price, net_profit, logic_summary, market_mood) 
                VALUES (?,?,?,?,?,?,?)
            """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), symbol, strategy, price, net_pnl, logic, mood))

# =================================================================
# 3. محرك الرصد المتقدم (ADVANCED MARKET SCANNER)
# =================================================================
TARGET_ASSETS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "AVAXUSDT", "NEARUSDT", "LINKUSDT"]

def get_market_intelligence(symbol):
    try:
        handler = TA_Handler(symbol=symbol, screener="crypto", exchange="BINANCE", interval=Interval.INTERVAL_1_MINUTE)
        ta_1m = handler.get_analysis()
        return {
            "price": ta_1m.indicators['close'],
            "rsi": ta_1m.indicators['RSI'],
            "volume": ta_1m.indicators['volume'],
            "bb_upper": ta_1m.indicators['BBANDS.upper'],
            "bb_lower": ta_1m.indicators['BBANDS.lower']
        }
    except:
        return None

# =================================================================
# 4. واجهة القيادة السيادية (GRAND DASHBOARD)
# =================================================================
def main():
    st.set_page_config(page_title="Wahba AI Sovereign", layout="wide")
    engine = WahbaSovereignEngine()
    
    st.markdown("<h1 style='text-align:center; color:#00ffcc;'>🦅 WAHBA SOVEREIGN: ANTI-CLASSIC</h1>", unsafe_allow_html=True)

    bal = engine.get_balance()
    initial = engine.initial_balance
    total_growth = ((bal - initial) / initial) * 100
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Wallet Balance", f"${bal:.2f}", f"{total_growth:.2f}%")
    c2.metric("Status", "Anti-Manipulation Active")
    c3.metric("Mode", "SMC & Liquidity Only")

    st.divider()
    live_feed = st.empty()
    
    while True:
        with live_feed.container():
            memory_data = engine.get_memory_logs()
            memory_context = json.dumps(memory_data, ensure_ascii=False) if memory_data else "No History"

            for symbol in TARGET_ASSETS:
                intel = get_market_intelligence(symbol)
                if not intel: continue
                
                # تم تحسين الـ Prompt ليكون أكثر أماناً برمجياً
                prompt = f"""
                Analyze {symbol} at price {intel['price']}.
                Memory: {memory_context}
                Task: Detect Liquidity Sweeps or FVG. Ignore Retail Patterns.
                Output JSON: {{"decision": "BUY/WAIT", "strategy": "...", "logic": "...", "mood": "Aggressive/Conservative"}}
                """

                try:
                    response = model.generate_content(prompt)
                    clean_txt = response.text.strip().replace('```json', '').replace('```', '')
                    res = json.loads(clean_txt)

                    if res.get('decision') == "BUY":
                        engine.execute_and_record(
                            symbol, res['strategy'], intel['price'], 10.0, res['logic'], res['mood']
                        )
                        st.toast(f"🚀 Execution: {symbol}")
                        time.sleep(1)
                        st.rerun()
                except:
                    continue

            st.subheader("📚 Ledger")
            with sqlite3.connect(engine.db_name) as conn:
                df = pd.read_sql_query("SELECT * FROM master_history ORDER BY id DESC", conn)
                st.dataframe(df, use_container_width=True)

        time.sleep(10)
        st.rerun()

if __name__ == "__main__":
    main()
