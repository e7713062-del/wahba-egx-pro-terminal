import streamlit as st
import google.generativeai as genai
import pandas as pd
import sqlite3
from datetime import datetime
import json
import time

# =================================================================
# 1. إعداد العقل المركزي (Gemini AI)
# =================================================================
# يفضل وضع الـ API Key في Streamlit Secrets
# إذا كنت تضعه يدوياً:
API_KEY = "YOUR_GEMINI_API_KEY" 

if API_KEY == "YOUR_GEMINI_API_KEY":
    st.error("⚠️ من فضلك ضع مفتاح API Key الخاص بجوجل ليعمل العقل المركزي.")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# =================================================================
# 2. نظام الذاكرة المطور (Neural Memory)
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
            row = conn.execute("SELECT balance FROM wallet").fetchone()
            return row[0] if row else 190.0

    def record_final_trade(self, school, decision, pnl, logic):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("UPDATE wallet SET balance = balance + ?", (pnl,))
            conn.execute("INSERT INTO experience_vault (time, school_name, decision, pnl, logic_summary) VALUES (?, ?, ?, ?, ?)",
                         (datetime.now().strftime("%Y-%m-%d %H:%M"), school, decision, pnl, logic))

# =================================================================
# 3. محرك التفكير والتعلم (Thinking Engine)
# =================================================================
class WahbaSovereignAI:
    def __init__(self, memory):
        self.memory = memory
        self.stop_limit = 160.0

    def think_and_learn(self, market_data):
        balance = self.memory.get_balance()
        if balance <= self.stop_limit:
            return {"error": "STOP_LIMIT_REACHED"}

        # استرجاع التاريخ لتعليمه لـ Gemini
        with sqlite3.connect(self.memory.db_name) as conn:
            history_df = pd.read_sql_query("SELECT school_name, decision, pnl FROM experience_vault ORDER BY id DESC LIMIT 5", conn)
            history_text = history_df.to_string()

        prompt = f"""
        أنت 'وهبة' المتداول الرقمي البشري. رصيدك الحالي {balance}$. حد الأمان 160$.
        بيانات السوق: {market_data}. تاريخك الأخير: {history_text}.
        حلل السوق باستخدام مدرسة حديثة (ICT, SMC, Wyckoff).
        أجب فقط وحصراً بصيغة JSON كالتالي:
        {{"school": "اسم المدرسة", "decision": "شراء/بيع/انتظار", "logic": "السبب باختصار"}}
        ممنوع أي كلام خارج الـ JSON.
        """
        
        try:
            response = model.generate_content(prompt)
            # معالجة النصوص لتفادي خطأ SyntaxError
            res_text = response.text.strip()
            if "```json" in res_text:
                res_text = res_text.split("```json")[1].split("```")[0].strip()
            elif "```" in res_text:
                res_text = res_text.split("```")[1].split("```")[0].strip()
            
            return json.loads(res_text)
        except Exception as e:
            return {
                "school": "تحليل طوارئ",
                "decision": "انتظار",
                "logic": f"خطأ في معالجة البيانات من Gemini. السبب: {str(e)}"
            }

# =================================================================
# 4. الواجهة الرسومية (Command Center)
# =================================================================
def main():
    st.set_page_config(page_title="Wahba AI Sovereign", layout="wide", page_icon="🦅")
    
    if 'mem' not in st.session_state:
        st.session_state.mem = WahbaNeuralMemory()
        st.session_state.bot = WahbaSovereignAI(st.session_state.mem)

    mem = st.session_state.mem
    bot = st.session_state.bot
    balance = mem.get_balance()

    st.markdown("<h1 style='text-align:center; color:#f3ba2f;'>🦅 WAHBA SOVEREIGN AI</h1>", unsafe_allow_html=True)
    
    # صمام الأمان الصارم
    if balance <= 160:
        st.error(f"🛑 تم إيقاف النظام فورياً للأمان! الرصيد الحالي: {balance:.2f}$. (أقل من حد الـ 160$)")
        st.info("النظام لن ينفذ أي عمليات جديدة حتى يتم زيادة الرصيد.")
        return

    # عرض العدادات الحية
    c1, c2, c3 = st.columns(3)
    c1.metric("الرصيد الكلي", f"${balance:.2f}", delta=f"{balance-190:.2f}")
    c2.metric("الحالة", "نشط (تعلم مستمر)")
    c3.metric("حد التوقف", "$160.00")

    st.divider()

    col_left, col_right = st.columns([2, 1])

    with col_right:
        st.subheader("⚙️ وحدة التحكم")
        m_data = st.text_area("بيانات السوق الحالية:", "BTC: 65200, RSI: 58, Market Structure: Bullish")
        if st.button("🚀 اطلب تحليل 'وهبة' الجديد"):
            with st.spinner("وهبة يحلل السوق ويتعلم مدارس جديدة..."):
                res = bot.think_and_learn(m_data)
                if res == "STOP_LIMIT_REACHED":
                    st.error("لا يمكن التحليل، الرصيد منخفض جداً.")
                else:
                    st.session_state.current_dec = res

    with col_left:
        st.subheader("🧠 قرار العقل المدبر")
        if 'current_dec' in st.session_state:
            res = st.session_state.current_dec
            st.success(f"**المدرسة المقترحة:** {res.get('school', 'غير معروفة')}")
            st.warning(f"**القرار المتخذ:** {res.get('decision', 'انتظار')}")
            st.info(f"**المنطق التعليمي:** {res.get('logic', 'لا يوجد سبب محدد')}")
            
            if st.button("✅ تنفيذ الصفقة وتخزين الدرس"):
                # هنا محاكاة لربح/خسارة (سيتم ربط Binance API هنا مستقبلاً)
                pnl = 5.0 if res['decision'] != "انتظار" else 0.0
                mem.record_final_trade(res['school'], res['decision'], pnl, res['logic'])
                st.success("تم التخزين في الذاكرة التراكمية!")
                time.sleep(1)
                st.rerun()

    # سجل الدروس والمدارس
    st.divider()
    st.subheader("📚 سجل الخبرة التاريخي (ما تعلمه البوت)")
    with sqlite3.connect(mem.db_name) as conn:
        df = pd.read_sql_query("SELECT * FROM experience_vault ORDER BY id DESC", conn)
        st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()
