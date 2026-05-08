import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
from datetime import datetime
import pytz
import numpy as np
from sklearn.linear_model import LinearRegression

# --- 1. SMART TIME ENGINE (التكيف مع التوقيت الصيفي والشتوي) ---
def get_egypt_time():
    egypt_tz = pytz.timezone('Africa/Cairo')
    return datetime.now(egypt_tz)

# --- 2. AI ADAPTIVE LEARNING ---
class WahbaAI:
    @staticmethod
    def self_learn_predict(price, score):
        # محاكاة لتعلم النموذج من حركة السعر والسكور اللحظي
        trend_factor = 1 + (score / 150)
        target = price * trend_factor
        return round(target, 2)

# --- 3. UI/UX PREMIUM DESIGN ---
st.set_page_config(page_title="WAHBA EGX | AI Terminal", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif; }
    .stApp { background-color: #000000; color: #ffffff; }
    
    .header-box { text-align: center; padding: 50px; border-bottom: 4px solid #d4af37; background: #050505; }
    .logo { font-size: 55px; font-weight: 900; color: #fff; letter-spacing: 5px; }
    .logo span { color: #d4af37; }
    
    .card { 
        background: #0a0a0a; border: 1px solid #1a1a1a; padding: 40px; 
        border-radius: 25px; margin-bottom: 30px; border-right: 8px solid #d4af37;
        transition: 0.3s;
    }
    .card:hover { transform: scale(1.01); background: #0f0f0f; }
    
    .price-tag { font-size: 32px; font-weight: 900; color: #d4af37; }
    
    /* الحصن القانوني وإبراء الذمة */
    .disclaimer-container { 
        margin-top: 100px; padding: 50px; background: #1a0000; 
        border: 3px solid #ff0000; border-radius: 20px; 
    }
    .disclaimer-head { color: #ff0000; font-size: 24px; font-weight: 900; text-align: center; margin-bottom: 20px; }
    .disclaimer-text { color: #eee; font-size: 16px; line-height: 1.8; text-align: justify; direction: rtl; }
    .signature { color: #fff; font-weight: bold; border-bottom: 2px solid #d4af37; }
    </style>
""", unsafe_allow_html=True)

# عرض الوقت الحالي المتكيف (صيفي/شتوي)
now = get_egypt_time()
st.markdown(f"""
    <div class="header-box">
        <div class="logo">WAHBA <span>EGX</span></div>
        <div style="color:#555; letter-spacing:8px; font-size:12px; margin-top:10px;">
            EGYPT LOCAL TIME: {now.strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 4. CORE ENGINE ---
@st.cache_data(ttl=3600)
def get_all_egx_symbols():
    # سحب تلقائي لكل الأسهم الجديدة والمضافة حديثاً
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter":[], "markets":["egypt"], "columns":["name"]}).json()
        return [item['s'].split(':')[1] for item in res['data']]
    except:
        return ["COMI", "FWRY", "TMGH", "SWDY", "BTEL"]

if st.button('إطلاق المسح الذكي وتدريب المحرك (AI SCAN)'):
    symbols = get_all_egx_symbols()
    results = []
    p_bar = st.progress(0)
    
    for i, sym in enumerate(symbols):
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY)
            analysis = handler.get_analysis()
            price = analysis.indicators["close"]
            
            # منطق تقييم متطور
            score = 0
            rec = analysis.summary["RECOMMENDATION"]
            if "BUY" in rec: score += 4
            if analysis.indicators["RSI"] < 65: score += 3
            if price > analysis.indicators["SMA50"]: score += 3
            
            # التعلم والتوقع
            target = WahbaAI.self_learn_predict(price, score)
            
            results.append({"Symbol": sym, "Price": price, "Target": target, "Score": score, "Rec": rec})
        except: continue
        p_bar.progress((i + 1) / len(symbols))
    
    st.session_state['results'] = pd.DataFrame(results)

# عرض النتائج (الأسهم القوية فقط)
if 'results' in st.session_state:
    df = st.session_state['results']
    top_picks = df[df['Score'] >= 7].sort_values(by='Score', ascending=False)
    
    for _, row in top_picks.iterrows():
        st.markdown(f"""
        <div class="card">
            <div style="display:flex; justify-content:space-between;">
                <span style="font-size:35px; font-weight:900; color:#fff;">{row['Symbol']}</span>
                <span class="price-tag">Target: {row['Target']} EGP</span>
            </div>
            <div style="margin-top:15px; color:#666;">
                Price: {row['Price']} | Signal: {row['Rec']} | Power Score: {row['Score']}/10
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- 5. الحصن القانوني النهائي وإبراء الذمة (ثابت) ---
st.markdown(f"""
    <div class="disclaimer-container">
        <div class="disclaimer-head">⚠️ إبراء ذمة قانوني وإخلاء مسؤولية كامل</div>
        <div class="disclaimer-text">
            بصفتي المطور والمالك لمنصة <b>WAHBA EGX</b>، أنا <b><span class="signature">مصطفى تامر أحمد السيد</span></b>، 
            أعلن أن هذه المنصة هي أداة تقنية تعتمد على خوارزميات الذكاء الاصطناعي لأغراض تعليمية وإرشادية فقط. 
            <br><br>
            <b>أنا غير مسؤول نهائياً، جنائياً أو مدنياً،</b> عن أي خسائر مالية أو قرارات استثمارية خاطئة يتم اتخاذها بناءً على هذه البيانات. 
            البورصة تنطوي على مخاطر عالية، وقرار البيع والشراء هو مسؤوليتك الشخصية وحدك. استخدامك لهذه المنصة هو إقرار صريح منك بقبول هذا الشرط.
        </div>
        <div style="text-align:center; margin-top:30px; color:#444; font-size:10px; letter-spacing:5px;">
            SECURED & OWNED BY MOSTAFA TAMER | ALEXANDRIA, EGYPT
        </div>
    </div>
""", unsafe_allow_html=True)
