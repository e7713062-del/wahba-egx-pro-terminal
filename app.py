import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
import yfinance as yf

# 1. إعدادات الصفحة
st.set_page_config(page_title="Wahba EGX Pro", layout="wide")

st.markdown("""
    <style>
    .main-header { text-align: center; color: #00ffcc; background: #111; padding: 20px; border-radius: 15px; border: 1px solid #333; }
    .stButton>button { background: #00ffcc; color: black; font-weight: bold; width: 100%; border-radius: 10px; height: 3.5em; }
    .stock-card { background: #1e1e1e; padding: 15px; border-radius: 10px; border-left: 5px solid #00ffcc; margin-bottom: 10px; }
    </style>
    <div class="main-header">
        <h1>WAHBA EGX TERMINAL</h1>
        <p style="opacity: 0.6;">نظام التحليل المزدوج (TradingView + yfinance)</p>
    </div>
""", unsafe_allow_html=True)

# قائمة احتياطية لأهم الأسهم في حال استخدام yfinance
BACKUP_STOCKS = ['COMI.CA', 'FWRY.CA', 'TMGH.CA', 'SWDY.CA', 'ABUK.CA', 'EAST.CA', 'TALM.CA', 'ESRS.CA']

@st.cache_data(ttl=43200)
def get_combined_report():
    cairo_tz = pytz.timezone('Africa/Cairo')
    report_time = datetime.now(cairo_tz).strftime("%Y-%m-%d | %I:%M %p")
    results = []
    source = ""

    # المحاولة الأولى: TradingView (لجلب كل الأسهم والجديد منها)
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {
            "filter": [{"left": "recommendation_all", "operation": "in_range", "right": [0.1, 5]}],
            "markets": ["egypt"],
            "columns": ["name", "close", "change", "description"],
            "range": [0, 500]
        }
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code == 200:
            data = res.json().get('data', [])
            for item in data:
                d = item['d']
                results.append({"Ticker": d[0], "Price": d[1], "Change": d[2], "Desc": d[3]})
            source = "TradingView (Live Scan)"
    except:
        pass

    # المحاولة الثانية: لو النتائج فاضية (حصل بلوك)، ادخل على yfinance
    if not results:
        source = "yfinance (Backup Server)"
        for symbol in BACKUP_STOCKS:
            try:
                t = yf.Ticker(symbol)
                h = t.history(period="2d")
                if len(h) >= 2:
                    cp = h['Close'].iloc[-1]
                    pc = h['Close'].iloc[-2]
                    ch = ((cp - pc) / pc) * 100
                    results.append({"Ticker": symbol.replace('.CA',''), "Price": cp, "Change": ch, "Desc": ""})
            except:
                continue
                
    return results, report_time, source

st.write("")

if st.button("🚀 إصدار تقرير الإغلاق الذكي"):
    with st.spinner("جاري الاتصال بأسرع سيرفر متاح..."):
        data, r_time, r_source = get_combined_report()
        
        if data:
            st.info(f"المصدر الحالي: {r_source} | التوقيت: {r_time}")
            for item in data:
                color = "#00ff00" if item['Change'] >= 0 else "#ff4b4b"
                st.markdown(f"""
                <div class="stock-card">
                    <b style="color: #00ffcc; font-size: 18px;">{item['Ticker']}</b>
                    <div style="color: #bbb; margin-top: 5px;">
                        السعر: {item['Price']:.2f} | التغير: <span style="color: {color};">{item['Change']:+.2f}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("جميع السيرفرات مشغولة حالياً، يرجى المحاولة بعد قليل.")

st.caption("Wahba EGX | Hybrid Data Engine")
