import streamlit as st
import pandas as pd
import sqlite3
import threading
import time
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from tradingview_ta import TA_Handler, Interval
from binance.client import Client
from binance.exceptions import BinanceAPIException # طوبة التعامل مع الأخطاء

# =================================================================
# 🛡️ 1. الأساس والأمان (The Foundation)
# =================================================================
DB_NAME = "wahba_final_empire_2026.db"
SAFE_WALL = 190.0 
INITIAL_BAL = 5000.0

# ربط بينانس مع إضافة نظام الأمان
API_KEY = 'YOUR_API_KEY'
API_SECRET = 'YOUR_API_SECRET'

try:
    client = Client(API_KEY, API_SECRET)
    # طوبة مزامنة الوقت (حل مشكلة التوقيت اللي بتبعت أخطاء)
    client.get_system_status() 
except:
    client = None # لو المفاتيح غلط، هنكمل كأنه نظام تجريبي

class WahbaSovereignCore:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        self._build_tables()

    def _build_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS wallet (id INTEGER PRIMARY KEY, balance REAL)")
        cursor.execute("""CREATE TABLE IF NOT EXISTS neural_memory (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            pattern_hash TEXT, result TEXT, pnl REAL, logic TEXT)""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS trade_journal (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            timestamp TEXT, style TEXT, action TEXT, 
                            pnl REAL, balance REAL, vss_info TEXT)""")
        if not cursor.execute("SELECT balance FROM wallet").fetchone():
            cursor.execute("INSERT INTO wallet VALUES (1, ?)", (INITIAL_BAL,))
        self.conn.commit()

    def get_balance(self):
        # طوبة ذكية: لو بينانس شغال يجيب منه، لو وقع يجيب من الداتابيز
        if client:
            try:
                acc = client.get_asset_balance(asset='USDT')
                return float(acc['free'])
            except: pass
        return self.conn.execute("SELECT balance FROM wallet").fetchone()[0]

# =================================================================
# 🏫 2. مدارس التحليل (SMC & Squeeze) - ثابتة كما هي
# =================================================================
class AdvancedSchools:
    @staticmethod
    def smc_analysis(symbol, interval):
        try:
            h = TA_Handler(symbol=symbol, exchange="BINANCE", screener="crypto", interval=interval, timeout=5)
            ind = h.get_analysis().indicators
            if ind['close'] > ind['high'] * 0.999: return "LIQUIDITY_SWEEP_TOP"
            if ind['close'] < ind['low'] * 1.001: return "LIQUIDITY_SWEEP_BOTTOM"
            return "NORMAL_STRUCTURE"
        except: return "SCANNING"

    @staticmethod
    def squeeze_momentum(symbol, interval):
        import random
        return random.choice(["SQUEEZE_RELEASE", "IN_SQUEEZE", "NO_SIGNAL"])

# =================================================================
# ⚙️ 4. المحرك التنفيذي (The Protected Engine)
# =================================================================
def master_engine(core, style_name, interval, volume, cooldown):
    schools = AdvancedSchools()
    symbol = "BTCUSDT"
    
    while True:
        try:
            balance = core.get_balance()
            if balance <= SAFE_WALL: break 

            h = TA_Handler(symbol=symbol, exchange="BINANCE", screener="crypto", interval=interval, timeout=5)
            analysis = h.get_analysis()
            entry_price = analysis.indicators['close']
            
            smc_state = schools.smc_analysis(symbol, interval)
            sqz_state = schools.squeeze_momentum(symbol, interval)
            
            if smc_state != "NORMAL_STRUCTURE" or sqz_state == "SQUEEZE_RELEASE":
                time.sleep(cooldown) 
                
                # جلب سعر الخروج
                h_exit = TA_Handler(symbol=symbol, exchange="BINANCE", screener="crypto", interval=interval, timeout=5)
                exit_price = h_exit.get_analysis().indicators['close']
                
                price_diff_pct = (exit_price - entry_price) / entry_price
                gross_pnl = volume * price_diff_pct
                net_pnl = gross_pnl - (volume * 0.001 * 2) # خصم العمولة
                
                new_bal = balance + net_pnl
                
                with core.conn as conn:
                    conn.execute("UPDATE wallet SET balance = ?", (new_bal,))
                    conn.execute("""INSERT INTO trade_journal (timestamp, style, action, pnl, balance, vss_info) 
                                    VALUES (?,?,?,?,?,?)""",
                                 (datetime.now().strftime("%H:%M:%S"), style_name, "ENTRY", net_pnl, new_bal, f"{smc_state}"))
                    conn.commit()
        except Exception as e:
            print(f"Engine Warning: {e}") # عشان المحرك ميتوقفش لو حصل خطأ لحظي
        
        time.sleep(30)

# =================================================================
# 🖥️ 5. الواجهة السيادية (Dashboard)
# =================================================================
def main():
    st.set_page_config(page_title="WAHBA EMPIRE 2026", layout="wide")
    core = WahbaSovereignCore()

    st.markdown("<h1 style='text-align:center; color:#f3ba2f;'>🦅 WAHBA SOVEREIGN EMPIRE v21.0</h1>", unsafe_allow_html=True)
    
    # تنبيه في حال وجود مشكلة في الـ API
    if client is None:
        st.warning("⚠️ نظام الـ API غير مفعل أو المفاتيح خاطئة. يعمل النظام الآن في وضع المحاكاة التجريبي.")

    with st.sidebar:
        st.header("⚙️ إدارة المحركات")
        if st.button("🚀 إطلاق الإمبراطورية"):
            threading.Thread(target=master_engine, args=(core, "SCALPING", "1m", 100, 60), daemon=True).start()
            threading.Thread(target=master_engine, args=(core, "DAY", "15m", 500, 300), daemon=True).start()
            threading.Thread(target=master_engine, args=(core, "SWING", "4h", 2000, 3600), daemon=True).start()
            st.success("المحركات في وضع الاستعداد!")

    current_bal = core.get_balance()
    journal = pd.read_sql_query("SELECT * FROM trade_journal ORDER BY id DESC", core.conn)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 الرصيد الحالي", f"${current_bal:,.2f}")
    c2.metric("📉 السكالبينج", f"{len(journal[journal['style']=='SCALPING'])}")
    c3.metric("📊 الداي", f"{len(journal[journal['style']=='DAY'])}")
    c4.metric("🐋 السوينج", f"{len(journal[journal['style']=='SWING'])}")

    if not journal.empty:
        st.plotly_chart(go.Figure(go.Scatter(x=journal['timestamp'], y=journal['balance'], mode='lines', line=dict(color='#00FFCC'))), use_container_width=True)
    
    st.dataframe(journal.head(10), use_container_width=True)

    # مراقب السعر (محمي بـ try/except)
    monitor = st.empty()
    while True:
        price_text = "N/A"
        try:
            if client:
                price = float(client.get_symbol_ticker(symbol="BTCUSDT")['price'])
                price_text = f"${price:,.2f}"
            else:
                # لو مفيش بينانس، نجيب السعر من مصدر بديل
                h = TA_Handler(symbol="BTCUSDT", exchange="BINANCE", screener="crypto", interval="1m", timeout=5)
                price_text = f"${h.get_analysis().indicators['close']:,.2f}"
        except: pass
        
        with monitor.container():
            st.markdown(f"<div style='background:#000; border:2px solid #f3ba2f; padding:30px; border-radius:20px; text-align:center;'><h1 style='font-size:5rem; color:white; margin:0;'>{price_text}</h1></div>", unsafe_allow_html=True)
        time.sleep(10)

if __name__ == "__main__":
    main()
