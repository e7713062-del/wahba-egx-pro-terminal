import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import numpy as np
import requests
import os
from datetime import datetime
import pytz

# --- الإعدادات الفنية ---
egypt_tz = pytz.timezone('Africa/Cairo')
today_date = datetime.now(egypt_tz).strftime("%Y-%m-%d")
INTERNAL_DB = f"w_egx_gold_v4_{today_date}.log"

st.set_page_config(page_title="WAHBA EGX GOLD", layout="wide")

# --- محرك الحسابات ---
class WahbaEngineGold:
    @staticmethod
    def calculate_logic(df):
        df['Target'] = np.round(df['P'] + (df['R1'] - df['P']) * 1.618, 2)
        df['StopLoss'] = np.round(df['S1'] * 0.99, 2)
        df['ROI'] = np.round(((df['Target'] - df['Price']) / df['Price']) * 100, 1)
        return df

def run_wahba_engine():
    if os.path.exists(INTERNAL_DB): return pd.read_csv(INTERNAL_DB)
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=10).json()
        all_syms = [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except: return pd.DataFrame()
    results = []
    for s in all_syms[:20]:
        try:
            h = TA_Handler(symbol=s, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=7)
            analysis = h.get_analysis()
            ind = analysis.indicators
            sc = 8 if "STRONG_BUY" in analysis.summary["RECOMMENDATION"] else 5
            results.append({
                "Symbol": s, "Price": round(ind.get("close"), 2), "Score": sc,
                "S1": round(ind.get("Pivot.M.Classic.S1"), 2),
                "P": round(ind.get("Pivot.M.Classic.Middle"), 2),
                "R1": round(ind.get("Pivot.M.Classic.R1"), 2)
            })
        except: continue
    df = pd.DataFrame(results)
    if not df.empty:
        df = WahbaEngineGold.calculate_logic(df)
        df.to_csv(INTERNAL_DB, index=False)
    return df

# --- تصميم الواجهة (تكبير الأحجام) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background-color: #000; }
    
    .main-title {
        text-align: center; color: #d4af37; font-size: 40px; font-weight: 900;
        padding: 30px; border-bottom: 3px solid #d4af37; margin-bottom: 30px;
    }
    
    .stButton>button {
        background: linear-gradient(180deg, #fceabb, #f8b500) !important;
        color: #000 !important; font-weight: 900 !important; height: 70px !important;
        font-size: 24px !important; border-radius: 15px !important; border: none !important;
        width: 100% !important; margin-bottom: 40px;
    }

    .card-gold {
        background: #0a0a0a; border: 3px solid #d4af37; border-radius: 20px;
        padding: 30px; margin-bottom: 40px; box-shadow: 0 0 20px rgba(212,175,55,0.3);
    }

    .sym-name { font-size: 45px; font-weight: 900; color: #d4af37; }
    .score-tag { background: #d4af37; color: #000; padding: 5px 15px; border-radius: 10px; font-size: 20px; font-weight: bold; }

    .target-box-gold {
        background: linear-gradient(135deg, #fceabb, #f8b500);
        border-radius: 15px; padding: 25px; text-align: center; margin: 25px 0;
    }
    .target-label { font-size: 20px; color: #000; font-weight: bold; }
    .target-value { font-size: 60px; font-weight: 900; color: #006400; line-height: 1; }
    .roi-tag { font-size: 22px; color: #006400; font-weight: 900; margin-top: 10px; }

    .tech-table { width: 100%; margin-top: 20px; border-collapse: collapse; }
    .label-tech { font-size: 16px; color: #888; }
    .val-tech { font-size: 24px; color: #d4af37; font-weight: bold; }

    .sl-box { color: #ff4b4b; font-weight: bold; font-size: 22px; text-align: left; margin-top: 20px; border-top: 1px solid #333; padding-top: 10px; }
</style>
""", unsafe_allow_html=True)

# --- عرض المحتوى ---
st.markdown('<div class="main-title">WAHBA EGX GOLD</div>', unsafe_allow_html=True)

if st.button("تحديث المسح الشامل للسوق"):
    if os.path.exists(INTERNAL_DB): os.remove(INTERNAL_DB)
    with st.spinner("جاري التحليل..."):
        df = run_wahba_engine()
    
    if not df.empty:
        for _, row in df.iterrows():
            st.markdown(f"""
            <div class="card-gold">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="sym-name">{row['Symbol']}</span>
                    <span class="score-tag">SCORE: {row['Score']}/10</span>
                </div>
                
                <div style="font-size:25px; margin:15px 0; color:#fff;">السعر الحالي: <b>{row['Price']}</b> ج.م</div>

                <div class="target-box-gold">
                    <div class="target-label">الهدف المستهدف (Fib 1.618)</div>
                    <div class="target-value">{row['Target']}</div>
                    <div class="roi-tag">العائد المتوقع: {row['ROI']}% +</div>
                </div>

                <table class="tech-table">
                    <tr>
                        <td><div class="label-tech">S1 (دعم)</div><div class="val-tech">{row['S1']}</div></td>
                        <td><div class="label-tech">P (ارتكاز)</div><div class="val-tech">{row['P']}</div></td>
                        <td><div class="label-tech">R1 (مقاومة)</div><div class="val-tech">{row['R1']}</div></td>
                    </tr>
                </table>

                <div class="sl-box">⚠️ وقف الخسارة: {row['StopLoss']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error("فشل في جلب البيانات.")
