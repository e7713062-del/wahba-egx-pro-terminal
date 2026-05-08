import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import numpy as np
import requests
from datetime import datetime, date
from concurrent.futures import ThreadPoolExecutor

# ==========================================
# 1. CORE CONFIGURATION & IDENTITY
# ==========================================
CORP_NAME = "WAHBA QUANTITATIVE SOLUTIONS"
FOUNDER = "MUSTAFA TAMER"
VERSION = "PLATINUM INSTITUTIONAL v8.0.0"
GOLD_COLOR = "#D4AF37"
BG_DARK = "#0A0A0A"
CARD_BG = "#111111"

# ==========================================
# 2. SMART CACHE ENGINE
# ==========================================
@st.cache_data(ttl=86400)
def get_daily_market_data(_last_update_date):
    try:
        scanner_url = "https://scanner.tradingview.com/egypt/scan"
        payload = {"filter": [{"left": "market_cap_basic", "operation": "nempty"}],
                   "markets": ["egypt"], "columns": ["name"]}
        res = requests.post(scanner_url, json=payload, timeout=10).json()
        symbols = [i['s'].split(':')[1] for i in res['data'] if ":" in i['s']]
        
        results = []
        def fetch(s):
            try:
                h = TA_Handler(symbol=s, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=3)
                ind = h.get_analysis().indicators
                return {
                    "Symbol": s, 
                    "Price": ind["close"], 
                    "P": ind["Pivot.M.Classic.Middle"], 
                    "R1": ind["Pivot.M.Classic.R1"],
                    "RSI": ind["RSI"],
                    "Volume": ind["volume"]
                }
            except: return None

        with ThreadPoolExecutor(max_workers=30) as executor:
            results = list(filter(None, executor.map(fetch, symbols)))
            
        df = pd.DataFrame(results)
        return df
    except Exception:
        return pd.DataFrame()

# ==========================================
# 3. LUXURY UI FRAMEWORK
# ==========================================
st.set_page_config(page_title=f"{CORP_NAME} | Terminal", layout="wide")

st.markdown(f"""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {BG_DARK};
        font-family: 'Inter', sans-serif;
        color: #E0E0E0;
    }}

    /* Institutional Header */
    .header-container {{
        border-bottom: 1px solid #262626;
        padding-bottom: 20px;
        margin-bottom: 30px;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
    }}

    /* Luxury Card */
    .metric-card {{
        background: linear-gradient(145deg, #111111, #161616);
        border: 1px solid #262626;
        padding: 25px;
        border-radius: 4px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
    }}
    
    .metric-card:hover {{
        border-color: {GOLD_COLOR};
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}

    .metric-card::after {{
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 2px;
        background: linear-gradient(90deg, transparent, {GOLD_COLOR}, transparent);
        opacity: 0; transition: 0.3s;
    }}
    
    .metric-card:hover::after {{ opacity: 1; }}

    /* Typography */
    .symbol-title {{ font-size: 14px; color: #888; letter-spacing: 2px; text-transform: uppercase; }}
    .price-value {{ font-size: 28px; font-weight: 700; color: #FFFFFF; margin: 10px 0; }}
    .roi-badge {{
        background: rgba(0, 255, 170, 0.1);
        color: #00ffaa;
        padding: 4px 12px;
        border-radius: 2px;
        font-size: 13px;
        font-weight: bold;
    }}
    
    /* Custom Tabs */
    .stTabs [data-baseweb="tab-list"] {{ gap: 20px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent !important;
        border: none !important;
        color: #666 !important;
        font-weight: 600 !important;
    }}
    .stTabs [aria-selected="true"] {{
        color: {GOLD_COLOR} !important;
        border-bottom: 2px solid {GOLD_COLOR} !important;
    }}

    /* Status Dot */
    .status-indicator {{
        display: inline-block;
        width: 8px; height: 8px;
        background: #00ffaa;
        border-radius: 50%;
        margin-right: 8px;
        box-shadow: 0 0 10px #00ffaa;
    }}
</style>
""", unsafe_allow_html=True)

def main():
    today_str = str(date.today())
    
    # --- HEADER SECTION ---
    st.markdown(f"""
    <div class="header-container">
        <div>
            <div style="color:{GOLD_COLOR}; font-weight:700; letter-spacing:3px; font-size:12px;">{CORP_NAME}</div>
            <h1 style="margin:0; font-weight:300; font-size:36px; color:#FFF;">Quantitative <span style="font-weight:700;">Terminal</span></h1>
        </div>
        <div style="text-align:right;">
            <div style="font-size:12px; color:#666; margin-bottom:5px;">SYSTEM STATUS</div>
            <div style="font-size:13px; font-weight:600;">
                <span class="status-indicator"></span> LIVE ARCHIVE MODE
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- DATA ENGINE ---
    with st.spinner("Initializing neural link to EGX..."):
        df_daily = get_daily_market_data(today_str)

    if not df_daily.empty:
        # Advanced Quant Calculations
        df_daily['Target'] = np.round(df_daily['P'] + (df_daily['R1'] - df_daily['P']) * 1.618, 2)
        df_daily['ROI'] = np.round(((df_daily['Target'] - df_daily['Price']) / df_daily['Price']) * 100, 1)
        
        # --- FILTERS ROW ---
        col_f1, col_f2, col_f3 = st.columns([2, 1, 1])
        with col_f1:
            search = st.text_input("🔍 Search Asset Code", "").upper()
        
        if search:
            df_daily = df_daily[df_daily['Symbol'].str.contains(search)]

        # --- DASHBOARD TABS ---
        tab1, tab2, tab3 = st.tabs(["PREMIUM SIGNALS", "MARKET OVERVIEW", "TERMINAL LOGS"])
        
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            top_hits = df_daily[df_daily['ROI'] > 0].sort_values(by='ROI', ascending=False).head(12)
            
            # Grid Layout
            for i in range(0, len(top_hits), 3):
                cols = st.columns(3)
                batch = top_hits.iloc[i:i+3].to_dict(orient='records')
                for idx, row in enumerate(batch):
                    with cols[idx]:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span class="symbol-title">{row['Symbol']}</span>
                                <span class="roi-badge">+{row['ROI']}%</span>
                            </div>
                            <div class="price-value">{row['Target']} <small style="font-size:12px; color:#666;">EGP</small></div>
                            <div style="display:flex; justify-content:space-between; font-size:12px; color:#555; border-top:1px solid #222; pt-10; margin-top:10px; padding-top:10px;">
                                <span>LTP: <b>{row['Price']}</b></span>
                                <span>RSI: <b style="color:{'#ff4b4b' if row['RSI'] > 70 else '#00ffaa'}">{int(row['RSI'])}</b></span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

        with tab2:
            st.markdown("<div style='padding:20px 0;'>", unsafe_allow_html=True)
            # استايل الجدول المؤسسي
            st.dataframe(
                df_daily.style.format(subset=['Price', 'Target', 'ROI'], formatter="{:.2f}")
                .background_gradient(subset=['ROI'], cmap='Greens'),
                use_container_width=True, 
                height=500
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with tab3:
            st.info(f"System Version: {VERSION} | Founder: {FOUNDER}")
            st.code(f"Last Sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nData Source: TradingView Institutional API\nLocation: Egypt (EGX)")

    else:
        st.error("Terminal Synchronization Failed. Connection to Data Feed interrupted.")

    # --- FOOTER ---
    st.markdown(f"""
    <div style="margin-top:100px; padding:40px; border-top: 1px solid #1a1a1a; text-align:center;">
        <div style="color:{GOLD_COLOR}; font-size:14px; font-weight:700; letter-spacing:2px;">{CORP_NAME}</div>
        <div style="color:#444; font-size:10px; margin-top:10px;">
            STRICTLY CONFIDENTIAL | FOR INSTITUTIONAL USE ONLY | © 2024 PRIVATE EQUITY
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
