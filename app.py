import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import numpy as np
import requests
import os
from datetime import datetime
import pytz

# ==========================================
# 1. LEGAL & LUXURY CONFIG (Mustafa Tamer)
# ==========================================
OWNER = "MUSTAFA TAMER"
SYSTEM_NAME = "WAHBA EGX"
STATION_ID = "EXECUTIVE TERMINAL V3.0"

LEGAL_EN = f"© {datetime.now().year} {OWNER}. ALL RIGHTS RESERVED. PROPRIETARY ALGORITHMS."
LEGAL_AR = f"جميع الحقوق محفوظة © {datetime.now().year} للمالك {OWNER}. خوارزميات خاصة."

RISK_NOTICE_EN = "TRADING INVOLVES SIGNIFICANT RISK. PAST PERFORMANCE IS NOT INDICATIVE OF FUTURE RESULTS."
RISK_NOTICE_AR = "التداول ينطوي على مخاطر جوهرية. الأداء السابق ليس مؤشراً على النتائج المستقبلية."

# ==========================================
# 2. DATA ENGINE
# ==========================================
@st.cache_data(ttl=600)
def get_market_intelligence():
    try:
        scanner_url = "https://scanner.tradingview.com/egypt/scan"
        payload = {"filter": [{"left": "market_cap_basic", "operation": "nempty"}],
                   "markets": ["egypt"], "columns": ["name"]}
        res = requests.post(scanner_url, json=payload, timeout=10).json()
        symbols = [i['s'].split(':')[1] for i in res['data'] if ":" in i['s']]
        
        results = []
        for sym in symbols[:30]:
            try:
                h = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", 
                               interval=Interval.INTERVAL_1_DAY, timeout=5)
                ind = h.get_analysis().indicators
                results.append({
                    "Symbol": sym, "Price": ind["close"], "Score": h.get_analysis().summary["BUY"],
                    "P": ind["Pivot.M.Classic.Middle"], "R1": ind["Pivot.M.Classic.R1"]
                })
            except: continue
        return pd.DataFrame(results)
    except: return pd.DataFrame()

# ==========================================
# 3. LUXURY UI DESIGN
# ==========================================
st.set_page_config(page_title=f"{SYSTEM_NAME} | {OWNER}", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;700&family=Cinzel:wght@400;700&family=Montserrat:wght@200;400;800&display=swap');
    
    .stApp { background: #050505; color: #e0e0e0; }
    h1, h2, .luxury-text { font-family: 'Cinzel', serif; letter-spacing: 3px; }
    body, div, p { font-family: 'Montserrat', 'Cairo', sans-serif; }

    .main-header {
        text-align: center;
        padding: 50px 20px;
        border-bottom: 1px solid rgba(212, 175, 55, 0.2);
    }

    .gold { color: #D4AF37; }

    /* Risk Section Styling */
    .risk-banner {
        background: rgba(255, 0, 0, 0.03);
        border: 1px solid rgba(255, 75, 75, 0.2);
        padding: 20px;
        margin: 20px auto;
        text-align: center;
        max-width: 900px;
        border-radius: 2px;
    }

    .luxury-card {
        background: #0a0a0a;
        border: 1px solid #1a1a1a;
        padding: 30px;
        margin-bottom: 25px;
        transition: 0.4s;
    }

    .luxury-card:hover {
        border-color: #D4AF37;
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.05);
    }

    .footer {
        padding: 40px;
        text-align: center;
        font-size: 10px;
        color: #333;
        border-top: 1px solid #111;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. EXECUTION FLOW
# ==========================================
def main():
    # 1. Gatekeeper & Risk Acknowledgment
    if 'authorized' not in st.session_state:
        st.markdown(f"""
        <div style="text-align:center; padding:80px 20px;">
            <h1 class="gold" style="font-size:3.5rem;">{SYSTEM_NAME}</h1>
            <p style="letter-spacing:10px; font-weight:200; color:#555;">PRESTIGE ACCESS</p>
            <div class="risk-banner">
                <p style="color:#ff4b4b; font-weight:bold; letter-spacing:2px; font-size:14px;">HIGH-RISK INVESTMENT WARNING</p>
                <p style="font-size:12px; color:#888;">{RISK_NOTICE_EN}</p>
                <p style="direction:rtl; font-size:13px; color:#888;">{RISK_NOTICE_AR}</p>
            </div>
            <div style="max-width:700px; margin:20px auto; color:#444; font-size:11px;">
                {LEGAL_EN} <br> {LEGAL_AR}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("CONFIRM & INITIALIZE", use_container_width=True):
            st.session_state.authorized = True
            st.rerun()
        return

    # 2. Main Terminal Header
    st.markdown(f"""
    <div class="main-header">
        <p style="letter-spacing:5px; font-size:10px; color:#D4AF37;">SYSTEM OWNER: {OWNER}</p>
        <h1 style="font-size:3rem; margin:10px 0;">{SYSTEM_NAME} <span class="gold">QUANT</span></h1>
    </div>
    """, unsafe_allow_html=True)

    # Risk Warning Inside Terminal (Luxury Small Banner)
    st.markdown(f"""
    <div style="text-align:center; padding:10px; font-size:10px; color:#611; letter-spacing:2px; border-bottom:1px solid #111;">
        CAPITAL AT RISK • PERFORMANCE NOT GUARANTEED • {OWNER} EXECUTIVE TERMINAL
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("ANALYZING ASSET VECTORS..."):
        df = get_market_intelligence()

    if not df.empty:
        df['T'] = np.round(df['P'] + (df['R1'] - df['P']) * 1.618, 2)
        df['ROI'] = np.round(((df['T'] - df['Price']) / df['Price']) * 100, 1)
        
        signals = df[df['Score'] >= 5].sort_values(by='ROI', ascending=False).head(9)
        
        cols = st.columns(3)
        for i, (_, row) in enumerate(signals.iterrows()):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="luxury-card">
                    <div style="display:flex; justify-content:space-between;">
                        <span style="font-family:'Cinzel'; font-size:1.5rem; font-weight:bold;">{row['Symbol']}</span>
                        <span style="color:#D4AF37; font-size:9px;">EXCLUSIVE</span>
                    </div>
                    <div style="background:#000; padding:20px; border:1px solid #1a1a1a; margin:20px 0;">
                        <div style="color:#D4AF37; font-size:9px; letter-spacing:2px;">ALGO TARGET</div>
                        <div style="font-size:30px; font-weight:bold; color:#00ffaa;">{row['T']}</div>
                        <div style="color:#00ffaa; font-size:12px;">+{row['ROI']}% POTENTIAL</div>
                    </div>
                    <div style="font-size:11px; color:#333; text-align:center;">
                        USE PROPER RISK MANAGEMENT • {OWNER} QUANT
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # 3. Footer
    st.markdown(f"""
    <div class="footer">
        <p>{LEGAL_EN} | {RISK_NOTICE_EN}</p>
        <p style="direction:rtl;">{LEGAL_AR} | {RISK_NOTICE_AR}</p>
        <p style="margin-top:20px; color:#D4AF37; font-family:'Cinzel';">MUSTAFA TAMER LUXURY EDITION</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
