import streamlit as st
import google.generativeai as genai
import pandas as pd
import sqlite3
import json
import time
from datetime import datetime
from tradingview_ta import TA_Handler, Interval, Exchange

# =================================================================
# 1. إعدادات العقل الكلي (OMNI-STRATEGIST CONFIG)
# =================================================================
API_KEY = "AIzaSyAHLshGDTIRhodR1CMAWGP_DH3622aADJQ" 
genai.configure(api_key=API_KEY)

# إعدادات تضمن ذكاءً حاداً وقدرة على الربط بين المدارس
generation_config = {
    "temperature": 0.3, 
    "top_p": 1,
    "max_output_tokens": 2048,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config
)

# =================================================================
# 2. محرك إدارة الثروة والتعلّم التراكمي (WEALTH ENGINE)
# =================================================================
class WahbaSovereignEngine:
    def __init__(self, db_name="wahba_ultimate_wealth.db"):
        self.db_name = db_name
        self.initial_balance = 190.0
        self._initialize_db()

    def _initialize_db(self):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS wallet (balance REAL)")
            conn.execute("""CREATE TABLE IF NOT EXISTS master_history (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            time TEXT, 
                            symbol TEXT, 
                            strategy_school TEXT, 
                            logic TEXT, 
                            raw_profit REAL,
                            binance_fees REAL,
                            net_profit REAL,
                            current_balance REAL)""")
            if not conn.execute("SELECT balance FROM wallet").fetchone():
                conn.execute("INSERT INTO wallet VALUES (?)", (self.initial_balance,))

    def get_balance(self):
        with sqlite3.connect(self.db_name) as conn:
            return conn.execute("SELECT balance FROM wallet").fetchone()[0]

    def get_memory(self, limit=7):
        """استرجاع الذاكرة لتحليل الأداء وتطوير الاستراتيجية"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                return pd.read_sql_query("SELECT net_profit, strategy_school, logic FROM master_history ORDER BY id DESC LIMIT ?", 
                                         conn, params=(limit,)).to_dict(orient='records')
        except: return []

    def record_trade(self, symbol, school, logic, raw_profit, mood):
        """تنفيذ حسابي دقيق يراعي العمولات وينمي رأس المال"""
        balance = self.get_balance()
        
        # إدارة مخاطر: دخول هجومي (45%) أو حذر (15%) بناءً على رؤية الـ AI
        risk_pct = 0.45 if mood == "Aggressive" else 0.15
        position_value = balance * risk_pct
        
        # حساب العمولات (بيع وشراء = 0.2%)
        fees = position_value * 0.002
        net_profit = raw_profit - fees
        new_balance = balance + net_profit

        with sqlite3.connect(self.db_name) as conn:
            conn.execute("UPDATE wallet SET balance = ?", (new_balance,))
            conn.execute("""INSERT INTO master_history 
                            (time, symbol, strategy_school, logic, raw_profit, binance_fees, net_profit, current_balance) 
                            VALUES (?,?,?,?,?,?,?,?)""",
                         (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), symbol, school, logic, raw_profit, fees, net_profit, new_balance))

# =================================================================
# 3. رادار اقتناص البيانات (MARKET RADAR)
# =================================================================
HALAL_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "AVAXUSDT", "NEARUSDT", "LINKUSDT"]

def fetch_market_data(symbol):
    try:
        handler = TA_Handler(symbol=symbol, screener="crypto", exchange="BINANCE", interval=Interval.INTERVAL_1_MINUTE)
        ta = handler.get_analysis()
        return {
            "price": ta.indicators['close'],
            "rsi": ta.indicators['RSI'],
            "volume": ta.indicators['volume'],
            "mfi": ta.indicators.get('MFI', 50),
            "ema20": ta.indicators['EMA20'],
            "bb_u": ta.indicators['BBANDS.upper'],
            "bb_l": ta.indicators['BBANDS.lower']
        }
    except: return None

# =================================================================
# 4. الواجهة التنفيذية (DASHBOARD)
# =================================================================
def main():
    st.set_page_config(page_title="Wahba Omni-Engine", layout="wide", page_icon="🦅")
    engine = WahbaSovereignEngine()
    
    st.markdown("<h1 style='text-align:center; color:#00ffcc;'>🦅 WAHBA OMNI-STRATEGIST: THE BEAST</h1>", unsafe_allow_html=True)

    # عرض الرصيد والنمو
    balance = engine.get_balance()
    growth = ((balance - 190.0) / 190.0) * 100
    
    col_bal, col_risk, col_fees = st.columns(3)
    col_bal.metric("صافي الرصيد الحالي (NET)", f"${balance:.2f}", f"{growth:.2f}%")
    col_risk.metric("إدارة المخاطر", "هجومية (Hyper-Growth)")
    col_fees.metric("العمولات", "خصم تلقائي 0.2%")

    st.divider()
    monitor = st.empty()

    while True:
        with monitor.container():
            # سحب الذاكرة لضمان التطور المستمر
            memory = engine.get_memory()
            memory_ctx = json.dumps(memory, ensure_ascii=False) if memory else "لا توجد أخطاء سابقة."

            for sym in HALAL_SYMBOLS:
                data = fetch_market_data(sym)
                if not data: continue

                # برومبت العقل الكلي (دمج كل المدارس ضد صناع السوق)
                omni_prompt = f"""
                أنت 'وهبة السيادي'. مهمتك تنمية الرصيد عبر كشف تلاعب الحيتان.
                الذاكرة (الدروس السابقة): {memory_ctx}
                البيانات الحالية لـ {sym}: السعر {data['price']}, RSI {data['rsi']:.1f}, Volume {data['volume']}.
                
                التعليمات الصارمة:
                1. استخدم (SMC, ICT, VSA, Elliott Waves, Wyckoff).
                2. ابحث عن فخاخ السيولة (Liquidity Traps) والفجوات (FVG).
                3. تجاهل المدارس الكلاسيكية؛ ادخل فقط مع 'المال الذكي'.
                4. راعِ أن هناك عمولة 0.2%؛ لا تدخل إلا في صفقة ربحها يغطي التكلفة بمرات.
                
                رد بصيغة JSON فقط:
                {{
                    "decision": "BUY" or "WAIT",
                    "school": "المدرسة المستخدمة",
                    "logic": "لماذا هذه المدرسة هي الأنسب الآن وما هو الفخ المكتشف؟",
                    "mood": "Aggressive" or "Conservative",
                    "est_profit": 12.0
                }}
                """

                try:
                    response = model.generate_content(omni_prompt)
                    res = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
                    
                    if res.get('decision') == "BUY":
                        engine.record_trade(sym, res['school'], res['logic'], res['est_profit'], res['mood'])
                        st.toast(f"🚀 صفقة ناجحة بناءً على {res['school']} في {sym}")
                        time.sleep(1)
                        st.rerun()
                except: continue

            # سجل العمليات الكامل
            st.subheader("📚 السجل السيادي الموحد (Omni Ledger)")
            with sqlite3.connect(engine.db_name) as conn:
                df = pd.read_sql_query("SELECT * FROM master_history ORDER BY id DESC", conn)
                st.dataframe(df, use_container_width=True)

        time.sleep(10)
        st.rerun()

if __name__ == "__main__":
    main()
