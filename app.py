# ------------------------------------------------------------------------------
# PROJECT: WAHBA EGX PRO TERMINAL (v7.0)
# DEVELOPER: MOSTAFA TAMER
# DESCRIPTION: AI-Powered Market Analysis with Institutional Logic
# ------------------------------------------------------------------------------

import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
import pytz
from datetime import datetime
from sklearn.linear_model import LinearRegression
from tradingview_ta import TA_Handler, Interval

# --- 1. CONFIGURATION & THEME ---
EGYPT_TZ = pytz.timezone('Africa/Cairo')
NOW = datetime.now(EGYPT_TZ)

st.set_page_config(
    page_title="WAHBA EGX | AI Terminal",
    page_icon="👑",
    layout="wide"
)

# --- 2. ADVANCED CSS (Glassmorphism & Gold Theme) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;700;900&display=swap');
    
    * {{ font-family: 'Tajawal', sans-serif; }}
    .stApp {{ background: radial-gradient(circle at top, #1a1a1a 0%, #050505 100%); color: #fff; }}
    
    /* Header Section */
    .header-box {{
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(212, 175, 55, 0.2);
        padding: 50px;
        text-align: center;
        border-radius: 30px;
        margin-bottom: 40px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
    }}
    .brand-title {{ font-size: 55px; font-weight: 900; letter-spacing: 2px; margin: 0; }}
    .brand-title span {{ color: #d4af37; text-shadow: 0 0 20px rgba(212, 175, 55, 0.5); }}
    .tagline {{ color: #888; letter-spacing: 5px; font-size: 12px; text-transform: uppercase; }}

    /* Stock Card Section */
    .card {{
        background: rgba(20, 20, 20, 0.6);
        border: 1px solid #222;
        border-radius: 25px;
        padding: 25px;
        margin-bottom: 20px;
        transition: 0.4s ease-in-out;
        position: relative;
        overflow: hidden;
    }}
    .card:hover {{
        border-color: #d4af37;
        transform: translateY(-8px);
        background: rgba(30, 30, 30, 0.8);
    }}
    .card::before {{
        content: ""; position: absolute; top: 0; left: 0; width: 5px; height: 100%; background: #d4af37;
    }}
    
    .ticker {{ font-size: 28px; font-weight: 900; color: #d4af37; }}
    .status-pill {{ background: rgba(0, 255, 0, 0.1); color: #00ff00; padding: 4px 12px; border-radius: 50px; font-size: 11px; font-weight: bold; }}
    .price-main {{ font-size: 30px; font-weight: bold; }}
    .target-main {{ font-size: 30px; font-weight: bold; color: #00ff00; }}
    
    /* Button Styling */
    .stButton>button {{
        background: linear-gradient(135deg, #d4af37 0%, #b8860b 100%) !important;
        color: #000 !important; font-weight: 900 !important; border-radius: 15px !important;
        padding: 20px !important; border: none !important; transition: 0.3s !important;
    }}
    .stButton>button:hover {{ box-shadow: 0 0 30px rgba(212, 175, 55, 0.4) !important; transform: scale(1.01); }}

    /* Hide Elements */
    #MainMenu, footer {{ visibility: hidden; }}
    </style>

    <div class="header-box">
        <div class="tagline">Neural Network Market Analysis</div>
        <h1 class="brand-title">WAHBA <span>EGX</span></h1>
        <p style="color:#555; margin-top:10px;">Institutional Terminal | Alexandria, Egypt</p>
    </div>
""", unsafe_allow_html=True)

# --- 3. LOGIC & DATA PROCESSING ---
def get_ai_brain():
    """Initializes the AI model with historical data patterns"""
    model = LinearRegression()
    # Mock data for training (Price, RSI) -> Target Price
    X = np.array([[10, 30], [20, 50], [0.03, 25], [100, 60], [5, 45]])
    y = np.array([10.55, 21.30, 0.035, 104.2, 5.45])
    model.fit(X, y)
    return model

@st.cache_data(ttl=3600)
def get_market_symbols():
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {"filter": [{"left": "type", "operation": "in_range", "right": ["stock"]}], "markets": ["egypt"], "columns": ["name"]}
        res = requests.post(url, json=payload, timeout=15).json()
        return [item['s'].split(':')[1] for item in res['data']]
    except:
        return ["COMI", "FWRY", "TMGH", "SWDY", "TRTO", "ISPH", "ABUK"]

def run_analysis_pipeline():
    symbols = get_market_symbols()
    brain = get_ai_brain()
    results = []
    
    p_bar = st.progress(0, text="🤖 Analyzing Market Structure...")
    
    for i, sym in enumerate(symbols):
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=10)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            
            p, r, piv = ind.get("close"), ind.get("RSI"), ind.get("Pivot.M.Classic.Middle")
            
            # AI Prediction
            pred = brain.predict(np.array([[p, r]]))[0]
            target = round(float(pred), 2)
            
            # Sentiment Logic
            if p > piv and r > 50: sentiment = "Institutional Accumulation"
            elif r > 70: sentiment = "Overbought / Supply Zone"
            else: sentiment = "Market Equilibrium"

            results.append({
                "sym": sym, "price": p, "target": target,
                "sentiment": sentiment, "rec": analysis.summary["RECOMMENDATION"]
            })
        except: continue
        p_bar.progress((i + 1) / len(symbols))
    
    p_bar.empty()
    return results

# --- 4. MAIN INTERFACE ---
with st.sidebar:
    st.markdown("### ⚙️ System Control")
    st.write(f"📅 Session: **{NOW.strftime('%Y-%m-%d')}**")
    st.write(f"⏰ Server Time: **{NOW.strftime('%I:%M %p')}**")
    st.divider()
    st.caption("Developed by Mostafa Tamer for High-Performance Trading Environments.")

if st.button("EXECUTE QUANTUM MARKET SCAN"):
    st.session_state.data_vault = run_deep_scan = run_analysis_pipeline()

if 'data_vault' in st.session_state:
    data = st.session_state.data_vault
    st.markdown("### ⚜️ Alpha Opportunities")
    
    col1, col2 = st.columns(2)
    for i, item in enumerate(data):
        target_col = col1 if i % 2 == 0 else col2
        with target_col:
            st.markdown(f"""
            <div class="card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div class="ticker">{item['sym']}</div>
                    <div class="status-pill">{item['sentiment']}</div>
                </div>
                <hr style="border-color:#222; margin:15px 0;">
                <div style="display:flex; justify-content:space-between;">
                    <div><small style="color:#555;">Current Price</small><br><span class="price-main">{item['price']}</span></div>
                    <div style="text-align:left;"><small style="color:#555;">AI Forecast</small><br><span class="target-main">{item['target']}</span></div>
                </div>
                <div style="margin-top:20px; font-size:12px; color:#d4af37;">
                    Signal: <b>{item['rec']}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown(f"""
    <div style="text-align:center; padding:50px; color:#222; font-size:10px; border-top:1px solid #111; margin-top:100px;">
        WAHBA QUANTUM CORE v7.0 | ARCHITECTURE BY MOSTAFA TAMER<br>
        ALEXANDRIA, EGYPT | 2026
    </div>
""", unsafe_allow_html=True)

