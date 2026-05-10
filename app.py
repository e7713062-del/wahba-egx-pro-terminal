import streamlit as st
import google.generativeai as genai
import pandas as pd
import sqlite3
from datetime import datetime
import json
import time

# --- إعداد العقل المركزي (Gemini) ---
API_KEY = "YOUR_GEMINI_API_KEY" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# =================================================================
# 1. نظام الذاكرة المطور (تخزين الصفقات والمدارس)
# =================================================================
class WahbaNeuralMemory:
    def __init__(self, db_name="wahba_final_v3.db"):
        self.db_name = db_name
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS wallet (balance REAL)")
            conn.execute("""CREATE TABLE IF NOT EXISTS experience_vault (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            time TEXT,
                            school_name TEXT,
                            decision TEXT,
                            pnl REAL,
                            logic_summary TEXT)""")
            if not conn.execute("SELECT balance FROM wallet").fetchone():
                conn.execute("INSERT INTO wallet VALUES (190.0)")

    def get_balance(self):
        with sqlite3.connect(self.db_name) as conn:
            return conn.execute("SELECT balance FROM wallet").fetchone()[0]

    def record_final_trade(self, school, decision, pnl, logic):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("UPDATE wallet SET balance = balance + ?", (pnl,))
            conn.execute("INSERT INTO experience_vault (time, school_name, decision, pnl, logic_summary) VALUES (?, ?, ?, ?, ?)",
                         (datetime.now().strftime("%H:%M"), school, decision, pnl, logic))

# =================================================================
# 2. محرك التداول (جاهز للربط بـ Binance لاحقاً)
# =================================================================
class WahbaSovereignAI:
    def __init__(self, memory):
        self.memory = memory
        self.stop_limit = 160.0
        # هنا سيتم إضافة self.exchange = ccxt.binance(...) في المستقبل

    def think_and_learn(self, market_data):
        balance = self.memory.get_balance()
        if balance <= self.stop_limit: return "STOPPED"

        with sqlite3.connect(self.memory.db_name) as conn:
            history = pd.read_sql_query("SELECT * FROM experience_vault ORDER BY id DESC LIMIT 5", conn).to_string()

        prompt = f"""
        أنت 'وهبة' - متداول بشري رقمي. رصيدك {balance}$. حد الأمان 160$.
        السوق الحالي: {market_data}. تاريخك: {history}.
        حلل السوق واستخدم أحدث مدرسة تداول (SMC, ICT, Wyckoff). 
        رد بصيغة JSON: {{"school": "...", "decision": "شراء/بيع/انتظار", "logic": "..."}}
        """
        response = model.generate_content(prompt)
        return json.loads(response.text.replace('```json', '').replace('
```', '').strip())

    def execute_on_binance(self, decision, amount):
        """
        هذه الدالة هي 'مكان الربط المستقبلي'
        سيتم وضع كود ccxt هنا لفتح الصفقات آلياً
        """
        # print("جاري إرسال الأمر لمنصة Binance...")
        pass

# =================================================================
# 3. الواجهة (Command Center)
# =================================================================
def main():
    st.set_page_config(page_title="Wahba AI Sovereign", layout="wide")
    
    if 'mem' not in st.session_state:
        st.session_state.mem = WahbaNeuralMemory()
        st.session_state.bot = WahbaSovereignAI(st.session_state.mem)

    mem = st.session_state.mem
    bot = st.session_state.bot
    balance = mem.get_balance()

    st.title("🦅 Wahba AI: التداول الآلي والتعلم الذاتي")
    
    # صمام الأمان
    if balance <= 160:
        st.error(f"🛑 تم إيقاف النظام للأمان. الرصيد الحالي: {balance:.2f}$")
        return

    # عرض البيانات
    c1, c2 = st.columns(2)
    c1.metric("رصيد المحفظة", f"${balance:.2f}")
    c2.info("النظام جاهز للتعلم وتخزين المدارس الجديدة")

    # لوحة التحكم
    if st.button("🚀 ابدأ تحليل السوق واتخاذ قرار"):
        with st.spinner("وهبة يتواصل مع العقل المركزي ويراجع المدارس الجديدة..."):
            decision_data = bot.think_and_learn("BTC: 65000, Trend: Bullish")
            st.session_state.current_dec = decision_data

    if 'current_dec' in st.session_state:
        res = st.session_state.current_dec
        st.success(f"المدرسة المقترحة: {res['school']}")
        st.write(f"المنطق: {res['logic']}")
        
        if st.button("تأكيد التنفيذ (محاكاة حالياً)"):
            # عند ربط Binance، سيتم استدعاء bot.execute_on_binance هنا
            mem.record_final_trade(res['school'], res['decision'], 5.0, res['logic'])
            st.rerun()

    # سجل الخبرة
    st.divider()
    st.subheader("📚 ذاكرة وهبة الرقمية (المدارس المخزنة)")
    with sqlite3.connect(mem.db_name) as conn:
        st.dataframe(pd.read_sql_query("SELECT * FROM experience_vault", conn), use_container_width=True)

if __name__ == "__main__":
    main()
