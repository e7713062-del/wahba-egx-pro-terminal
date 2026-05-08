import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
from datetime import datetime
import pytz
import sqlite3
import numpy as np
from sklearn.linear_model import LinearRegression

# --- 1. إعدادات الوقت وقاعدة البيانات ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)
today_key = now_egypt.strftime("%Y-%m-%d")

class WahbaVault:
    @staticmethod
    def init_db():
        with sqlite3.connect("wahba_final_vault.db") as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS daily_archive 
                         (Symbol TEXT PRIMARY KEY, Price REAL, Score INTEGER, 
                          S1 REAL, P REAL, R1 REAL, Signal TEXT, 
                          ai_target REAL, reason TEXT, date TEXT)''')
            conn.commit()

    @staticmethod
    def save_data(df):
        with sqlite3.connect("wahba_final_vault.db") as conn:
            conn.execute("DELETE FROM daily_archive")
            df['date'] = today_key
            df.to_sql("daily_archive", conn, if_exists="append", index=False)

    @staticmethod
    def load_data():
        with sqlite3.connect("wahba_final_vault.db") as conn:
            return pd.read_sql_query("SELECT * FROM daily_archive", conn)

# --- 2. محرك الذكاء الاصطناعي (AI Brain) ---
class AI_Processor:
    @staticmethod
    def predict(price, score):
        X = np.array([1, 2, 3, 4, 5]).reshape(-1, 1)
        y = np.array([price * (1 + (score/100)*i) for i in range(5)])
        model = LinearRegression().fit(X, y)
        return round(model.predict(np.array([[6]]))[0], 2)

st.set_page_config(page_title="Wahba Intelligence AI", layout="wide")

# --- 3. التصميم الأساسي (بدون تعديل) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif; }
    .stApp { background-color: #000000; color: #ffffff; }
    .nav-bar { text-align: center; padding: 30px; border-bottom: 2px solid #d4af37; margin-bottom: 20px; }
    .logo-text { font-size: 30px; font-weight: 900; color: #fff; letter-spacing: 2px; }
    .logo-text span { color: #d4af37; }
    .section-header { color: #d4af37; border-right: 5px solid #d4af37; padding-right: 15px; margin: 40px 0 20px 0; font-size: 24px; font-weight: bold; }
    .stock-card { background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 15px; padding: 25px; margin-bottom: 20px; border-top: 3px solid #d4af37; }
    .symbol-name { font-size: 28px; font-weight: 900; color: #d4af37; }
    .price-val { font-size: 24px; font-weight: bold; color: #fff; }
    .levels-grid { display: flex; justify-content: space-between; margin-top: 20px; background: #000; padding: 10px; border-radius: 8px; border: 1px solid #111; }
    .level-item { text-align: center; }
    .label { font-size: 10px; color: #555; display: block; }
    .num { font-size: 14px; font-weight: bold; color: #d4af37; font-family: monospace; }
    .stButton>button { background: #d4af37 !important; color: #000 !important; font-weight: 900 !important; border-radius: 10px !important; height: 60px !important; width: 100% !important; border: none !important; }
    .footer-box { margin-top: 80px; padding: 40px; text-align: center; border-top: 1px solid #1a1a1a; color: #444; font-size: 12px; }
    </style>
    <div class="nav-bar">
        <div class="logo-text">WAHBA <span>INTELLIGENCE AI</span></div>
        <p style="color:#444; font-size:10px;">INSTITUTIONAL AI STORAGE TERMINAL</p>
    </div>
""", unsafe_allow_html=True)

# --- 4. محرك البيانات الاستراتيجي ---
WahbaVault.init_db()

@st.cache_data(ttl=86400)
def fetch_symbols():
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=15).json()
        return [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except: return ["COMI", "FWRY", "TMGH", "SWDY"]

def run_strategic_scan():
    symbols = fetch_symbols()
    results = []
    p_bar = st.progress(0)
    for i, sym in enumerate(symbols):
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=10)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            rec = analysis.summary["RECOMMENDATION"]
            score = 0
            if "STRONG_BUY" in rec: score += 5
            elif "BUY" in rec: score += 3
            if ind.get("RSI") and 50 <= ind.get("RSI") <= 68: score += 3
            if ind.get("close") > ind.get("Pivot.M.Classic.Middle"): score += 2
            
            ai_target = AI_Processor.predict(ind.get("close"), score)
            results.append({
                "Symbol": sym, "Price": round(ind.get("close"), 2), "Score": score,
                "S1": round(ind.get("Pivot.M.Classic.S1"), 2), "P": round(ind.get("Pivot.M.Classic.Middle"), 2),
                "R1": round(ind.get("Pivot.M.Classic.R1"), 2), "Signal": rec,
                "ai_target": ai_target, "reason": "تحليل استراتيجي مؤرشف"
            })
        except: continue
        p_bar.progress((i + 1) / len(symbols))
    p_bar.empty()
    df = pd.DataFrame(results)
    WahbaVault.save_data(df)
    return df

# --- 5. العرض والتحكم ---
if st.button('🔄 إصدار وحفظ التقرير الذهبي بالذكاء الاصطناعي'):
    run_strategic_scan()
    st.success("تم تحديث البيانات وحفظها في الخزنة.")

data = WahbaVault.load_data()

if not data.empty:
    st.write(f"توقيت التقرير المؤرشف: {data['date'].iloc[0]}")
    
    # تصنيف 1: نخبة النخبة الذهبية (التي طلبتها)
    t1 = data[data['Score'] >= 9]
    if not t1.empty:
        st.markdown('<div class="section-header">⚜️ نخبـة نخبـة الصعـود (AI Optimized)</div>', unsafe_allow_html=True)
        for _, row in t1.iterrows():
            st.markdown(f"""
            <div class="stock-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="symbol-name">{row['Symbol']}</span>
                    <span style="color:#d4af37; font-weight:bold;">{row['Signal']}</span>
                </div>
                <div style="color:#00ff87; font-size:12px; margin-bottom:5px;">🧠 AI PREDICTED TARGET: {row['ai_target']}</div>
                <div class="price-val">{row['Price']} <small style="font-size:12px; color:#444;">EGP</small></div>
                <div class="levels-grid">
                    <div class="level-item"><span class="label">S1 (دعم)</span><span class="num">{row['S1']}</span></div>
                    <div class="level-item"><span class="label">PIVOT (ارتكاز)</span><span class="num">{row['P']}</span></div>
                    <div class="level-item"><span class="label">R1 (مقاومة)</span><span class="num">{row['R1']}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # تصنيف 2: النخبة الصاعدة
    t2 = data[(data['Score'] >= 6) & (data['Score'] < 9)]
    if not t2.empty:
        st.markdown('<div class="section-header">💎 نخبـة الصعـود</div>', unsafe_allow_html=True)
        cols = st.columns(2)
        for idx, row in t2.reset_index().iterrows():
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="stock-card" style="border-top: 1px solid #d4af37;">
                    <div style="font-size:20px; font-weight:900;">{row['Symbol']}</div>
                    <div style="color:#d4af37; font-size:18px;">{row['Price']} EGP</div>
                    <div style="font-size:11px; color:#00ff87;">Target: {row['ai_target']}</div>
                    <div style="font-size:11px; color:#444; margin-top:10px;">R1: {row['R1']} | S1: {row['S1']}</div>
                </div>
                """, unsafe_allow_html=True)

# --- 6. القسم القانوني الكامل (الذي طلبته) ---
st.markdown("""
    <div class="footer-box">
        <p style="font-weight:bold; color:#d4af37;">WAHBA INTELLIGENCE • INSTITUTIONAL DIVISION</p>
        <p>هذا التقرير ملكية فكرية حصرية لـ <b>مصطفى تامر أحمد السيد</b>. التقرير مؤرشف لضمان الثبات الكامل لبيانات الذكاء الاصطناعي.</p>
        <p style="font-size:10px; color:#222;">© 2026 WAHBA AI LABS • ALEXANDRIA • ALL RIGHTS RESERVED</p>
    </div>
""", unsafe_allow_html=True)
