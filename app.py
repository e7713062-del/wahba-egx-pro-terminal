import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
from datetime import datetime
import pytz
import sqlite3
import numpy as np
from sklearn.linear_model import LinearRegression

# --- 1. SETTINGS & DATABASE ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)
today_key = now_egypt.strftime("%Y-%m-%d")

class WahbaVault:
    @staticmethod
    def init_db():
        with sqlite3.connect("wahba_professional_vault.db") as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS daily_archive 
                         (Symbol TEXT PRIMARY KEY, Price REAL, Score INTEGER, 
                          S1 REAL, P REAL, R1 REAL, Signal TEXT, 
                          ai_target REAL, stop_loss REAL, risk_reward TEXT, date TEXT)''')
            conn.commit()

    @staticmethod
    def save_data(df):
        with sqlite3.connect("wahba_professional_vault.db") as conn:
            conn.execute("DELETE FROM daily_archive")
            df['date'] = today_key
            df.to_sql("daily_archive", conn, if_exists="append", index=False)

    @staticmethod
    def load_data():
        with sqlite3.connect("wahba_professional_vault.db") as conn:
            return pd.read_sql_query("SELECT * FROM daily_archive", conn)

# --- 2. AI & RISK ENGINE ---
class AI_Risk_Engine:
    @staticmethod
    def predict(price, score):
        X = np.array([1, 2, 3, 4, 5]).reshape(-1, 1)
        y = np.array([price * (1 + (score/100)*i) for i in range(5)])
        model = LinearRegression().fit(X, y)
        return round(model.predict(np.array([[6]]))[0], 2)

    @staticmethod
    def calculate_risk(price, target):
        stop_loss = round(price * 0.97, 2)
        reward = target - price
        risk = price - stop_loss
        rr_ratio = round(reward / risk, 2) if risk != 0 else 0
        return stop_loss, f"1:{rr_ratio}"

# --- 3. UI/UX DESIGN (THE TERMINAL LOOK) ---
st.set_page_config(page_title="WAHBA EGX Premium", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif; }
    .stApp { background-color: #000000; color: #ffffff; }
    
    /* Header */
    .nav-bar { 
        text-align: center; padding: 60px 20px; 
        border-bottom: 4px solid #d4af37; 
        background: linear-gradient(180deg, #0a0a0a 0%, #000000 100%);
        margin-bottom: 50px; 
    }
    .logo-text { font-size: 65px; font-weight: 900; color: #fff; letter-spacing: 8px; text-transform: uppercase; }
    .logo-text span { color: #d4af37; }
    .sub-logo { color: #444; font-size: 14px; letter-spacing: 12px; margin-top: 10px; }

    /* Cards & Tiers */
    .section-header { 
        color: #d4af37; border-right: 10px solid #d4af37; 
        padding-right: 25px; margin: 60px 0 30px 0; 
        font-size: 38px; font-weight: 900; letter-spacing: 2px;
    }
    .stock-card { 
        background: #050505; border: 1px solid #1a1a1a; border-radius: 25px; 
        padding: 45px; margin-bottom: 40px; border-top: 6px solid #d4af37;
    }
    .symbol-name { font-size: 45px; font-weight: 900; color: #d4af37; line-height: 1; }
    .price-val { font-size: 35px; font-weight: bold; color: #fff; margin: 15px 0; }
    .signal-badge { font-size: 18px; font-weight: 900; color: #d4af37; border: 1px solid #d4af37; padding: 5px 20px; border-radius: 50px; }

    /* Risk Box */
    .risk-box { background: #000; border: 1px solid #111; padding: 30px; border-radius: 15px; margin: 30px 0; }
    .risk-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 30px; text-align: center; }
    .risk-label { font-size: 11px; color: #555; text-transform: uppercase; letter-spacing: 2px; }
    .risk-data { font-size: 22px; font-weight: 900; color: #fff; }
    .risk-highlight { color: #d4af37; }
    .risk-stop { color: #ff4b4b; }

    /* Levels */
    .levels-grid { display: flex; justify-content: space-around; background: #0a0a0a; padding: 25px; border-radius: 15px; border: 1px solid #111; }
    .num { font-size: 20px; font-weight: 900; color: #d4af37; font-family: monospace; }

    /* Button */
    .stButton>button { 
        background: #d4af37 !important; color: #000 !important; 
        font-weight: 900 !important; border-radius: 15px !important; 
        height: 100px !important; width: 100% !important; border: none !important;
        font-size: 24px !important; letter-spacing: 3px !important;
    }
    
    /* Legal Section */
    .legal-container { margin-top: 100px; padding: 60px; background: #020202; border: 1px solid #111; border-radius: 20px; }
    .legal-header { color: #d4af37; font-size: 18px; font-weight: 900; letter-spacing: 3px; margin-bottom: 25px; text-transform: uppercase; }
    .legal-text { color: #666; font-size: 13px; line-height: 1.8; text-align: justify; }
    .legal-header-ar { color: #d4af37; font-size: 20px; font-weight: 900; margin: 25px 0; text-align: right; direction: rtl; }
    .legal-text-ar { color: #666; font-size: 14px; line-height: 2; text-align: justify; direction: rtl; }
    .owner-signature { color: #fff; font-weight: bold; border-bottom: 1px solid #d4af37; }
    </style>
    
    <div class="nav-bar">
        <div class="logo-text">WAHBA <span>EGX</span></div>
        <div class="sub-logo">INSTITUTIONAL QUANTITATIVE TERMINAL</div>
    </div>
""", unsafe_allow_html=True)

# --- 4. DATA LOGIC ---
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
            
            ai_target = AI_Risk_Engine.predict(ind.get("close"), score)
            stop_loss, rr_ratio = AI_Risk_Engine.calculate_risk(ind.get("close"), ai_target)
            
            results.append({
                "Symbol": sym, "Price": round(ind.get("close"), 2), "Score": score,
                "S1": round(ind.get("Pivot.M.Classic.S1"), 2), "P": round(ind.get("Pivot.M.Classic.Middle"), 2),
                "R1": round(ind.get("Pivot.M.Classic.R1"), 2), "Signal": rec,
                "ai_target": ai_target, "stop_loss": stop_loss, "risk_reward": rr_ratio
            })
        except: continue
        p_bar.progress((i + 1) / len(symbols))
    p_bar.empty()
    df = pd.DataFrame(results)
    WahbaVault.save_data(df)
    return df

# --- 5. MAIN DISPLAY ---
if st.button('GENERATE AND ARCHIVE GOLDEN REPORT'):
    run_strategic_scan()
    st.success("VAULT SYNCHRONIZED")

data = WahbaVault.load_data()

if not data.empty:
    t1 = data[data['Score'] >= 9]
    if not t1.empty:
        st.markdown('<div class="section-header">GOLD TIER SELECTIONS</div>', unsafe_allow_html=True)
        for _, row in t1.iterrows():
            st.markdown(f"""
            <div class="stock-card">
                <div style="display:flex; justify-content:space-between;">
                    <div><div class="symbol-name">{row['Symbol']}</div><div class="price-val">{row['Price']} EGP</div></div>
                    <span class="signal-badge">{row['Signal']}</span>
                </div>
                <div class="risk-box">
                    <div class="risk-grid">
                        <div><div class="risk-label">AI Target</div><div class="risk-data risk-highlight">{row['ai_target']}</div></div>
                        <div><div class="risk-label">Stop Loss</div><div class="risk-data risk-stop">{row['stop_loss']}</div></div>
                        <div><div class="risk-label">Risk/Reward</div><div class="risk-data">{row['risk_reward']}</div></div>
                    </div>
                </div>
                <div class="levels-grid">
                    <div style="text-align:center"><small style="color:#444">PIVOT</small><br><span class="num">{row['P']}</span></div>
                    <div style="text-align:center"><small style="color:#444">R1</small><br><span class="num">{row['R1']}</span></div>
                </div>
            </div>""", unsafe_allow_html=True)

# --- 6. FIXED LEGAL FORTRESS ---
st.markdown("""
    <div class="legal-container">
        <div class="legal-header">Intellectual Property & Legal Disclaimer</div>
        <div class="legal-text">
            <b>PROPRIETARY RIGHTS NOTICE:</b> This terminal, known as <b>WAHBA EGX</b>, 
            is the exclusive intellectual property of <span class="owner-signature">Mostafa Tamer Ahmed El-Sayed</span>. 
            Any unauthorized duplication or reverse engineering is strictly prohibited.
            <br><br>
            <b>FINANCIAL DISCLAIMER:</b> AI predictions provided by WAHBA EGX are for informational purposes only. 
            Trading involves high risk, and the developer holds no liability for financial losses.
        </div>
        <hr style="border:0; border-top:1px solid #1a1a1a; margin:30px 0;">
        <div class="legal-header-ar">الملكية الفكرية وإخلاء المسؤولية القانونية</div>
        <div class="legal-text-ar">
            تعتبر منصة <b>WAHBA EGX</b> ملكية فكرية حصرية لـ <span class="owner-signature">مصطفى تامر أحمد السيد</span>. 
            يُمنع منعاً باتاً أي نسخ غير مصرح به. التوقعات الناتجة هي لأغراض تعليمية فقط ولا يتحمل المطور مسؤولية أي خسائر مالية.
        </div>
        <div style="margin-top:40px; color:#222; font-size:10px; letter-spacing:5px; text-align:center;">
            VERIFIED TERMINAL ID: WAHBA-EGX-2026-ALEX
        </div>
    </div>
""", unsafe_allow_html=True)
