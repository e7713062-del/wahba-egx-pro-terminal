import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import sqlite3
from datetime import datetime

# ==========================================
# 1. INSTITUTIONAL BRANDING (THE VIBE)
# ==========================================
CORP_NAME = "WAHBA QUANTITATIVE SOLUTIONS"
FOUNDER = "MUSTAFA TAMER"
VERSION = "VSA PRO ELITE v9.0"

# ==========================================
# 2. VSA CORE ENGINE (ADVANCED LOGIC)
# ==========================================
def perform_vsa_analysis():
    try:
        handler = TA_Handler(
            symbol="BTCUSDT",
            exchange="BINANCE",
            screener="crypto",
            interval=Interval.INTERVAL_4_HOURS
        )
        analysis = handler.get_analysis()
        ind = analysis.indicators

        # -- متغيرات VSA الأساسية --
        price = ind["close"]
        high = ind["high"]
        low = ind["low"]
        volume = ind["volume"]
        prev_volume = ind.get("volume.1", volume)
        spread = high - low
        
        # تحديد موقع الإغلاق (Closing Position)
        # إذا أغلق في الثلث العلوي = قوة، الثلث السفلي = ضعف
        close_pos = (price - low) / (spread if spread != 0 else 1)

        # -- كشف نماذج VSA --
        vsa_signal = "Searching for Market Anomalies..."
        vsa_color = "#888"

        # 1. Stopping Volume (إشارة شراء قوية)
        if volume > prev_volume * 1.5 and close_pos > 0.5 and spread > 0:
            vsa_signal = "💎 STOPPING VOLUME (Smart Money Buying)"
            vsa_color = "#00FFCC"
        
        # 2. Upthrust (فخ بيعي)
        elif close_pos < 0.3 and spread > (high-low)*0.7 and volume > prev_volume:
            vsa_signal = "⚠️ UPTHRUST (Potential Distribution/Trap)"
            vsa_color = "#FF3131"

        # 3. No Supply (اختبار العرض - إيجابي)
        elif volume < prev_volume and spread < (high-low) and close_pos > 0.4:
            vsa_signal = "⚖️ NO SUPPLY TEST (Bullish Confirmation)"
            vsa_color = "#D4AF37"

        # -- Squeeze Momentum Logic --
        bb_upper = ind["BB.upper"]
        kc_upper = ind["EMA20"] + (1.5 * ind.get("ATR", 100))
        is_squeeze = bb_upper < kc_upper
        
        return {
            "price": price,
            "vsa_signal": vsa_signal,
            "vsa_color": vsa_color,
            "squeeze": "LOCKED (Ready to Explode)" if is_squeeze else "RELEASED",
            "squeeze_color": "#FF3131" if is_squeeze else "#00FFCC",
            "volume_status": "High Effort" if volume > prev_volume else "Low Interest"
        }
    except Exception as e:
        st.error(f"Engine Failure: {e}")
        return None

# ==========================================
# 3. HIGH-END UI DESIGN
# ==========================================
st.set_page_config(page_title=CORP_NAME, layout="wide")

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .stApp {{ background: #000000; color: #ffffff; font-family: 'Inter', sans-serif; }}
    
    .header-box {{
        border-bottom: 2px solid #D4AF37; padding: 20px; text-align: center;
        background: linear-gradient(to right, #000, #111, #000); margin-bottom: 30px;
    }}
    
    .vsa-card {{
        background: #080808; border: 1px solid #1a1a1a; padding: 30px;
        border-radius: 4px; position: relative; overflow: hidden;
    }}
    
    .vsa-card::before {{
        content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 2px;
        background: #D4AF37;
    }}

    .status-text {{ font-family: 'Orbitron', sans-serif; font-size: 1.8rem; letter-spacing: 2px; }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. EXECUTION
# ==========================================
def main():
    # Branding
    st.markdown(f"""
    <div class="header-box">
        <h1 style="color:#D4AF37; font-family:'Orbitron'; font-size:2.5rem; margin:0;">{CORP_NAME}</h1>
        <p style="color:#555; letter-spacing:5px;">VSA INTELLIGENCE • QUANTUM ANALYSIS • {VERSION}</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar Tools
    with st.sidebar:
        st.markdown("<h3 style='color:#D4AF37;'>OPERATOR PANEL</h3>", unsafe_allow_html=True)
        st.info(f"CHIEF: {FOUNDER}")
        scan_btn = st.button("RUN VSA DEEP SCAN", use_container_width=True)
        st.divider()
        st.caption("This tool uses Real-time Volume Spread Analysis to track Smart Money movements.")

    if scan_btn:
        with st.spinner("DECRYPTING MARKET VOLUME..."):
            data = perform_vsa_analysis()
            if data:
                # عرض النتائج
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <div class="vsa-card">
                        <p style="color:#666; font-size:0.8rem;">PRICE ACTION STATUS</p>
                        <h2 style="color:white;">BTC/USDT SPOT</h2>
                        <h1 class="status-text">${data['price']:,}</h1>
                        <p style="color:#444;">VOLUME: {data['volume_status']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div class="vsa-card">
                        <p style="color:#666; font-size:0.8rem;">SQUEEZE MOMENTUM</p>
                        <h2 style="color:{data['squeeze_color']};">{data['squeeze']}</h2>
                        <hr style="opacity:0.1">
                        <p style="color:#666; font-size:0.8rem;">VSA SIGNAL</p>
                        <h3 style="color:{data['vsa_color']};">{data['vsa_signal']}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.success("INTELLIGENCE ARCHIVED")
    else:
        st.markdown("<div style='text-align:center; padding:100px; color:#222;'><h1>SYSTEM READY</h1><p>Waiting for scan command...</p></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
