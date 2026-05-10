import streamlit as st
import google.generativeai as genai
import pandas as pd
import sqlite3
import json
import time
from datetime import datetime
from tradingview_ta import TA_Handler, Interval, Exchange

# =================================================================
# 1. إعدادات السيادة الرقمية (AI CONFIGURATION)
# =================================================================
# مفتاح API الخاص بـ Gemini
API_KEY = "AIzaSyAHLshGDTIRhodR1CMAWGP_DH3622aADJQ" 
genai.configure(api_key=API_KEY)

# إعدادات العقل الاصطناعي لضمان أعلى درجات الدقة التقنية
generation_config = {
    "temperature": 0.1,  # لضمان عدم الهلوسة والالتزام بالبيانات الرقمية
    "top_p": 0.95,
    "max_output_tokens": 1500,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config
)

# =================================================================
# 2. محرك إدارة الذاكرة والتراكم (THE SOVEREIGN ENGINE)
# =================================================================
class WahbaSovereignEngine:
    """
    هذا المحرك هو قلب النظام، مسؤول عن الحسابات، التخزين،
    وتوفير الذاكرة التاريخية للذكاء الاصطناعي ليتعلم من التلاعبات.
    """
    def __init__(self, db_name="wahba_final_sovereign.db"):
        self.db_name = db_name
        self.initial_balance = 190.0
        self._initialize_db()

    def _initialize_db(self):
        """تأسيس البنية التحتية للبيانات"""
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            # تخزين الرصيد اللحظي
            conn.execute("CREATE TABLE IF NOT EXISTS wallet (balance REAL, last_trade_time TEXT)")
            
            # سجل العمليات المتطور (The Ledger)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS master_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    time TEXT, 
                    symbol TEXT, 
                    strategy TEXT, 
                    price REAL,
                    net_profit REAL, 
                    logic_summary TEXT,
                    market_mood TEXT,
                    lesson_learned TEXT
                )
            """)
            
            if not conn.execute("SELECT balance FROM wallet").fetchone():
                conn.execute("INSERT INTO wallet (balance, last_trade_time) VALUES (?, ?)", 
                             (self.initial_balance, datetime.now().isoformat()))

    def get_balance(self):
        with sqlite3.connect(self.db_name) as conn:
            return conn.execute("SELECT balance FROM wallet").fetchone()[0]

    def get_memory_logs(self, count=7):
        """تجهيز سجل الصفقات ليقوم الـ AI بتحليلها والتعلم منها"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                query = "SELECT net_profit, strategy, logic_summary FROM master_history ORDER BY id DESC LIMIT ?"
                return pd.read_sql_query(query, conn, params=(count,)).to_dict(orient='records')
        except:
            return []

    def execute_and_record(self, symbol, strategy, price, raw_profit, logic, mood):
        """تسجيل الصفقة وتحديث المحفظة بناءً على إدارة المخاطر الذكية"""
        current_balance = self.get_balance()
        
        # إدارة مخاطر "صياد الحيتان":
        # دخول ثقيل في الصفقات التي يكتشف فيها AI فخاً واضحاً (Aggressive)
        risk_factor = 0.45 if mood == "Aggressive" else 0.15
        
        # حساب العمولة (تقديرية 0.2%)
        fees = (current_balance * risk_factor) * 0.002
        net_pnl = raw_profit - fees
        
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("UPDATE wallet SET balance = balance + ?", (net_pnl,))
            conn.execute("""
                INSERT INTO master_history 
                (time, symbol, strategy, price, net_profit, logic_summary, market_mood) 
                VALUES (?,?,?,?,?,?,?)
            """, (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                symbol, strategy, price, net_pnl, logic, mood
            ))

# =================================================================
# 3. محرك الرصد المتقدم (ADVANCED MARKET SCANNER)
# =================================================================
# قائمة العملات الحلال ذات السيولة العالية المناسبة لاصطياد الفخاخ
TARGET_ASSETS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "AVAXUSDT", "NEARUSDT", "LINKUSDT"]

def get_market_intelligence(symbol):
    """جلب البيانات الخام لتسليمها لغرفة اتخاذ القرار"""
    try:
        # فحص الفريم القصير (الدقيقة) والفريم المتوسط (الساعة)
        ta_1m = TA_Handler(symbol=symbol, screener="crypto", exchange="BINANCE", interval=Interval.INTERVAL_1_MINUTE).get_analysis()
        ta_1h = TA_Handler(symbol=symbol, screener="crypto", exchange="BINANCE", interval=Interval.INTERVAL_1_HOUR).get_analysis()
        
        return {
            "price": ta_1m.indicators['close'],
            "rsi": ta_1m.indicators['RSI'],
            "volume": ta_1m.indicators['volume'],
            "ema_fast": ta_1m.indicators['EMA20'],
            "bb_upper": ta_1m.indicators['BBANDS.upper'],
            "bb_lower": ta_1m.indicators['BBANDS.lower'],
            "trend_context": ta_1h.summary['RECOMMENDATION']
        }
    except:
        return None

# =================================================================
# 4. واجهة القيادة السيادية (GRAND DASHBOARD)
# =================================================================
def main():
    st.set_page_config(page_title="Wahba AI Sovereign v3", layout="wide", page_icon="🦅")
    
    # تهيئة المحرك
    engine = WahbaSovereignEngine()
    
    # تصميم الواجهة الاحترافي
    st.markdown("""
        <style>
        .stMetric { background: #111; border: 1px solid #333; padding: 20px; border-radius: 15px; }
        h1 { text-shadow: 2px 2px 5px #000; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align:center; color:#00ffcc;'>🦅 WAHBA SOVEREIGN: ANTI-CLASSIC ENGINE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#888;'>نظام متطور لاصطياد تلاعبات صناع السوق (Liquidity & SMC Only)</p>", unsafe_allow_html=True)

    # الإحصائيات الحيوية
    bal = engine.get_balance()
    initial = engine.initial_balance
    total_growth = ((bal - initial) / initial) * 100
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("المحفظة الحالية", f"${bal:.2f}", f"{total_growth:.2f}%")
    c2.metric("وضع التحليل", "Anti-Manipulation")
    c3.metric("الاستهداف", "Halal Assets Only")
    c4.metric("قوة الذاكرة", "7 Recent Trades")

    st.divider()
    
    # منطقة العرض المباشر
    live_feed = st.empty()
    
    while True:
        with live_feed.container():
            # استرجاع الدروس السابقة
            memory_data = engine.get_memory_logs()
            memory_context = json.dumps(memory_data, ensure_ascii=False) if memory_data else "لا يوجد تاريخ متاح."

            for symbol in TARGET_ASSETS:
                intel = get_market_intelligence(symbol)
                if not intel: continue
                
                # بناء البرومبت "صياد الثعالب"
                sovereign_prompt = f"""
                [Identity]: You are 'Wahba Sovereign AI'. You trade against retail traders and with Market Makers.
                [Rules]: 
                1. NEVER use Support/Resistance/Trendlines (Retail Traps).
                2. FOCUS on: Liquidity Grabs, Fair Value Gaps (FVG), Order Blocks, and Stop Hunts.
                3. ANALYSIS: If the price is at a 'Classic Support', wait for the break (Fakeout) then buy the recovery.
                
                [Context]:
                - Memory (Last Trades): {memory_context}
                - Asset: {symbol} | Price: {intel['price']} | RSI: {intel['rsi']:.2f}
                - Trend (1H): {intel['trend_context']}
                
                [Output]: Return JSON ONLY.
                {{
                    "decision": "BUY" or "WAIT",
                    "strategy": "Liquidity Sweep / FVG Inversion / Stop Hunt Catch",
                    "logic": "Explain the manipulation detected",
                    "mood": "Aggressive" or "Conservative"
                }}
                """

                try:
                    response = model.generate_content(sovereign_prompt)
                    # تنظيف وتجهيز الـ JSON
                    clean_txt = response.text.replace('```json', '').replace('
```', '').strip()
                    res = json.loads(clean_txt)

                    if res['decision'] == "BUY":
                        # محاكاة الربح في بيئة الاختبار (10 دولار ربح افتراضي)
                        engine.execute_and_record(
                            symbol, res['strategy'], intel['price'], 10.0, res['logic'], res['mood']
                        )
                        st.toast(f"🎯 تم كشف فخ في {symbol} وتنفيذ {res['strategy']}", icon="🚀")
                        time.sleep(1)
                        st.rerun()
                except:
                    continue

            # عرض سجل العمليات التاريخي
            st.subheader("📚 سجل التعلّم السيادي (Intelligence Ledger)")
            with sqlite3.connect(engine.db_name) as conn:
                df = pd.read_sql_query("SELECT * FROM master_history ORDER BY id DESC", conn)
                st.dataframe(df, use_container_width=True)

        time.sleep(10)
        st.rerun()

if __name__ == "__main__":
    main()
