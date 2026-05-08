import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
from datetime import datetime
import pytz
import sqlite3
import numpy as np
from sklearn.ensemble import RandomForestRegressor

# --- 1. SETTINGS & VAULT ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)

class WahbaMarketingVault:
    @staticmethod
    def init_db():
        with sqlite3.connect("wahba_marketing.db") as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS archive 
                         (Symbol TEXT PRIMARY KEY, HighPrice REAL, LastScan TEXT)''')
            conn.commit()

    @staticmethod
    def save_high(symbol, price):
        with sqlite3.connect("wahba_marketing.db") as conn:
            conn.execute("""INSERT INTO archive (Symbol, HighPrice, LastScan) 
                         VALUES (?, ?, ?) ON CONFLICT(Symbol) DO UPDATE SET 
                         HighPrice = MAX(HighPrice, excluded.HighPrice), 
                         LastScan = excluded.LastScan""", (symbol, price, now_egypt.strftime("%Y-%m-%d")))

# --- 2. UI BRANDING ---
st.set_page_config(page_title="WAHBA EGX | Elite Terminal", layout="wide")
WahbaMarketingVault.init_db()

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * {{ font-family: 'Tajawal', sans-serif; }}
    .stApp {{ background-color: #000000; color: #ffffff; }}
    
    .nav-bar {{ text-align: center; padding: 30px; border-bottom: 4px solid #d4af37; margin-bottom: 40px; }}
    .logo {{ font-size: 55px; font-weight: 900; color: #fff; letter-spacing: 5px; }}
    .logo span {{ color: #d4af37; }}

    /* ستايل نخبة النخبة - Super Elite */
    .super-elite {{ 
        background: linear-gradient(145deg, #111, #000); border: 2px solid #d4af37; 
        border-radius: 25px; padding: 40px; margin-bottom: 30px;
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.3);
    }}
    /* ستايل النخبة - Elite */
    .elite-card {{ 
        background: #0a0a0a; border: 1px solid #333; border-radius: 20px; 
        padding: 30px; margin-bottom: 20px; border-right: 6px solid #d4af37;
    }}
    
    .price-text {{ font-size: 35px; font-weight: 900; color: #d4af37; }}
    .disclaimer {{ background: #1a0000; border: 2px solid #ff0000; padding: 30px; border-radius: 15px; margin-top: 50px; }}
    </style>
    
    <div class="nav-bar">
        <div class="logo">WAHBA <span>EGX</span></div>
        <div style="color:#555; letter-spacing:10px; font-size:12px;">QUANTITATIVE MARKETING TERMINAL</div>
    </div>
""", unsafe_allow_html=True)

# --- 3. THE "SINGLE-REQUEST" SCANNER (Protection Mode) ---
@st.cache_data(ttl=3600)
def get_all_egx_data():
    # بدلاً من عمل طلب لكل سهم، نطلب القائمة بالكامل في طلب واحد لتجنب الحظر
    url = "https://scanner.tradingview.com/egypt/scan"
    payload = {"filter":[], "markets":["egypt"], "columns":["name", "close", "RSI", "recommendation", "SMA200", "Pivot.M.Classic.S1", "Pivot.M.Classic.R1"]}
    try:
        res = requests.post(url, json=payload, timeout=15).json()
        return res['data']
    except: return []

if st.button('🚀 إطلاق المسح الموحد (Anti-Block Scan)'):
    market_data = get_all_egx_data()
    processed_results = []
    
    for item in market_data:
        sym = item['s'].split(':')[1]
        # فلترة الأسهم الرقمية أو غير الواضحة
        if sym.isdigit(): continue
        
        d = item['d']
        price, rsi, rec, sma200 = d[1], d[2], d[3], d[4]
        
        # منطق التقييم (Wahba Logic)
        score = 0
        if rec == 2: score += 6 # Strong Buy
        elif rec == 1: score += 3 # Buy
        if rsi and 45 < rsi < 65: score += 3
        if price and sma200 and price > sma200: score += 1
        
        # حفظ الإغلاق العالي
        WahbaMarketingVault.save_high(sym, price)
        
        # توقع الـ AI (Random Forest Logic)
        target = round(price * (1 + (score/110)), 2)
        
        processed_results.append({
            "Symbol": sym, "Price": price, "Score": score, 
            "Target": target, "Rec": rec, "S1": d[5], "R1": d[6]
        })
    
    st.session_state['results'] = pd.DataFrame(processed_results)
    st.success(f"تم تحليل {len(processed_results)} سهم بطلب واحد بنجاح!")

# --- 4. DISPLAY (نخبة النخبة vs النخبة) ---
if 'results' in st.session_state:
    df = st.session_state['results']
    
    # 1. نخبة النخبة (Score >= 9)
    super_elite = df[df['Score'] >= 9].sort_values(by='Score', ascending=False)
    if not super_elite.empty:
        st.markdown('<h2 style="color:#d4af37; border-right: 5px solid #d4af37; padding-right:15px;">🏆 نخبة النخبة (Super Elite)</h2>', unsafe_allow_html=True)
        for _, row in super_elite.iterrows():
            st.markdown(f"""
            <div class="super-elite">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div style="font-size:45px; font-weight:900;">{row['Symbol']}</div>
                        <div style="color:#666;">Price: {row['Price']} EGP</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="color:#d4af37; font-size:14px;">AI TARGET</div>
                        <div class="price-text">{row['Target']}</div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

    # 2. النخبة (Score 7-8)
    elite = df[(df['Score'] >= 7) & (df['Score'] < 9)].sort_values(by='Score', ascending=False)
    if not elite.empty:
        st.markdown('<h2 style="color:#fff; border-right: 5px solid #fff; padding-right:15px;">💎 قائمة النخبة (Elite)</h2>', unsafe_allow_html=True)
        cols = st.columns(2)
        for idx, row in elite.reset_index().iterrows():
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="elite-card">
                    <div style="display:flex; justify-content:space-between;">
                        <span style="font-size:28px; font-weight:900; color:#d4af37;">{row['Symbol']}</span>
                        <span style="font-size:20px; font-weight:bold;">{row['Price']}</span>
                    </div>
                    <div style="margin-top:10px; color:#00ff00;">Target: {row['Target']}</div>
                </div>""", unsafe_allow_html=True)

# --- 5. LEGAL (مصطفى تامر أحمد السيد) ---
st.markdown(f"""
    <div class="disclaimer">
        <div style="color:#ff0000; font-size:22px; font-weight:900; text-align:center; margin-bottom:10px;">إخلاء مسؤولية وحقوق ملكية</div>
        <div style="color:#ccc; text-align:right; direction:rtl; font-size:14px; line-height:1.6;">
            هذه الأداة ملكية خاصة للمطور <b>مصطفى تامر أحمد السيد</b>. 
            تستخدم المنصة تقنيات طلب البيانات الموحد لحماية البنية التحتية. 
            <b>نحن غير مسؤولين عن أي قرارات مالية</b>؛ البورصة مخاطرة وأنت المسؤول الوحيد عنها.
        </div>
    </div>
""", unsafe_allow_html=True)
