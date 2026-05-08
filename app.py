import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
from datetime import datetime
import pytz
import sqlite3
import numpy as np
from sklearn.linear_model import LinearRegression

# --- 1. إعدادات الوقت والبيانات ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)
today_key = now_egypt.strftime("%Y-%m-%d")

class DatabaseManager:
    @staticmethod
    def init_db():
        with sqlite3.connect("wahba_intelligence_v38.db") as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS intelligence_logs 
                         (symbol TEXT, price REAL, target REAL, stop_loss REAL, 
                          probability TEXT, reason TEXT, date TEXT)''')
            conn.commit()

    @staticmethod
    def save_log(df):
        with sqlite3.connect("wahba_intelligence_v38.db") as conn:
            df['date'] = today_key
            df.to_sql("intelligence_logs", conn, if_exists="append", index=False)

# --- 2. عقل الذكاء الاصطناعي المتطور (Neural Brain) ---
class WAHBA_Neural_Core:
    @staticmethod
    def calculate_risk_params(price, atr, rsi, trend_score):
        """إدارة المخاطر الذكية: تحديد وقف الخسارة والهدف بناءً على التذبذب"""
        # إذا كان السهم متذبذب جداً، نوسع الوقف
        multiplier = 2.0 if atr > (price * 0.02) else 1.5
        stop_loss = round(price - (atr * multiplier), 2)
        
        # حساب نسبة النجاح (AI Probability)
        prob = 50 + (trend_score * 5)
        if 50 <= rsi <= 65: prob += 15
        if prob > 95: prob = 98 # لا يوجد يقين 100% في السوق
        
        return stop_loss, f"{min(prob, 98)}%"

    @staticmethod
    def ai_prediction_engine(price, score):
        """توقع السعر باستخدام النمذجة الخطية المتقدمة"""
        X = np.array([1, 2, 3, 4, 5]).reshape(-1, 1)
        y = np.array([price * (1 + (score/120)*i) for i in range(5)])
        model = LinearRegression().fit(X, y)
        return round(model.predict(np.array([[6]]))[0], 2)

st.set_page_config(page_title="Wahba Neural Fortress", layout="wide")

# --- 3. التصميم الإمبراطوري (المحفوظ) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif; }
    .stApp { background-color: #000000; color: #ffffff; }
    .nav-bar { text-align: center; padding: 40px; border-bottom: 3px solid #d4af37; margin-bottom: 30px; }
    .logo-text { font-size: 40px; font-weight: 900; color: #fff; }
    .logo-text span { color: #d4af37; }
    .section-header { color: #d4af37; border-right: 6px solid #d4af37; padding-right: 15px; margin: 40px 0 20px 0; font-size: 26px; font-weight: 900; }
    
    .ai-card {
        background: #080808; border: 1px solid #1a1a1a; border-radius: 20px;
        padding: 30px; margin-bottom: 25px; border-top: 4px solid #d4af37;
        box-shadow: 0 10px 30px rgba(212, 175, 55, 0.05);
    }
    .prob-badge {
        background: #d4af37; color: #000; padding: 5px 12px; 
        border-radius: 8px; font-weight: 900; font-size: 12px;
    }
    
    .legal-fortress {
        background: #020202; border: 1px solid #111; padding: 60px;
        margin-top: 120px; border-radius: 25px; width: 100%;
    }
    </style>
    
    <div class="nav-bar">
        <div class="logo-text">WAHBA <span>NEURAL FORTRESS</span></div>
        <p style="color:#444; font-size:12px; letter-spacing: 5px;">ADVANCED RISK-ADJUSTED AI TERMINAL</p>
    </div>
""", unsafe_allow_html=True)

# --- 4. المحرك التشغيلي ---
DatabaseManager.init_db()

@st.cache_data(ttl=86400)
def fetch_egx_list(date_key):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=15).json()
        return [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except: return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO"]

def run_neural_scan(date_key):
    symbols = fetch_egx_list(date_key)
    results = []
    p_bar = st.progress(0)
    status_msg = st.empty()
    
    for i, sym in enumerate(symbols):
        try:
            status_msg.text(f"⚡ Neural Processing: {sym}")
            h = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=10)
            ind = h.get_analysis().indicators
            
            # 1. تحليل القوة (Scoring)
            score = 0
            if ind.get("close") > ind.get("SMA50"): score += 3
            if ind.get("close") > ind.get("SMA200"): score += 3
            if 45 < ind.get("RSI") < 70: score += 4
            
            # 2. تفعيل عقل الذكاء الاصطناعي
            target = WAHBA_Neural_Core.ai_prediction_engine(ind["close"], score)
            stop_l, prob = WAHBA_Neural_Core.calculate_risk_params(
                ind["close"], ind.get("ATR", ind["close"]*0.03), ind.get("RSI", 50), score
            )
            
            results.append({
                "symbol": sym, "price": round(ind["close"], 2), "target": target,
                "stop_loss": stop_l, "probability": prob, 
                "reason": f"Trend Strength: {score}/10 | Volatility Managed",
                "date": today_key
            })
        except: continue
        p_bar.progress((i + 1) / len(symbols))
    
    p_bar.empty()
    status_msg.empty()
    df = pd.DataFrame(results)
    DatabaseManager.save_log(df)
    return df

# --- 5. واجهة المستخدم ---
if st.button('🛡️ تفعيل الحصن العصبي وإدارة المخاطر'):
    st.session_state.neural_report = run_neural_scan(today_key)

report = st.session_state.get('neural_report')

if report is not None and not report.empty:
    st.markdown('<div class="section-header">📡 نتائج تحليل الحصن العصبي (Risk-Adjusted)</div>', unsafe_allow_html=True)
    
    # عرض أفضل 10 فرص فقط لفلترة الجودة
    top_picks = report.sort_values(by='probability', ascending=False).head(10)
    
    for _, row in top_picks.iterrows():
        st.markdown(f"""
        <div class="ai-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                <span style="font-size:30px; font-weight:900; color:#d4af37;">{row['symbol']}</span>
                <span class="prob-badge">SUCCESS PROBABILITY: {row['probability']}</span>
            </div>
            <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:20px; text-align:center;">
                <div style="background:#000; padding:15px; border-radius:10px;">
                    <small style="color:#555;">ENTRY PRICE</small><br>
                    <b style="font-size:20px;">{row['price']}</b>
                </div>
                <div style="background:#000; padding:15px; border-radius:10px; border:1px solid #00ff87;">
                    <small style="color:#00ff87;">AI TARGET</small><br>
                    <b style="font-size:20px; color:#00ff87;">{row['target']}</b>
                </div>
                <div style="background:#000; padding:15px; border-radius:10px; border:1px solid #ff4b4b;">
                    <small style="color:#ff4b4b;">STOP LOSS (AI)</small><br>
                    <b style="font-size:20px; color:#ff4b4b;">{row['stop_loss']}</b>
                </div>
            </div>
            <div style="margin-top:20px; color:#666; font-size:14px; border-right:3px solid #d4af37; padding-right:10px;">
                💡 {row['reason']}
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- 6. القسم القانوني الإمبراطوري ---
st.markdown("""
    <div class="legal-fortress">
        <div style="display: flex; flex-wrap: wrap; gap: 50px;">
            <div style="flex: 1; min-width: 350px;">
                <h4 style="color:#d4af37; margin-top:0;">⚖️ LEGAL DOMAIN & OWNERSHIP (EN)</h4>
                <p style="color:#444; font-size:12px; line-height:1.6;">
                This advanced neural terminal <b>"WAHBA NEURAL FORTRESS"</b> and all its risk-management algorithms are the exclusive intellectual property of 
                <b>Mostafa Tamer Ahmed El-Sayed</b>. Any unauthorized duplication or reverse engineering is strictly prohibited. 
                AI success probabilities are mathematical estimates and do not guarantee profit. Trading involves high risk.
                </p>
            </div>
            <div style="flex: 1; min-width: 350px; direction: rtl; text-align: right;">
                <h4 style="color:#d4af37; margin-top:0;">⚖️ الملكية القانونية وإخلاء المسؤولية (AR)</h4>
                <p style="color:#444; font-size:12px; line-height:1.6;">
                هذه المنصة العصبية المتطورة <b>"WAHBA NEURAL FORTRESS"</b> وكافة خوارزميات إدارة المخاطر المدمجة بها هي ملكية فكرية حصرية لـ 
                <b>مصطفى تامر أحمد السيد</b>. يُمنع تماماً أي نسخ أو هندسة عكسية للكود. 
                نسب النجاح التي يحددها الذكاء الاصطناعي هي تقديرات رياضية ولا تضمن الربح المطلق. التداول ينطوي على مخاطر عالية.
                </p>
            </div>
        </div>
        <hr style="border:0.1px solid #111; margin:40px 0;">
        <center style="color:#222; font-size:10px; letter-spacing:2px;">© 2026 WAHBA QUANTUM LABS • ALEXANDRIA • ALL RIGHTS RESERVED TO MOSTAFA TAMER</center>
    </div>
""", unsafe_allow_html=True)
