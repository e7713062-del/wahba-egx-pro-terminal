import streamlit as st
import google.generativeai as genai
import pandas as pd
import sqlite3
from datetime import datetime
import json
import time
from tradingview_ta import TA_Handler, Interval

# =================================================================
# 1. إعداد العقل المركزي (Gemini AI) - مفتاحك مدمج وصحيح
# =================================================================
API_KEY = "AIzaSyAHLshGDTIRhodR1CMAWGP_DH3622aADJQ" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# =================================================================
# 2. إدارة الذاكرة السيادية (التعلم والبيانات)
# =================================================================
class WahbaHalalMemory:
    def __init__(self, db_name="wahba_final_v4.db"):
        self.db_name = db_name
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS wallet (balance REAL)")
            conn.execute("""CREATE TABLE IF NOT EXISTS history (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            time TEXT,
                            symbol TEXT,
                            style TEXT,
                            school TEXT,
                            pnl REAL,
                            logic TEXT)""")
            if not conn.execute("SELECT balance FROM wallet").fetchone():
                conn.execute("INSERT INTO wallet VALUES (190.0)")

    def get_balance(self):
        with sqlite3.connect(self.db_name) as conn:
            row = conn.execute("SELECT balance FROM wallet").fetchone()
            return row[0] if row else 190.0

    def record_trade(self, symbol, style, school, pnl, logic):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("UPDATE wallet SET balance = balance + ?", (pnl,))
            conn.execute("""INSERT INTO history (time, symbol, style, school, pnl, logic) 
                         VALUES (?,?,?,?,?,?)""",
                         (datetime.now().strftime("%Y-%m-%d %H:%M"), symbol, style, school, pnl, logic))

# =================================================================
# 3. محرك المسح الحي (Live Market Halal Filter)
# =================================================================
# عملات السيولة العالية فقط (حلال سبوت)
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "AVAXUSDT", "NEARUSDT"]

def fetch_live_data(symbol):
    try:
        handler = TA_Handler(
            symbol=symbol, screener="crypto", exchange="BINANCE", interval=Interval.INTERVAL_5_MINUTES
        )
        analysis = handler.get_analysis()
        return {
            "price": analysis.indicators['close'],
            "summary": analysis.summary['RECOMMENDATION'],
            "rsi": analysis.indicators['RSI']
        }
    except: return None

# =================================================================
# 4. واجهة التحكم والتشغيل (Auto-Pilot Dashboard)
# =================================================================
def main():
    st.set_page_config(page_title="Wahba AI: Sovereign", layout="wide", page_icon="🦅")
    
    mem = WahbaHalalMemory()
    balance = mem.get_balance()

    # التنسيق الجمالي
    st.markdown("<h1 style='text-align:center; color:#f3ba2f;'>🦅 WAHBA SOVEREIGN AI: PRO</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#888;'>نظام مستقل | سبوت حلال | مدارس حديثة (SMC/ICT)</p>", unsafe_allow_html=True)

    # نظام الحماية الصارم
    if balance <= 160:
        st.error(f"🚨 تم تفعيل صمام الأمان! الرصيد الحالي ({balance:.2f}$) وصل لحد التوقف.")
        return

    # عرض العدادات
    c1, c2, c3 = st.columns(3)
    c1.metric("رصيد المحفظة", f"${balance:.2f}", delta=f"{balance-190:.2f}")
    c2.metric("نوع التداول", "Spot (Halal)")
    c3.metric("الوضع الحالي", "الطيار الآلي" if st.session_state.get('run') else "انتظار")

    st.divider()

    # وحدة التحكم بالتشغيل
    col_btn, col_info = st.columns([1, 2])
    with col_btn:
        if st.button("🚀 تشغيل الطيار الآلي المستقل"):
            st.session_state.run = True
            st.success("بدأ 'وهبة' في رصد السيولة آلياً...")

    # حلقة التشغيل الآلي
    if st.session_state.get('run'):
        display_box = st.empty()
        while True:
            with display_box.container():
                for sym in SYMBOLS:
                    market = fetch_live_data(sym)
                    if not market: continue
                    
                    st.write(f"🔍 فحص {sym}: السعر `{market['price']}` | الاتجاه `{market['summary']}`")
                    
                    # استشارة Gemini بالمدارس الحديثة
                    prompt = f"""
                    أنت المتداول 'وهبة'. رصيدك {balance}$. 
                    الهدف: نمو سريع جداً في 'السبوت الحلال'.
                    العملة: {sym} | السعر: {market['price']} | المؤشرات: {market}.
                    التعليمات:
                    1. استخدم حصراً SMC/ICT/Wyckoff.
                    2. ابحث عن Liquidity Sweeps و Order Blocks.
                    3. إذا وجدت فرصة (Scalp/Day/Swing) رد بـ JSON حصراً:
                    {{"decision": "BUY", "style": "نوع الصفقة", "school": "المدرسة الحديثة", "logic": "التحليل"}}
                    4. إذا لم تجد، رد بـ {{"decision": "WAIT"}}
                    """
                    
                    try:
                        resp = model.generate_content(prompt)
                        res = json.loads(resp.text.replace('```json', '').replace('```', '').strip())
                        
                        if res['decision'] == "BUY":
                            # محاكاة الربح (سيتم ربط Binance API هنا مستقبلاً)
                            pnl = 6.50 
                            mem.record_trade(sym, res['style'], res['school'], pnl, res['logic'])
                            st.balloons()
                            st.success(f"✅ صفقة شراء ناجحة في {sym}!")
                            time.sleep(2)
                            st.rerun()
                    except: continue
                
                st.info("🔄 جاري تحديث البيانات والبحث عن فرص جديدة في السيولة...")
                time.sleep(30) # انتظار نصف دقيقة قبل المسح التالي
                st.rerun()

    # سجل الخبرة التراكمي
    st.divider()
    st.subheader("📚 سجل الخبرة والمدارس المكتسبة آلياً")
    with sqlite3.connect(mem.db_name) as conn:
        df = pd.read_sql_query("SELECT * FROM history ORDER BY id DESC", conn)
        st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()
