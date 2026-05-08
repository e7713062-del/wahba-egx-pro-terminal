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
today_date = now_egypt.strftime("%Y-%m-%d")

class WahbaStorage:
    @staticmethod
    def init_db():
        with sqlite3.connect("wahba_strategic_vault.db") as conn:
            # ننشئ الجدول لو مش موجود
            conn.execute('''CREATE TABLE IF NOT EXISTS daily_analysis 
                         (symbol TEXT PRIMARY KEY, price REAL, target REAL, 
                          stop_loss REAL, probability TEXT, reason TEXT, date TEXT)''')
            conn.commit()

    @staticmethod
    def save_new_analysis(df):
        with sqlite3.connect("wahba_strategic_vault.db") as conn:
            # نمسح أي داتا قديمة عشان نحط تحليل اليوم الجديد فريش
            conn.execute("DELETE FROM daily_analysis")
            df['date'] = today_date
            df.to_sql("daily_analysis", conn, if_exists="append", index=False)

    @staticmethod
    def get_last_analysis():
        with sqlite3.connect("wahba_strategic_vault.db") as conn:
            return pd.read_sql_query("SELECT * FROM daily_analysis", conn)

# --- 2. محرك الذكاء الاصطناعي (AI Brain) ---
class AI_Engine:
    @staticmethod
    def predict_target(price, score):
        X = np.array([1, 2, 3, 4, 5]).reshape(-1, 1)
        y = np.array([price * (1 + (score/100)*i) for i in range(5)])
        model = LinearRegression().fit(X, y)
        return round(model.predict(np.array([[6]]))[0], 2)

st.set_page_config(page_title="Wahba Strategic Vault", layout="wide")

# --- 3. التصميم الإمبراطوري المحفوظ ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif; }
    .stApp { background-color: #000000; color: #ffffff; }
    .nav-bar { text-align: center; padding: 40px; border-bottom: 3px solid #d4af37; margin-bottom: 30px; }
    .logo-text { font-size: 40px; font-weight: 900; color: #fff; }
    .logo-text span { color: #d4af37; }
    .stock-card { background: #080808; border: 1px solid #1a1a1a; border-radius: 20px; padding: 30px; margin-bottom: 25px; border-top: 4px solid #d4af37; }
    .legal-fortress { background: #020202; border: 1px solid #111; padding: 60px; margin-top: 120px; border-radius: 25px; width: 100%; }
    </style>
    <div class="nav-bar">
        <div class="logo-text">WAHBA <span>STRATEGIC VAULT</span></div>
        <p style="color:#444; font-size:12px; letter-spacing: 5px;">INSTITUTIONAL PERMANENT ANALYSIS v39.0</p>
    </div>
""", unsafe_allow_html=True)

# --- 4. منطق التشغيل والحفظ ---
WahbaStorage.init_db()

@st.cache_data(ttl=86400)
def get_symbols():
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=15).json()
        return [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except: return ["COMI", "FWRY", "TMGH", "SWDY"]

def run_deep_scan():
    symbols = get_symbols()
    results = []
    p_bar = st.progress(0)
    for i, sym in enumerate(symbols):
        try:
            h = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=10)
            ind = h.get_analysis().indicators
            score = 5 if ind["close"] > ind["SMA50"] else 2
            target = AI_Engine.predict_target(ind["close"], score)
            results.append({
                "symbol": sym, "price": round(ind["close"], 2), "target": target,
                "stop_loss": round(ind["close"] * 0.95, 2), "probability": f"{60 + score*5}%",
                "reason": "تحليل يومي استراتيجي محفوظ"
            })
        except: continue
        p_bar.progress((i + 1) / len(symbols))
    p_bar.empty()
    df = pd.DataFrame(results)
    WahbaStorage.save_new_analysis(df)
    return df

# --- 5. واجهة المستخدم النهائية ---

# محاولة تحميل البيانات المحفوظة أولاً
saved_data = WahbaStorage.get_last_analysis()

col1, col2 = st.columns([2, 1])
with col2:
    if st.button('🔄 تحديث التحليل وحفظه لليوم'):
        saved_data = run_deep_scan()
        st.success("تم تحديث " + today_date + " بنجاح!")

with col1:
    if not saved_data.empty:
        last_date = saved_data['date'].iloc[0]
        st.info(f"📅 تعرض المنصة حالياً تحليل يوم: {last_date}")
    else:
        st.warning("⚠️ لا توجد بيانات محفوظة. برجاء الضغط على زر التحديث.")

if not saved_data.empty:
    for _, row in saved_data.iterrows():
        st.markdown(f"""
        <div class="stock-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:30px; font-weight:900; color:#d4af37;">{row['symbol']}</span>
                <span style="background:#d4af37; color:#000; padding:5px 10px; border-radius:5px; font-weight:bold;">{row['probability']}</span>
            </div>
            <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:20px; margin-top:20px; text-align:center;">
                <div><small style="color:#555;">السعر الحالي</small><br><b>{row['price']}</b></div>
                <div><small style="color:#00ff87;">الهدف المحفوظ</small><br><b style="color:#00ff87;">{row['target']}</b></div>
                <div><small style="color:#ff4b4b;">وقف الخسارة</small><br><b style="color:#ff4b4b;">{row['stop_loss']}</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- 6. الفوتر القانوني الإمبراطوري ---
st.markdown("""
    <div class="legal-fortress">
        <div style="display: flex; flex-wrap: wrap; gap: 50px;">
            <div style="flex: 1; min-width: 350px;">
                <h4 style="color:#d4af37; margin-top:0;">⚖️ STRATEGIC DOMAIN & OWNERSHIP (EN)</h4>
                <p style="color:#444; font-size:12px;">This data is permanently archived for 24-hour cycles. Proprietary intellectual property of <b>Mostafa Tamer Ahmed El-Sayed</b>.</p>
            </div>
            <div style="flex: 1; min-width: 350px; direction: rtl; text-align: right;">
                <h4 style="color:#d4af37; margin-top:0;">⚖️ الملكية الاستراتيجية (AR)</h4>
                <p style="color:#444; font-size:12px;">هذه البيانات مؤرشفة لدورات تبلغ 24 ساعة. ملكية فكرية حصرية لـ <b>مصطفى تامر أحمد السيد</b>.</p>
            </div>
        </div>
        <hr style="border:0.1px solid #111; margin:40px 0;">
        <center style="color:#222; font-size:10px;">© 2026 WAHBA STRATEGIC VAULT • ALL RIGHTS RESERVED</center>
    </div>
""", unsafe_allow_html=True)
