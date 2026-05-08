import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import numpy as np
import requests
from datetime import datetime

# ==========================================
# 1. INSTITUTIONAL IDENTITY
# ==========================================
CORP_NAME = "WAHBA QUANTITATIVE SOLUTIONS"
FOUNDER = "MUSTAFA TAMER"
SYSTEM_NAME = "WAHBA EGX PRO"
VERSION = "INSTITUTIONAL v5.2.1"

# ==========================================
# 2. DATA ENGINE (FIXED IMPORT ISSUES)
# ==========================================
def get_market_data():
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
# 3. LUXURY & CORPORATE UI (FIXED RENDERING)
# ==========================================
st.set_page_config(page_title=f"{SYSTEM_NAME} | {FOUNDER}", layout="wide")

# CSS لإصلاح الترتيب والشكل الفخم
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;700&family=Cinzel:wght@400;700&family=Montserrat:wght@200;400;800&display=swap');
    
    .stApp { background: #020202; color: #f0f0f0; }
    h1, h2, .luxury-font { font-family: 'Cinzel', serif; letter-spacing: 4px; }
    body, p, div { font-family: 'Montserrat', 'Cairo', sans-serif; }

    .header-box {
        background: linear-gradient(90deg, #000 0%, #0a0a0a 100%);
        padding: 40px; border-bottom: 2px solid #D4AF37; margin-bottom: 30px;
    }

    .status-bar {
        display: flex; justify-content: space-around;
        background: #000; border: 1px solid #111; padding: 10px;
        margin-bottom: 30px; font-size: 10px; color: #555; text-transform: uppercase;
    }

    .asset-card {
        background: #080808; border: 1px solid #1a1a1a; padding: 25px;
        margin-bottom: 20px; border-left: 3px solid #D4AF37;
    }

    .target-val { font-size: 30px; font-weight: 800; color: #00ffaa; margin: 10px 0; }
    
    .footer {
        padding: 60px; text-align: center; border-top: 1px solid #111;
        font-size: 11px; color: #333; line-height: 1.8;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. EXECUTION
# ==========================================
def main():
    # بوابة الدخول المؤسسية
    if 'auth' not in st.session_state:
        st.markdown(f"""
        <div style="text-align:center; padding:100px 20px;">
            <p style="letter-spacing:10px; color:#D4AF37; font-size:14px;">{CORP_NAME}</p>
            <h1 style="font-size:3.5rem;">TERMINAL ACCESS</h1>
            <div style="max-width:750px; margin:40px auto; border:1px solid #111; padding:40px; background:#050505;">
                <p style="color:#666; font-size:12px;">SYSTEM INITIALIZATION REQUIRED. PROPRIETARY ALGORITHMS PROTECTED BY {FOUNDER} & PARTNERS.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # تصحيح الزر (Fixed TypeError)
        if st.button("INITIALIZE SECURE SESSION", use_container_width=True):
            st.session_state.auth = True
            st.rerun()
        return

    # الهيدر المؤسسي (Fixed Rendering)
    st.markdown(f"""
    <div class="header-box">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div style="color:#D4AF37; font-size:10px; letter-spacing:5px;">{CORP_NAME}</div>
                <h1 style="font-size:2.5rem; margin:5px 0;">{SYSTEM_NAME}</h1>
            </div>
            <div style="text-align:right;">
                <p style="color:#555; font-size:10px; margin:0;">MASTER OPERATOR</p>
                <p style="color:#D4AF37; font-weight:bold; margin:0;">{FOUNDER}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="status-bar">
        <span>● DATA CLUSTER: ACTIVE</span>
        <span>● RISK ALGO: OPERATIONAL</span>
        <span>● VERSION: {VERSION}</span>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("FETCHING INSTITUTIONAL VECTORS..."):
        df = get_market_data()

    if not df.empty:
        df['T'] = np.round(df['P'] + (df['R1'] - df['P']) * 1.618, 2)
        df['ROI'] = np.round(((df['T'] - df['Price']) / df['Price']) * 100, 1)
        
        signals = df[df['Score'] >= 5].sort_values(by='ROI', ascending=False).head(12)
        
        cols = st.columns(3)
        for i, (_, row) in enumerate(signals.iterrows()):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="asset-card">
                    <div style="font-family:'Cinzel'; font-size:1.5rem;">{row['Symbol']}</div>
                    <div style="font-size:9px; color:#444;">INSTITUTIONAL GRADE</div>
                    <div style="background:#000; padding:15px; border:1px solid #111; margin:15px 0; text-align:center;">
                        <div style="color:#555; font-size:9px;">LIQUIDITY TARGET</div>
                        <div class="target-val">{row['T']}</div>
                        <div style="color:#00ffaa; font-size:12px;">+{row['ROI']}% POTENTIAL</div>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:10px; color:#222;">
                        <span>ENTRY: {row['Price']}</span>
                        <span>NODE: EX-04</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # الفوتر المؤسسي
    st.markdown(f"""
    <div class="footer">
        <p style="color:#D4AF37; letter-spacing:3px;">{CORP_NAME}</p>
        © {datetime.now().year} {FOUNDER} & PARTNERS. ALL RIGHTS RESERVED.<br>
        TRADING INVOLVES SIGNIFICANT RISK. SYSTEM OPERATED UNDER INSTITUTIONAL LICENSE.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
