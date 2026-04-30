import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz

# 1. إعدادات الصفحة والبراندنج
st.set_page_config(page_title="Wahba EGX Pro", layout="wide")

st.markdown("""
    <style>
    .main-header { text-align: center; color: #00ffcc; background: #111; padding: 20px; border-radius: 15px; border: 1px solid #333; }
    .stButton>button { background: #00ffcc; color: black; font-weight: bold; width: 100%; border-radius: 10px; height: 3.5em; font-size: 18px; }
    .report-box { background: #222; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #444; margin-bottom: 20px; }
    .stock-card { background: #1e1e1e; padding: 15px; border-radius: 10px; border-left: 5px solid #00ffcc; margin-bottom: 10px; }
    </style>
    <div class="main-header">
        <h1>WAHBA EGX TERMINAL</h1>
        <p style="opacity: 0.6;">نظام تحليل الإغلاق اليومي الذكي</p>
    </div>
""", unsafe_allow_html=True)

# 2. محرك جلب البيانات (مرة واحدة كل 12 ساعة)
@st.cache_data(ttl=43200) 
def get_daily_closing_report():
    url = "https://scanner.tradingview.com/egypt/scan"
    # طلب البيانات بناءً على التحليل الفني اليومي (Daily Timeframe)
    payload = {
        "filter": [{"left": "recommendation_all", "operation": "in_range", "right": [0.1, 5]}],
        "options": {"lang": "en"},
        "markets": ["egypt"],
        "columns": ["name", "close", "change", "RSI", "recommendation_all", "description"],
        "sort": {"sortBy": "recommendation_all", "sortOrder": "desc"},
        "range": [0, 500] # يغطي أي سهم جديد ينزل البورصة
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15).json()
        
        # ضبط التوقيت الصيفي/الشتوي تلقائياً
        cairo_tz = pytz.timezone('Africa/Cairo')
        now_cairo = datetime.now(cairo_tz)
        timestamp = now_cairo.strftime("%Y-%m-%d | %I:%M %p")
        
        return response.get('data', []), timestamp
    except:
        return None, None

# 3. واجهة المستخدم والتنفيذ
st.write("") # مسافة

if st.button("🚀 إصدار تقرير الخلاصة اليومية"):
    with st.spinner("جاري استخلاص الفرص الفنية..."):
        data, report_time = get_daily_closing_report()
        
        if data and report_time:
            # عرض وقت التقرير (ثابت طول الـ 12 ساعة)
            st.markdown(f"""
                <div class="report-box">
                    <span style="color: #888; font-size: 14px;">توقيت إصدار التقرير (توقيت القاهرة المحلي):</span><br>
                    <b style="color: #00ffcc; font-size: 20px;">{report_time}</b>
                </div>
            """, unsafe_allow_html=True)
            
            # عرض الأسهم التي حصلت على إشارة شراء
            for item in data:
                d = item['d']
                status = "شراء قوي 🔥" if d[4] >= 0.5 else "شراء 🟢"
                st.markdown(f"""
                <div class="stock-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 19px; font-weight: bold; color: #fff;">{d[0]}</span>
                        <span style="color: #00ffcc; font-weight: bold;">{status}</span>
                    </div>
                    <div style="color: #aaa; font-size: 14px; margin-top: 8px;">
                        السعر: <b>{d[1]:,.2f}</b> | 
                        التغير: <span style="color: {'#00ff00' if d[2] >= 0 else '#ff4b4b'};">{d[2]:+.2f}%</span> | 
                        RSI: {round(d[3], 2) if d[3] else 'N/A'}
                    </div>
                    <div style="font-size: 12px; color: #666; margin-top: 5px;">{d[5]}</div>
                </div>
                """, unsafe_allow_html=True)
                
            st.info("ملاحظة: هذا التقرير يعتمد على إغلاق شمعة اليوم ويتم تحديثه مرة واحدة كل جلسة.")
        else:
            st.error("السيرفر مشغول حالياً أو تحت الحماية. يرجى الانتظار دقيقة وإعادة المحاولة.")

st.markdown("<p style='text-align:center; font-size:10px; color:#444; margin-top:30px;'>Wahba EGX Smart Terminal v3.0</p>", unsafe_allow_html=True)
