# =================================================================
# PROJECT: WAHBA SOVEREIGN AI (V1.0 - HALAL SPOT EDITION)
# DEVELOPER: MUSTAFA TAMER & GEMINI
# PURPOSE: AUTONOMOUS SMART MONEY TRADING
# =================================================================

import streamlit as st
import pandas as pd
import sqlite3
import google.generativeai as genai
import ccxt
import time
from datetime import datetime

# -----------------------------------------------------------------
# 1. الإعدادات المركزية (Global Configuration)
# -----------------------------------------------------------------
# هنا نضع الثوابت لسهولة التحكم دون تعديل منطق الكود
CONFIG = {
    "API": {
        "GEMINI_KEY": "YOUR_GEMINI_API_KEY",
        "BINANCE_KEY": "YOUR_API_KEY",
        "BINANCE_SECRET": "YOUR_SECRET_KEY"
    },
    "TRADING": {
        "SYMBOLS": ["BTC/USDT", "ETH/USDT", "SOL/USDT"],
        "TIMEFRAME": "15m",
        "RETAIL_LOOKBACK": 20, # عدد الشموع لتحديد مناطق السيولة
        "RISK_PERCENT": 0.1,    # الدخول بـ 10% من الرصيد المتوفر
        "MODE": "spot"          # تداول فوري حلال
    },
    "DB_NAME": "wahba_sovereign_v1.db"
}

# -----------------------------------------------------------------
# 2. محرك قاعدة البيانات (Database Management)
# -----------------------------------------------------------------
class DatabaseManager:
    """مسؤول عن حفظ تاريخ التداول والتعلم الآلي"""
    def __init__(self, db_path):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trade_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    side TEXT,
                    price REAL,
                    ai_decision TEXT,
                    timestamp TEXT
                )
            """)

    def log_trade(self, symbol, side, price, ai_decision):
        with sqlite3.connect(self.db_path) as conn:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute(
                "INSERT INTO trade_history (symbol, side, price, ai_decision, timestamp) VALUES (?,?,?,?,?)",
                (symbol, side, price, ai_decision, now)
            )

    def get_recent_trades(self, limit=10):
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql(f"SELECT * FROM trade_history ORDER BY id DESC LIMIT {limit}", conn)

# -----------------------------------------------------------------
# 3. العقل المدبر (AI & Strategy Engine)
# -----------------------------------------------------------------
class SovereignBrain:
    """المسؤول عن التحليل الفني واستشارة Gemini"""
    def __init__(self, gemini_key):
        genai.configure(api_key=gemini_key)
        self.ai_model = genai.GenerativeModel('gemini-1.5-flash')

    def detect_smc_signal(self, df):
        """تحليل هيكل السوق بحثاً عن سحب السيولة"""
        lookback = CONFIG["TRADING"]["RETAIL_LOOKBACK"]
        
        # تحديد قمم وقيعان المتداولين الأفراد
        df['r_low'] = df['low'].shift(1).rolling(window=lookback).min()
        df['r_high'] = df['high'].shift(1).rolling(window=lookback).max()
        
        last_candle = df.iloc[-1]
        
        # منطق صيد السيولة
        if last_candle['low'] < last_candle['r_low'] and last_candle['close'] > last_candle['r_low']:
            return "BUY"
        elif last_candle['high'] > last_candle['r_high'] and last_candle['close'] < last_candle['r_high']:
            return "SELL"
        return "NEUTRAL"

    def consult_gemini(self, symbol, side, price, market_data):
        """إرسال البيانات لـ Gemini لفلترة القرار وتطوير الاستراتيجية"""
        try:
            summary = market_data.tail(15).to_string()
            prompt = f"""
            بصفتك مدير تداول لمصطفى، حلل هذه الفرصة:
            العملة: {symbol} | الإشارة: {side} | السعر: {price}
            بيانات السوق الأخيرة:
            {summary}
            
            المطلوب:
            1. رد بـ 'APPROVE' أو 'REJECT' في بداية السطر.
            2. هل تلاحظ أي مدرسة تحليل جديدة يجب تعلمها؟
            3. اشرح القرار بالعربية.
            """
            response = self.ai_model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"REJECT: Error connecting to AI ({e})"

# -----------------------------------------------------------------
# 4. الذراع التنفيذية (Exchange Interface)
# -----------------------------------------------------------------
class ExchangeManager:
    """المسؤول عن الاتصال بـ Binance وتنفيذ الأوامر"""
    def __init__(self, api_key, secret_key):
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret_key,
            'enableRateLimit': True,
            'options': {'defaultType': CONFIG["TRADING"]["MODE"]}
        })
        self.exchange.set_sandbox_mode(True) # وضع التجربة (Testnet)

    def get_balance(self):
        balance = self.exchange.fetch_balance()
        return float(balance['total']['USDT'])

    def fetch_market_data(self, symbol):
        ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe=CONFIG["TRADING"]["TIMEFRAME"], limit=100)
        df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        return df

    def execute_order(self, symbol, side, price):
        """تنفيذ أمر السوق (Spot Market Order)"""
        try:
            balance = self.get_balance()
            if side == "BUY":
                # شراء بـ 10% من رصيد الـ USDT
                amount_usdt = balance * CONFIG["TRADING"]["RISK_PERCENT"]
                quantity = amount_usdt / price
                return self.exchange.create_market_buy_order(symbol, quantity)
            elif side == "SELL":
                # بيع كامل الكمية المملوكة من العملة
                coin = symbol.split('/')[0]
                coin_bal = self.exchange.fetch_balance()['total'].get(coin, 0)
                if coin_bal > 0:
                    return self.exchange.create_market_sell_order(symbol, coin_bal)
            return None
        except Exception as e:
            st.error(f"Execution Error: {e}")
            return None

# -----------------------------------------------------------------
# 5. الواجهة الرسومية (Main Application)
# -----------------------------------------------------------------
def run_app():
    # إعدادات واجهة Streamlit
    st.set_page_config(page_title="WAHBA SOVEREIGN AI", layout="wide", page_icon="🦅")
    
    # تهيئة المكونات (مرة واحدة في الجلسة)
    if 'db' not in st.session_state:
        st.session_state.db = DatabaseManager(CONFIG["DB_NAME"])
        st.session_state.brain = SovereignBrain(CONFIG["API"]["GEMINI_KEY"])
        st.session_state.exchange = ExchangeManager(CONFIG["API"]["BINANCE_KEY"], CONFIG["API"]["BINANCE_SECRET"])

    db = st.session_state.db
    brain = st.session_state.brain
    exchange = st.session_state.exchange

    # --- القائمة الجانبية ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2533/2533515.png", width=80)
        st.title("🦅 مركز التحكم")
        st.write("---")
        bal = exchange.get_balance()
        st.metric("الرصيد المتاح (USDT)", f"${bal:,.2f}")
        st.info("الوضع: Spot Trading (حلال)")

    # --- لوحة العرض الرئيسية ---
    st.title("🦅 Wahba Sovereign AI:Autonomous Trader")
    st.markdown("### نظام التداول الذكي ذاتي التعلم والمراقب لسيولة المؤسسات")
    
    # شبكة العرض للعملات
    cols = st.columns(len(CONFIG["TRADING"]["SYMBOLS"]))
    
    for i, symbol in enumerate(CONFIG["TRADING"]["SYMBOLS"]):
        with cols[i]:
            # جلب البيانات والتحليل
            df = exchange.fetch_market_data(symbol)
            current_price = df.iloc[-1]['close']
            signal = brain.detect_smc_signal(df)
            
            st.subheader(f"💎 {symbol}")
            st.metric("Price", f"${current_price:,.2f}")
            
            # منطق اتخاذ القرار الآلي
            if signal != "NEUTRAL":
                st.write(f"🔍 إشارة {signal} رصدت.. استشارة AI...")
                decision = brain.consult_gemini(symbol, signal, current_price, df)
                
                if "APPROVE" in decision.upper():
                    st.success(f"✅ Gemini وافق: {decision}")
                    order = exchange.execute_order(symbol, signal, current_price)
                    if order:
                        db.log_trade(symbol, signal, current_price, decision)
                else:
                    st.warning(f"❌ Gemini رفض: {decision}")
            
            st.line_chart(df['close'].tail(30))

    # --- سجل النشاط التاريخي ---
    st.divider()
    st.subheader("📜 سجل الصفقات والتعلم الآلي")
    history_df = db.get_recent_trades()
    st.dataframe(history_df, use_container_width=True)

    # التحديث التلقائي
    time.sleep(60)
    st.rerun()

if __name__ == "__main__":
    run_app()
