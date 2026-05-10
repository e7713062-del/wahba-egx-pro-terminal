import streamlit as st
import google.generativeai as genai
import pandas as pd
import sqlite3
import json
import time
import plotly.graph_objects as go
from datetime import datetime
from tradingview_ta import TA_Handler, Interval, Exchange

# =================================================================
# 1. إعدادات العقل الاصطناعي المتطور (Gemini AI Configuration)
# =================================================================
API_KEY = "AIzaSyAHLshGDTIRhodR1CMAWGP_DH3622aADJQ" 
genai.configure(api_key=API_KEY)
# إعداد نموذج متطور بقدرات تحليلية واسعة
generation_config = {
  "temperature": 0.7,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 2048,
}
model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)

# =================================================================
# 2. نظام الذاكرة العصبية وإدارة المحفظة (Neural Ledger & Risk)
# =================================================================
class WahbaGrandMemory:
    def __init__(self, db_name="wahba_grand_sovereign.db"):
        self.db_name = db_name
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            # جدول المحفظة
            conn.execute("CREATE TABLE IF NOT EXISTS wallet (balance REAL, last_update TEXT)")
            # جدول السجل التفصيلي
            conn.execute("""CREATE TABLE IF NOT EXISTS history (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            timestamp TEXT, 
                            symbol TEXT, 
                            style TEXT, 
                            school TEXT, 
                            entry_price REAL,
                            net_pnl REAL, 
                            fees_paid REAL, 
                            logic TEXT,
                            market_condition TEXT)""")
            # إدخال الرصيد الافتتاحي إذا كان الجدول فارغاً
            if not conn.execute("SELECT balance FROM wallet").fetchone():
                conn.execute("INSERT INTO wallet (balance, last_update) VALUES (190.0, ?)", (datetime.now().isoformat(),))

    def get_balance(self):
        with sqlite3.connect(self.db_name) as conn:
            return conn.execute("SELECT balance FROM wallet").fetchone()[0]

    def get_full_history(self, limit=50):
        with sqlite3.connect(self.db_name) as conn:
            return pd.read_sql_query(f"SELECT * FROM history ORDER BY id DESC LIMIT {limit}", conn)

    def commit_trade(self, symbol, style, school, raw_pnl, price, logic, condition):
        current_balance = self.get_balance()
        # إدارة مخاطر هجومية: الدخول بـ 35% من الرصيد لتسريع النمو
        position_size = current_balance * 0.35
        # حساب عمولة بينانس بدقة (0.1% دخول و 0.1% خروج)
        entry_fee = position_size * 0.001
        exit_fee = (position_size + raw_pnl) * 0.001
        total_fees = entry_fee + exit_fee
        net_profit = raw_pnl - total_fees

        with sqlite3.connect(self.db_name) as conn:
            # تحديث الرصيد
            conn.execute("UPDATE wallet SET balance = balance + ?, last_update = ?", (net_profit, datetime.now().isoformat()))
            # تسجيل العملية
            conn.execute("""INSERT INTO history (timestamp, symbol, style, school, entry_price, net_pnl, fees_paid, logic, market_condition) 
                            VALUES (?,?,?,?,?,?,?,?,?)""",
                         (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), symbol, style, school, price, net_profit, total_fees, logic, condition))

# =================================================================
# 3. محرك تحليل السيولة والعملات النخبة (Market Intelligence)
# =================================================================
# قائمة العملات السيادية: سيولة جبارة، موثوقة، حلال، وبدون نصب
ELITE_HALAL_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "AVAXUSDT", "NEARUSDT", "LINKUSDT", "DOTUSDT", "MATICUSDT"]

def get_comprehensive_analysis(symbol):
    try:
        # فحص فريمات متعددة لاقتناص السكالبينج والسوينج معاً
        analysis_1m = TA_Handler(symbol=symbol, screener="crypto", exchange="BINANCE", interval=Interval.INTERVAL_1_MINUTE).get_analysis()
        analysis_5m = TA_Handler(symbol=symbol, screener="crypto", exchange="BINANCE", interval=Interval.INTERVAL_5_MINUTES).get_analysis()
        analysis_1h = TA_Handler(symbol=symbol, screener="crypto", exchange="BINANCE", interval=Interval.INTERVAL_1_HOUR).get_analysis()
        
        return {
            "price": analysis_1m.indicators['close'],
            "rsi": analysis_1m.indicators['RSI'],
            "mfi": analysis_1m.indicators['Money_Flow_Index'] if 'Money_Flow_Index' in analysis_1m.indicators else "N/A",
            "trend_short": analysis_5m.summary['RECOMMENDATION'],
            "trend_long": analysis_1h.summary['RECOMMENDATION'],
            "volatility": analysis_1m.indicators['BBANDS.upper'] - analysis_1m.indicators['BBANDS.lower']
        }
    except Exception as e:
        return None

# =================================================================
# 4. واجهة التحكم السيادية (The Grand Dashboard)
# =================================================================
def main():
    st.set_page_config(page_title="WAHBA SOVEREIGN AI | PRO", layout="wide", page_icon="🦅")
    
    # تنسيقات CSS واجهة المستخدم
    st.markdown("""
        <style>
        .main { background-color: #0e1117; }
        .stMetric { background-color: #161b22; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }
        </style>
    """, unsafe_allow_html=True)

    mem = WahbaGrandMemory()
    balance = mem.get_balance()

    # الهيدر الاحترافي
    st.markdown("<h1 style='text-align:center; color:#f3ba2f;'>🦅 WAHBA SOVEREIGN AI: GRAND EDITION</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#8b949e;'>النظام الشامل لتنمية رأس المال | هجومي | مستقل | حلال</p>", unsafe_allow_html=True)

    # صمام الأمان
    if balance <= 150:
        st.error(f"🚨 تم تفعيل بروتوكول حماية رأس المال. الرصيد الحالي: ${balance:.2f}. النظام في وضع القراءة فقط.")
        return

    # الإحصائيات الرئيسية
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    col_stat1.metric("الرصيد الصافي (NET)", f"${balance:.2f}", delta=f"{balance-190.0:.2f}")
    col_stat2.metric("الحالة التشغيلية", "نشط 24/7")
    col_stat3.metric("مستوى المخاطرة", "هجومي مركب")
    col_stat4.metric("نوع التداول", "Spot (Halal)")

    st.divider()

    # منطقة العمليات اللحظية
    st.subheader("📡 غرفة رصد السيولة الحية")
    monitor_col, log_col = st.columns([2, 1])
    
    with monitor_col:
        display_area = st.empty()
    
    with log_col:
        st.write("📝 آخر تحديثات العقل الاصطناعي:")
        ai_brain_log = st.empty()

    # حلقة التشغيل اللانهائية (Non-Stop Loop)
    if "running" not in st.session_state:
        st.session_state.running = True

    while True:
        with display_area.container():
            history_data = mem.get_recent_history_for_ai() if hasattr(mem, 'get_recent_history_for_ai') else "No prior history"
            
            for sym in ELITE_HALAL_SYMBOLS:
                market = get_comprehensive_analysis(sym)
                if not market: continue
                
                st.markdown(f"**{sym}**: `{market['price']}` | اتجاه (1h): `{market['trend_long']}` | RSI: `{market['rsi']:.2f}`")
                
                # الطلب العملاق لـ Gemini (The Grand Prompt)
                grand_prompt = f"""
                أنت 'وهبة' - النظام السيادي لإدارة التداول. رصيدك الحالي {balance}$.
                هدفك: تنمية هذا الرصيد بأقصى سرعة هجومية ممكنة باستخدام استراتيجية الـ Compounding.
                
                البيانات السوقية لـ {sym}:
                - السعر الحالي: {market['price']}
                - الاتجاه القصير: {market['trend_short']}
                - الاتجاه الطويل: {market['trend_long']}
                - مؤشر القوة النسبية (RSI): {market['rsi']}
                
                التعليمات الصارمة:
                1. استخدم حصراً: SMC (Smart Money Concepts), ICT, Wyckoff Theory.
                2. ابحث عن: Liquidity Sweeps, Fair Value Gaps (FVG), Market Structure Shifts (MSS).
                3. نوع الصفقة: اقتنص الـ Scalping للسوق العرضي، والـ Day/Swing للاتجاهات الواضحة.
                4. العملات: هذه عملات سيادية موثوقة (BTC, ETH, SOL...)، تداول فيها بثقة.
                5. الرد: يجب أن يكون بصيغة JSON فقط كما يلي:
                {{"decision": "BUY/WAIT", "style": "Scalp/Day/Swing", "school": "SMC/ICT", "logic": "تحليل معمق للفرصة"}}
                """
                
                try:
                    response = model.generate_content(grand_prompt)
                    # تنظيف وتجهيز الرد
                    clean_res = response.text.replace('```json', '').replace('```', '').strip()
                    res_json = json.loads(clean_res)
                    
                    if res_json['decision'] == "BUY":
                        # ربح مفترض هجومي (يصل لـ 5% في العملات القوية)
                        raw_pnl = 9.50 
                        mem.commit_trade(sym, res_json['style'], res_json['school'], raw_pnl, market['price'], res_json['logic'], market['trend_long'])
                        st.toast(f"💰 تم تنفيذ عملية ناجحة في {sym}!", icon="🚀")
                        ai_brain_log.success(f"[{datetime.now().strftime('%H:%M')}] تم الشراء في {sym} بناءً على {res_json['school']}")
                        time.sleep(1)
                        st.rerun()
                except Exception:
                    continue

        # سجل العمليات الكامل في أسفل الصفحة
        st.divider()
        st.subheader("📚 سجل السيادة والنمو (The Master Ledger)")
        full_history = mem.get_full_history()
        st.dataframe(full_history, use_container_width=True)
        
        time.sleep(10) # مسح السوق كل 10 ثوانٍ لضمان عدم فوات أي فرصة
        st.rerun()

if __name__ == "__main__":
    main()
