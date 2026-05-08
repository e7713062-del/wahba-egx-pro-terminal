import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import numpy as np
import requests
import os
from datetime import datetime
import pytz

# --- إعدادات النظام ---
egypt_tz = pytz.timezone('Africa/Cairo')
today_date = datetime.now(egypt_tz).strftime("%Y-%m-%d")
INTERNAL_DB = f"w_egx_gold_fixed_{today_date}.log"

st.set_page_config(page_title="WAHBA EGX GOLD", layout="wide")

# --- محرك الحسابات ---
def run_wahba_engine():
    if os.path.exists(INTERNAL_DB): return pd.read_csv(INTERNAL_DB)
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=10).json()
        all_syms = [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except: return pd.DataFrame()
    
    results = []
    for s in all_syms[:15]:
        try:
            h = TA_Handler(symbol=s, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=7)
            analysis = h.get_analysis()
            ind = analysis.indicators
            sc = 8 if "STRONG_BUY" in analysis.summary["RECOMMENDATION"] else 5
            
            # الحسابات الفنية
            price = round(ind.get("close"), 2)
            p_point = round(ind.get("Pivot.M.Classic.Middle"), 2)
            r1 = round(ind.get("Pivot.M.Classic.R1"), 2)
            s1 = round(ind.get("Pivot.M.Classic.S1"), 2)
            target = round(p_point + (r1 - p_point) * 1.618, 2)
            
            results.append({
                "Symbol": s, "Price": price, "Score": sc,
                "S1": s1, "P": p_point, "R1": r1,
                "Target": target, "SL": round(s1 * 0.99, 2),
                "ROI": round(((target - price) / price) * 100, 1)
            })
        except: continue
    df = pd.DataFrame(results)
    if not df.empty: df.to_csv(INTERNAL_DB, index=False)
    return df

# --- الاستايل (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background-color: #000; }
    .gold-title { text-align: center; color: #d4af37; font-size: 35px; font-weight: 900; padding: 20px; border-bottom: 2px solid #d4af37; }
    
    .card-gold {
        background: #0a0a0a; border: 3px solid #d4af37; border-radius: 20px;
        padding: 25px; margin-bottom: 30px; text-align: right;
    }
    .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
    .sym-name { font-size: 40px; font-weight: 900; color: #d4af37; }
    .score-badge { background: #d4af37; color: #000; padding: 5px 15px; border-radius: 10px; font-weight: bold; font-size: 20px; }
    
    .target-container {
        background: linear-gradient(135deg, #fceabb, #f8b500);
        border-radius: 15px; padding: 20px; text-align: center; margin: 20px 0;
    }
    .t-val { font-size: 55px; font-weight: 900; color: #006400; line-height: 1; }
    .t-roi { font-size: 20px; color: #006400; font-weight: bold; }
    
    .tech-grid { width: 100%; border-collapse: collapse; margin-top: 15px; }
    .tech-grid td { text-align: center; padding: 10px; border: 1px solid #222; }
    .l-t { font-size: 14px; color: #888; }
    .v-t { font-size: 20px; color: #d4af37; font-weight: bold; }
    
    .sl-text { color: #ff4b4b; font-weight: bold; font-size: 22px; margin-top: 20px; text-align: left; border-top: 1px solid #222; padding-top: 10px; }
</style>
""", unsafe_allow_html=True)

# --- عرض المحتوى ---
st.markdown('<div class="gold-title">WAHBA EGX GOLD</div>', unsafe_allow_html=True)
st.write("") # مسافة

if st.button("تحديث المسح الشامل للسوق"):
    if os.path.exists(INTERNAL_DB): os.remove(INTERNAL_DB)
    with st.spinner("جاري تحليل الذهب..."):
        market_df = run_wahba_engine()
    
    if not market_df.empty:
        for _, row in market_df.iterrows():
            # استخدام f-string داخل st.markdown مع تفعيل unsafe_allow_html
            card_html = f"""
            <div class="card-gold">
                <div class="card-header">
                    <span class="sym-name">{row['Symbol']}</span>
                    <span class="score-badge">SCORE: {row['Score']}/10</span>
                </div>
                
                <div style="font-size:22px; color:#fff; margin-bottom:10px;">السعر الحالي: <b>{row['Price']}</b> ج.م</div>

                <div class="target-container">
                    <div style="color:#000; font-weight:bold; font-size:18px;">الهدف المستهدف (Fib 1.618)</div>
                    <div class="t-val">{row['Target']}</div>
                    <div class="t-roi">ربح متوقع: {row['ROI']}% +</div>
                </div>

                <table class="tech-grid">
                    <tr>
                        <td><div class="l-t">S1 (دعم)</div><div class="v-t">{row['S1']}</div></td>
                        <td><div class="l-t">P (ارتكاز)</div><div class="v-t">{row['P']}</div></td>
                        <td><div class="l-t">R1 (مقاومة)</div><div class="v-t">{row['R1']}</div></td>
                    </tr>
                </table>

                <div class="sl-text">⚠️ وقف الخسارة: {row['SL']}</div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.error("فشل في جلب البيانات.")
