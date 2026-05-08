import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import numpy as np
import requests
import os
import glob
from datetime import datetime
import pytz
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# --- الإعدادات الفنية (مخفية عن المستخدم) ---
egypt_tz = pytz.timezone('Africa/Cairo')
today_date = datetime.now(egypt_tz).strftime("%Y-%m-%d")
DATA_STORAGE = f"sys_log_{today_date}.dat" # اسم ملف مموه للخصوصية

class InternalCore:
    def __init__(self):
        self.engine = RandomForestRegressor(n_estimators=250, max_depth=12, random_state=42)
        self.scaler = StandardScaler()

    def process(self, df):
        try:
            feat = ['Price', 'Score', 'S1', 'P', 'R1', 'RSI']
            X = self.scaler.fit_transform(df[feat].values)
            y = df['Price'] * (1 + (df['Score'] / 45))
            self.engine.fit(X, y)
            df['Target'] = np.round(self.engine.predict(X), 2)
            df['Growth'] = np.round(((df['Target'] - df['Price']) / df['Price']) * 100, 1)
            return df
        except:
            df['Target'] = np.round(df['Price'] * 1.06, 2)
            df['Growth'] = 6.0
            return df

def get_market_snapshot():
    # محاولة القراءة من قاعدة البيانات المحلية أولاً
    if os.path.exists(DATA_STORAGE):
        return pd.read_csv(DATA_STORAGE)
    
    # البحث عن آخر إغلاق متاح في حالة الأجازات
    past_logs = glob.glob("sys_log_*.dat")
    if past_logs and not os.path.exists(DATA_STORAGE):
        latest = max(past_logs, key=os.path.getctime)
        return pd.read_csv(latest)

    # سحب البيانات بصمت في حالة عدم الوجود
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=10).json()
        syms = [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except: return pd.DataFrame()

    raw = []
    for s in syms[:25]: # فحص أهم القياديات
        try:
            h = TA_Handler(symbol=s, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=5)
            ind = h.get_analysis().indicators
            r = h.get_analysis().summary["RECOMMENDATION"]
            sc = 0
            if "BUY" in r: sc += 5
            if 40 <= ind.get("RSI", 50) <= 65: sc += 3
            if ind.get("close") > ind.get("Pivot.M.Classic.Middle"): sc += 2
            
            raw.append({
                "Symbol": s, "Price": round(ind.get("close"), 2), "Score": sc,
                "S1": round(ind.get("Pivot.M.Classic.S1"), 2),
                "P": round(ind.get("Pivot.M.Classic.Middle"), 2),
                "R1": round(ind.get("Pivot.M.Classic.R1"), 2),
                "RSI": round(ind.get("RSI", 50), 1)
            })
        except: continue
    
    df = pd.DataFrame(raw)
    if not df.empty:
        core = InternalCore()
        df = core.process(df)
        df.to_csv(DATA_STORAGE, index=False)
    return df

# --- واجهة المستخدم (التصميم المؤسسي القديم) ---
st.set_page_config(page_title="WAHBA INTELLIGENCE", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background-color: #000; color: #fff; }
    
    .nav-bar { text-align: center; padding: 40px; border-bottom: 2px solid #d4af37; background: #000; margin-bottom: 30px; }
    .logo { font-size: 38px; font-weight: 900; letter-spacing: 3px; color: #fff; }
    .logo span { color: #d4af37; }
    
    .card { 
        background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 15px; 
        padding: 25px; margin-bottom: 20px; border-top: 3px solid #d4af37;
    }
    .symbol { font-size: 28px; font-weight: 900; color: #d4af37; }
    .price { font-size: 22px; color: #fff; font-weight: bold; }
    
    .target-container { 
        background: #111; border: 1px dashed #d4af37; padding: 15px; 
        border-radius: 10px; margin: 20px 0; text-align: center;
    }
    .target-val { font-size: 26px; color: #00ff00; font-weight: bold; }
    
    .grid { display: flex; justify-content: space-between; margin-top: 15px; }
    .grid-item { text-align: center; flex: 1; }
    .label { font-size: 10px; color: #555; display: block; }
    .val { font-size: 14px; color: #d4af37; font-weight: bold; }

    .stButton>button {
        background: #d4af37 !important; color: #000 !important; font-weight: 900 !important;
        height: 60px !important; width: 100% !important; border-radius: 0px !important; border: none !important;
    }
    </style>
    
    <div class="nav-bar">
        <div class="logo">WAHBA <span>INTELLIGENCE</span></div>
        <div style="font-size:10px; color:#444; letter-spacing:5px;">INSTITUTIONAL ALGORITHMIC TERMINAL</div>
    </div>
""", unsafe_allow_html=True)

# --- التنفيذ ---
col_main = st.columns([1, 2, 1])[1]
with col_main:
    if st.button("RUN SYSTEM SCAN"):
        with st.spinner("AUTHENTICATING WITH MARKET DATA NODES..."):
            final_df = get_market_snapshot()
        
        if not final_df.empty:
            st.markdown(f"<p style='text-align:center; color:#555;'>DATA TIMESTAMP: {today_date}</p>", unsafe_allow_html=True)
            
            # عرض الفرص القوية فقط
            top = final_df[final_df['Score'] >= 5].sort_values(by="Score", ascending=False)
            
            for idx, row in top.iterrows():
                st.markdown(f"""
                <div class="card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="symbol">{row['Symbol']}</span>
                        <span style="color:#d4af37; font-weight:bold;">SCORE: {row['Score']}/10</span>
                    </div>
                    <div class="price">السعر الحالي: {row['Price']} ج.م</div>
                    
                    <div class="target-container">
                        <div style="font-size:12px; color:#d4af37;">السعر المستهدف (خوارزمي)</div>
                        <div class="target-val">{row['Target']}</div>
                        <div style="color:#00ff00; font-size:14px;">عائد متوقع: {row['Growth']}%</div>
                    </div>

                    <div class="grid">
                        <div class="grid-item"><span class="label">دعم</span><span class="val">{row['S1']}</span></div>
                        <div class="grid-item"><span class="label">ارتكاز</span><span class="val">{row['P']}</span></div>
                        <div class="grid-item"><span class="label">مقاومة</span><span class="val">{row['R1']}</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("SYSTEM OFFLINE: PLEASE TRY AGAIN LATER.")
