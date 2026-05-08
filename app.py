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

LEGAL_EN = f"© {datetime.now().year} {OWNER}. PRESTIGE EDITION. PROPRIETARY QUANTUM ALGORITHMS PROTECTED BY INTERNATIONAL LAW."
LEGAL_AR = f"حقوق الملكية © {datetime.now().year} للمالك {OWNER}. النسخة الفاخرة. الخوارزميات محمية بموجب قوانين الملكية الفكرية الدولية."

# ==========================================
# 2. DATA ARCHITECTURE (Institutional Grade)
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
        for sym in symbols[:30]: # Focus on high-quality assets
            try:
                h = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", 
                               interval=Interval.INTERVAL_1_DAY, timeout=5)
                ind = h.get_analysis().indicators
                results.append({
                    "Symbol": sym, "Price": ind["close"], "Score": h.get_analysis().summary["BUY"],
                    "P": ind["Pivot.M.Classic.Middle"], "R1": ind["Pivot.M.Classic.R1"], "S1": ind["Pivot.M.Classic.S1"]
                })
            except: continue
        return pd.DataFrame(results)
    except: return pd.DataFrame()

# ==========================================
# 3. LUXURY UI DESIGN (CSS)
# ==========================================
st.set_page_config(page_title=f"{SYSTEM_NAME} LUXURY | {OWNER}", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;700&family=Cinzel:wght@400;700&family=Montserrat:wght@200;400;800&display=swap');
    
    /* Luxury Dark Background */
    .stApp {
        background: radial-gradient(circle at top, #1a1a1a 0%, #050505 100%);
        color: #e0e0e0;
    }

    /* Fonts */
    h1, h2, .luxury-text { font-family: 'Cinzel', serif; letter-spacing: 3px; }
    body, div, p { font-family: 'Montserrat', 'Cairo', sans-serif; }

    /* Header Styling */
    .main-header {
        text-align: center;
        padding: 80px 20px;
        border-bottom: 1px solid rgba(212, 175, 55, 0.2);
        margin-bottom: 60px;
    }

    .gold-accent {
        color: #D4AF37;
        text-shadow: 0 0 15px rgba(212, 175, 55, 0.4);
    }

    /* Luxury Card (Glassmorphism) */
    .luxury-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(212, 175, 55, 0.15);
        padding: 40px;
        border-radius: 0px; /* Sharp edges for institutional look */
        margin-bottom: 30px;
        transition: 0.5s all ease;
        backdrop-filter: blur(10px);
    }

    .luxury-card:hover {
        background: rgba(212, 175, 55, 0.05);
        border-color: #D4AF37;
        transform: scale(1.02);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    .target-box {
        border-top: 1px solid #D4AF37;
        border-bottom: 1px solid #D4AF37;
        padding: 20px 0;
        margin: 25px 0;
        text-align: center;
    }

    /* Custom Button */
    .stButton>button {
        background: transparent;
        border: 1px solid #D4AF37;
        color: #D4AF37;
        font-family: 'Cinzel';
        padding: 15px 50px;
        letter-spacing: 2px;
        transition: 0.4s;
    }

    .stButton>button:hover {
        background: #D4AF37;
        color: #000;
    }

    .footer {
        padding: 60px;
        text-align: center;
        border-top: 1px solid #222;
        font-size: 10px;
        letter-spacing: 2px;
        color: #555;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. EXECUTION TERMINAL
# ==========================================
def main():
    # Luxury Entrance (Gatekeeper)
    if 'authorized' not in st.session_state:
        st.markdown(f"""
        <div style="text-align:center; margin-top:100px;">
            <h1 class="gold-accent" style="font-size:4rem;">{SYSTEM_NAME}</h1>
            <p style="letter-spacing:10px; font-weight:200;">PRESTIGE TERMINAL</p>
            <div style="max-width:700px; margin:40px auto; padding:30px; border:1px solid #222; font-size:12px; color:#666;">
                <p>{LEGAL_EN}</p>
                <hr style="border-color:#222">
                <p style="direction:rtl;">{LEGAL_AR}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns([1, 1, 1])
        with cols[1]:
            if st.button("ENTER TERMINAL", use_container_width=True):
                st.session_state.authorized = True
                st.rerun()
        return

    # Main Interface
    st.markdown(f"""
    <div class="main-header">
        <p style="letter-spacing:8px; font-size:12px; color:#D4AF37;">STATION: {STATION_ID}</p>
        <h1 style="font-size:4.5rem; margin:10px 0;">{SYSTEM_NAME} <span class="gold-accent">LUXURY</span></h1>
        <p style="color:#555; font-weight:200;">CURATED INTELLIGENCE FOR <b>{OWNER}</b></p>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("CALIBRATING ASSET VECTORS..."):
        df = get_market_intelligence()

    if not df.empty:
        # Proprietary Luxury Algo
        df['T'] = np.round(df['P'] + (df['R1'] - df['P']) * 1.618, 2)
        df['ROI'] = np.round(((df['T'] - df['Price']) / df['Price']) * 100, 1)
        
        # Display Top Executive Picks
        signals = df[df['Score'] >= 5].sort_values(by='ROI', ascending=False).head(9)
        
        cols = st.columns(3)
        for i, (_, row) in enumerate(signals.iterrows()):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="luxury-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-family:'Cinzel'; font-size:1.8rem; font-weight:bold;">{row['Symbol']}</span>
                        <span style="color:#D4AF37; font-size:9px; border:1px solid #D4AF37; padding:2px 8px;">VIP ACCESS</span>
                    </div>
                    <p style="color:#444; font-size:10px; margin-top:5px; letter-spacing:2px;">CERTIFIED BY {OWNER}</p>
                    
                    <div class="target-box">
                        <small style="color:#555; font-size:10px; letter-spacing:3px;">PROPRIETARY TARGET</small>
                        <div style="font-size:36px; font-weight:bold; color:#D4AF37;">{row['T']}</div>
                        <div style="color:#00ffaa; font-size:14px; letter-spacing:1px;">Est. Growth: {row['ROI']}%</div>
                    </div>
                    
                    <div style="display:flex; justify-content:space-between; color:#333; font-size:12px;">
                        <span>ENTRY PRICE: {row['Price']}</span>
                        <span>STATUS: ACTIVE</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.error("Access Denied. Terminal cannot reach the market server.")

    # Luxury Footer
    st.markdown(f"""
    <div class="footer">
        <p>{LEGAL_EN}</p>
        <p style="direction:rtl; margin-top:10px;">{LEGAL_AR}</p>
        <h3 style="margin-top:30px; font-size:14px; color:#D4AF37;">DESIGNED BY {OWNER}</h3>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
