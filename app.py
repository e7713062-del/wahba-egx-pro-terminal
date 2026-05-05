import streamlit as st
from tradingview_ta import TA_Handler, Interval
import requests
from datetime import datetime
import pytz

# --- 1. الإعدادات الأساسية والوقت ---
egypt_tz = pytz.timezone('Africa/Cairo')
now = datetime.now(egypt_tz)
# اليوم الحالي لاتخاذ قرار المسح أو الحفظ في الذاكرة
today_key = now.strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba Elite Predictor", layout="wide")

# --- 2. ستايل الواجهة (التصميم الفاخر للماركتينج) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif; }
    .stApp { background-color: #000000; color: #ffffff; }
    
    .main-header {
        text-align: center; padding: 45px;
        background: radial-gradient(circle, #1a1a1a 0%, #000 100%);
        border-bottom: 2px solid #d4af37;
        margin-bottom: 40px;
    }
    .predict-card {
        background: #0a0a0a; border: 1px solid #1a1a1a;
        border-right: 8px solid #d4af37; border-radius: 15px;
        padding: 25px; margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.05);
    }
    .badge-tomorrow {
        background: #d4af37; color: #000; padding: 3px 12px;
        border-radius: 4px; font-size: 11px; font-weight: 900;
    }
    .price-text { font-size: 34px; font-weight: 900; color: #fff; margin: 10px 0; }
    .metric-row { display: flex; justify-content: space-between; margin-top: 15px; background: #111; padding: 10px; border-radius: 8px; }
    </style>
    
    <div class="main-header">
        <div style="letter-spacing: 4px; color: #d4af37; font-size: 12px; font-weight: bold;">PREDICTIVE ANALYTICS</div>
        <h1 style="margin-top:10px;">WAHBA <span style="color:#d4af37;">ELITE</span> PREDICTOR</h1>
        <p style="color:#555;">تحليل الإغلاق اليومي وتوقع القوة الشرائية للجلسة القادمة</p>
    </div>
""", unsafe_allow_html=True)

# --- 3. محرك التوقع الذكي (Closing-Based Predictor) ---

@st.cache_data(ttl=86400) # يحفظ النتائج لمدة 24 ساعة (دورة يومية كاملة)
def get_elite_predictions(date_str):
    try:
        # جلب الرموز أوتوماتيكياً
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=15).json()
        all_symbols = [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
        
        final_list = []
        for sym in all_symbols:
            try:
                handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=2)
                analysis = handler.get_analysis()
                ind = analysis.indicators
                
                # --- خوارزمية صعود "ثاني يوم" ---
                close = ind.get("close")
                high = ind.get("high")
                prev_high = ind.get("high[1]")
                adx = ind.get("ADX")
                rsi = ind.get("RSI")
                
                # المعايير:
                # 1. اختراق قمة الأمس (تأكيد المسار الصاعد).
                # 2. الإغلاق عند أعلى نقطة (يدل على جوع المشترين للصعود غداً).
                # 3. قوة اتجاه (ADX) تتجاوز 35 (زخم انفجاري).
                # 4. توصية شراء قوي من 26 مؤشر فني.
                
                is_bullish_close = close >= (high * 0.996) # أغلق عند القمة تماماً
                is_breakout = close > prev_high
                is_super_trend = adx > 35
                
                if is_bullish_close and is_breakout and is_super_trend and 55 < rsi < 72:
                    if "STRONG_BUY" in analysis.summary["RECOMMENDATION"]:
                        final_list.append({
                            "symbol": sym,
                            "price": round(close, 2),
                            "target": round(ind.get("Pivot.M.Classic.R2"), 2),
                            "power": round(adx, 1),
                            "rsi": round(rsi, 1)
                        })
            except: continue
        return final_list
    except: return []

# --- 4. عرض النتائج النهائية ---

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2534/2534348.png", width=50)
st.sidebar.title("النظام الذكي")
st.sidebar.write(f"📅 التاريخ: {today_key}")
if st.sidebar.button("🔄 تحديث يدوي للبيانات"):
    st.cache_data.clear()
    st.rerun()

with st.spinner("جاري تحليل الإغلاقات الرسمية وتوقع حركة الغد..."):
    results = get_elite_predictions(today_key)

if results:
    st.markdown(f"### 🛡️ أسهم النخبة المؤكدة (مرشحة لصعود الغد)")
    cols = st.columns(2)
    for idx, s in enumerate(results):
        with cols[idx % 2]:
            st.markdown(f"""
            <div class="predict-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:26px; font-weight:900; color:#d4af37;">{s['symbol']}</span>
                    <span class="badge-tomorrow">TARGET TOMORROW</span>
                </div>
                <div class="price-text">{s['price']} <span style="font-size:14px; color:#444;">EGP</span></div>
                <div style="color:#00ff00; font-weight:bold;">الهدف المتوقع: {s['target']} EGP 🎯</div>
                
                <div class="metric-row">
                    <div style="text-align:center;">
                        <span style="font-size:10px; color:#555; display:block;">قوة الاندفاع</span>
                        <span style="font-weight:bold;">{s['power']}</span>
                    </div>
                    <div style="text-align:center;">
                        <span style="font-size:10px; color:#555; display:block;">مؤشر الزخم</span>
                        <span style="font-weight:bold;">{s['rsi']}</span>
                    </div>
                    <div style="text-align:center;">
                        <span style="font-size:10px; color:#555; display:block;">الحالة</span>
                        <span style="color:#00ff00; font-weight:bold;">اختراق</span>
                    </div>
                </div>
                <br>
                <a href="https://www.tradingview.com/chart/?symbol=EGX:{s['symbol']}" target="_blank" style="text-decoration:none;">
                    <div style="text-align:center; padding:10px; border:1px solid #d4af37; color:#d4af37; border-radius:8px; font-size:13px;">
                        عرض التحليل المباشر ↗
                    </div>
                </a>
            </div>
            """, unsafe_allow_html=True)
else:
    st.warning("⚠️ لم يتم رصد أسهم حققت معايير 'نخبة النخبة' للغد بناءً على إغلاق اليوم. يفضل الانتظار خارج السوق.")

st.markdown("""
<div style="text-align:center; margin-top:50px; color:#333; font-size:11px; border-top:1px solid #111; padding-top:20px;">
    Wahba Predictor Engine v5.0 | All Rights Reserved © 2024
</div>
""", unsafe_allow_html=True)
