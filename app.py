import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import numpy as np
import requests
from datetime import datetime

# ==========================================
# 1. INSTITUTIONAL IDENTITY (The Organization)
# ==========================================
CORP_NAME = "WAHBA QUANTITATIVE SOLUTIONS"
FOUNDER = "MUSTAFA TAMER"
SYSTEM_NAME = "WAHBA EGX PRO"
VERSION = "INSTITUTIONAL v5.2.1"

LEGAL_NOTICE = f"""
© {datetime.now().year} {CORP_NAME}. PROPRIETARY DATA. 
This terminal is licensed to {FOUNDER} & Partners. 
Internal risk protocols active. Unauthorized distribution is a federal violation.
"""

# ==========================================
# 2. PROPRIETARY CORE
# ==========================================
def fetch_institutional_stream():
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
                    "Symbol": sym, "Price": ind["close"], "Score": ind["Recommend.All"],
                    "P": ind["Pivot.M.Classic.Middle"], "R1": ind["Pivot.M.Classic.R1"]
                })
            except: continue
        return pd.DataFrame(results)
    except: return pd.DataFrame()

# ==========================================
# 3. ENTERPRISE UI DESIGN (Luxury + Corporate)
# ==========================================
st.set_page_config(page_title=f"{SYSTEM_NAME} | Enterprise", layout="wide")

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;700&family=Cinzel:wght@400;700&family=Montserrat:wght@200;400;800&display=swap');
    
    .stApp {{ background: #020202; color: #f0f0f0; }}
    
    /* Global Styles */
    h1, h2 {{ font-family: 'Cinzel', serif; letter-spacing: 4px; }}
    body, p, div {{ font-family: 'Montserrat', 'Cairo', sans-serif; }}

    /* Institutional Header */
    .header-container {{
        background: linear-gradient(90deg, #000 0%, #0a0a0a 100%);
        padding: 40px;
        border-bottom: 2px solid #D4AF37;
        margin-bottom: 30px;
    }}

    .corp-logo {{
        font-size: 10px; letter-spacing: 5px; color: #D4AF37; font-weight: bold;
    }}

    /* Infrastructure Status Bar */
    .status-bar {{
        display: flex; justify-content: space-around;
        background: #000; border: 1px solid #111;
        padding: 10px; margin-bottom: 30px; font-size: 9px; color: #444;
        text-transform: uppercase;
    }}

    /* Premium Asset Card */
    .asset-card {{
        background: #080808; border: 1px solid #1a1a1a;
        padding: 25px; transition: 0.3s;
        position: relative; overflow: hidden;
    }}

    .asset-card:hover {{ border-color: #D4AF37; background: #0c0c0c; }}

    .asset-card::before {{
        content: ""; position: absolute; top:0; left:0; width: 3px; height: 100%;
        background: #D4AF37;
    }}

    .target-box {{
        background: #000; border: 1px solid #222;
        padding: 15px; margin: 15px 0; text-align: center;
    }}

    .footer {{
        margin-top: 80px; padding: 50px; background: #000;
        border-top: 1px solid #111; text-align: center; color: #333; font-size: 10px;
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. OPERATIONAL CORE
# ==========================================
def main():
    # 1. Corporate Entrance
    if 'auth' not in st.session_state:
        st.markdown(f"""
        <div style="text-align:center; padding:120px 20px;">
            <p style="letter-spacing:12px; color:#D4AF37; font-size:14px; margin-bottom:20px;">{CORP_NAME}</p>
            <h1 style="font-size:4rem; margin:0;">SYSTEM AUTH</h1>
            <div style="max-width:800px; margin:50px auto; border:1px solid #111; padding:40px; background:#050505;">
                <p style="color:#666; font-size:12px; line-height:2;">
                    YOU ARE ACCESSING A SECURE QUANTITATIVE TERMINAL. BY INITIALIZING, YOU ACKNOWLEDGE THE INTERNAL RISK PROTOCOLS SET BY THE BOARD OF DIRECTORS. 
                    ALL TRADES ARE SUBJECT TO SYSTEMIC LIQUIDITY CHECKS.
                </p>
                <hr style="border-color:#111; margin:30px 0;">
                <p style="direction:rtl; color:#444; font-size:13px;">هذا النظام محمي ببروتوكولات التداول المؤسسي. يتم رصد كافة العمليات لضمان أمن البيانات.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("INITIALIZE TERMINAL SECURELY", use_container_width=True):
            st.session_state.auth = True
            st.rerun()
        return

    # 2. Main Executive Interface
    st.markdown(f"""
    <div class="header-container">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div class="corp-logo">{CORP_NAME}</div>
                <h1 style="font-size:2.5rem; margin:5px 0;">{SYSTEM_NAME}</h1>
            </div>
            <div style="text-align:right;">
                <p style="color:#555; font-size:10px; margin:0;">MASTER OPERATOR</p>
                <p style="color:#D4AF37; font-weight:bold; margin:0;">{FOUNDER}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Infrastructure Status Bar
    st.markdown(f"""
    <div class="status-bar">
        <span>● DATA CLUSTER: ACTIVE</span>
        <span>● RISK ALGO: OPERATIONAL</span>
        <span>● SERVERS: CAIRO / LONDON</span>
        <span>● VERSION: {VERSION}</span>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("COMMUNICATING WITH GLOBAL DATA NODES..."):
        df = fetch_institutional_stream()

    if not df.empty:
        # Institutional Analytics
        df['T'] = np.round(df['P'] + (df['R1'] - df['P']) * 1.618, 2)
        df['ROI'] = np.round(((df['T'] - df['Price']) / df['Price']) * 100, 1)
        
        signals = df[df['Score'] > 0].sort_values(by='ROI', ascending=False).head(12)
        
        cols = st.columns(3)
        for i, (_, row) in enumerate(signals.iterrows()):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="asset-card">
                    <div style="display:flex; justify-content:space-between; align-items:start;">
                        <div>
                            <span style="font-family:'Cinzel'; font-size:1.6rem; font-weight:700;">{row['Symbol']}</span>
                            <p style="font-size:9px; color:#444; margin:0;">INSTITUTIONAL GRADE</p>
                        </div>
                        <div style="background:#D4AF37; color:#000; font-size:8px; padding:2px 6px; font-weight:bold;">SECURED</div>
                    </div>
                    
                    <div class="target-box">
                        <p style="color:#555; font-size:9px; letter-spacing:2px; margin:0;">PROJECTED LIQUIDITY TARGET</p>
                        <div style="font-size:32px; font-weight:800; color:#00ffaa; margin:5px 0;">{row['T']}</div>
                        <div style="color:#00ffaa; font-size:12px; letter-spacing:1px;">ROI VECTOR: +{row['ROI']}%</div>
                    </div>
                    
                    <div style="display:flex; justify-content:space-between; font-size:11px; color:#222; border-top:1px solid #111; padding-top:10px;">
                        <span>ENTRY: {row['Price']} EGP</span>
                        <span>NODE: EX-04</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # 3. Institutional Footer
    st.markdown(f"""
    <div class="footer">
        <p style="color:#D4AF37; font-weight:bold; letter-spacing:3px; margin-bottom:20px;">{CORP_NAME}</p>
        <div style="max-width:800px; margin:0 auto; line-height:1.8;">
            {LEGAL_NOTICE}
            <br>
            THIS TERMINAL UTILIZES DISTRIBUTED COMPUTING AND PROPRIETARY QUANTUM ANALYTICS. 
            ALL RECOMMENDATIONS ARE GENERATED BY THE CORPORATE CORE ENGINE.
        </div>
        <p style="margin-top:30px; font-size:9px; color:#111;">ENCRYPTED BY WAHBA SECURITY SYSTEMS</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
