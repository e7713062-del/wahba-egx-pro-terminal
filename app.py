import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import numpy as np
import requests
import os
from datetime import datetime
import pytz

# ==========================================
# 1. LEGAL & IP TERMINAL (Mustafa Tamer)
# ==========================================
OWNER = "MUSTAFA TAMER"
SYSTEM_NAME = "WAHBA EGX"
LEGAL_EN = f"""
LEGAL NOTICE: © {datetime.now().year} {OWNER}. All Rights Reserved. 
This terminal and its underlying logic are protected under international intellectual property treaties. 
Any attempt to decompile, scrape, or replicate the algorithms of {SYSTEM_NAME} will result in legal action.
"""
LEGAL_AR = f"""
إخطار قانوني: جميع الحقوق محفوظة © {datetime.now().year} للمالك {OWNER}.
نظام {SYSTEM_NAME} وخوارزمياته محمية بموجب قوانين الملكية الفكرية الدولية.
أي محاولة لفك شفرة الكود أو استخراج البيانات أو تقليد المنطق الحسابي ستعرض صاحبها للملاحقة القانونية الصارمة.
"""

# ==========================================
# 2. DATA ARCHITECTURE
# ==========================================
def get_institutional_data():
    try:
        scanner_url = "https://scanner.tradingview.com/egypt/scan"
        payload = {"filter": [{"left": "market_cap_basic", "operation": "nempty"}],
                   "markets": ["egypt"], "columns": ["name"]}
        res = requests.post(scanner_url, json=payload, timeout=10).json()
        symbols = [i['s'].split(':')[1] for i in res['data'] if ":" in i['s']]
        
        results = []
        for sym in symbols[:40]: 
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
# 3. ADVANCED UI (New Typography & Layout)
# ==========================================
st.set_page_config(page_title=f"{SYSTEM_NAME} | {OWNER}", layout="wide")

# تغيير الخطوط لخطوط مؤسسية قوية
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&family=Montserrat:wght@400;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Cairo', 'Montserrat', sans-serif;
        background-color: #050505;
        color: #ffffff;
    }

    .main-header {
        background: #000;
        border-bottom: 2px solid #D4AF37;
        padding: 60px 20px;
        text-align: center;
        margin-bottom: 50px;
    }

    .legal-alert {
        background: rgba(212, 175, 55, 0.05);
        border: 1px solid #D4AF37;
        padding: 30px;
        border-radius: 5px;
        margin-bottom: 40px;
        text-align: center;
    }

    .quant-card {
        background: #0d0d0d;
        border: 1px solid #1a1a1a;
        padding: 30px;
        border-radius: 8px;
        margin-bottom: 20px;
        transition: 0.3s;
    }

    .quant-card:hover {
        border-color: #D4AF37;
        transform: translateY(-5px);
    }

    .footer {
        background: #000;
        padding: 40px;
        margin-top: 100px;
        border-top: 1px solid #1a1a1a;
        font-size: 12px;
        color: #444;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. EXECUTION TERMINAL
# ==========================================
def main():
    # بوابة الحماية القانونية (Gatekeeper)
    if 'authorized' not in st.session_state:
        st.markdown(f"<h1 style='text-align:center; color:#D4AF37; font-family:Montserrat;'>{SYSTEM_NAME} TERMINAL</h1>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="legal-alert">
            <p style="color:#D4AF37; font-weight:bold; font-size:18px;">LEGAL DISCLOSURE / إقرار قانوني</p>
            <p style="font-size:14px; color:#aaa;">{LEGAL_EN}</p>
            <hr style="border-color:#222">
            <p style="font-size:14px; color:#aaa; direction:rtl;">{LEGAL_AR}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("I ACCEPT THE TERMS & CONDITIONS / أوافق على الشروط", use_container_広告=True):
            st.session_state.authorized = True
            st.rerun()
        return

    # Header
    st.markdown(f"""
    <div class="main-header">
        <h1 style="font-family:Montserrat; font-weight:800; font-size:4rem; margin:0;">{SYSTEM_NAME} <span style="color:#D4AF37;">EG</span></h1>
        <p style="color:#555; letter-spacing:5px;">INSTITUTIONAL QUANTUM TERMINAL BY {OWNER}</p>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("DECRYPTING MARKET VECTORS..."):
        df = get_institutional_data()

    if not df.empty:
        # خوارزمية مشفرة (Internal Vectors)
        df['T'] = np.round(df['P'] + (df['R1'] - df['P']) * 1.618, 2)
        df['ROI'] = np.round(((df['T'] - df['Price']) / df['Price']) * 100, 1)
        
        signals = df[df['Score'] >= 5].sort_values(by='ROI', ascending=False).head(12)
        
        cols = st.columns(3)
        for i, (_, row) in enumerate(signals.iterrows()):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="quant-card">
                    <h2 style="margin:0; font-family:Montserrat;">{row['Symbol']}</h2>
                    <p style="color:#444; font-size:12px;">ASSET SECURED BY {OWNER.split()[0]}</p>
                    <div style="background:#000; padding:20px; margin:20px 0; border-left:4px solid #D4AF37;">
                        <small style="color:#D4AF37;">TARGET VECTOR</small>
                        <div style="font-size:32px; font-weight:bold; color:#00ffaa;">{row['T']}</div>
                        <div style="color:#00ffaa; font-size:14px;">+{row['ROI']}% POTENTIAL</div>
                    </div>
                    <div style="font-size:14px; color:#666;">
                        ENTRY: {row['Price']} EGP
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Footer - الملكية الفكرية
    st.markdown(f"""
    <div class="footer">
        {LEGAL_EN}<br><br>
        <div style="direction:rtl;">{LEGAL_AR}</div>
        <br>
        <p style="color:#D4AF37; font-weight:bold;">BY {OWNER}</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
