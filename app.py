import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import numpy as np
import requests
import os
import glob
from datetime import datetime
import pytz

# --- الإعدادات الفنية (النسخة المطورة 3.1) ---
egypt_tz = pytz.timezone('Africa/Cairo')
today_date = datetime.now(egypt_tz).strftime("%Y-%m-%d")
INTERNAL_DB = f"w_egx_core_{today_date}.log"

class WahbaEngineV3:
    @staticmethod
    def calculate_logic(df):
        # 1. الهدف بناءً على امتداد فيبوناتشي الذهبي 1.618
        # الهدف = نقطة الارتكاز + (المسافة للمقاومة * 1.618)
        df['Target'] = np.round(df['P'] + (df['R1'] - df['P']) * 1.618, 2)
        
        # 2. وقف الخسارة الديناميكي (أسفل الدعم الأول بـ 1%)
        df['StopLoss'] = np.round(df['S1'] * 0.99, 2)
        
        # 3. حساب العائد المتوقع الجديد
        df['ROI'] = np.round(((df['Target'] - df['Price']) / df['Price']) * 100, 1)
        return df

def run_wahba_engine():
    if os.path.exists(INTERNAL_DB):
        return pd.read_csv(INTERNAL_DB)
    
    # سحب البيانات (نفس المنطق السابق مع تحسين التصفية)
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=10).json()
        all_syms = [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except:
        return pd.DataFrame()

    results = []
    for s in all_syms[:40]: # زيادة نطاق البحث لـ 40 سهم
        try:
            h = TA_Handler(symbol=s, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=5)
            analysis = h.get_analysis()
            ind = analysis.indicators
            
            # نظام تقييم (Score) محسن يدمج القوة النسبية والاتجاه
            sc = 0
            rec = analysis.summary["RECOMMENDATION"]
            rsi = ind.get("RSI")
            
            if "BUY" in rec: sc += 5
            if "STRONG_BUY" in rec: sc += 2
            if 45 <= rsi <= 65: sc += 3 # منطقة ارتداد مثالية
            
            results.append({
                "Symbol": s, "Price": round(ind.get("close"), 2), "Score": sc,
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

# --- الواجهة الرسومية المحسنة ---
st.set_page_config(page_title="WAHBA EGX PRO", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background-color: #050505; color: #fff; }
    .card-v3 { background: #0e0e0e; border: 1px solid #1a1a1a; border-radius: 12px; padding: 20px; margin-bottom: 20px; border-right: 4px solid #d4af37; }
    .target-box { background: linear-gradient(90deg, #0f2027, #203a43, #2c5364); padding: 15px; border-radius: 8px; margin: 15px 0; text-align: center; border: 1px solid #d4af37; }
    .stop-loss { color: #ff4b4b; font-size: 14px; font-weight: bold; border: 1px solid #ff4b4b; padding: 2px 8px; border-radius: 4px; }
    .gold-text { color: #d4af37; font-weight: 900; }
</style>
""", unsafe_allow_html=True)

st.title("WAHBA EGX | النسخة الاحترافية 3.1")

if st.button("تحديث المسح الشامل للسوق"):
    with st.spinner("جاري تحليل السيولة ونقاط فيبوناتشي..."):
        market_df = run_wahba_engine()
    
    if not market_df.empty:
        # عرض فقط الأسهم ذات التقييم المرتفع
        top_picks = market_df[market_df['Score'] >= 6].sort_values(by="Score", ascending=False)
        
        cols = st.columns(2) # توزيع الكروت على عمودين
        for i, (idx, row) in enumerate(top_picks.iterrows()):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="card-v3">
                    <div style="display:flex; justify-content:space-between;">
                        <span style="font-size:24px;" class="gold-text">{row['Symbol']}</span>
                        <span class="stop-loss">إيقاف الخسارة: {row['StopLoss']}</span>
                    </div>
                    <div style="margin: 10px 0;">السعر الحالي: <b>{row['Price']} ج.م</b></div>
                    <div class="target-box">
                        <div style="font-size:12px; color:#d4af37;">الهدف الفني (Fib 1.618)</div>
                        <div style="font-size:28px; font-weight:bold; color:#00ff00;">{row['Target']}</div>
                        <div style="color:#00ff00; font-size:14px;">ربح متوقع: {row['ROI']}%</div>
                    </div>
                    <div style="display:flex; justify-content:space-around; font-size:12px; color:#888;">
                        <span>دعم: {row['S1']}</span>
                        <span>ارتكاز: {row['P']}</span>
                        <span>مقاومة: {row['R1']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("فشل في جلب البيانات، تأكد من الاتصال بالإنترنت.")
