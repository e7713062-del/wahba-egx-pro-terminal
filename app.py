import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import numpy as np
import requests
from datetime import datetime, date
from concurrent.futures import ThreadPoolExecutor

# ==========================================
# 1. CORP CONFIG
# ==========================================
CORP_NAME = "WAHBA QUANTITATIVE SOLUTIONS"
FOUNDER = "MUSTAFA TAMER"
VERSION = "INSTITUTIONAL v7.0.0 (Daily Archive Mode)"

# ==========================================
# 2. SMART STORAGE ENGINE (الحل الجوهري)
# ==========================================

# استخدام الـ Cache لحفظ البيانات على مستوى السيرفر وليس فقط جلسة المستخدم
@st.cache_data(ttl=86400) # التخزين لمدة 24 ساعة (يوم كامل)
def get_daily_market_data(_last_update_date):
    """
    هذه الدالة ستعمل مرة واحدة فقط في اليوم. 
    أول مستخدم يدخل سيقوم النظام بعمل سكان، والباقي سيشاهدون النتائج المحفوظة.
    """
    try:
        # 1. جلب الرموز
        scanner_url = "https://scanner.tradingview.com/egypt/scan"
        payload = {"filter": [{"left": "market_cap_basic", "operation": "nempty"}],
                   "markets": ["egypt"], "columns": ["name"]}
        res = requests.post(scanner_url, json=payload, timeout=10).json()
        symbols = [i['s'].split(':')[1] for i in res['data'] if ":" in i['s']]
        
        results = []
        
        # 2. جلب البيانات (بالتوازي لتوفير الوقت في أول مرة فقط)
        def fetch(s):
            try:
                h = TA_Handler(symbol=s, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=2)
                ind = h.get_analysis().indicators
                return {"Symbol": s, "Price": ind["close"], "P": ind["Pivot.M.Classic.Middle"], "R1": ind["Pivot.M.Classic.R1"]}
            except: return None

        with ThreadPoolExecutor(max_workers=20) as executor:
            results = list(filter(None, executor.map(fetch, symbols)))
            
        df = pd.DataFrame(results)
        df['Update_Date'] = str(date.today())
        return df
    except Exception as e:
        return pd.DataFrame()

# ==========================================
# 3. INTERFACE & LOGIC
# ==========================================
st.set_page_config(page_title=CORP_NAME, layout="wide")

# CSS لإعطاء مظهر احترافي للمنصة
st.markdown("""
<style>
    .stApp { background: #050505; color: #ffffff; }
    .status-tag { background: #1a1a1a; padding: 5px 15px; border-radius: 50px; font-size: 12px; color: #D4AF37; border: 1px solid #D4AF37; }
    .card { background: #0f0f0f; border: 1px solid #1e1e1e; padding: 20px; border-radius: 10px; transition: 0.3s; }
    .card:hover { border-color: #D4AF37; background: #151515; }
    .price-tag { color: #00ffaa; font-size: 24px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

def main():
    # التحقق من تاريخ اليوم
    today_str = str(date.today())
    
    # Header
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; padding: 20px 0; border-bottom: 1px solid #222;">
        <div>
            <h1 style="margin:0; color:#D4AF37;">WAHBA PRO TERMINAL</h1>
            <p style="margin:0; color:#666;">Institutional Analysis Engine | Founder: {FOUNDER}</p>
        </div>
        <div class="status-tag">● SYSTEM STATUS: STABLE</div>
    </div>
    """, unsafe_allow_html=True)

    # جلب البيانات (ستعمل فقط لو التاريخ تغير أو أول مرة)
    with st.spinner("Synchronizing with Egyptian Exchange Daily Closures..."):
        df_daily = get_daily_market_data(today_str)

    if not df_daily.empty:
        # حسابات الأهداف (تتم في الذاكرة فوراً)
        df_daily['Target'] = np.round(df_daily['P'] + (df_daily['R1'] - df_daily['P']) * 1.618, 2)
        df_daily['ROI'] = np.round(((df_daily['Target'] - df_daily['Price']) / df_daily['Price']) * 100, 1)
        
        # عرض البيانات
        tab1, tab2 = st.tabs(["🎯 Top Signals", "📊 Full Market Sheet"])
        
        with tab1:
            st.markdown(f"### 🚀 High Potential Signals - {today_str}")
            top_hits = df_daily.sort_values(by='ROI', ascending=False).head(12)
            
            cols = st.columns(3)
            for idx, row in enumerate(top_hits.to_dict(orient='records')):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="card">
                        <div style="display:flex; justify-content:space-between;">
                            <b style="font-size:18px;">{row['Symbol']}</b>
                            <span style="color:#888;">{today_str}</span>
                        </div>
                        <div style="margin:15px 0;">
                            <small style="color:#555;">DAILY PROJECTION</small>
                            <div class="price-tag">{row['Target']} EGP</div>
                        </div>
                        <div style="display:flex; justify-content:space-between;">
                            <span style="color:#00ffaa;">+{row['ROI']}% ROI</span>
                            <span style="color:#444;">Last: {row['Price']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")

        with tab2:
            st.markdown("### 📋 Full Market Archive (Read-Only)")
            st.dataframe(df_daily, use_container_width=True, height=600)
    else:
        st.error("Unable to sync data. Please check your connection.")

    # Footer للبراندينج
    st.markdown(f"""
    <div style="text-align:center; padding:50px; color:#333; font-size:12px;">
        COPYRIGHT © 2024 {CORP_NAME} | ALL RIGHTS RESERVED<br>
        DATA REFRESHES AUTOMATICALLY EVERY 24 HOURS
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
