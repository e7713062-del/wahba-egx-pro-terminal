import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import numpy as np
import requests
from datetime import datetime, date
from concurrent.futures import ThreadPoolExecutor
import sqlite3
import os

# ==========================================
# 1. LUXURY CONFIGURATION
# ==========================================
CORP_NAME = "WAHBA QUANTITATIVE SOLUTIONS"
FOUNDER = "MUSTAFA TAMER"
PLATINUM_GOLD = "#D4AF37"
DEEP_BLACK = "#050505"
NEON_GREEN = "#00FFAA"
SOFT_GRAY = "#888888"

st.set_page_config(page_title=CORP_NAME, layout="wide")

# ==========================================
# 2. THE IMPERIAL UI (CSS)
# ==========================================
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;400;700&family=JetBrains+Mono:wght@300&display=swap');

    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {DEEP_BLACK};
        color: #FFFFFF;
        font-family: 'Inter', sans-serif;
    }}

    /* Institutional Header */
    .header-wrapper {{
        border-bottom: 1px solid #1A1A1A;
        padding: 40px 0 20px 0;
        margin-bottom: 40px;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
    }}

    .corp-title {{
        letter-spacing: 5px;
        color: {PLATINUM_GOLD};
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 5px;
    }}

    .main-title {{
        font-size: 42px;
        font-weight: 200;
        margin: 0;
        line-height: 1;
    }}

    /* Pulsing Status Label */
    .live-status-box {{
        background: rgba(0, 255, 170, 0.05);
        border: 1px solid rgba(0, 255, 170, 0.2);
        padding: 8px 20px;
        border-radius: 2px;
        display: flex;
        align-items: center;
    }}

    .pulse-dot {{
        height: 8px; width: 8px;
        background-color: {NEON_GREEN};
        border-radius: 50%;
        margin-right: 12px;
        box-shadow: 0 0 15px {NEON_GREEN};
        animation: pulse-animation 2s infinite;
    }}

    @keyframes pulse-animation {{
        0% {{ opacity: 0.4; }}
        50% {{ opacity: 1; }}
        100% {{ opacity: 0.4; }}
    }}

    /* Luxury Signal Cards */
    .luxury-card {{
        background: linear-gradient(180deg, #0A0A0A 0%, #0F0F0F 100%);
        border: 1px solid #1A1A1A;
        padding: 30px;
        border-radius: 0px; /* المؤسسات تفضل الحواف الحادة */
        position: relative;
        transition: 0.5s cubic-bezier(0.2, 1, 0.3, 1);
    }}

    .luxury-card:hover {{
        border-color: {PLATINUM_GOLD};
        background: #121212;
        transform: translateY(-5px);
    }}

    .card-ticker {{
        font-size: 14px;
        color: {SOFT_GRAY};
        letter-spacing: 2px;
    }}

    .card-target {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 32px;
        margin: 15px 0;
        color: #FFF;
    }}

    .card-roi {{
        color: {NEON_GREEN};
        font-size: 14px;
        font-weight: 700;
    }}

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {{ gap: 40px; }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent !important;
        border: none !important;
        color: #444 !important;
        font-size: 16px !important;
        padding: 10px 0 !important;
    }}
    .stTabs [aria-selected="true"] {{
        color: {PLATINUM_GOLD} !important;
        border-bottom: 1px solid {PLATINUM_GOLD} !important;
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. AUTO-ARCHIVE ENGINE (SQLite)
# ==========================================
def init_archive():
    conn = sqlite3.connect('wahba_vault.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS history 
                    (date TEXT, symbol TEXT, price REAL, target REAL, roi REAL)''')
    conn.close()

def archive_data(df):
    today = str(date.today())
    conn = sqlite3.connect('wahba_vault.db')
    existing = pd.read_sql(f"SELECT * FROM history WHERE date='{today}'", conn)
    if existing.empty:
        df['date'] = today
        df.to_sql('history', conn, if_exists='append', index=False)
    conn.close()

# ==========================================
# 4. QUANT DATA CORE
# ==========================================
@st.cache_data(ttl=3600)
def get_institutional_feed(_trigger):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {{"filter": [{"left": "market_cap_basic", "operation": "nempty"}],
                   "markets": ["egypt"], "columns": ["name"]}}
        res = requests.post(url, json=payload, timeout=15).json()
        symbols = [i['s'].split(':')[1] for i in res['data'][:80] if ":" in i['s']]
        
        results = []
        def fetch(s):
            try:
                h = TA_Handler(symbol=s, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=8)
                ind = h.get_analysis().indicators
                p, r1 = ind.get("Pivot.M.Classic.Middle", 0), ind.get("Pivot.M.Classic.R1", 0)
                if p == 0: return None
                target = np.round(p + (r1 - p) * 1.618, 2)
                roi = np.round(((target - ind["close"]) / ind["close"]) * 100, 2)
                return {{"symbol": s, "price": ind["close"], "target": target, "roi": roi, "rsi": ind.get("RSI", 0)}}
            except: return None

        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(filter(None, executor.map(fetch, symbols)))
        return pd.DataFrame(results)
    except: return pd.DataFrame()

# ==========================================
# 5. MAIN TERMINAL
# ==========================================
def main():
    init_archive()
    
    # Header Section
    st.markdown(f"""
    <div class="header-wrapper">
        <div>
            <div class="corp-title">{CORP_NAME}</div>
            <h1 class="main-title">QUANTITATIVE <span style="font-weight:700;">TERMINAL</span></h1>
        </div>
        <div class="live-status-box">
            <div class="pulse-dot"></div>
            <span style="color:{NEON_GREEN}; font-size:11px; font-weight:700; letter-spacing:2px;">LIVE ARCHIVE ACTIVE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Synchronizing Institutional Data..."):
        df = get_institutional_feed(str(date.today()))
        if not df.empty: archive_data(df)

    if not df.empty:
        t1, t2, t3 = st.tabs(["PREMIUM ALPHA", "MARKET ARCHIVE", "VAULT SYSTEM"])

        with t1:
            st.markdown("<br>", unsafe_allow_html=True)
            top_df = df[df['roi'] > 0].sort_values(by='roi', ascending=False).head(12)
            for i in range(0, len(top_df), 3):
                cols = st.columns(3)
                batch = top_df.iloc[i:i+3].to_dict(orient='records')
                for idx, row in enumerate(batch):
                    with cols[idx]:
                        st.markdown(f"""
                        <div class="luxury-card">
                            <div class="card-ticker">{row['symbol']}</div>
                            <div class="card-target">{row['target']} <span style="font-size:12px; color:#444;">EGP</span></div>
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span class="card-roi">+{row['roi']}% ROI</span>
                                <span style="color:#333; font-size:11px;">RSI: {int(row['rsi'])}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

        with t2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True, hide_index=True)

        with t3:
            st.info("System is configured to archive market data automatically every 24 hours.")
            if st.button("Force Database Sync"):
                st.cache_data.clear()
                st.rerun()
    else:
        st.error("System Sync Failed. Feed Unresponsive.")

    # Footer
    st.markdown(f"""
    <div style="margin-top:100px; padding:40px; border-top:1px solid #111; text-align:center;">
        <div style="color:#222; font-size:10px; letter-spacing:5px;">PRIVATE & CONFIDENTIAL | {FOUNDER}</div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
