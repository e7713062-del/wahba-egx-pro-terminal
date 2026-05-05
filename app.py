import streamlit as st
from tradingview_ta import TA_Handler, Interval
import requests
from datetime import datetime
import pytz

# --- 1. إعدادات الوقت والهوية ---
egypt_tz = pytz.timezone('Africa/Cairo')
today_key = datetime.now(egypt_tz).strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba Elite Predictor", layout="wide")

# --- 2. التصميم الاحترافي (CSS Customization) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif; }
    .stApp { background-color: #000000; color: #ffffff; }
    
    .main-header {
        text-align: center; padding: 40px;
        background: radial-gradient(circle, #1a1a1a 0%, #000 100%);
        border-bottom: 2px solid #d4af37;
        margin-bottom: 30px;
    }
    .elite-card {
        background: #0d0d0d; border: 1px solid #1a1a1a;
        border-right: 8px solid #d4af37; border-radius: 15px;
        padding: 25px; margin-bottom: 20px;
        transition: 0.3s ease;
    }
    .elite-card:hover { border-color: #d4af37; transform: translateY(-5px); }
    
    .badge-gold { background: #d4af37; color: #000; padding: 3px 12px; border-radius: 4px; font-size: 11px; font-weight: 900; }
    .badge-silver { background: #333; color: #fff; padding: 3px 12px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    
    .price-text { font-size: 34px; font-weight: 900; color: #fff; margin: 10px 0; }
    .target-box { color: #00ff00; font-weight: bold; font-size: 18px; background: rgba(0,255,0,0.05); padding: 5px; border-radius: 5px; }
    </style>
    
    <div class="main-header">
        <div style="letter-spacing: 4px; color: #d4af37; font-size: 11px; font-weight: bold;">WAHBA INTELLIGENCE ALGO</div>
        <h1 style="margin-top:10px;">ELITE <span style="color:#d4af37;">PREDICTOR</span></h1>
        <p style="color:#666;">رادار الفرص الذهبية وتوقعات الجلسة القادمة</p>
    </div>
""", unsafe_allow_html=True)

# --- 3. محرك التحليل الهجين (Hybrid Prediction Engine) ---

@st.cache_data(ttl=86400)
def get_final_hybrid_picks(date_str):
    try:
        # جلب قائمة أسهم مصر
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=15).json()
        all_symbols = [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
        
        picks = []
        for sym in all_symbols:
            try:
                handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=2)
                analysis = handler.get_analysis()
                ind = analysis.indicators
                
                close = ind.get("close")
                high = ind.get("high")
                prev_high = ind.get("high[1]")
                adx = ind.get("ADX")
                rsi = ind.get("RSI")
                recommendation = analysis.summary["RECOMMENDATION"]

                # -- المستوى الأول: انفجار لثاني يوم (أولوية قصوى) --
                if (close >= (high * 0.995) and close > prev_high and adx > 30 and "STRONG_BUY" in recommendation):
                    label = "انفجار لثاني يوم 🚀"
                    badge = "badge-gold"
                    rank = 1
                
                # -- المستوى الثاني: نخبة النخبة (بديل قوي) --
                elif (close > ind.get("SMA50") and 55 < rsi < 72 and adx > 20 and "BUY" in recommendation):
                    label = "نخبة النخبة ✅"
                    badge = "badge-silver"
                    rank = 2
                else:
                    continue

                picks.append({
                    "sym": sym,
                    "price": round(close, 2),
                    "target": round(ind.get("Pivot.M.Classic.R2"), 2),
                    "adx": round(adx, 1),
                    "label": label,
                    "badge": badge,
                    "rank": rank
                })
            except: continue
            
        # ترتيب بحيث يظهر الـ Rank 1 (الانفجار) أولاً
        return sorted(picks, key=lambda x: x['rank'])
    except: return []

# --- 4. العرض النهائي للموقع ---

st.sidebar.title("⚙️ الإعدادات")
if st.sidebar.button("🔄 تحديث يدوي للبيانات"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.info(f"آخر تحديث للرادار: {today_key}")

# استدعاء البيانات
with st.spinner("جاري تحليل الإغلاقات الرسمية وتجهيز قائمة النخبة..."):
    final_results = get_final_hybrid_picks(today_key)

if final_results:
    st.markdown(f"### 🎯 فرص تم رصدها اليوم")
    cols = st.columns(2)
    for idx, s in enumerate(final_results):
        with cols[idx % 2]:
            st.markdown(f"""
            <div class="elite-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:26px; font-weight:900; color:#d4af37;">{s['sym']}</span>
                    <span class="{s['badge']}">{s['label']}</span>
                </div>
                <div class="price-text">{s['price']} <span style="font-size:14px; color:#444;">EGP</span></div>
                <div style="margin-top:10px;">
                    الهدف المتوقع القادم: <span class="target-box">{s['target']} EGP</span>
                </div>
                <div style="display:flex; justify-content:space-between; margin-top:20px; font-size:12px; color:#555;">
                    <span>قوة الاتجاه: {s['adx']}</span>
                    <span>الحالة: إغلاق إيجابي</span>
                </div>
                <br>
                <a href="https://www.tradingview.com/chart/?symbol=EGX:{s['sym']}" target="_blank" style="text-decoration:none;">
                    <div style="text-align:center; padding:10px; border:1px solid #333; border-radius:8px; color:#d4af37; font-size:12px;">
                        فتح الرسم البياني المتقدم 📈
                    </div>
                </a>
            </div>
            """, unsafe_allow_html=True)
else:
    st.error("لم يتم رصد فرص مطابقة لمعايير النخبة حالياً. يفضل الانتظار خارج السوق.")

st.markdown("""
<div style="text-align:center; margin-top:50px; color:#222; font-size:10px; border-top:1px solid #111; padding-top:20px;">
    Wahba Predictor Engine v5.1 | All Rights Reserved © 2024
</div>
""", unsafe_allow_html=True)
