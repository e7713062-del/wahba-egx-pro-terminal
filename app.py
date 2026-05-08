import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import numpy as np
import requests
import os
from datetime import datetime
import pytz

# ==========================================
# 1. الإعدادات العامة والثوابت
# ==========================================
EGYPT_TZ = pytz.timezone('Africa/Cairo')
TODAY_STR = datetime.now(EGYPT_TZ).strftime("%Y-%m-%d")
DB_FILE = f"wahba_egx_data_{TODAY_STR}.csv"

# ==========================================
# 2. محرك التحليل الفني (Wahba Engine)
# ==========================================
class WahbaEngineV3:
    @staticmethod
    def calculate_logic(df):
        """حساب الأهداف الفنية بناءً على مستويات البيفوت وفيوناتشي"""
        if df.empty:
            return df
            
        # حساب الهدف: نقطة الارتكاز + (المقاومة الأولى - الارتكاز) * 1.618
        df['Target'] = np.round(df['P'] + (df['R1'] - df['P']) * 1.618, 2)
        
        # حساب وقف الخسارة: أقل من الدعم الأول بـ 1%
        df['StopLoss'] = np.round(df['S1'] * 0.99, 2)
        
        # حساب العائد المتوقع نسبة مئوية
        df['ROI'] = np.round(((df['Target'] - df['Price']) / df['Price']) * 100, 1)
        
        return df

def fetch_market_data():
    """جلب وتحليل بيانات الأسهم من TradingView"""
    
    # محاولة جلب البيانات من الملف المحلي أولاً (كاش لليوم الحالي)
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)

    try:
        # 1. جلب قائمة الرموز المتاحة في البورصة المصرية
        scanner_url = "https://scanner.tradingview.com/egypt/scan"
        payload = {
            "filter": [{"left": "market_cap_basic", "operation": "nempty"}],
            "markets": ["egypt"],
            "columns": ["name"]
        }
        response = requests.post(scanner_url, json=payload, timeout=15).json()
        symbols = [item['s'].split(':')[1] for item in response['data'] if ":" in item['s']]
    except Exception as e:
        st.error(f"خطأ في الاتصال بالسيرفر: {e}")
        return pd.DataFrame()

    results = []
    
    # 2. تحليل كل سهم على حدة (تم رفع العدد لـ 50 سهم)
    progress_bar = st.progress(0)
    for i, sym in enumerate(symbols[:50]):
        try:
            handler = TA_Handler(
                symbol=sym,
                screener="egypt",
                exchange="EGX",
                interval=Interval.INTERVAL_1_DAY,
                timeout=10
            )
            analysis = handler.get_analysis()
            indicators = analysis.indicators
            
            # استخراج المؤشرات الأساسية
            close_price = indicators.get("close")
            p_point = indicators.get("Pivot.M.Classic.Middle") or indicators.get("Pivot.M.Traditional.Middle")
            s1_level = indicators.get("Pivot.M.Classic.S1") or indicators.get("Pivot.M.Traditional.S1")
            r1_level = indicators.get("Pivot.M.Classic.R1") or indicators.get("Pivot.M.Traditional.R1")
            rsi = indicators.get("RSI")

            if None in [close_price, p_point, s1_level, r1_level]:
                continue

            # نظام النقاط (Scoring System)
            score = 0
            rec = analysis.summary["RECOMMENDATION"]
            
            if "BUY" in rec: score += 5
            if "STRONG_BUY" in rec: score += 3
            if rsi and 45 <= rsi <= 65: score += 2  # منطقة قوة شرائية متزنة

            results.append({
                "Symbol": sym,
                "Price": round(close_price, 2),
                "Score": score,
                "S1": s1_level,
                "P": p_point,
                "R1": r1_level
            })
        except:
            continue
        
        progress_bar.progress((i + 1) / 50)

    # 3. معالجة البيانات النهائية
    df = pd.DataFrame(results)
    if not df.empty:
        df = WahbaEngineV3.calculate_logic(df)
        df.to_csv(DB_FILE, index=False)
    
    return df

# ==========================================
# 3. واجهة المستخدم (Streamlit UI)
# ==========================================
st.set_page_config(page_title="WAHBA EGX PRO", layout="wide", initial_sidebar_state="expanded")

# تصميم CSS احترافي وواسع
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
        text-align: right;
    }
    
    .main-title {
        color: #d4af37;
        text-align: center;
        font-size: 3rem;
        font-weight: 900;
        margin-bottom: 30px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    .stock-card {
        background: linear-gradient(145deg, #121212, #1a1a1a);
        border: 1px solid #2d2d2d;
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 25px;
        transition: transform 0.3s;
    }
    
    .stock-card:hover {
        transform: translateY(-5px);
        border-color: #d4af37;
    }
    
    .symbol-name { font-size: 28px; color: #d4af37; font-weight: bold; }
    .price-tag { font-size: 20px; color: #ffffff; }
    .stop-loss-tag { background: #441111; color: #ff4b4b; padding: 5px 15px; border-radius: 5px; font-weight: bold; }
    .target-container {
        background: #000;
        border: 1px solid #00ff00;
        border-radius: 10px;
        padding: 15px;
        margin-top: 15px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">WAHBA EGX | النسخة الاحترافية</h1>', unsafe_allow_html=True)

# القائمة الجانبية
with st.sidebar:
    st.header("لوحة التحكم")
    if st.button("🔄 تحديث شامل للسوق"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        st.rerun()
    st.info("البيانات يتم تحديثها بناءً على إغلاق الفريم اليومي.")

# تشغيل المحرك
market_df = fetch_market_data()

if not market_df.empty:
    # فلترة أفضل الفرص (Score >= 7)
    top_picks = market_df[market_df['Score'] >= 7].sort_values(by="Score", ascending=False)
    
    if top_picks.empty:
        st.warning("⚠️ لا توجد أسهم تحقق شروط الدخول القوية حالياً. انتظر إشارات أفضل.")
    else:
        # عرض البيانات في أعمدة (2 في كل صف)
        cols = st.columns(2)
        for i, (idx, row) in enumerate(top_picks.iterrows()):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="stock-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="symbol-name">{row['Symbol']}</span>
                        <span class="stop-loss-tag">وقف: {row['StopLoss']}</span>
                    </div>
                    <hr style="border-color: #333;">
                    <div class="price-tag">السعر الحالي: <b>{row['Price']} ج.م</b></div>
                    <div class="target-container">
                        <div style="color: #aaa; font-size: 14px;">الهدف الفني القادم</div>
                        <div style="font-size: 32px; color: #00ff00; font-weight: bold;">{row['Target']}</div>
                        <div style="color: #00ff00;">نسبة صعود متوقعة: {row['ROI']}%</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
else:
    st.error("تعذر جلب البيانات. تأكد من أنك متصل بالإنترنت وأن منصة TradingView تعمل.")
