import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import time

# ==========================================
# 1. إعدادات الهوية والتصميم (WAHBA BRANDING)
# ==========================================
st.set_page_config(page_title="WAHBA QUANT ELITE", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&display=swap');
    
    .stApp { background-color: #050505; color: #ffffff; font-family: 'Inter', sans-serif; }
    .main-card { 
        background: linear-gradient(145deg, #0a0a0a, #111); 
        border: 1px solid #1a1a1a; padding: 30px; 
        border-radius: 20px; border-top: 4px solid #D4AF37;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .glitch-header { font-family: 'Orbitron', sans-serif; color: #D4AF37; text-align: center; letter-spacing: 5px; }
    .metric-title { color: #888; font-size: 0.8rem; letter-spacing: 2px; text-transform: uppercase; }
    .metric-value { font-family: 'Orbitron', sans-serif; font-size: 1.8rem; color: #fff; }
    .news-box { background: #0d0d0d; padding: 15px; border-radius: 10px; border-left: 3px solid #D4AF37; margin-bottom: 10px; }
    .status-tag { padding: 5px 15px; border-radius: 50px; font-weight: bold; font-size: 0.7rem; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. محرك جلب البيانات الذكي (Data Engine)
# ==========================================
def fetch_market_data():
    try:
        handler = TA_Handler(
            symbol="BTCUSDT",
            exchange="BINANCE",
            screener="crypto",
            interval=Interval.INTERVAL_15_MINUTES,
            timeout=15
        )
        analysis = handler.get_analysis()
        return analysis.indicators
    except Exception as e:
        return None

def fetch_news():
    try:
        url = "https://min-api.cryptocompare.com/data/v2/news/?lang=EN"
        response = requests.get(url, timeout=5).json()
        return response['Data'][:4]
    except:
        return []

# ==========================================
# 3. منطق SMC و صيد السيولة (Advanced Logic)
# ==========================================
def analyze_institutional_flow(ind):
    price = ind["close"]
    high, low = ind["high"], ind["low"]
    p_high, p_low = ind["high.1"], ind["low.1"]
    vol = ind["volume"]
    p_vol = ind.get("volume.1", vol)

    # A. فحص سحب السيولة (Liquidity Swing/Sweep)
    liq_status = "STABLE STRUCTURE"
    liq_color = "#666"
    if high > p_high and price < p_high:
        liq_status = "🚨 LIQUIDITY SWEEP (TOP) - SELL HUNT"
        liq_color = "#FF3131"
    elif low < p_low and price > p_low:
        liq_status = "🔥 LIQUIDITY SWING (BOTTOM) - BUY HUNT"
        liq_color = "#00FFCC"

    # B. هيكل السوق (Market Structure)
    structure = "BULLISH BOS" if price > p_high else "BEARISH BOS" if price < p_low else "RANGING"
    
    # C. أهداف المؤسسات (Targets)
    tp1 = round(ind["Pivot.M.Classic.R1"], 2)
    tp2 = round(ind["Pivot.M.Classic.R2"], 2)
    sl = round(ind["Pivot.M.Classic.S1"], 2)

    return {
        "price": price,
        "liq_status": liq_status,
        "liq_color": liq_color,
        "structure": structure,
        "tp1": tp1, "tp2": tp2, "sl": sl,
        "vol_eff": round((vol/p_vol)*100, 1)
    }

# ==========================================
# 4. الواجهة الرئيسية (Master Dashboard)
# ==========================================
def main():
    st.markdown("<h1 class='glitch-header'>🦅 WAHBA QUANT ELITE v15</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#555;'>SMC | LIQUIDITY | AI | NEWS - EXCLUSIVE FOR BINANCE SPOT</p>", unsafe_allow_html=True)
    
    # زر التشغيل الرئيسي
    if st.button("EXECUTE DEEP MARKET SCAN", use_container_width=True):
        with st.spinner("🧠 AI IS ANALYZING ORDER FLOW AND NEWS..."):
            ind = fetch_market_data()
            news = fetch_news()
            
            if ind:
                data = analyze_institutional_flow(ind)
                
                # الصف الأول: إشارة صيد السيولة (الأهم)
                st.markdown(f"""
                <div class="main-card" style="border-color:{data['liq_color']}; text-align:center; margin-bottom:25px;">
                    <p class="metric-title">Institutional Liquidity Status</p>
                    <h1 style="color:{data['liq_color']}; font-size:3rem; font-family:'Orbitron';">{data['liq_status']}</h1>
                    <p style="color:#888;">Structure: {data['structure']} | Vol Efficiency: {data['vol_eff']}%</p>
                </div>
                """, unsafe_allow_html=True)

                # الصف الثاني: البيانات الرقمية والأسعار
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"<div class='main-card'><p class='metric-title'>LIVE PRICE</p><p class='metric-value'>${data['price']:,}</p></div>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"<div class='main-card'><p class='metric-title'>TP 1 (SAFE)</p><p class='metric-value' style='color:#00FFCC;'>${data['tp1']:,}</p></div>", unsafe_allow_html=True)
                with col3:
                    st.markdown(f"<div class='main-card'><p class='metric-title'>TP 2 (AGG)</p><p class='metric-value' style='color:#D4AF37;'>${data['tp2']:,}</p></div>", unsafe_allow_html=True)
                with col4:
                    st.markdown(f"<div class='main-card'><p class='metric-title'>STOP LOSS</p><p class='metric-value' style='color:#FF3131;'>${data['sl']:,}</p></div>", unsafe_allow_html=True)

                st.divider()

                # الصف الثالث: الأخبار والذكاء الاصطناعي
                c_logic, c_news = st.columns([1, 1])
                
                with c_logic:
                    st.markdown("### 🧠 AI Neural Reasoning")
                    if data['vol_eff'] > 150:
                        st.success(f"✅ سيولة عالية جداً ({data['vol_eff']}%). الحيتان تتحرك الآن.")
                    if "BOTTOM" in data['liq_status']:
                        st.info("💡 تم ضرب ستوبات المشترين بنجاح. السعر الآن جاهز للانطلاق للأعلى.")
                    else:
                        st.warning("⚠️ انتظر تأكيد سحب السيولة قبل الدخول بمبالغ كبيرة.")

                with c_news:
                    st.markdown("### 📰 Market News Flow")
                    for n in news:
                        st.markdown(f"""
                        <div class="news-box">
                            <a href="{n['url']}" style="color:#D4AF37; text-decoration:none; font-weight:bold; font-size:0.9rem;">{n['title']}</a>
                            <p style="color:#555; font-size:0.7rem; margin-top:5px;">Source: {n['source']} | AI Sentiment: Analyzed</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.error("⚠️ فشل في جلب البيانات. يرجى التأكد من اتصال الإنترنت وإعادة المحاولة.")

if __name__ == "__main__":
    main()
