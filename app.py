import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import time
from datetime import datetime
import pytz

# --- 1. إعدادات الوقت ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_alex = datetime.now(egypt_tz)
today_key = now_alex.strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba Intelligence | Advanced Pro", layout="wide")

# --- 2. التصميم (Black & Gold Elite) ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    .main-header { 
        text-align: center; padding: 20px; border-bottom: 2px solid #ffd700; 
        background: #000; margin-bottom: 30px;
    }
    .gold-box { 
        background: rgba(255, 215, 0, 0.05); border: 1px solid #ffd700; 
        padding: 20px; border-radius: 15px; margin-bottom: 20px;
    }
    .support-text { color: #00ff00; font-weight: bold; font-size: 14px; }
    .resistance-text { color: #ff4b4b; font-weight: bold; font-size: 14px; }
    </style>
    <div class="main-header">
        <h1 style="color:#ffd700; font-size: 35px;">WAHBA <span style="color:#fff;">INTELLIGENCE</span> PRO</h1>
        <p style="color:#888;">Advanced Support/Resistance Detection Terminal</p>
    </div>
""", unsafe_allow_html=True)

# --- 3. الدوال الذكية ---

@st.cache_data(ttl=14400)
def run_advanced_scan(date_key):
    # محاكاة لجلب الرموز (يمكن استبدالها بدالة get_live_tickers السابقة)
    symbols = ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK", "MFOT", "ETEL"] 
    results = []
    
    progress_bar = st.progress(0)
    for i, symbol in enumerate(symbols):
        try:
            handler = TA_Handler(symbol=symbol, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=7)
            analysis = handler.get_analysis()
            
            # جلب البيانات اللازمة لحساب الدعم والمقاومة
            close = analysis.indicators["close"]
            high = analysis.indicators["high"]
            low = analysis.indicators["low"]
            
            # حساب Pivot Points (المستويات الفنية)
            pivot = (high + low + close) / 3
            r1 = (2 * pivot) - low
            s1 = (2 * pivot) - high
            
            rec = analysis.summary["RECOMMENDATION"]
            rsi = analysis.indicators["RSI"]
            
            # معيار "نخبة النخبة"
            score = 0
            if "BUY" in rec: score += 1
            if "STRONG" in rec: score += 2
            if 40 < rsi < 60: score += 2
            
            results.append({
                "السهم": symbol,
                "السعر الحالي": round(close, 2),
                "الدعم (S1)": round(s1, 2),
                "المقاومة (R1)": round(r1, 2),
                "RSI": round(rsi, 2),
                "التوصية": rec,
                "score": score
            })
            progress_bar.progress((i + 1) / len(symbols))
        except: continue
    progress_bar.empty()
    return pd.DataFrame(results)

# --- 4. العرض ---

if st.button('🎯 تحليل السوق وتحديد مستويات الدخول والخروج', use_container_width=True):
    df = run_advanced_scan(today_key)
    
    # قسم "نخبة النخبة" مع مستويات الدعم والمقاومة
    golden = df.sort_values(by="score", ascending=False).head(2)
    
    st.markdown("<div class='gold-box'><h2>💎 رادار نخبة النخبة (أهداف الغد)</h2></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    for col, (_, row) in zip([col1, col2], golden.iterrows()):
        with col:
            st.markdown(f"""
                <div style="background:#111; padding:20px; border-radius:10px; border:1px solid #333;">
                    <h2 style="color:#00ff00; margin:0;">{row['السهم']}</h2>
                    <h3 style="color:#fff;">السعر: {row['السعر الحالي']}</h3>
                    <hr style="border-color:#222;">
                    <p class="support-text">🟢 منطقة الشراء (دعم): {row['الدعم (S1)']}</p>
                    <p class="resistance-text">🔴 منطقة البيع (مقاومة): {row['المقاومة (R1)']}</p>
                    <p style="font-size:12px; color:#666;">RSI: {row['RSI']} | التقييم: {row['score']} نقاط</p>
                </div>
            """, unsafe_allow_html=True)

    st.divider()
    st.markdown("### 📊 جدول البيانات الفنية لجميع الفرص")
    st.dataframe(df[['السهم', 'السعر الحالي', 'الدعم (S1)', 'المقاومة (R1)', 'RSI', 'التوصية']], use_container_width=True, hide_index=True)

st.markdown(f"<div style='text-align:center; color:#444; font-size:10px; padding:20px;'>Wahba Intelligence v4.5 | Developed by Mostafa Wahba</div>", unsafe_allow_html=True)
