import streamlit as st
import pandas as pd
import sqlite3
import google.generativeai as genai
import ccxt
import time
from datetime import datetime

# =================================================================
# 1. المركز الرئيسي للإعدادات (Sovereign Configuration)
# =================================================================
CONFIG = {
    "API": {
        "GEMINI_KEY": "YOUR_GEMINI_API_KEY",
        "BINANCE_KEY": "YOUR_TESTNET_API_KEY",
        "BINANCE_SECRET": "YOUR_TESTNET_SECRET_KEY"
    },
    "TRADING": {
        "SYMBOLS": ["BTC/USDT", "ETH/USDT", "SOL/USDT"],
        "TIMEFRAME": "15m",
        "RISK_PERCENT": 0.1,  # الدخول بـ 10% من الرصيد المتوفر
        "LOOKBACK": 20
    },
    "DB_NAME": "wahba_final_system.db"
}

# =================================================================
# 2. مدير قاعدة البيانات (The Historian)
# =================================================================
class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self._setup()

    def _setup(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trade_logs 
                (id INTEGER PRIMARY KEY AUTOINCREMENT, symbol TEXT, side TEXT, price REAL, decision TEXT, time TEXT)
            """)

    def save_log(self, symbol, side, price, decision):
        with sqlite3.connect(self.db_path) as conn:
            now = datetime.now().strftime("%H:%M:%S")
            conn.execute("INSERT INTO trade_logs (symbol, side, price, decision, time) VALUES (?,?,?,?,?)",
                         (symbol, side, price, decision, now))

    def get_logs(self):
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql("SELECT * FROM trade_history ORDER BY id DESC LIMIT 10", conn)

# =================================================================
# 3. محرك التداول الذكي (The Intelligence Engine)
# =================================================================
class WahbaSovereign:
    def __init__(self):
        # تهيئة الذكاء الاصطناعي
        genai.configure(api_key=CONFIG["API"]["GEMINI_KEY"])
        self.ai_model = genai.GenerativeModel('gemini-1.5-flash')
        
        # تهيئة بورصة بينانس (وضع التجربة)
        self.exchange = ccxt.binance({
            'apiKey': CONFIG["API"]["BINANCE_KEY"],
            'secret': CONFIG["API"]["BINANCE_SECRET"],
            'enableRateLimit': True,
            'timeout': 30000,
            'options': {'defaultType': 'spot'}
        })
        self.exchange.set_sandbox_mode(True)

    def safe_get_balance(self):
        """جلب الرصيد بأمان لتجنب انهيار الكود"""
        try:
            balance = self.exchange.fetch_balance()
            return float(balance['total'].get('USDT', 0.0))
        except:
            return 0.0

    def fetch_market_data(self, symbol):
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe=CONFIG["TRADING"]["TIMEFRAME"], limit=100)
            df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
            df['time'] = pd.to_datetime(df['time'], unit='ms')
            return df
        except:
            return None

    def analyze_smc(self, df):
        """تحليل الـ SMC (سحب السيولة)"""
        lb = CONFIG["TRADING"]["LOOKBACK"]
        df['low_min'] = df['low'].shift(1).rolling(window=lb).min()
        df['high_max'] = df['high'].shift(1).rolling(window=lb).max()
        
        last = df.iloc[-1]
        if last['low'] < last['low_min'] and last['close'] > last['low_min']: return "BUY"
        if last['high'] > last['high_max'] and last['close'] < last['high_max']: return "SELL"
        return "WAIT"

    def ask_gemini(self, symbol, side, price, df):
        """قرار Gemini النهائي"""
        try:
            context = df.tail(10).to_string()
            prompt = f"Analyze {symbol} {side} signal at {price}. Market: {context}. Reply 'APPROVE' or 'REJECT' + short Arabic reason."
            response = self.ai_model.generate_content(prompt)
            return response.text.strip()
        except:
            return "REJECT: AI Offline"

    def execute_spot(self, symbol, side, price):
        """تنفيذ الصفقة فوري (حلال)"""
        try:
            bal = self.safe_get_balance()
            if side == "BUY" and bal > 10:
                qty = (bal * CONFIG["TRADING"]["RISK_PERCENT"]) / price
                return self.exchange.create_market_buy_order(symbol, qty)
            return None
        except:
            return None

# =================================================================
# 4. واجهة المستخدم (The Dashboard)
# =================================================================
def main():
    st.set_page_config(page_title="Wahba Sovereign AI", layout="wide")
    
    # تهيئة المكونات في الـ Session
    if 'bot' not in st.session_state:
        st.session_state.bot = WahbaSovereign()
        st.session_state.db = DatabaseManager(CONFIG["DB_NAME"])

    bot = st.session_state.bot
    db = st.session_state.db

    st.title("🦅 Wahba Sovereign AI")
    st.caption("نظام التداول ذاتي الإدارة والتعلم - نسخة الـ Spot الحلال")

    # القائمة الجانبية
    with st.sidebar:
        st.header("📊 حالة الحساب")
        current_bal = bot.safe_get_balance()
        st.metric("رصيد USDT التجريبي", f"${current_bal:,.2f}")
        if current_bal == 0:
            st.warning("⚠️ لم يتم الربط ببينانس (تأكد من المفاتيح)")
        st.divider()
        st.write("المدارس النشطة: SMC, AI-Filter")

    # العرض الرئيسي
    cols = st.columns(len(CONFIG["TRADING"]["SYMBOLS"]))
    for i, sym in enumerate(CONFIG["TRADING"]["SYMBOLS"]):
        with cols[i]:
            df = bot.fetch_market_data(sym)
            if df is not None:
                price = df.iloc[-1]['close']
                signal = bot.analyze_smc(df)
                
                st.subheader(sym)
                st.metric("Price", f"${price:,.2f}")
                
                if signal != "WAIT":
                    st.info(f"🔍 رصد إشارة {signal}")
                    decision = bot.ask_gemini(sym, signal, price, df)
                    
                    if "APPROVE" in decision.upper():
                        st.success(f"✅ تم القبول: {decision}")
                        bot.execute_spot(sym, signal, price)
                        db.save_log(sym, signal, price, decision)
                    else:
                        st.warning(f"❌ رفض Gemini: {decision}")
                
                st.line_chart(df['close'].tail(25))
            else:
                st.error(f"فشل جلب بيانات {sym}")

    st.divider()
    st.subheader("📜 سجل العمليات")
    try:
        st.dataframe(pd.read_sql("SELECT * FROM trade_logs ORDER BY id DESC LIMIT 10", sqlite3.connect(CONFIG["DB_NAME"])), use_container_width=True)
    except:
        st.write("لا توجد عمليات مسجلة بعد.")

    time.sleep(60)
    st.rerun()

if __name__ == "__main__":
    main()
