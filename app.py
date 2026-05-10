import streamlit as st
import pandas as pd
import sqlite3
import threading
import time
import random
from datetime import datetime
from tradingview_ta import TA_Handler, Interval
import plotly.graph_objects as go

# =================================================================
# 1. الأساسات: الذاكرة السيادية والحماية (Core & Safety)
# =================================================================
class WahbaSovereignV100:
    def __init__(self, db_name="wahba_final_v100.db"):
        self.db_name = db_name
        self.initial_balance = 5000.0
        self.max_loss_limit = 160.0
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS wallet (balance REAL)")
            conn.execute("""CREATE TABLE IF NOT EXISTS school_genes (
                            name TEXT PRIMARY KEY, wins INTEGER DEFAULT 0, 
                            losses INTEGER DEFAULT 0, reliability REAL DEFAULT 0.5)""")
            conn.execute("""CREATE TABLE IF NOT EXISTS trade_logs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, style TEXT, 
                            pnl REAL, time TEXT, school TEXT, status TEXT)""")
            if not conn.execute("SELECT balance FROM wallet").fetchone():
                conn.execute("INSERT INTO wallet VALUES (5000.0)")
            conn.commit()

    def get_balance(self):
        with sqlite3.connect(self.db_name) as conn:
            return conn.execute("SELECT balance FROM wallet").fetchone()[0]

    def is_safety_triggered(self):
        return (self.initial_balance - self.get_balance()) >= self.max_loss_limit

# =================================================================
# 2. الطابق الفني: رادار المدارس الذكي (SMC, Wyckoff, AI)
# =================================================================
class SchoolRadar:
    @staticmethod
    def scan(symbol, interval, core):
        try:
            h = TA_Handler(symbol=symbol, exchange="BINANCE", screener="crypto", interval=interval, timeout=5)
            analysis = h.get_analysis()
            ind = analysis.indicators
            signals = []

            # --- [مدرسة SMC: سحب السيولة] ---
            if ind['close'] < ind['low'] * 1.0005: signals.append(("مدرسة SMC - شراء", "BUY"))
            elif ind['close'] > ind['high'] * 0.9995: signals.append(("مدرسة SMC - بيع", "SELL"))

            # --- [مدرسة Wyckoff: الفوليوم والتجميع] ---
            if "STRONG" in analysis.summary['RECOMMENDATION']:
                signals.append(("مدرسة وايكوف", "BUY" if "BUY" in analysis.summary['RECOMMENDATION'] else "SELL"))

            # --- [تعلم مدارس جديدة: الاندفاع السعري] ---
            if abs(ind['close'] - ind['open']) > (ind['high'] - ind['low']) * 0.7:
                signals.append(("مدرسة حركة السعر", "BUY" if ind['close'] > ind['open'] else "SELL"))

            with sqlite3.connect(core.db_name) as conn:
                for s in signals:
                    conn.execute("INSERT OR IGNORE INTO school_genes (name) VALUES (?)", (s[0],))
            
            return signals, ind['close']
        except: return [], None

# =================================================================
# 3. غرفة المحركات: التنفيذ والتعلم الذاتي (Execution & ML)
# =================================================================
class SovereignEngine:
    def __init__(self, core):
        self.core = core

    def start_trading(self, style, interval, vol):
        while True:
            if self.core.is_safety_triggered(): break
            
            signals, price = SchoolRadar.scan("BTCUSDT", interval, self.core)
            if signals:
                with sqlite3.connect(self.core.db_name) as conn:
                    gene = conn.execute("SELECT name, reliability FROM school_genes WHERE name=?", (signals[0][0],)).fetchone()
                    reliability = gene[1] if gene else 0.5
                
                if reliability >= 0.4:
                    win = random.random() < (reliability + 0.05)
                    pnl = vol * random.uniform(0.05, 0.1) if win else -(vol * 0.04)
                    status = "ربح 🚀" if win else "خسارة ❌"
                    
                    with sqlite3.connect(self.core.db_name) as conn:
                        new_bal = self.core.get_balance() + pnl
                        conn.execute("UPDATE wallet SET balance = ?", (new_bal,))
                        # تعريب الأنماط في السجل
                        style_ar = "سكالبينج" if style == "SCALPING" else "تداول يومي"
                        conn.execute("INSERT INTO trade_logs (style, pnl, time, school, status) VALUES (?, ?, ?, ?, ?)",
                                     (style_ar, pnl, datetime.now().strftime("%H:%M:%S"), signals[0][0], status))
                        field = "wins" if win else "losses"
                        conn.execute(f"UPDATE school_genes SET {field} = {field} + 1 WHERE name = ?", (signals[0][0],))
                        conn.execute("UPDATE school_genes SET reliability = CAST(wins AS REAL)/(wins+losses) WHERE name=?", (signals[0][0],))
            
            time.sleep(40 if style == "SCALPING" else 300)

# =================================================================
# 4. واجهة السيادة المعربة (The Final Dashboard)
# =================================================================
def main():
    st.set_page_config(page_title="إمبراطورية وهبة v100", layout="wide")
    core = WahbaSovereignV100()
    engine = SovereignEngine(core)

    if 'active' not in st.session_state:
        threading.Thread(target=engine.start_trading, args=("SCALPING", "1m", 80), daemon=True).start()
        threading.Thread(target=engine.start_trading, args=("DAY_TRADE", "15m", 300), daemon=True).start()
        st.session_state.active = True

    # --- التصميم ---
    is_halted = core.is_safety_triggered()
    color = "#FF4B4B" if is_halted else "#00FFCC"
    st.markdown(f"<h1 style='text-align:right; color:{color}; direction:rtl;'>🦅 إمبراطورية وهبة السيادية v100.0</h1>", unsafe_allow_html=True)
    
    bal = core.get_balance()
    loss = 5000 - bal
    
    c1, c2, c3 = st.columns(3)
    c1.metric("الرصيد الحالي", f"${bal:,.2f}", delta=f"{bal-5000:,.2f}")
    c2.metric("حالة النظام", "متوقف" if is_halted else "يعمل بنجاح")
    c3.metric("المتبقي من الحماية", f"${160-loss:.2f}")

    st.divider()
    
    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.markdown("<h3 style='text-align:right; direction:rtl;'>🧠 بنك الجينات (المدارس المتعلمة)</h3>", unsafe_allow_html=True)
        with sqlite3.connect(core.db_name) as conn:
            genes_df = pd.read_sql_query("SELECT name as 'اسم المدرسة', wins as 'أرباح', losses as 'خسائر', reliability as 'الموثوقية' FROM school_genes", conn)
            st.dataframe(genes_df, use_container_width=True)
            
            logs_df = pd.read_sql_query("SELECT style as 'النمط', school as 'المدرسة', pnl as 'الربح', status as 'الحالة', time as 'الوقت' FROM trade_logs ORDER BY id DESC LIMIT 10", conn)
            if not logs_df.empty:
                st.markdown("<h3 style='text-align:right; direction:rtl;'>📈 منحنى النمو اللحظي</h3>", unsafe_allow_html=True)
                st.line_chart(logs_df.set_index('الوقت')['الربح'].cumsum() + 5000)

    with col_r:
        st.markdown("<h3 style='text-align:right; direction:rtl;'>📜 آخر التحركات السيادية</h3>", unsafe_allow_html=True)
        st.table(logs_df[['المدرسة', 'الحالة', 'الربح']])

    if is_halted:
        st.error("🚨 تم تفعيل صمام الأمان! الخسارة وصلت 160 دولار. التداول متوقف لحماية الرصيد.")

    time.sleep(10)
    st.rerun()

if __name__ == "__main__":
    main()
