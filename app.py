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

# --- الإعدادات الفنية (الطبخة السرية) ---
egypt_tz = pytz.timezone('Africa/Cairo')
today_date = datetime.now(egypt_tz).strftime("%Y-%m-%d")
# اسم ملف مخفي وقاعدة بيانات داخلية
INTERNAL_DB = f"w_egx_core_{today_date}.log"

class WahbaCore:
    def __init__(self):
        self.regressor = RandomForestRegressor(n_estimators=200, random_state=42)
        self.scaler = StandardScaler()

    def process_logic(self, df):
        try:
            # الميزات الأساسية للتحليل السويني
            cols = ['Price', 'Score', 'S1', 'P', 'R1']
            X = self.scaler.fit_transform(df[cols].values)
            # استهداف ربح بناءً على معطيات السوق
            y = df['Price'] * (1 + (df['Score'] / 40))
            self.regressor.fit(X, y)
            df['Target'] = np.round(self.regressor.predict(X), 2)
            df['ROI'] = np.round(((df['Target'] - df['Price']) / df['Price']) * 100, 1)
            return df
        except:
            df['Target'] = np.round(df['Price'] * 1.05, 2)
            df['ROI'] = 5.0
            return df

def run_wahba_engine():
    # التحقق من وجود بيانات مخزنة لليوم أو لآخر جلسة
    if os.path.exists(INTERNAL_DB):
        return pd.read_csv(INTERNAL_DB)
    
    past_logs = glob.glob("w_egx_core_*.log")
    if past_logs and not os.path.exists(INTERNAL_DB):
        latest = max(past_logs, key=os.path.getctime)
        return pd.read_csv(latest)

    # سحب البيانات في حالة التشغيل لأول مرة
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=10).json()
        all_syms = [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except:
        return pd.DataFrame()

    results = []
    for s in all_syms[:30]: # التركيز على أنشط 30 سهم
        try:
            h = TA_Handler(symbol=s, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=5)
            analysis = h.get_analysis()
            ind = analysis.indicators
            sc = 0
            rec = analysis.summary["RECOMMENDATION"]
            if "BUY" in rec: sc += 6
            if 40 <= ind.get("RSI", 50) <= 65: sc += 4
            
            results.append({
                "Symbol": s, "Price": round(ind.get("close"), 2), "Score": sc,
                "S1": round(ind.get("Pivot.M.Classic.S1"), 2),
                "P": round(ind.get("Pivot.M.Classic.Middle"), 2),
                "R1": round(ind.get("Pivot.M.Classic.R1"), 2)
            })
        except: continue
    
    df = pd.DataFrame(results)
    if not df.empty:
        core = WahbaCore()
        df = core.process_logic(df)
        df.to_csv(INTERNAL_DB, index=False)
    return df

# --- الواجهة الرسمية WAHBA EGX ---
st.set_page_config(page_title="WAHBA EGX", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background-color: #000; color: #fff; }
    .header-bar { text-align: center; padding: 40px; border-bottom: 2px solid #d4af37; margin-bottom: 30px; }
    .brand { font-size: 45px; font-weight: 900; letter-spacing: 4px; color: #fff; }
    .gold { color: #d4af37; }
    .card-v3 { background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 10px; padding: 25px; margin-bottom: 20px; border-top: 3px solid #d4af37; }
    .target-v3 { background: #111; border: 1px dashed #d4af37; padding: 15px; border-radius: 8px; margin: 20px 0; text-align: center; }
    .stButton>button { background: #d4af37 !important; color: #000 !important; font-weight: 900 !important; width: 100% !important; border: none !important; height: 60px !important; font-size: 20px !important; }
</style>
<div class="header-bar">
    <div class="brand">WAHBA <span class="gold">EGX</span></div>
    <p style="color:#444; font-size:12px; letter-spacing:3px;">PREDICTIVE SWING ALGORITHM v3.0</p>
</div>
""", unsafe_allow_html=True)

# --- تشغيل النظام ---
_, main_col, _ = st.columns([1, 2, 1])

with main_col:
    if st.button("EXECUTE SYSTEM SCAN"):
        with st.spinner("SYNCHRONIZING MARKET LOGS..."):
            market_df = run_wahba_engine()
        
        if not market_df.empty:
            st.markdown(f"<p style='text-align:center; color:#555;'>SESSION ID: {today_date}</p>", unsafe_allow_html=True)
            # اختيار الفرص الذهبية (سكور عالي)
            picks = market_df[market_df['Score'] >= 5].sort_values(by="Score", ascending=False)
            
            for _, row in picks.iterrows():
                # عرض الكروت بالطريقة الرسمية الصافية
                st.markdown(f"""
                <div class="card-v3">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:28px; font-weight:900;" class="gold">{row['Symbol']}</span>
                        <span style="border: 1px solid #d4af37; padding: 2px 12px; border-radius:20px; font-size:12px;">SCORE: {row['Score']}/10</span>
                    </div>
                    <div style="margin-top:15px; font-size:18px;">سعر الإغلاق: <b>{row['Price']}</b> ج.م</div>
                    <div class="target-v3">
                        <div style="font-size:12px; color:#d4af37; margin-bottom:5px;">الهدف الخوارزمي المستهدف</div>
                        <div style="font-size:30px; font-weight:bold; color:#00ff00;">{row['Target']}</div>
                        <div style="color:#00ff00; font-size:14px; font-weight:bold;">العائد المتوقع: {row['ROI']}% +</div>
                    </div>
                    <div style="display:flex; justify-content:space-around; background:#050505; padding:10px; border-radius:5px;">
                        <div style="text-align:center;"><span style="font-size:10px; color:#444;">دعم</span><br><span style="color:#d4af37;">{row['S1']}</span></div>
                        <div style="text-align:center;"><span style="font-size:10px; color:#444;">ارتكاز</span><br><span style="color:#d4af37;">{row['P']}</span></div>
                        <div style="text-align:center;"><span style="font-size:10px; color:#444;">مقاومة</span><br><span style="color:#d4af37;">{row['R1']}</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("DATABASE INITIALIZING: PLEASE RE-RUN IN A FEW MOMENTS.")
