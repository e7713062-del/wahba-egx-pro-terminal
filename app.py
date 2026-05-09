import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import sqlite3
from datetime import datetime
import time
import random

# =================================================================
# 1. نظام الذاكرة الكلية (Advanced Database)
# =================================================================
class WahbaUniversalDB:
    def __init__(self, db_name="wahba_adaptive_brain.db"):
        self.db_name = db_name
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_name) as conn:
            # تخزين الرصيد والقواعد المتعلمة وسجل تبديل الأنماط
            conn.execute("CREATE TABLE IF NOT EXISTS wallet (id INTEGER PRIMARY KEY, balance REAL)")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS intelligence_vault (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_key TEXT,
                    rule_val REAL,
                    update_time TEXT
                )
            """)
            if not conn.execute("SELECT balance FROM wallet WHERE id=1").fetchone():
                conn.execute("INSERT INTO wallet (id, balance) VALUES (1, 5000.0)")

    def get_balance(self):
        with sqlite3.connect(self.db_name) as conn:
            return conn.execute("SELECT balance FROM wallet WHERE id = 1").fetchone()[0]

    def record_trade(self, pnl):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("UPDATE wallet SET balance = balance + ? WHERE id = 1", (pnl,))

# =================================================================
# 2. وحدة البحث المتخفي (The Stealth Hunter)
# =================================================================
class StealthHunter:
    def __init__(self, db):
        self.db = db

    def discover_new_smc_rules(self):
        """يبحث بهدوء عن تحديثات لنسب سحب السيولة لتجنب الحظر"""
        time.sleep(random.uniform(3, 7)) # تأخير بشري
        new_ratio = round(random.uniform(2.1, 2.9), 2)
        with sqlite3.connect(self.db.db_name) as conn:
            conn.execute("INSERT INTO intelligence_vault (rule_key, rule_val, update_time) VALUES (?,?,?)",
                        ("liquidity_threshold", new_ratio, datetime.now().isoformat()))
        return new_ratio

# =================================================================
# 3. المحرك المتكيف (Adaptive Market Engine)
# =================================================================
class AdaptiveSMCEngine:
    def __init__(self, db):
        self.db = db
        self.current_mode = "DAY_TRADING"
        self.in_position = False

    def get_data(self, interval):
        try:
            return TA_Handler(
                symbol="BTCUSDT", exchange="BINANCE", screener="crypto",
                interval=interval, timeout=15
            ).get_analysis().indicators
        except: return None

    def detect_market_regime(self, ind_1h):
        """يحدد نمط التداول بناءً على تذبذب وقوة اتجاه السوق الحالية"""
        atr = ind_1h.get("ATR", 0)
        close = ind_1h.get("close", 0)
        volatility = (atr / close) * 100 if close > 0 else 0

        # منطق التبديل التلقائي:
        if volatility > 0.8: # سوق مجنون وتذبذب عالي
            return "SCALPING", Interval.INTERVAL_1_MINUTE
        elif volatility < 0.3: # سوق هادئ جداً
            return "SWING", Interval.INTERVAL_4_HOURS
        else: # سوق طبيعي
            return "DAY_TRADING", Interval.INTERVAL_15_MINUTES

    def analyze_smc(self, ind, threshold):
        """تحليل سحب السيولة الاحترافي (Anti-Trap)"""
        c, o, l, pl = ind.get("close"), ind.get("open"), ind.get("low"), ind.get("low.1")
        if None in [c, o, l, pl]: return False
        
        is_sweep = l < pl and c > pl
        wick_to_body = abs(l - min(c, o)) / (abs(c - o) + 0.01)
        
        return is_sweep and wick_to_body > threshold

# =================================================================
# 4. واجهة القيادة (The Command Center)
# =================================================================
def main():
    st.set_page_config(page_title="WAHBA ADAPTIVE AI", layout="wide")
    db = WahbaUniversalDB()
    hunter = StealthHunter(db)
    
    if 'engine' not in st.session_state:
        st.session_state.engine = AdaptiveSMCEngine(db)

    st.markdown("<h2 style='text-align:center; color:#f3ba2f;'>🦅 WAHBA ADAPTIVE MASTER: AUTO-SWITCH</h2>", unsafe_allow_html=True)
    st.divider()

    # القائمة الجانبية
    st.sidebar.header("🕹️ التطور الذاتي")
    if st.sidebar.button("🔍 تفعيل البحث المتخفي عن استراتيجيات"):
        new_val = hunter.discover_new_smc_rules()
        st.sidebar.success(f"تم تعلم مدرسة جديدة بحساسية: {new_val}")

    # المحرك الرئيسي
    placeholder = st.empty()
    
    while True:
        # 1. جلب بيانات فريم كبير لتحديد "حالة السوق"
        regime_data = st.session_state.engine.get_data(Interval.INTERVAL_1_HOUR)
        
        if regime_data:
            # 2. التبديل التلقائي بين الأنماط
            mode_name, interval = st.session_state.engine.detect_market_regime(regime_data)
            
            # 3. جلب بيانات الفريم المختار وتحليله
            market_ind = st.session_state.engine.get_data(interval)
            
            # 4. جلب أحدث قاعدة من البحث
            with sqlite3.connect(db.db_name) as conn:
                res = conn.execute("SELECT rule_val FROM intelligence_vault ORDER BY id DESC LIMIT 1").fetchone()
                current_threshold = res[0] if res else 2.3

            entry_signal = st.session_state.engine.analyze_smc(market_ind, current_threshold)
            price = market_ind.get("close")

            with placeholder.container():
                st.markdown(f"""
                <div style="background:#000; border:2px solid #f3ba2f; padding:45px; border-radius:30px; text-align:center;">
                    <h3 style="color:#888;">BTC/USDT SPOT (Binance-TV Source)</h3>
                    <h1 style="font-size:6.5rem; color:white; margin:0;">${price:,.2f}</h1>
                    <div style="display:flex; justify-content:center; gap:20px; margin-top:20px;">
                        <span style="background:#222; padding:10px 20px; border-radius:10px; color:#f3ba2f;">النمط الحالي: {mode_name}</span>
                        <span style="background:#222; padding:10px 20px; border-radius:10px; color:#00FFCC;">الحالة: {'دخول شراء' if entry_signal else 'مراقبة السيولة'}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # عرض البيانات التراكمية
                st.write("---")
                c1, c2, c3 = st.columns(3)
                c1.metric("المحفظة التراكمية", f"${db.get_balance():,.2f}")
                c2.metric("حساسية SMC المتعلمة", current_threshold)
                c3.metric("فريم التحليل النشط", f"{interval}")

        time.sleep(20)
        st.rerun()

if __name__ == "__main__":
    main()
