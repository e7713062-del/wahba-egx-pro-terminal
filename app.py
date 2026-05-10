import streamlit as st
import pandas as pd
import sqlite3
import threading
import time
import random 
import os
import csv
from datetime import datetime
from tradingview_ta import TA_Handler, Interval
import plotly.graph_objects as go

# =================================================================
# 📂 القسم 1: مركز التخزين (Wahba Storage Hub)
# =================================================================
class WahbaStorage:
    DB_NAME = "wahba_empire_pro.db"
    VAULT_FILE = "wahba_trading_vault.csv"

    @staticmethod
    def init_storage():
        """تجهيز الداتابيز والخزنة المحلية عند التشغيل"""
        conn = sqlite3.connect(WahbaStorage.DB_NAME, check_same_thread=False)
        cursor = conn.cursor()
        # محفظة وهبة
        cursor.execute("CREATE TABLE IF NOT EXISTS wallet (id INTEGER PRIMARY KEY, balance REAL)")
        # سجل العمليات (Journal)
        cursor.execute("""CREATE TABLE IF NOT EXISTS journal (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            ts TEXT, style TEXT, type TEXT, 
                            pnl REAL, bal REAL, logic TEXT)""")
        # الذاكرة العصبية الذكية
        cursor.execute("""CREATE TABLE IF NOT EXISTS brain (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            pattern TEXT, result TEXT, pnl REAL)""")
        
        if not cursor.execute("SELECT balance FROM wallet").fetchone():
            cursor.execute("INSERT INTO wallet VALUES (1, 5000.0)")
        conn.commit()
        conn.close()

    @staticmethod
    def save_to_csv(data):
        """حفظ نسخة احتياطية فورية في ملف CSV"""
        file_exists = os.path.isfile(WahbaStorage.VAULT_FILE)
        with open(WahbaStorage.VAULT_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Timestamp', 'Strategy', 'Net_PNL', 'Current_Balance', 'Market_Logic'])
            writer.writerow(data)

# =================================================================
# 🧠 القسم 2: مختبر التحليل (SMC & Wyckoff Lab)
# =================================================================
class MarketAnalyst:
    @staticmethod
    def get_signal(symbol, interval):
        """تحليل عميق للسوق باستخدام SMC و Wyckoff"""
        try:
            h = TA_Handler(symbol=symbol, exchange="BINANCE", screener="crypto", interval=interval, timeout=7)
            analysis = h.get_analysis()
            ind = analysis.indicators
            curr_p = ind['close']
            
            # --- منطق المال الذكي (SMC) ---
            logic = "ACCUMULATION" # تجميع (وايكوف)
            if curr_p > ind['high'] * 0.9995: logic = "LIQUIDITY_HUNT_TOP"
            elif curr_p < ind['low'] * 1.0005: logic = "LIQUIDITY_HUNT_BOTTOM"
            
            # --- مراجعة الزخم (Squeeze) ---
            momentum = "STABLE"
            if ind['RSI'] > 70: momentum = "OVERBOUGHT"
            elif ind['RSI'] < 30: momentum = "OVERSOLD"
            
            return curr_p, logic, momentum
        except:
            return None, "CONNECTING", "STABLE"

# =================================================================
# ⚙️ القسم 3: محركات التنفيذ (The Sovereign Engines)
# =================================================================
class TradingEngine:
    def __init__(self, style, interval, volume, duration):
        self.style = style
        self.interval = interval
        self.volume = volume
        self.duration = duration
        self.fee_rate = 0.002 # عمولة 0.2% (دخول وخروج)

    def run(self):
        """تشغيل المحرك في مسار منفصل"""
        while True:
            try:
                price, logic, mom = MarketAnalyst.get_signal("BTCUSDT", self.interval)
                
                if price:
                    # شرط الدخول: سحب سيولة أو تشبع بيعي/شرائي
                    if logic != "ACCUMULATION" or mom != "STABLE":
                        entry_p = price
                        time.sleep(self.duration) # مدة الصفقة
                        
                        # سعر الخروج وحساب النتائج
                        exit_data = MarketAnalyst.get_signal("BTCUSDT", self.interval)
                        exit_p = exit_data[0] if exit_data[0] else entry_p
                        
                        # الحسبة المالية (صافي الربح بعد العمولات)
                        pnl = (self.volume * (exit_p - entry_p) / entry_p) - (self.volume * self.fee_rate)
                        
                        # التحديث في الداتابيز
                        self._update_empire(pnl, logic)
            except: pass
            time.sleep(15)

    def _update_empire(self, pnl, logic):
        conn = sqlite3.connect(WahbaStorage.DB_NAME)
        curr_bal = conn.execute("SELECT balance FROM wallet").fetchone()[0]
        new_bal = curr_bal + pnl
        ts = datetime.now().strftime("%H:%M:%S")
        
        with conn:
            conn.execute("UPDATE wallet SET balance = ?", (new_bal,))
            conn.execute("INSERT INTO journal (ts, style, type, pnl, bal, logic) VALUES (?,?,?,?,?,?)",
                         (ts, self.style, "BOT_ACTION", pnl, new_bal, logic))
            conn.execute("INSERT INTO brain (pattern, result, pnl) VALUES (?,?,?)",
                         (f"{self.style}_{logic}", "WIN" if pnl > 0 else "LOSS", pnl))
        conn.close()
        # حفظ في الخزنة الخارجية
        WahbaStorage.save_to_csv([ts, self.style, f"{pnl:.4f}", f"{new_bal:.2f}", logic])

# =================================================================
# 🖥️ القسم 4: واجهة التحكم (The Command Center)
# =================================================================
def main():
    st.set_page_config(page_title="WAHBA EMPIRE v32", layout="wide")
    WahbaStorage.init_storage()

    # تصميم الواجهة الملكي
    st.markdown("""
        <style>
        .main { background-color: #0e1117; }
        .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #f3ba2f; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align:center; color:#f3ba2f;'>🦅 WAHBA SOVEREIGN EMPIRE v32.0</h1>", unsafe_allow_html=True)
    
    # العدادات العلوية
    conn = sqlite3.connect(WahbaStorage.DB_NAME)
    bal = conn.execute("SELECT balance FROM wallet").fetchone()[0]
    journal_df = pd.read_sql_query("SELECT * FROM journal ORDER BY id DESC", conn)
    brain_count = conn.execute("SELECT COUNT(*) FROM brain").fetchone()[0]
    conn.close()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 الرصيد الإجمالي", f"${bal:,.2f}")
    c2.metric("🧠 الذكاء المكتسب", f"{brain_count} نمط")
    c3.metric("📊 صفقات اليوم", len(journal_df))
    c4.metric("📂 الخزنة المحلية", "Active")

    # لوحة إطلاق المحركات
    with st.sidebar:
        st.header("⚙️ إدارة المحركات")
        if st.button("🚀 إطلاق الإمبراطورية"):
            # 1. محرك السكالبينج (سريع - حجم صغير)
            threading.Thread(target=TradingEngine("SCALPING", "1m", 100, 60).run, daemon=True).start()
            # 2. محرك اليومي (متوسط - حجم أكبر)
            threading.Thread(target=TradingEngine("DAY_TRADE", "15m", 500, 300).run, daemon=True).start()
            # 3. محرك السوينج (صيد الحيتان - حجم كبير)
            threading.Thread(target=TradingEngine("SWING", "1h", 2000, 3600).run, daemon=True).start()
            st.success("تم تشغيل جميع الأنظمة!")

    # عرض الرسوم البيانية والسجلات
    if not journal_df.empty:
        col_left, col_right = st.columns([2, 1])
        with col_left:
            fig = go.Figure(go.Scatter(x=journal_df['ts'], y=journal_df['bal'], mode='lines+markers', name='Wealth'))
            fig.update_layout(title="منحنى نمو الإمبراطورية", template="plotly_dark", height=400)
            st.plotly_chart(fig, use_container_width=True)
        with col_right:
            st.write("### 📜 آخر العمليات")
            st.dataframe(journal_df[['ts', 'style', 'pnl', 'logic']].head(10), use_container_width=True)

    # مراقب السوق الحي
    st.divider()
    monitor = st.empty()
    while True:
        try:
            p, _, _ = MarketAnalyst.get_signal("BTCUSDT", "1m")
            with monitor.container():
                st.markdown(f"<div style='text-align:center;'><h2 style='color:#f3ba2f;'>LIVE BTC PRICE: ${p:,.2f}</h2></div>", unsafe_allow_html=True)
        except: pass
        time.sleep(5)

if __name__ == "__main__":
    main()
