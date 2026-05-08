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
# 1. IDENTITY & CONFIG
# ==========================================
CORP_NAME = "WAHBA QUANTITATIVE SOLUTIONS"
FOUNDER = "MUSTAFA TAMER"
GOLD_COLOR = "#D4AF37"
ACCENT_GREEN = "#00FFAA"

# إعداد الصفحة
st.set_page_config(page_title=CORP_NAME, layout="wide")

# ==========================================
# 2. DATABASE ENGINE (للحفظ التلقائي الدائم)
# ==========================================
def init_db():
    conn = sqlite3.connect('market_archive.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS signals 
                 (date TEXT, symbol TEXT, price REAL, target REAL, roi REAL, rsi REAL)''')
    conn.commit()
    conn.close()

def save_to_db(df, current_date):
    conn = sqlite3.connect('market_archive.db')
    # التأكد أننا لا نحفظ بيانات نفس اليوم مرتين
    existing_data = pd.read_sql(f"SELECT * FROM signals WHERE date='{current_date}'", conn)
    if existing_data.empty:
        df['date'] = current_date
        df.to_sql('signals', conn, if_exists='append', index=False)
    conn.close()

def get_history_from_db():
    if os.path.exists('market_archive.db'):
        conn = sqlite3.connect('market_archive.db')
        df = pd.read_sql("SELECT * FROM signals ORDER BY date DESC", conn)
        conn.close()
        return df
    return pd.DataFrame()

# ==========================================
# 3. DATA FETCHING (التنفيذ التلقائي)
# ==========================================
@st.cache_data(ttl=3600)
def fetch_and_process_daily():
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {"filter": [{"left": "market_cap_basic", "operation": "nempty"}],
                   "markets": ["egypt"], "columns": ["name"]}
        res = requests.post(url, json=payload, timeout=15).json()
        symbols = [i['s'].split(':')[1] for i in res['data'][:70] if ":" in i['s']]
        
        results = []
        def process(s):
            try:
                h = TA_Handler(symbol=s, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=7)
                ind = h.get_analysis().indicators
                p, r1 = ind.get("Pivot.M.Classic.Middle", 0), ind.get("Pivot.M.Classic.R1", 0)
                if p == 0: return None
                target = np.round(p + (r1 - p) * 1.618, 2)
                roi = np.round(((target - ind["close"]) / ind["close"]) * 100, 2)
                return {"symbol": s, "price": ind["close"], "target": target, "roi": roi, "rsi": ind.get("RSI", 0)}
            except: return None

        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(filter(None, executor.map(process, symbols)))
        
        df = pd.DataFrame(results)
        return df
    except:
        return pd.DataFrame()

# ==========================================
# 4. LUXURY UI CSS
# ==========================================
st.markdown(f"""
<style>
    [data-testid="stAppViewContainer"] {{ background-color: #050505; color: #eee; font-family: sans-serif; }}
    .header-box {{ border-bottom: 1px solid #1A1A1A; padding: 20px 0; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: center; }}
    .status-badge {{ display: flex; align-items: center; background: rgba(0, 255, 170, 0.1); padding: 5px 15px; border-radius: 50px; border: 1px solid {ACCENT_GREEN}; }}
    .status-dot {{ height: 10px; width: 10px; background-color: {ACCENT_GREEN}; border-radius: 50%; display: inline-block; margin-right: 10px; box-shadow: 0 0 10px {ACCENT_GREEN}; animation: pulse 2s infinite; }}
    @keyframes pulse {{ 0% {{ opacity: 0.5; }} 50% {{ opacity: 1; }} 100% {{ opacity: 0.5; }} }}
    .signal-card {{ background: #0F0F0F; border: 1px solid #222; padding: 20px; border-radius: 5px; border-left: 3px solid {GOLD_COLOR}; }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 5. MAIN APP
# ==========================================
def main():
    init_db()
    today_str = str(date.today())

    # Header
    st.markdown(f"""
    <div class="header-box">
        <div>
            <h1 style="margin:0; color:white;">WAHBA <span style="color:{GOLD_COLOR};">PLATINUM</span></h1>
            <p style="margin:0; color:#555; font-size:12px;">AUTOMATED QUANTITATIVE ARCHIVE | {FOUNDER}</p>
        </div>
        <div class="status-badge">
            <span class="status-dot"></span>
            <span style="color:{ACCENT_GREEN}; font-size:12px; font-weight:bold;">AUTO-SYNC ACTIVE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # المزامنة والحفظ التلقائي
    with st.spinner("Processing daily closures and archiving..."):
        df_today = fetch_and_process_daily()
        if not df_today.empty:
            save_to_db(df_today, today_str)

    # عرض البيانات
    tab1, tab2, tab3 = st.tabs(["🎯 TODAY'S SIGNALS", "📂 HISTORICAL ARCHIVE", "⚙️ SYSTEM"])

    with tab1:
        if not df_today.empty:
            st.markdown("<br>", unsafe_allow_html=True)
            top = df_today.sort_values(by='roi', ascending=False).head(12)
            for i in range(0, len(top), 3):
                cols = st.columns(3)
                for idx, row in enumerate(top.iloc[i:i+3].to_dict(orient='records')):
                    with cols[idx]:
                        st.markdown(f"""
                        <div class="signal-card">
                            <div style="display:flex; justify-content:space-between;"><b>{row['symbol']}</b> <span style="color:{ACCENT_GREEN}">+{row['roi']}%</span></div>
                            <div style="font-size:28px; font-weight:bold; margin:10px 0;">{row['target']} <small style="font-size:12px;">EGP</small></div>
                            <div style="color:#444; font-size:11px;">RSI: {int(row['rsi'])} | LTP: {row['price']}</div>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.warning("Waiting for market data...")

    with tab2:
        st.markdown("### 🏛️ Full Market Database")
        history_df = get_history_from_db()
        if not history_df.empty:
            # فلتر لاختيار التاريخ
            available_dates = history_df['date'].unique()
            selected_date = st.selectbox("Select Trading Session", available_dates)
            filtered_history = history_df[history_df['date'] == selected_date]
            st.dataframe(filtered_history, use_container_width=True, hide_index=True)
        else:
            st.info("Archive is empty. Database will grow every day after market close.")

    with tab3:
        st.info(f"Database File: market_archive.db\nLocation: {os.getcwd()}\nStatus: Operational")
        if st.button("Clear Cache"):
            st.cache_data.clear()
            st.rerun()

if __name__ == "__main__":
    main()
