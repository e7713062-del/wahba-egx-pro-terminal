import streamlit as st
from tradingview_ta import TA_Handler, Interval
import requests
from datetime import datetime
import pytz

# --- 1. إعدادات الهوية والوقت ---
egypt_tz = pytz.timezone('Africa/Cairo')
now = datetime.now(egypt_tz)
today_key = now.strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba Super-Spike Radar", layout="wide")

# --- 2. التصميم الفاخر (UI/UX) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif; }
    .stApp { background-color: #000; color: #fff; }
    
    .header-container {
        text-align: center; padding: 40px;
        background: linear-gradient(180deg, #1a0000 0%, #000 100%);
        border-bottom: 3px solid #ff4b4b; margin-bottom: 30px;
    }
    .spike-card {
        background: #0d0d0d; border: 1px solid #1a1a1a;
        border-right: 10px solid #ff4b4b; border-radius: 15px;
        padding: 25px; margin-bottom: 20px;
    }
    .price-val { font-size: 36px; font-weight: 900; color: #fff; }
    .badge-spike { background: #ff4b4b; color: white; padding: 4px 12px; border-radius: 50px; font-size: 11px; font-weight: bold; }
    .target-val { color: #00ff00; font-weight: bold; font-size: 20px; }
    </style>
    
    <div class="header-container">
        <div style="color:#ff4b4b; font-size:12px; letter-spacing:5px; font-weight:bold;">MARKET ANOMALY DETECTOR</div>
        <h1 style="margin:10px 0;">WAHBA <span style="color:#ff4b4b;">SPIKE</span> RADAR</h1>
        <p style="color:#666;">صيد طفرات السيولة والأسهم التي تسبح عكس التيار</p>
    </div>
""", unsafe_allow_html=True)

# --- 3. محرك صيد الطفرات المعتمد على الإغلاق (The Spike Engine) ---

@st.cache_data(ttl=86400) # تحليل يومي يعتمد على إغلاق الأمس لخطة عمل اليوم
def get_final_spikes(date_str):
    try:
        # جلب الرموز أوتوماتيكياً
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=15).json()
        all_symbols = [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
        
        spike_results = []
        for sym in all_symbols:
            try:
                handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=2)
                analysis = handler.get_analysis()
                ind = analysis.indicators
                
                # --- معادلة الطفرة (Spike Formula) ---
                close = ind.get("close")
                volume = ind.get("volume")
                avg_vol = ind.get("average_volume_10d")
                mfi = ind.get("MoneyFlow") # تدفق السيولة
                bb_upper = ind.get("BB.upper")
                
                # الشروط:
                # 1. سيولة انفجارية (أكبر من متوسط 10 أيام بـ 50% على الأقل).
                # 2. اختراق حدود الحركة الطبيعية (BB Upper).
                # 3. تدفق أموال إيجابي (MFI > 55).
                # 4. إغلاق إيجابي قوي.
                
                if (volume > (avg_vol * 1.5) and close > bb_upper and mfi > 55):
                    spike_results.append({
                        "sym": sym,
                        "price": round(close, 2),
                        "vol_ratio": round(volume / avg_vol, 1),
                        "mfi": round(mfi, 1),
                        "target": round(ind.get("Pivot.M.Classic.R3"), 2), # هدف الطفرة البعيد
                        "change": round(ind.get("change"), 2)
                    })
            except: continue
        return spike_results
    except: return []

# --- 4. العرض التشغيلي ---

# زر التحديث اليدوي في الجانب
if st.sidebar.button("🔄 تحديث الرادار الآن"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.info(f"تحليل الإغلاق ليوم: {today_key}")

with st.spinner("جاري فحص السيولة وتحديد الطفرات القادمة..."):
    final_picks = get_final_spikes(today_key)

if final_picks:
    st.markdown(f"### 🚨 تم رصد {len(final_picks)} طفرات سعرية مؤكدة")
    cols = st.columns(2)
    for idx, s in enumerate(final_picks):
        with cols[idx % 2]:
            st.markdown(f"""
            <div class="spike-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:28px; font-weight:900; color:#ff4b4b;">{s['sym']}</span>
                    <span class="badge-spike">سيولة ضخمة x{s['vol_ratio']}</span>
                </div>
                <div class="price-val">{s['price']} <span style="font-size:14px; color:#444;">EGP</span></div>
                <div style="margin:10px 0;">
                    الهدف الجنوني المتوقع: <span class="target-val">{s['target']} EGP</span>
                </div>
                <div style="display:flex; justify-content:space-between; margin-top:20px; font-size:12px; color:#555;">
                    <span>تدفق السيولة (MFI): {s['mfi']}</span>
                    <span>التغير: +{s['change']}%</span>
                </div>
                <br>
                <a href="https://www.tradingview.com/chart/?symbol=EGX:{s['sym']}" target="_blank" style="text-decoration:none;">
                    <div style="text-align:center; padding:12px; border:1px solid #ff4b4b; border-radius:8px; color:#ff4b4b; font-size:13px; font-weight:bold;">
                        تحليل الطفرة لحظياً ↗
                    </div>
                </a>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("رادار الطفرات في حالة تأهب. لا توجد سيولة غير طبيعية حالياً.")

st.markdown(f"""
    <div style="text-align:center; margin-top:50px; color:#222; font-size:10px; border-top:1px solid #111; padding-top:20px;">
        Wahba Spike Intelligence v6.0 | Closing Basis | Cairo Time: {now.strftime("%H:%M")}
    </div>
""", unsafe_allow_html=True)
