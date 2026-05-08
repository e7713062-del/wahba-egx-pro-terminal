import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import numpy as np
import requests
import os
import glob
from datetime import datetime
import pytz

# --- الإعدادات الفنية ---
egypt_tz = pytz.timezone('Africa/Cairo')
today_date = datetime.now(egypt_tz).strftime("%Y-%m-%d")
INTERNAL_DB = f"w_egx_core_{today_date}.log"

class WahbaEngineV3:
    @staticmethod
    def calculate_logic(df):
        # تأكد أن الأسماء هنا مطابقة تماماً لما يتم استدعاؤه في الواجهة
        df['Target'] = np.round(df['P'] + (df['R1'] - df['P']) * 1.618, 2)
        df['StopLoss'] = np.round(df['S1'] * 0.99, 2) # تأكد من الاسم StopLoss
        df['ROI'] = np.round(((df['Target'] - df['Price']) / df['Price']) * 100, 1)
        return df

def run_wahba_engine():
    # التحقق من وجود بيانات مخزنة لليوم
    if os.path.exists(INTERNAL_DB):
        try:
            return pd.read_csv(INTERNAL_DB)
        except:
            pass

    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=10).json()
        all_syms = [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except:
        return pd.DataFrame()

    results = []
    for s in all_syms[:30]:
        try:
            h = TA_Handler(symbol=s, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=5)
            analysis = h.get_analysis()
            ind = analysis.indicators
            
            sc = 0
            rec = analysis.summary["RECOMMENDATION"]
            if "BUY" in rec: sc += 6
            if 40 <= ind.get("RSI", 50) <= 65: sc += 4
            
            results.append({
                "Symbol": s, 
                "Price": round(ind.get("close"), 2), 
                "Score": sc,
                "S1": round(ind.get("Pivot.M.Classic.S1"), 2),
                "P": round(ind.get("Pivot.M.Classic.Middle"), 2),
                "R1": round(ind.get("Pivot.M.Classic.R1"), 2)
            })
        except: continue
    
    df = pd.DataFrame(results)
    if not df.empty:
        df = WahbaEngineV3.calculate_logic(df)
        df.to_csv(INTERNAL_DB, index=False)
    return df

# --- الواجهة ---
st.set_page_config(page_title="WAHBA EGX PRO", layout="wide")

# CSS لإصلاح الاتجاه والمظهر
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background-color: #050505; color: #fff; }
    .card-v3 { background: #0e0e0e; border: 1px solid #1a1a1a; border-radius: 12px; padding: 20px; margin-bottom: 20px; border-right: 4px solid #d4af37; text-align: right; }
    .target-box { background: #111; padding: 15px; border-radius: 8px; margin: 15px 0; text-align: center; border: 1px dashed #d4af37; }
    .stop-loss { color: #ff4b4b; border: 1px solid #ff4b4b; padding: 2px 8px; border-radius: 4px; font-size: 14px; }
    .gold { color: #d4af37; }
</style>
""", unsafe_allow_html=True)

st.title("WAHBA EGX | النسخة الاحترافية")

if st.button("تحديث المسح"):
    with st.spinner("جاري التحليل..."):
        # مسح الملف القديم لضمان تحديث البيانات وتجنب KeyError من ملفات قديمة
        if os.path.exists(INTERNAL_DB): os.remove(INTERNAL_DB)
        
        market_df = run_wahba_engine()
    
    if not market_df.empty:
        picks = market_df[market_df['Score'] >= 5].sort_values(by="Score", ascending=False)
        
        cols = st.columns(2)
        for i, (idx, row) in enumerate(picks.iterrows()):
            with cols[i % 2]:
                # تم توحيد الاسم هنا ليكون row['StopLoss']
                st.markdown(f"""
                <div class="card-v3">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:24px;" class="gold">{row['Symbol']}</span>
                        <span class="stop-loss">إيقاف الخسارة: {row['StopLoss']}</span>
                    </div>
                    <div style="margin-top:10px;">السعر: <b>{row['Price']}</b> ج.م</div>
                    <div class="target-box">
                        <div style="font-size:12px; color:#aaa;">الهدف الفني المتوقع</div>
                        <div style="font-size:28px; font-weight:bold; color:#00ff00;">{row['Target']}</div>
                        <div style="color:#00ff00; font-size:14px;">عائد: {row['ROI']}%</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.error("لم يتم العثور على بيانات، حاول مرة أخرى.")
