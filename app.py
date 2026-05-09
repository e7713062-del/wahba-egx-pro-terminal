import streamlit as st
from tradingview_ta import TA_Handler, Interval
from binance.client import Client
import pandas as pd
import sqlite3
from datetime import datetime
import time
import os

# =================================================================
# 1. إعدادات قاعدة البيانات (الذاكرة الدائمة)
# =================================================================
def initialize_database():
    """تهيئة ملفات الذاكرة والرصيد لضمان عدم ضياع البيانات"""
    connection = sqlite3.connect("wahba_professional_memory.db")
    cursor = connection.cursor()
    
    # جدول الرصيد الوهمي
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_wallet (
            id INTEGER PRIMARY KEY, 
            balance REAL
        )
    """)
    
    # جدول سجل الصفقات والخبرة المكتسبة
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trade_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            entry_price REAL,
            exit_price REAL,
            profit_loss REAL,
            result TEXT, -- 'WIN' or 'LOSS'
            logic_used TEXT
        )
    """)
    
    # التأكد من وجود الرصيد الأولي (5000 دولار)
    cursor.execute("SELECT balance FROM user_wallet WHERE id = 1")
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO user_wallet (id, balance) VALUES (1, 5000.0)")
    
    connection.commit()
    connection.close()

def get_current_balance():
    conn = sqlite3.connect("wahba_professional_memory.db")
    res = conn.execute("SELECT balance FROM user_wallet WHERE id = 1").fetchone()
    conn.close()
    return res[0]

def update_db_after_trade(profit, entry, exit, status):
    conn = sqlite3.connect("wahba_professional_memory.db")
    conn.execute("UPDATE user_wallet SET balance = balance + ? WHERE id = 1", (profit,))
    conn.execute("""
        INSERT INTO trade_history (timestamp, entry_price, exit_price, profit_loss, result, logic_used)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), entry, exit, profit, status, "SMC_LIQUIDITY_SWEEP"))
    conn.commit()
    conn.close()

# =================================================================
# 2. محرك تحليل البيتكوين (SMC Spot Only)
# =================================================================
class BitcoinSpotAnalyzer:
    """المسؤول عن جلب وتحليل حركة البيتكوين فقط"""
    def __init__(self, symbol="BTCUSDT"):
        self.symbol = symbol

    def fetch_market_data(self):
        try:
            handler = TA_Handler(
                symbol=self.symbol,
                exchange="BINANCE",
                screener="crypto",
                interval=Interval.INTERVAL_15_MINUTES,
                timeout=20
            )
            analysis = handler.get_analysis()
            return analysis.indicators
        except Exception as e:
            st.error(f"خطأ في جلب البيانات: {e}")
            return None

    def detect_smc_setup(self, indicators):
        """تحليل سحب السيولة (Liquidity Sweep)"""
        if not indicators:
            return False, 0
        
        current_close = indicators.get("close")
        current_low = indicators.get("low")
        previous_low = indicators.get("low.1")
        
        # حماية من القيم الفارغة (None) لتجنب TypeError
        if None in [current_close, current_low, previous_low]:
            return False, 0
            
        # منطق سحب السيولة: السعر يضرب القاع السابق ثم يرتد للأعلى
        is_sweep = (current_low < previous_low) and (current_close > previous_low)
        return is_sweep, current_low

# =================================================================
# 3. نظام التداول الآلي والربط (Binance Ready)
# =================================================================
class TradingBot:
    def __init__(self):
        self.is_in_position = False
        self.active_trade = {}

    def process_market_cycle(self, indicators, api_mode):
        if not indicators:
            return "⏳ جاري محاولة الاتصال بالسوق..."
        
        price = indicators.get("close")
        analyzer = BitcoinSpotAnalyzer()
        is_setup, low_point = analyzer.detect_smc_setup(indicators)

        # --- حالة: البحث عن دخول (Buy) ---
        if not self.is_in_position:
            if is_setup:
                self.is_in_position = True
                stop_loss = low_point * 0.998 # ستوب تحت القاع بمسافة آمنة
                take_profit = price + (price - stop_loss) * 2.5 # هدف 2.5 ضعف المخاطرة
                
                self.active_trade = {
                    'entry': price,
                    'sl': stop_loss,
                    'tp': take_profit,
                    'start_time': datetime.now()
                }
                
                # هنا يتم إضافة كود تنفيذ API بينانس الحقيقي مستقبلاً
                if api_mode == "Real Account":
                    pass # client.order_market_buy(...)
                
                return f"🚀 تم دخول صفقة شراء سبوت عند {price:,.2f}"
            return "🔍 يراقب البيتكوين بانتظار سحب السيولة..."

        # --- حالة: إدارة صفقة مفتوحة (Exit) ---
        else:
            if price >= self.active_trade['tp']:
                profit = 200 # ربح تقديري للرصيد الوهمي
                update_db_after_trade(profit, self.active_trade['entry'], price, "WIN")
                self.is_in_position = False
                return "✅ مبروك! تم ضرب الهدف بربح."

            elif price <= self.active_trade['sl']:
                loss = -100 # خسارة تقديرية
                update_db_after_trade(loss, self.active_trade['entry'], price, "LOSS")
                self.is_in_position = False
                return "🛑 للأسف تم ضرب وقف الخسارة."

            return f"🟢 صفقة مفتوحة | الربح الحالي: {price - self.active_trade['entry']:.2f}"

# =================================================================
# 4. واجهة المستخدم (The Dashboard)
# =================================================================
def main():
    st.set_page_config(page_title="WAHBA BTC PRO", layout="wide")
    initialize_database()
    
    # الجلسة (Session State) للحفاظ على حالة البوت
    if 'my_bot' not in st.session_state:
        st.session_state.my_bot = TradingBot()

    st.markdown("<h1 style='text-align:center; color:#FFD700;'>🦅 WAHBA MASTER: BITCOIN SPOT AI</h1>", unsafe_allow_html=True)
    st.divider()

    # القائمة الجانبية (Sidebar)
    st.sidebar.header("🕹️ التحكم والبيانات")
    current_bal = get_current_balance()
    st.sidebar.metric("المحفظة (Demo Balance)", f"${current_bal:,.2f}", delta=f"{current_bal - 5000:,.2f}")
    
    api_status = st.sidebar.selectbox("وضع التشغيل:", ["Simulation Mode", "Real Account (API)"])
    
    with st.sidebar.expander("🔑 إعدادات الـ API"):
        api_key = st.text_input("Binance API Key", type="password")
        api_secret = st.text_input("Binance Secret Key", type="password")

    # المساحة الرئيسية للعرض
    main_display = st.empty()

    while True:
        analyzer = BitcoinSpotAnalyzer()
        market_indicators = analyzer.fetch_market_data()
        
        if market_indicators:
            current_price = market_indicators.get("close")
            bot_message = st.session_state.my_bot.process_market_cycle(market_indicators, api_status)

            with main_display.container():
                # كارت السعر
                st.markdown(f"""
                <div style="background:#111; padding:30px; border-radius:20px; border:2px solid #333; text-align:center;">
                    <h2 style="color:#888; margin:0;">BTC / USDT SPOT</h2>
                    <h1 style="font-size:5rem; color:#FFD700; margin:10px 0;">${current_price:,.2f}</h1>
                    <div style="background:#222; padding:15px; border-radius:10px; color:#00FFCC; font-size:1.2rem;">
                        {bot_message}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # تفاصيل الصفقة الحالية إذا وجدت
                if st.session_state.my_bot.is_in_position:
                    st.write("---")
                    c1, c2, c3 = st.columns(3)
                    t = st.session_state.my_bot.active_trade
                    c1.info(f"سعر الدخول: {t['entry']:,.2f}")
                    c2.success(f"الهدف (TP): {t['tp']:,.2f}")
                    c3.error(f"الستوب (SL): {t['sl']:,.2f}")

        time.sleep(15) # تحديث كل 15 ثانية
        st.rerun()

if __name__ == "__main__":
    main()
