import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import numpy as np
import requests
import os
from datetime import datetime
import pytz

# ==========================================
# 1. LEGAL & IP CONFIGURATION (Mustafa Tamer)
# ==========================================
OWNER = "MUSTAFA TAMER"
SYSTEM_NAME = "WAHBA EGX" # الاسم المطلوب
LEGAL_DISCLAIMER_EN = f"""
© {datetime.now().year} {OWNER}. All Rights Reserved. 
The {SYSTEM_NAME} terminal and its proprietary algorithms are protected under international IP laws. 
Unauthorized reverse engineering, redistribution, or derivation is strictly prohibited.
"""
LEGAL_DISCLAIMER_AR = f"""
جميع الحقوق محفوظة © {datetime.now().year} للمالك {OWNER}.
نظام {SYSTEM_NAME} وخوارزمياته محمية بموجب قوانين الملكية الفكرية الدولية.
يحظر تماماً إعادة الهندسة العكسية أو الاقتباس أو التوزيع غير القانوني.
"""

# ==========================================
# 2. PROPRIETARY CORE (Hidden Logic)
# ==========================================
class QuantumEngine:
    @staticmethod
    def _compute_vectors(d):
        # Confidential logic - Vector calculation
        _p, _r, _s, _c = d['P'], d['R1'], d['S1'], d['Price']
        target = np.round(_p + (_r - _p) * 1.618, 2)
        sl = np.round(_s * 0.99, 2)
        roi = np.round(((target - _c) / _c) * 100, 1)
        return target, sl, roi

# ==========================================
# 3. DATA ARCHITECTURE
# ==========================================
def get_institutional_data():
    EGYPT_TZ = pytz.timezone('Africa/Cairo')
    DB_FILE = f"wahba_data_{datetime.now(EGYPT_TZ).strftime('%Y%m%d')}.csv"
    
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    
    try:
        scanner_url = "https://scanner.tradingview.com/egypt/scan"
        payload = {"filter": [{"left": "market_cap_basic", "operation": "nempty"}],
                   "markets": ["egypt"], "columns": ["name"]}
        res = requests.post(scanner_url, json=payload, timeout=10).json()
        symbols = [i['s'].split(':')[1] for i in res['data'] if ":" in i['s']]
        
        results = []
        for sym in symbols[:45]: 
            try:
                h = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", 
                               interval=Interval.INTERVAL_1_DAY, timeout=5)
                ind = h.get_analysis().indicators
                results.append({
                    "Symbol": sym, "Price": ind["close"], "Score": h.get_analysis().summary["BUY"],
                    "P": ind["Pivot.M.Classic.Middle"], "R1": ind["Pivot.M.Classic.R1"], "S1": ind["Pivot.M.Classic.S1"]
                })
            except: continue
            
        df = pd.DataFrame(results)
        if not df.empty: df.to_csv(DB_FILE, index=False)
        return df
    except: return pd.DataFrame()

# ==========================================
# 4. HIGH-END UI DESIGN (Enterprise Style)
# ==========================================
st.set_page_config(page_title=f"{SYSTEM_NAME} PRO | {OWNER}", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;600&display=swap');
    
    .stApp { background-color: #050505; color: #ffffff; }
    
    h1, h2, h3 { font-family: 'Orbitron', sans-serif; letter-spacing: 2px; }
    p, div { font-family: 'Inter', sans-serif; }

    .main-header {
        text-align: center;
        padding: 50px 20px;
        background: linear-gradient(180deg, #111 0%, #050505 100%);
        border-bottom: 1px solid #222;
        margin-bottom: 40px;
    }

    .gold-text { color: #D4AF37; }
    
    .quant-card {
        background: #0a0a0a;
        border: 1px solid #1a1a1a;
        padding: 25px;
        border-radius: 2px;
        transition: 0.3s all ease-in-out;
    }
    
    .quant-card:hover {
        border-color: #D4AF37;
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.05);
    }

    .legal-box {
        font-size: 11px;
        color: #333;
        text-align: center;
        margin-top: 120px;
        padding: 40px;
        border-top: 1px solid #111;
        background: #020202;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 5. EXECUTION TERMINAL
# ==========================================
def main():
    # Header
    st.markdown(f"""
    <div class="main-header">
        <h1 style="margin:0; font-size: 3.5rem;">{SYSTEM_NAME} <span class="gold-text">PRO</span></h1>
        <p style="color: #555; text-transform: uppercase; font-size: 11px; letter-spacing: 3px; margin-top:15px;">
            Proprietary Trading Terminal • Developed by <b>{OWNER}</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Core Engine Execution
    with st.spinner(f"AUTHENTICATING {SYSTEM_NAME} QUANTUM CORE..."):
        df = get_institutional_data()

    if not df.empty:
        # Secure Calculation
        df[['Target', 'SL', 'ROI']] = df.apply(lambda r: pd.Series(QuantumEngine._compute_vectors(r)), axis=1)
        
        # Grid Display (Top ROI Signals)
        signals = df[df['Score'] >= 5].sort_values(by='ROI', ascending=False).head(12)
        
        cols = st.columns(3)
        for i, (_, row) in enumerate(signals.iterrows()):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="quant-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size: 1.4rem; font-weight: bold; color:#fff;">{row['Symbol']}</span>
                        <div style="width:10px; height:10px; background:#00ffaa; border-radius:50%; box-shadow: 0 0 5px #00ffaa;"></div>
                    </div>
                    <div style="margin: 25px 0;">
                        <span style="color: #444; font-size: 11px; display:block;">MARKET PRICE</span>
                        <span style="font-size: 22px; font-weight: 600;">{row['Price']} <small style="font-size:12px; color:#444;">EGP</small></span>
                    </div>
                    <div style="background: #000; padding: 20px; border: 1px solid #1a1a1a;">
                        <span style="color: #D4AF37; font-size: 10px; font-weight: bold; display:block; margin-bottom:5px;">INSTITUTIONAL TARGET</span>
                        <span style="font-size: 28px; font-weight: bold; color: #00ffaa;">{row['Target']}</span>
                        <div style="color: #00ffaa; font-size: 13px; margin-top:5px;">+ {row['ROI']}% Projected Yield</div>
                    </div>
                    <div style="margin-top: 20px; color: #611; font-size: 11px; font-weight:bold;">
                        PROTECTION STOP: {row['SL']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.error("System Offline. Interface cannot reach the secure server.")

    # Footer
    st.markdown(f"""
    <div class="legal-box">
        <div style="margin-bottom: 10px;">{LEGAL_DISCLAIMER_EN}</div>
        <div style="direction: rtl;">{LEGAL_DISCLAIMER_AR}</div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
