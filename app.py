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
# 1. القبو: الذاكرة والحماية (الرصيد + صمام الـ 160$)
# =================================================================
class WahbaSovereignCore:
    def __init__(self, db_name="wahba_empire_final.db"):
        self.db_name = db_name
        self.initial_balance = 5000.0
        self.max_loss_limit = 160.0
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            # جدول المحفظة
            conn.execute("CREATE TABLE IF NOT EXISTS wallet (balance REAL)")
            # جدول جينات المدارس (للتعلم الذاتي)
            conn.execute("""CREATE TABLE IF NOT EXISTS school_genes (
                            name TEXT PRIMARY KEY, wins INTEGER DEFAULT 0, 
                            losses INTEGER DEFAULT 0, reliability REAL DEFAULT 0.5)""")
            # جدول السجل الشامل
            conn.execute("""CREATE TABLE IF NOT EXISTS trade_logs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, symbol TEXT, style TEXT, 
                            pnl REAL, time TEXT, school TEXT, status TEXT)""")
            if not conn.execute("SELECT balance FROM wallet").fetchone():
                conn.execute("INSERT INTO wallet VALUES (5000.0)")
            conn.commit()

    def get_balance(self):
        with sqlite3.connect(self.db_name) as conn:
            return conn.execute("SELECT balance FROM wallet").fetchone()[0]

    def is_safety_triggered(self):
        """التأكد أن إجمالي الخسارة لم يتخطى 160 دولار"""
        return (self.initial_balance - self.get_balance()) >= self.max_loss_limit

# =================================================================
# 2. الطوابق الفنية: رادار المدارس (SMC + Wyckoff + Price Action)
# =================================================================
class SchoolRadar:
    @staticmethod
    def scan(symbol, interval, core):
        try:
            h = TA_Handler(symbol=symbol, exchange="BINANCE", screener="crypto", interval=interval, timeout=5)
            analysis = h.get_analysis()
            ind = analysis.indicators
            signals = []

            # مدرسة SMC (سحب السيولة)
            if ind['close'] < ind['low'] * 1.0005: signals.append(("مدرسة SMC - شراء", "BUY"))
            elif ind['close'] > ind['high'] * 0.9995: signals.append(("مدرسة SMC - بيع", "SELL"))

            # مدرسة وايكوف (توصيات القوة)
            if "STRONG" in analysis.summary['RECOMMENDATION']:
                signals.append(("مدرسة وايكوف", "BUY" if "BUY" in analysis.summary['RECOMMENDATION'] else "SELL"))

            # مدرسة حركة السعر (الاندفاع)
            if abs(ind['close'] - ind['open']) > (ind['high'] - ind['low']) * 0.7:
                signals.append(("مدرسة حركة السعر", "BUY" if ind['close'] > ind['open'] else "SELL"))

            # تحديث بنك الجينات آلياً عند ظهور أي مدرسة جديدة
            with sqlite3.connect(core.db_name) as conn:
                for s in signals:
                    conn.execute("INSERT OR IGNORE INTO school_genes (name) VALUES (?)", (s[0],))
            
            return signals, ind['close']
        except: return [], None

# =================================================================
# 3. غرفة المحركات: التنفيذ الذكي متعدد العملات
# =================================================================
class SovereignEngine:
    def __init__(self, core):
        self.core = core
        self.symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]

    def run_engine(self, style, interval, vol):
        while True:
            if self.core.is_safety_triggered(): break
            
            for symbol in self.symbols:
                signals, price = SchoolRadar.scan(symbol, interval, self.core)
                if signals:
                    with sqlite3.connect(self.core.db_name) as conn:
                        gene = conn.execute("SELECT reliability FROM school_genes WHERE name=?", (signals[0][0],)).fetchone()
                        rel = gene[0] if gene else 0.5
                    
                    # لا يدخل إلا لو المدرسة أثبتت كفاءة أو جديدة (تعلم)
                    if rel >= 0.4:
                        win = random.random() < (rel + 0.05)
                        pnl = vol * random.uniform(0.05, 0.12) if win else -(vol * 0.05)
                        status = "ربح 🚀" if win else "خسارة ❌"
                        
                        with sqlite3.connect(self.core.db_name) as conn:
                            # تحديث المحفظة
                            new_bal = self.core.get_balance() + pnl
                            conn.execute("UPDATE wallet SET balance = ?", (new_bal,))
                            # تسجيل الصفقة بالعربي
                            style_ar = "سكالبينج" if style == "SCALPING" else "تداول يومي"
                            conn.execute("INSERT INTO trade_logs (symbol, style, pnl, time, school, status) VALUES (?, ?, ?, ?, ?, ?)",
                                         (symbol, style_ar, pnl, datetime.now().strftime("%H:%M:%S"), signals[0][0], status))
                            # تطوير الجينات (التعلم الذاتي)
                            field = "wins" if win else "losses"
                            conn.execute(f"UPDATE school_genes SET {field} = {field} + 1 WHERE name = ?", (signals[0][0],))
                            conn.execute("UPDATE school_genes SET reliability = CAST(wins AS REAL)/(wins+losses) WHERE name=?", (signals[0][0],))
                
                time.sleep(2) # حماية من حظر الـ API

            time.sleep(30 if style == "SCALPING" else 300)

# =================================================================
# 4. السطح: واجهة القيادة والتحكم (Dashboard)
# =================================================================
def main():
    st.set_page_config(page_title="إمبراطورية وهبة v110", layout="wide")
    core = WahbaSovereignCore()
    engine = SovereignEngine(core)

    if 'active' not in st.session_state:
        threading.Thread(target=engine.run_engine, args=("SCALPING", "1m", 80), daemon=True).start()
        threading.Thread(target=engine.run_engine, args=("DAY_TRADE", "15m", 300), daemon=True).start()
        st.session_state.active = True

    # العرض المرئي
    is_halted = core.is_safety_triggered()
    color = "#FF4B4B" if is_halted else "#00FFCC"
    st.markdown(f"<h1 style='text-align:right; color:{color}; direction:rtl;'>🦅 إمبراطورية وهبة - العمارة الكاملة v110.0</h1>", unsafe_allow_html=True)
    
    bal = core.get_balance()
    loss = 5000 - bal
    
    c1, c2, c3 = st.columns(3)
    c1.metric("الرصيد الإجمالي", f"${bal:,.2f}", delta=f"{bal-5000:,.2f}")
    c2.metric("درع الحماية", f"${160-loss:.2f}")
    c3.metric("العملات", "4 عملات سيولة")

    st.divider()
    
    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.markdown("<h3 style='text-align:right; direction:rtl;'>🧠 بنك الجينات وتطور المدارس</h3>", unsafe_allow_html=True)
        with sqlite3.connect(core.db_name) as conn:
            genes_df = pd.read_sql_query("SELECT name as 'المدرسة', reliability as 'الموثوقية', wins as 'فوز', losses as 'خسارة' FROM school_genes", conn)
            st.dataframe(genes_df, use_container_width=True)
            
            logs_df = pd.read_sql_query("SELECT symbol as 'العملة', style as 'النمط', pnl as 'الربح', status as 'الحالة', time as 'الوقت' FROM trade_logs ORDER BY id DESC LIMIT 10", conn)
            if not logs_df.empty:
                st.markdown("<h3 style='text-align:right; direction:rtl;'>📈 منحنى الأرباح اللحظي</h3>", unsafe_allow_html=True)
                st.line_chart(logs_df.set_index('الوقت')['الربح'].cumsum() + 5000)

    with col_r:
        st.markdown("<h3 style='text-align:right; direction:rtl;'>📜 سجل السيولة</h3>", unsafe_allow_html=True)
        st.table(logs_df[['العملة', 'الحالة', 'الربح']])

    if is_halted:
        st.error("🚨 توقف النظام! تم تفعيل صمام الأمان (160$ خسارة).")

    time.sleep(15)
    st.rerun()

if __name__ == "__main__":
    main()
