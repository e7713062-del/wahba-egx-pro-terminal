import streamlit as st
from tradingview_ta import TA_Handler, Interval
from binance.client import Client
import pandas as pd
import sqlite3
from datetime import datetime
import time

# ==========================================
# 1. SPOT ONLY CONFIG (تداول سبوت حقيقي فقط)
# ==========================================
# ملاحظة: التداول في Spot Binance هو شراء عملة حقيقية بمال حقيقي
API_KEY = 'YOUR_API_KEY'
API_SECRET = 'YOUR_SECRET_KEY'

# الاتصال ببينانس - تأكد أن الـ API مفعل فيه "Enable Spot Trading" فقط
try:
    client = Client(API_KEY, API_SECRET)
except:
    client = None

# ==========================================
# 2. PURE SMC LOGIC (Sourcing Liquidity)
# ==========================================
class SMCSpotEngine:
    @staticmethod
    def get_analysis():
        try:
            # التحليل مخصص للبيتكوين سبوت فقط على فريم 15 دقيقة
            handler = TA_Handler(
                symbol="BTCUSDT",
                exchange="BINANCE",
                screener="crypto",
                interval=Interval.INTERVAL_15_MINUTES,
                timeout=10
            )
            return handler.get_analysis().indicators
        except:
            return None

    @staticmethod
    def check_sweep(ind):
        c, l, pl = ind.get("close"), ind.get("low"), ind.get("low.1")
        # سحب سيولة قاع (دخول مع الأموال الذكية)
        return l < pl and c > pl, l

# ==========================================
# 3. MEMORY & BALANCE (الذاكرة والرصيد الوهمي)
# ==========================================
def init_db():
    with sqlite3.connect("wahba_halal_spot.db") as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS wallet (id INTEGER PRIMARY KEY, balance REAL)")
        conn.execute("CREATE TABLE IF NOT EXISTS memory (time TEXT, price REAL, res INTEGER)")
        if not conn.execute("SELECT balance FROM wallet WHERE id=1").fetchone():
            conn.execute("INSERT INTO wallet (id, balance) VALUES (1, 5000.0)")

def get_balance():
    with sqlite3.connect("wahba_halal_spot.db") as conn:
        return conn.execute("SELECT balance FROM wallet WHERE id=1").fetchone()[0]

def save_trade(price, res, profit):
    with sqlite3.connect("wahba_halal_spot.db") as conn:
        conn.execute("UPDATE wallet SET balance = balance + ? WHERE id=1", (profit,))
        conn.execute("INSERT INTO memory VALUES (?,?,?)", (datetime.now(), price, res))

# ==========================================
# 4. DASHBOARD & AUTO-TRADER
# ==========================================
st.set_page_config(page_title="WAHBA BTC SPOT", layout="wide")
init_db()

if 'bot_active' not in st.session_state: st.session_state.bot_active = False
if 'in_pos' not in st.session_state: st.session_state.in_pos = False
if 'trade' not in st.session_state: st.session_state.trade = {}

def main():
    st.markdown("<h2 style='text-align:center; color:#f3ba2f;'>₿ WAHBA BITCOIN SPOT AI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:gray;'>Pure SMC - No Leverage - Spot Only</p>", unsafe_allow_html=True)

    # الرصيد في القائمة الجانبية
    bal = get_balance()
    st.sidebar.metric("الرصيد الحالي (وهمي)", f"${bal:,.2f}", delta=f"{bal-5000:.2f}")
    
    # خيار الربط بالـ API (اختياري)
    mode = st.sidebar.toggle("تفعيل الربط الحقيقي (بينانس سبوت)")

    placeholder = st.empty()

    while True:
        ind = SMCSpotEngine.get_analysis()
        if ind:
            price = ind.get("close")
            is_sweep, low_val = SMCSpotEngine.check_sweep(ind)
            
            # --- منطق الدخول (شراء سبوت) ---
            if not st.session_state.in_pos and is_sweep:
                st.session_state.in_pos = True
                sl = low_val * 0.998 # ستوب لوز تحت منطقة السحب
                tp = price + (price - sl) * 2 # هدف رابح
                st.session_state.trade = {'entry': price, 'sl': sl, 'tp': tp}
                st.toast("🚀 دخلت صفقة شراء سبوت!")

            # --- منطق الخروج (بيع سبート) ---
            if st.session_state.in_pos:
                if price >= st.session_state.trade['tp']:
                    save_trade(price, 1, 150)
                    st.session_state.in_pos = False
                    st.balloons()
                elif price <= st.session_state.trade['sl']:
                    save_trade(price, 0, -100)
                    st.session_state.in_pos = False

            # --- الواجهة ---
            with placeholder.container():
                st.markdown(f"""
                <div style="background:#0a0a0a; padding:40px; border-radius:20px; border:1px solid #f3ba2f; text-align:center;">
                    <h1 style="color:white; font-size:4.5rem; margin:0;">${price:,.2f}</h1>
                    <p style="color:#f3ba2f;">{'🟢 في صفقة شراء الآن' if st.session_state.in_pos else '⚪ جاري مراقبة سيولة البيتكوين'}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.session_state.in_pos:
                    c1, c2 = st.columns(2)
                    c1.success(f"الهدف: {st.session_state.trade['tp']:.2f}")
                    c2.error(f"وقف الخسارة: {st.session_state.trade['sl']:.2f}")

        time.sleep(20)
        st.rerun()

if __name__ == "__main__":
    main()
