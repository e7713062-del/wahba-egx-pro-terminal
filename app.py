import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import numpy as np
import requests
from datetime import datetime, date
from concurrent.futures import ThreadPoolExecutor

# ==========================================
# 1. CORE CONFIGURATION
# ==========================================
CORP_NAME = "WAHBA QUANTITATIVE SOLUTIONS"
FOUNDER = "MUSTAFA TAMER"
GOLD_COLOR = "#D4AF37"

# ==========================================
# 2. DATA ENGINE (Ultra-Stable)
# ==========================================
@st.cache_data(ttl=86400)
def get_market_data(_update_trigger):
    try:
        # جلب قائمة الرموز من مصر
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {"filter": [{"left": "market_cap_basic", "operation": "nempty"}],
                   "markets": ["egypt"], "columns": ["name"]}
        res = requests.post(url, json=payload, timeout=10).json()
        symbols = [i['s'].split(':')[1] for i in res['data'] if ":" in i['s']]
        
        results = []
        def fetch_data(s):
            try:
                h = TA_Handler(symbol=s, screener="egypt", exchange="EGX", 
                               interval=Interval.INTERVAL_1_DAY, timeout=5)
                ind = h.get_analysis().indicators
                # حساب الأهداف مباشرة لتقليل المعالجة لاحقاً
                price = ind["close"]
                pivot = ind["Pivot.M.Classic.Middle"]
                r1 = ind["Pivot.M.Classic.R1"]
                target = np.round(pivot + (r1 - pivot) * 1.618, 2)
                roi = np.round(((target - price) / price) * 100, 2)
                
                return {
                    "Symbol": s, "Price": price, "Target": target, 
                    "ROI %": roi, "RSI": ind["RSI"], "Volume": ind["volume"]
                }
            except: return None

        with ThreadPoolExecutor(max_workers=15) as executor:
            results = list(filter(None, executor.map(fetch_data, symbols)))
        
        return pd.DataFrame(results)
    except:
        return pd.DataFrame()

# ==========================================
# 3. LUXURY UI DESIGN
# ==========================================
st.set_page_config(page_title=CORP_NAME, layout="wide")

# Custom CSS for Dark Luxury Theme
st.markdown(f"""
<style>
    [data-testid="stAppViewContainer"] {{ background-color: #050505; color: #eee; }}
    .main-header {{ border-bottom: 2px solid {GOLD_COLOR}; padding-bottom: 10px; margin-bottom: 30px; }}
    .luxury-card {{
        background: #111; border: 1px solid #222; padding: 20px; border-radius: 5px;
        border-left: 3px solid {GOLD_COLOR}; margin-bottom: 15px;
    }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 24px; }}
    .stTabs [data-baseweb="tab"] {{ color: #888; font-weight: bold; }}
    .stTabs [aria-selected="true"] {{ color: {GOLD_COLOR} !important; border-bottom-color: {GOLD_COLOR} !important; }}
</style>
""", unsafe_allow_html=True)

def main():
    # Header Section
    st.markdown(f"""
    <div class="main-header">
        <h1 style="margin:0; color:{GOLD_COLOR}; letter-spacing:-1px;">WAHBA <span style="font-weight:300; color:white;">PRO TERMINAL</span></h1>
        <p style="margin:0; color:#666; font-size:12px;">INSTITUTIONAL QUANTITATIVE ENGINE | {FOUNDER}</p>
    </div>
    """, unsafe_allow_html=True)

    # Sync Data
    with st.spinner("Accessing Institutional Data Feed..."):
        df = get_market_data(str(date.today()))

    if not df.empty:
        # Metrics Overview
        m1, m2, m3 = st.columns(3)
        m1.metric("Market Assets", len(df))
        m2.metric("Top Opportunity", f"{df['ROI %'].max()}%")
        m3.metric("Status", "STABLE", delta="LIVE")

        tab1, tab2 = st.tabs(["🎯 ALPHA SIGNALS", "📊 MARKET ARCHIVE"])

        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            # اختيار أعلى 12 فرصة ربحية
            top_df = df[df['ROI %'] > 0].sort_values(by='ROI %', ascending=False).head(12)
            
            for i in range(0, len(top_df), 3):
                cols = st.columns(3)
                for idx, row in enumerate(top_df.iloc[i:i+3].to_dict(orient='records')):
                    with cols[idx]:
                        st.markdown(f"""
                        <div class="luxury-card">
                            <div style="display:flex; justify-content:space-between;">
                                <span style="font-weight:bold; letter-spacing:1px;">{row['Symbol']}</span>
                                <span style="color:#00ffaa; font-weight:bold;">+{row['ROI %']}%</span>
                            </div>
                            <div style="font-size:24px; font-weight:bold; margin:10px 0;">{row['Target']} <small style="font-size:12px; color:#555;">EGP</small></div>
                            <div style="color:#666; font-size:11px;">Current: {row['Price']} | RSI: {int(row['RSI'])}</div>
                        </div>
                        """, unsafe_allow_html=True)

        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            # عرض الجدول بطريقة ذكية وحديثة (تغني عن الـ Styler المعقد)
            st.dataframe(
                df,
                column_config={
                    "Symbol": "Ticker",
                    "Price": st.column_config.NumberColumn("LTP", format="%.2f"),
                    "Target": st.column_config.NumberColumn("Target", format="%.2f"),
                    "ROI %": st.column_config.ProgressColumn("Potential ROI", min_value=0, max_value=float(df['ROI %'].max()), format="%f%%"),
                    "RSI": st.column_config.NumberColumn("RSI", format="%d"),
                    "Volume": st.column_config.NumberColumn("Vol", format="%d")
                },
                hide_index=True,
                use_container_width=True,
                height=500
            )

    else:
        st.error("Data synchronization failed. Please refresh.")

    # Footer
    st.markdown(f"""
    <div style="text-align:center; padding:50px; color:#222; font-size:10px; letter-spacing:2px;">
        © 2024 {CORP_NAME} | PRIVATE & CONFIDENTIAL
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
