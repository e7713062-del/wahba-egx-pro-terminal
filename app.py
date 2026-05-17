import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
from datetime import datetime
import pytz

# --- 1. إعدادات الوقت والهوية ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)
today_key = now_egypt.strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba Intelligence", layout="wide", initial_sidebar_state="collapsed")

# --- 2. التصميم المؤسسي المطور ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
* { font-family: 'Tajawal', sans-serif; }
.stApp { background-color: #000000; color: #ffffff; }
.nav-bar { text-align: center; padding: 25px; background: linear-gradient(180deg, #111 0%, #000 100%); border-bottom: 2px solid #d4af37; margin-bottom: 30px; }
.logo-text { font-size: 35px; font-weight: 900; color: #fff; letter-spacing: 2px; }
.logo-text span { color: #d4af37; }
.section-header { color: #d4af37; border-right: 5px solid #d4af37; padding-right: 15px; margin: 40px 0 20px 0; font-size: 24px; font-weight: bold; text-align: right; background: rgba(212, 175, 55, 0.05); padding: 10px; }
.stock-card { background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 15px; padding: 25px; margin-bottom: 10px; border-top: 3px solid #d4af37; transition: 0.3s; }
.stock-card:hover { border-color: #fff; background: #111; }
.symbol-name { font-size: 28px; font-weight: 900; color: #d4af37; }
.price-val { font-size: 24px; font-weight: bold; color: #fff; }
.trade-tag { background: #1a1a1a; color: #d4af37; padding: 4px 12px; border-radius: 6px; font-size: 13px; border: 1px solid #d4af37; margin-right: 10px; font-weight: bold; }
.stButton>button { background: #d4af37 !important; color: #000 !important; font-weight: 900 !important; border-radius: 10px !important; height: 50px !important; width: 100% !important; border: none !important; transition: 0.3s; }
.stButton>button:hover { background: #fff !important; transform: scale(1.02); }
.footer-box { margin-top: 80px; padding: 40px; text-align: center; border-top: 1px solid #1a1a1a; color: #666; font-size: 13px; }
/* تحسين عرض الـ Metrics */
[data-testid="stMetricValue"] { color: #fff !important; font-size: 18px !important; }
[data-testid="stMetricLabel"] { color: #d4af37 !important; }
</style>

<div class="nav-bar">
    <div class="logo-text">WAHBA <span>INTELLIGENCE</span></div>
    <p style="color:#666; font-size:12px; margin-top:5px;">PREMIUM ALGORITHMIC TRADING TERMINAL</p>
</div>
""", unsafe_allow_html=True)

# --- 3. محرك البيانات الاستراتيجي ---
@st.cache_data(ttl=86400)
def fetch_egx_list(date_key):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        payload = {"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}
        res = requests.post(url, json=payload, timeout=15).json()
        # تصفية الرموز لضمان الحصول على أسماء الشركات فقط
        return sorted(list(set([item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()])))
    except:
        return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK", "ETEL", "AMOC", "HRHO", "ESRS"]

@st.cache_data(ttl=3600, show_spinner=False)
def run_strategic_scan(date_key):
    symbols = fetch_egx_list(date_key)
    results = []
    
    status_text = st.empty()
    p_bar = st.progress(0)
    
    for i, sym in enumerate(symbols):
        try:
            status_text.text(f"جاري تحليل: {sym}...")
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=10)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            rec = analysis.summary["RECOMMENDATION"]
            
            # خوارزمية تسجيل النقاط (Scoring Algorithm القديم)
            score = 0
            if "STRONG_BUY" in rec: score += 5
            elif "BUY" in rec: score += 3
            
            rsi = ind.get("RSI")
            if rsi and 45 <= rsi <= 65: score += 3 # منطقة تجميع مثالية
            
            close = ind.get("close")
            pivot = ind.get("Pivot.M.Classic.Middle")
            if close and pivot and close > pivot: score += 2
            
            # تحديد نوع التداول بناءً على السيولة والتذبذب
            vol = ind.get("volume")
            avg_vol = ind.get("average_volume_10d")
            vol_ratio = (vol / avg_vol) if (vol and avg_vol) else 1
            change = ind.get("change") or 0
            
            t_type = "⚡ DAY TRADING" if (vol_ratio > 1.4 or abs(change) > 3) else "🌊 SWING"
            
            # --- تعديل الحساسية الذكي (Early Trend) بدون حذف أو تعديل القديم ---
            if close and pivot and rsi and vol_ratio:
                # 1. حساسية الـ RSI: لقط الأسهم اللي بتلف من تحت (بين 40 و 60)
                is_fresh_rsi = 40 <= rsi <= 60
                # 2. حساسية الارتكاز: السهم لسه قريب من الارتكاز (أعلى منه بـ 2% أو تحتيه بـ 1%) بيجمع عزم
                is_crossing_pivot = (pivot * 0.99) <= close <= (pivot * 1.02)
                # 3. حساسية السيولة: الفوليوم بدأ يسخن أعلى من المعتاد (أكبر من 1.05)
                is_volume_heating = vol_ratio > 1.05
                
                # إذا تحقق شرطين من الثلاثة، السهم ده حساسيته عالية ومبشر
                if (is_fresh_rsi and is_crossing_pivot) or (is_fresh_rsi and is_volume_heating):
                    score += 2  # إضافة مرنة لرفع الترتيب
                    t_type = "🚀 EARLY TREND"
            
            results.append({
                "Symbol": sym, "Price": close, "Score": score,
                "S1": ind.get("Pivot.M.Classic.S1"), "S2": ind.get("Pivot.M.Classic.S2"),
                "P": pivot, "R1": ind.get("Pivot.M.Classic.R1"),
                "R2": ind.get("Pivot.M.Classic.R2"), "Signal": rec.replace("_", " "), "Type": t_type
            })
        except: continue
        p_bar.progress((i + 1) / len(symbols))
        
    p_bar.empty()
    status_text.empty()
    return pd.DataFrame(results)

# --- 4. وظائف العرض ---
def display_stock_card(row):
    with st.container():
        st.markdown(f"""
        <div class="stock-card">
            <div style="display:flex; justify-content:space-between; align-items:center; direction: rtl;">
                <div>
                    <span class="symbol-name">{row['Symbol']}</span> 
                    <span class="trade-tag">{row['Type']}</span>
                </div>
                <div style="text-align: left;">
                    <div style="color:#d4af37; font-weight:900; font-size:18px;">{row['Signal']}</div>
                    <div style="color:#666; font-size:12px;">SCORE: {row['Score']}/10</div>
                </div>
            </div>
            <div class="price-val" style="text-align: right; margin-top:15px;">
                {row['Price']:.2f} <span style="font-size:14px; color:#666;">EGP</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # مؤشر القوة داخل النطاق السعري
        if pd.notnull(row['S2']) and pd.notnull(row['R2']) and row['R2'] > row['S2']:
            val = max(0, min(100, ((row['Price'] - row['S2']) / (row['R2'] - row['S2'])) * 100))
            st.markdown(f"<div style='text-align:right; font-size:11px; color:#d4af37; margin-bottom:5px;'>القوة الشرائية داخل النطاق</div>", unsafe_allow_html=True)
            st.progress(int(val))
        
        cols = st.columns(4)
        cols[0].metric("S1 (دعم)", f"{row['S1']:.2f}" if pd.notnull(row['S1']) else "N/A")
        cols[1].metric("Pivot (ارتكاز)", f"{row['P']:.2f}" if pd.notnull(row['P']) else "N/A")
        cols[2].metric("R1 (مقاومة)", f"{row['R1']:.2f}" if pd.notnull(row['R1']) else "N/A")
        cols[3].metric("R2 (هدف)", f"{row['R2']:.2f}" if pd.notnull(row['R2']) else "N/A")
        st.markdown("<div style='margin-bottom:30px;'></div>", unsafe_allow_html=True)

# --- 5. منطق التشغيل ---
st.write(f"📅 **تاريخ التقرير:** {today_key} | 🕒 **توقيت القاهرة:** {now_egypt.strftime('%H:%M')}")

col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    if st.button('🚀 تحديث وتحليل بيانات السوق الآن'):
        with st.spinner("جاري فحص الخوارزميات..."):
            st.session_state.final_report = run_strategic_scan(today_key)

if 'final_report' in st.session_state:
    df = st.session_state.final_report
    
    if not df.empty:
        # ترتيب النتائج حسب النتيجة الأعلى
        df = df.sort_values(by="Score", ascending=False)

        # التصنيف الأول: النخبة
        t1 = df[df['Score'] >= 8]
        if not t1.empty:
            st.markdown('<div class="section-header">⚜️ أسهم النخبة (إشارات قوية)</div>', unsafe_allow_html=True)
            for _, row in t1.iterrows(): display_stock_card(row)

        # التصنيف الثاني: المراقبة
        t2 = df[(df['Score'] >= 5) & (df['Score'] < 8)]
        if not t2.empty:
            st.markdown('<div class="section-header">💎 أسهم تحت المراقبة (إشارات إيجابية)</div>', unsafe_allow_html=True)
            for _, row in t2.iterrows(): display_stock_card(row)

        # التصنيف الثالث: السوق العام
        t3 = df[df['Score'] < 5]
        if not t3.empty:
            with st.expander("📊 استعراض باقي تحركات السوق"):
                for _, row in t3.iterrows(): display_stock_card(row)
    else:
        st.error("لم يتم العثور على بيانات. يرجى المحاولة لاحقاً.")

st.markdown("""
<div class="footer-box">
    <p style="font-weight:bold; color:#d4af37; letter-spacing:1px;">WAHBA INTELLIGENCE • INSTITUTIONAL DIVISION</p>
    <p>تحذير مخاطر: المعلومات المقدمة هي تحليل رقمي فني ولا تعتبر توصية مباشرة بالشراء أو البيع.</p>
    <p>© 2026 جميع الحقوق محفوظة</p>
</div>
""", unsafe_allow_html=True)
