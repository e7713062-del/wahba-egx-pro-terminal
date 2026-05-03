import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import time
from datetime import datetime
import pytz

# --- 1. إعدادات الوقت (إسكندرية) ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_alex = datetime.now(egypt_tz)
today_key = now_alex.strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba Intelligence | SMC Edition", layout="wide")

# --- 2. التصميم الاحترافي الفاخر ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    .main-header { 
        text-align: center; padding: 30px; border-bottom: 3px solid #00ff00; 
        background: linear-gradient(180deg, #111 0%, #050505 100%);
        margin-bottom: 30px; border-radius: 0 0 25px 25px;
    }
    .dev-name { color: #00ff00; font-family: 'Courier New', monospace; letter-spacing: 3px; font-size: 14px; font-weight: bold; }
    .gold-box { 
        background: linear-gradient(90deg, rgba(255,215,0,0.1) 0%, rgba(0,255,0,0.05) 100%);
        border: 2px solid #ffd700; padding: 25px; border-radius: 15px; margin-bottom: 25px;
        text-align: center; box-shadow: 0 0 20px rgba(255, 215, 0, 0.2);
    }
    .smc-tag {
        background-color: #1a1a1a; border: 1px solid #00ff00; color: #00ff00;
        padding: 2px 8px; border-radius: 5px; font-size: 10px; margin-right: 5px;
    }
    </style>
    <div class="main-header">
        <div class="dev-name">ENGINEERED BY MOSTAFA WAHBA</div>
        <h1 style="margin:10px 0; color:#ffffff; font-size: 40px;">WAHBA <span style="color:#00ff00;">SMC</span> INTELLIGENCE</h1>
        <div style="color: #888; font-size: 15px;">Smart Money Market Scanner v4.5</div>
    </div>
""", unsafe_allow_html=True)

# --- 3. الدوال الذكية (الذاكرة المشتركة و SMC) ---

@st.cache_data(ttl=3600)
def get_index_data(symbol, date_key):
    try:
        handler = TA_Handler(symbol=symbol, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=5)
        analysis = handler.get_analysis()
        return {"price": analysis.indicators["close"], "change": analysis.indicators["change"]}
    except: return None

@st.cache_data(ttl=86400)
def get_live_tickers():
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {"filter": [], "options": {"lang": "en"}, "markets": ["egypt"], "symbols": {"query": {"types": []}, "tickers": []}, "columns": ["name"]}
        res = requests.post(url, json=payload, timeout=15).json()
        return sorted(list(set([item['s'].split(':')[1] for item in res['data']])))
    except: return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK"]

@st.cache_data(ttl=14400) # ذاكرة 4 ساعات للتوافق مع إغلاقات السوق
def run_intelligent_scan(date_key):
    symbols = get_live_tickers()
    results = []
    idx30 = get_index_data("EGX30", date_key)
    
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, symbol in enumerate(symbols):
        try:
            status_text.text(f"🔍 تحليل هيكل السوق (SMC): {symbol}")
            handler = TA_Handler(symbol=symbol, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=7)
            analysis = handler.get_analysis()
            indicators = analysis.indicators
            rec = analysis.summary["RECOMMENDATION"]
            
            # --- منطق SMC (Smart Money Concepts) ---
            # 1. Bullish FVG (الفجوة السعرية الصاعدة)
            # الشروط: أدنى سعر لليوم الحالي > أعلى سعر لليوم قبل السابق
            has_fvg = indicators["low"] > indicators["high2"]
            
            # 2. Break of Structure (BOS)
            # الشروط: الإغلاق الحالي أعلى من أعلى سعر في الشمعة السابقة
            is_bos = indicators["close"] > indicators["high1"]
            
            if "BUY" in rec:
                rsi = indicators["RSI"]
                adx = indicators["ADX"]
                
                # حساب التقييم الرقمي المطور
                score = 1
                smc_signals = []
                
                if "STRONG" in rec: score += 1
                if 40 < rsi < 60: score += 1
                if adx > 25: score += 1
                
                # إضافة نقاط الـ SMC
                if has_fvg: 
                    score += 2 # الفجوة تدل على دخول سيولة مؤسسية
                    smc_signals.append("FVG")
                if is_bos: 
                    score += 1 # كسر الهيكل يؤكد الاتجاه
                    smc_signals.append("BOS")
                
                if idx30 and idx30['change'] > 0: score += 1
                
                results.append({
                    "السهم": symbol, 
                    "السعر": round(indicators["close"], 2),
                    "RSI": round(rsi, 2), 
                    "SMC": " + ".join(smc_signals) if smc_signals else "Structure",
                    "التقييم": score,
                    "النجوم": "⭐" * min(int(score), 5)
                })
            progress_bar.progress((i + 1) / len(symbols))
            time.sleep(0.05)
        except: continue
        
    status_text.empty()
    progress_bar.empty()
    return results

# --- 4. العرض الفعلي للنتائج ---

# المؤشرات العامة
c1, c2 = st.columns(2)
for c, s, n in zip([c1, c2], ["EGX30", "EGX70EWI"], ["EGX 30", "EGX 70"]):
    data = get_index_data(s, today_key)
    if data:
        clr = "#00ff00" if data['change'] >= 0 else "#ff4b4b"
        c.markdown(f"""<div class="index-card">
            <div style="font-size:14px; color:#888;">{n}</div>
            <div style="color:{clr}; font-size:28px; font-weight:bold;">{data['price']:,.2f}</div>
        </div>""", unsafe_allow_html=True)

st.write("")

if st.button('🚀 تشغيل رادار "وهبة" للسيولة الذكية (SMC Scan)', use_container_width=True):
    report_data = run_intelligent_scan(today_key)
    st.session_state.final_results = pd.DataFrame(report_data)

if 'final_results' in st.session_state and st.session_state.final_results is not None:
    df = st.session_state.final_results
    
    # --- قسم نخبة النخبة (Golden Picks) ---
    st.markdown("<br>", unsafe_allow_html=True)
    golden_picks = df.sort_values(by="التقييم", ascending=False).head(2)
    
    if not golden_picks.empty:
        st.markdown(f"""
            <div class="gold-box">
                <h2 style="color:#ffd700; margin:0;">💎 صيد الحيتان (SMC Golden Picks)</h2>
                <p style="color:#888;">أقوى الفرص بناءً على الفجوات السعرية وكسر الهيكل</p>
            </div>
        """, unsafe_allow_html=True)
        
        gc1, gc2 = st.columns(2)
        for col, (_, row) in zip([gc1, gc2], golden_picks.iterrows()):
            col.markdown(f"""
                <div style="background:#1a1a1a; padding:20px; border-radius:15px; border-left:5px solid #ffd700; text-align:center;">
                    <h1 style="color:#00ff00; margin:0;">{row['السهم']}</h1>
                    <div style="font-size:24px; color:#fff;">{row['السعر']} EGP</div>
                    <div style="color:#ffd700; font-size:18px; margin: 10px 0;">{row['النجوم']}</div>
                    <div style="color:#00ff00; font-weight:bold;">Signal: {row['SMC']}</div>
                </div>
            """, unsafe_allow_html=True)

    st.divider()
    
    # الجدول الكامل مع الـ SMC
    st.markdown("### 📊 القائمة الكاملة للفرص (SMC & Technicals)")
    st.dataframe(
        df[['السهم', 'السعر', 'SMC', 'RSI', 'النجوم']].sort_values(by="التقييم", ascending=False), 
        use_container_width=True, 
        hide_index=True
    )

st.markdown(f"<div style='text-align:center; color:#444; font-size:10px; padding:30px;'>Wahba Intelligence Protocol v4.5 | Developed by Mostafa Tamer Wahba</div>", unsafe_allow_html=True)
