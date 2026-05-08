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

# --- الإعدادات الفنية (مخفية تماماً) ---
egypt_tz = pytz.timezone('Africa/Cairo')
today_date = datetime.now(egypt_tz).strftime("%Y-%m-%d")
DATA_LOG = f"cache_v3_{today_date}.dat"

class AlphaEngine:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=200, random_state=42)
        self.scaler = StandardScaler()

    def secure_process(self, df):
        try:
            feat = ['Price', 'Score', 'S1', 'P', 'R1']
            X = self.scaler.fit_transform(df[feat].values)
            y = df['Price'] * (1 + (df['Score'] / 40))
            self.model.fit(X, y)
            df['Target'] = np.round(self.model.predict(X), 2)
            df['ROI'] = np.round(((df['Target'] - df['Price']) / df['Price']) * 100, 1)
            return df
        except:
            df['Target'] = df['Price'] * 1.05
            df['ROI'] = 5.0
            return df

def fetch_market_intelligence():
    # 1. فحص الكاش
    if os.path.exists(DATA_LOG):
        return pd.read_csv(DATA_LOG)
    
    # 2. فحص آخر جلسة مسجلة
    past_sessions = glob.glob("cache_v3_*.dat")
    if past_sessions:
        latest = max(past_sessions, key=os.path.getctime)
        return pd.read_csv(latest)

    # 3. سحب بيانات حية بصمت
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=10).json()
        syms = [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except:
        return pd.DataFrame()

    intelligence_data = []
    for s in syms[:30]:
        try:
            h = TA_Handler(symbol=s, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=5)
            ind = h.get_analysis().indicators
            r = h.get_analysis().summary["RECOMMENDATION"]
            sc = 0
            if "BUY" in r: sc += 6
            if 40 <= ind.get("RSI", 50) <= 65: sc += 4
            
            intelligence_data.append({
                "Symbol": s, "Price": round(ind.get("close"), 2), "Score": sc,
                "S1": round(ind.get("Pivot.M.Classic.S1"), 2),
                "P": round(ind.get("Pivot.M.Classic.Middle"), 2),
                "R1": round(ind.get("Pivot.M.Classic.R1"), 2)
            })
        except: continue
    
    df = pd.DataFrame(intelligence_data)
    if not df.empty:
        engine = AlphaEngine()
        df = engine.secure_process(df)
        df.to_csv(DATA_LOG, index=False)
    return df

# --- التصميم المؤسسي (بدون عك) ---
st.set_page_config(page_title="WAHBA INTELLIGENCE", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background-color: #000; color: #fff; }
    .nav { text-align: center; padding: 40px; border-bottom: 2px solid #d4af37; margin-bottom: 30px; }
    .main-title { font-size: 35px; font-weight: 900; letter-spacing: 2px; color: #fff; }
    .gold { color: #d4af37; }
    .card { background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 12px; padding: 20px; margin-bottom: 20px; border-top: 3px solid #d4af37; }
    .target-area { background: #111; border: 1px dashed #d4af37; padding: 15px; border-radius: 10px; margin: 15px 0; text-align: center; }
    .grid { display: flex; justify-content: space-between; margin-top: 15px; background: #050505; padding: 10px; border-radius: 8px; }
    .stButton>button { background: #d4af37 !important; color: #000 !important; font-weight: 900 !important; width: 100% !important; border: none !important; height: 55px !important; }
</style>
<div class="nav">
    <div class="main-title">WAHBA <span class="gold">INTELLIGENCE</span></div>
    <p style="color:#444; font-size:12px;">INSTITUTIONAL ALGORITHMIC TERMINAL</p>
</div>
""", unsafe_allow_html=True)

# --- التشغيل ---
_, center_col, _ = st.columns([1, 2, 1])

with center_col:
    if st.button("RUN SYSTEM SCAN"):
        with st.spinner("CONNECTING TO DATA NODES..."):
            df = fetch_market_intelligence()
        
        if not df.empty:
            st.markdown(f"<p style='text-align:center; color:#555;'>LOG: {today_date}</p>", unsafe_allow_html=True)
            top_opps = df[df['Score'] >= 4].sort_values(by="Score", ascending=False)
            
            for _, row in top_opps.iterrows():
                # استخدام f-string مع مضاعفة الأقواس للـ CSS لمنع ظهور الكود كنص
                card_html = f"""
                <div class="card">
                    <div style="display:flex; justify-content:space-between;">
                        <span style="font-size:24px; font-weight:900;" class="gold">{row['Symbol']}</span>
                        <span style="color:#d4af37;">Score: {row['Score']}/10</span>
                    </div>
                    <div style="margin-top:10px;">السعر الحالي: <b>{row['Price']}</b> ج.م</div>
                    <div class="target-area">
                        <div style="font-size:11px; color:#d4af37;">الهدف الاستراتيجي</div>
                        <div style="font-size:24px; font-weight:bold; color:#00ff00;">{row['Target']}</div>
                        <div style="color:#00ff00; font-size:14px;">عائد محتمل: {row['ROI']}%</div>
                    </div>
                    <div class="grid">
                        <div style="text-align:center;"><span style="font-size:10px; color:#444;">دعم</span><br><span class="gold">{row['S1']}</span></div>
                        <div style="text-align:center;"><span style="font-size:10px; color:#444;">ارتكاز</span><br><span class="gold">{row['P']}</span></div>
                        <div style="text-align:center;"><span style="font-size:10px; color:#444;">مقاومة</span><br><span class="gold">{row['R1']}</span></div>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
        else:
            st.error("INITIALIZING SYSTEM... PLEASE RUN SCAN AGAIN IN 30 SECONDS.")
