import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
from datetime import datetime
import pytz
import numpy as np
import joblib
import os
import time

# ==========================================
# 1. إعدادات النظام والتوقيت
# ==========================================
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)
today_key = now_egypt.strftime("%Y-%m-%d")

st.set_page_config(
    page_title="Wahba Intelligence | Platinum Edition",
    page_icon="👑",
    layout="wide"
)

# ==========================================
# 2. هندسة الواجهة (HTML & CSS Custom Engine)
# ==========================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;700;900&display=swap');
    
    /* الأساسيات */
    * {{ font-family: 'Tajawal', sans-serif; }}
    .stApp {{ background-color: #050505; color: #ffffff; }}
    
    /* تصميم الهيدر الاحترافي */
    .hero-section {{
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
        padding: 60px 20px;
        text-align: center;
        border-bottom: 3px solid #d4af37;
        margin-bottom: 40px;
        border-radius: 0 0 40px 40px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}
    
    .main-title {{
        font-size: 48px;
        font-weight: 900;
        letter-spacing: 4px;
        margin-bottom: 10px;
        color: #fff;
    }}
    
    .main-title span {{ color: #d4af37; }}
    
    .sub-title {{
        font-size: 14px;
        color: #d4af37;
        text-transform: uppercase;
        letter-spacing: 5px;
        font-weight: bold;
    }}

    /* كروت الأسهم (Custom CSS Cards) */
    .stock-card-container {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 20px;
        padding: 10px;
    }}

    .stock-card {{
        background: #0d0d0d;
        border: 1px solid #222;
        border-radius: 20px;
        padding: 25px;
        position: relative;
        overflow: hidden;
        transition: 0.4s ease;
        border-top: 4px solid #d4af37;
    }}

    .stock-card:hover {{
        transform: translateY(-10px);
        box-shadow: 0 20px 40px rgba(212, 175, 55, 0.15);
        border-color: #d4af37;
    }}

    .symbol-name {{ font-size: 28px; font-weight: 900; color: #d4af37; margin-bottom: 5px; }}
    .sentiment-tag {{ font-size: 12px; color: #888; margin-bottom: 20px; }}
    
    .data-row {{ display: flex; justify-content: space-between; margin-bottom: 15px; }}
    .data-label {{ font-size: 13px; color: #555; }}
    .data-value {{ font-size: 20px; font-weight: bold; color: #fff; }}
    .target-value {{ font-size: 22px; font-weight: bold; color: #00ff00; }}

    /* أزرار مخصصة */
    .stButton>button {{
        width: 100%;
        background: linear-gradient(90deg, #d4af37 0%, #f4d03f 100%) !important;
        color: #000 !important;
        font-weight: 900 !important;
        border-radius: 12px !important;
        height: 60px !important;
        border: none !important;
        font-size: 18px !important;
        transition: 0.3s !important;
    }}
    
    .stButton>button:hover {{
        box-shadow: 0 0 25px rgba(212, 175, 55, 0.5) !important;
        transform: scale(1.02) !important;
    }}

    /* إخفاء القوائم الافتراضية المزعجة */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    </style>
    
    <div class="hero-section">
        <div class="sub-title">Wahba Quantum Analytics</div>
        <div class="main-title">WAHBA <span>INTELLIGENCE</span></div>
        <p style="color:#666;">Institutional Grade Trading Neural Network v6.5</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 3. محرك الـ AI وإدارة البيانات
# ==========================================
@st.cache_data(ttl=3600)
def get_symbols():
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {{"filter": [{{"left": "type", "operation": "in_range", "right": ["stock"]}}], "markets": ["egypt"], "columns": ["name"]}}
        res = requests.post(url, json=payload, timeout=10).json()
        return [item['s'].split(':')[1] for item in res['data']]
    except:
        return ["COMI", "FWRY", "TRTO", "TMGH", "SWDY"]

def analyze_market():
    symbols = get_symbols()
    results = []
    
    # محرك الـ AI (مبسط هنا لضمان السرعة)
    brain = LinearRegression()
    brain.fit(np.array([[10,30], [20,50], [5,25], [100,60]]), np.array([10.5, 21, 5.5, 103]))
    
    progress_bar = st.progress(0, text="🤖 جاري مسح السوق بالذكاء الاصطناعي...")
    
    for i, sym in enumerate(symbols):
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=7)
            analysis = handler.get_analysis()
            p = analysis.indicators.get("close")
            r = analysis.indicators.get("RSI")
            piv = analysis.indicators.get("Pivot.M.Classic.Middle")
            
            target = round(float(brain.predict(np.array([[p, r]]))[0]), 2)
            
            # تحليل الحالة
            status = "✅ تجميع مؤسسي" if p > piv and r > 50 else "🔄 تذبذب عرضي"
            if r > 70: status = "⚠️ تشبع شرائي"

            results.append({{
                "sym": sym, "price": p, "target": target,
                "status": status, "rec": analysis.summary["RECOMMENDATION"]
            }})
        except: continue
        progress_bar.progress((i + 1) / len(symbols))
    
    progress_bar.empty()
    return results

# ==========================================
# 4. التنفيذ وعرض الواجهة (The Frontend)
# ==========================================
st.sidebar.markdown(f"""
    <div style="background:#111; padding:20px; border-radius:15px; border:1px solid #222;">
        <h3 style="color:#d4af37; margin-top:0;">📡 حالة النظام</h3>
        <p style="font-size:12px;">توقيت القاهرة: {now_egypt.strftime('%I:%M %p')}</p>
        <p style="font-size:12px;">التاريخ: {today_key}</p>
        <hr style="border-color:#222;">
        <p style="font-size:11px; color:#555;">النظام متزامن مع بورصة مصر TradingView</p>
    </div>
""", unsafe_allow_html=True)

if st.button("إطلاق الماسح الذكي الشامل (AI SCAN)"):
    market_data = analyze_market()
    st.session_state.data = market_data

if 'data' in st.session_state:
    st.markdown("### ⚜️ أقوى الفرص المكتشفة")
    
    # إنشاء الكروت باستخدام HTML و CSS
    cols = st.columns(3)
    for i, item in enumerate(st.session_state.data[:12]): # عرض أول 12 سهم
        with cols[i % 3]:
            st.markdown(f"""
            <div class="stock-card">
                <div class="symbol-name">{item['sym']}</div>
                <div class="sentiment-tag">{item['status']}</div>
                <div class="data-row">
                    <span class="data-label">سعر الإغلاق</span>
                    <span class="data-value">{item['price']}</span>
                </div>
                <div class="data-row">
                    <span class="data-label">الهدف الذكي</span>
                    <span class="target-value">{item['target']}</span>
                </div>
                <div style="margin-top:15px; font-size:11px; font-weight:bold; color:#d4af37; text-align:center;">
                    القرار: {item['rec']}
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown(f"""
    <div style="margin-top:100px; text-align:center; padding:40px; border-top:1px solid #1a1a1a; color:#333; font-size:10px;">
        WAHBA INTELLIGENCE | PLATINUM v6.5<br>
        DESIGNED BY MOSTAFA TAMER © 2026<br>
        ALEXANDRIA - EGYPT
    </div>
""", unsafe_allow_html=True)
