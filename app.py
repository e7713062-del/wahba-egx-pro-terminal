import streamlit as st
from tradingview_ta import TA_Handler, Interval
import requests
from datetime import datetime
import pytz

# --- 1. إعدادات الوقت والهوية ---
egypt_tz = pytz.timezone('Africa/Cairo')
now = datetime.now(egypt_tz)
today_key = now.strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba Ultimate Radar", layout="wide", initial_sidebar_state="expanded")

# --- 2. التصميم الفاخر (Ultimate UI) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif; }
    .stApp { background-color: #050505; color: #ffffff; }
    
    .main-title {
        text-align: center; padding: 60px 20px;
        background: radial-gradient(circle at center, #2b0000 0%, #000 70%);
        border-bottom: 4px solid #ff4b4b; margin-bottom: 40px;
        border-radius: 0 0 50px 50px;
    }
    
    .card-container {
        background: linear-gradient(145deg, #0f0f0f, #1a1a1a);
        border: 1px solid #333; border-radius: 20px;
        padding: 30px; margin-bottom: 25px;
        position: relative; overflow: hidden;
        transition: all 0.4s ease;
    }
    .card-container:hover {
        border-color: #ff4b4b; transform: translateY(-10px);
        box-shadow: 0 10px 30px rgba(255, 75, 75, 0.1);
    }
    
    .spike-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
    .symbol-name { font-size: 32px; font-weight: 900; color: #ff4b4b; }
    .price-tag { font-size: 40px; font-weight: 900; color: #fff; margin-bottom: 10px; }
    
    .status-badge {
        background: #ff4b4b; color: white; padding: 5px 15px;
        border-radius: 50px; font-size: 12px; font-weight: bold;
        box-shadow: 0 0 15px rgba(255, 75, 75, 0.4);
    }
    
    .metric-box {
        background: rgba(255,255,255,0.03); border-radius: 12px;
        padding: 15px; text-align: center; border: 1px solid #222;
    }
    .target-label { color: #00ff00; font-size: 22px; font-weight: bold; }
    
    /* Progress Bar */
    .strength-bar {
        height: 8px; width: 100%; background: #222;
        border-radius: 10px; margin: 15px 0; overflow: hidden;
    }
    .strength-fill { height: 100%; background: #ff4b4b; }
    </style>
    
    <div class="main-title">
        <h3 style="color:#ff4b4b; letter-spacing:8px; margin-bottom:10px;">WAHBA INTELLIGENCE</h3>
        <h1 style="font-size:50px; margin:0;">ULTIMATE <span style="color:#ff4b4b;">RADAR</span></h1>
        <p style="color:#888; font-size:18px; margin-top:15px;">النظام الشامل لصيد الطفرات والسيولة المؤسسية في البورصة المصرية</p>
    </div>
""", unsafe_allow_html=True)

# --- 3. محرك التحليل العميق (The Ultimate Engine) ---

@st.cache_data(ttl=86400)
def get_ultimate_spikes(date_str):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=15).json()
        all_symbols = [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
        
        results = []
        for sym in all_symbols:
            try:
                # فحص الفريم اليومي (الإغلاق)
                handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=2)
                analysis = handler.get_analysis()
                ind = analysis.indicators
                
                # --- متغيرات السيولة والاتجاه ---
                close = ind.get("close")
                vol = ind.get("volume")
                avg_vol_10 = ind.get("average_volume_10d")
                mfi = ind.get("MoneyFlow")
                rsi = ind.get("RSI")
                adx = ind.get("ADX")
                
                # حساب قوة الطفرة (من 100)
                vol_score = min((vol / avg_vol_10) * 20, 50) # قوة السيولة (50%)
                trend_score = min(adx, 50) # قوة الاتجاه (50%)
                total_strength = int(vol_score + trend_score)
                
                # --- الفلتر الذكي الشامل ---
                # 1. سيولة أعلى بـ 10% (حساسية عالية).
                # 2. السعر فوق المقاومة الأولى R1 (تأكيد الاختراق).
                # 3. تدفق أموال إيجابي MFI > 45.
                # 4. السعر فوق المتوسط المتحرك 20 (SMA20) لضمان الأمان.
                
                if (vol > (avg_vol_10 * 1.1) and close > ind.get("Pivot.M.Classic.R1") and mfi > 45 and close > ind.get("SMA20")):
                    results.append({
                        "sym": sym,
                        "price": round(close, 2),
                        "strength": total_strength,
                        "vol_ratio": round(vol / avg_vol_10, 1),
                        "target1": round(ind.get("Pivot.M.Classic.R2"), 2),
                        "target2": round(ind.get("Pivot.M.Classic.R3"), 2),
                        "mfi": round(mfi, 1),
                        "adx": round(adx, 1),
                        "change": round(ind.get("change"), 2)
                    })
            except: continue
        return sorted(results, key=lambda x: x['strength'], reverse=True)
    except: return []

# --- 4. العرض والتشغيل ---

st.sidebar.markdown(f"### 🛡️ لوحة التحكم")
st.sidebar.write(f"تاريخ التقرير: `{today_key}`")
if st.sidebar.button("💥 تحديث وتحليل السوق الآن"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.write("---")
st.sidebar.markdown("""
**دليل الرادار:**
* **السيولة:** تتبع دخول الأموال الذكية.
* **القوة:** مقياس من 100 لفرصة الانفجار.
* **الأهداف:** مستويات المقاومة القادمة.
""")

with st.spinner("🚀 جاري تشغيل المحرك العميق وفحص السيولة..."):
    final_picks = get_ultimate_spikes(today_key)

if final_picks:
    st.markdown(f"### 📡 تم رصد {len(final_picks)} فرصة طفرة مؤكدة")
    
    for s in final_picks:
        st.markdown(f"""
        <div class="card-container">
            <div class="spike-header">
                <span class="symbol-name">{s['sym']}</span>
                <span class="status-badge">سيولة حيتان x{s['vol_ratio']}</span>
            </div>
            
            <div style="display: flex; gap: 40px; align-items: center; flex-wrap: wrap;">
                <div>
                    <div class="price-tag">{s['price']} <span style="font-size:16px; color:#666;">EGP</span></div>
                    <div style="color:{'#00ff00' if s['change'] > 0 else '#ff4b4b'}; font-weight:bold;">
                        التغير اليومي: {s['change']}% {'▲' if s['change'] > 0 else '▼'}
                    </div>
                </div>
                
                <div style="flex-grow: 1;">
                    <div style="display:flex; justify-content:space-between; font-size:14px; color:#aaa;">
                        <span>مقياس الانفجار السعري</span>
                        <span>{s['strength']}%</span>
                    </div>
                    <div class="strength-bar">
                        <div class="strength-fill" style="width: {s['strength']}%"></div>
                    </div>
                </div>
                
                <div style="display: flex; gap: 20px;">
                    <div class="metric-box">
                        <div style="font-size:10px; color:#555;">الهدف الأول</div>
                        <div class="target-label">{s['target1']}</div>
                    </div>
                    <div class="metric-box">
                        <div style="font-size:10px; color:#555;">الهدف الذهبي</div>
                        <div class="target-label" style="color:#d4af37;">{s['target2']}</div>
                    </div>
                </div>
            </div>
            
            <div style="margin-top:20px; display:flex; gap:30px; border-top:1px solid #222; padding-top:15px; font-size:12px; color:#555;">
                <span>تدفق السيولة (MFI): <b>{s['mfi']}</b></span>
                <span>قوة الاتجاه (ADX): <b>{s['adx']}</b></span>
                <span style="margin-left:auto;">الحالة: <b>إغلاق إيجابي مخترق</b></span>
            </div>
            
            <div style="margin-top:20px; text-align:right;">
                <a href="https://www.tradingview.com/chart/?symbol=EGX:{s['sym']}" target="_blank" style="text-decoration:none; color:#ff4b4b; font-weight:bold;">
                    فتح الشارت الاحترافي 🔍
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="text-align:center; padding:100px; color:#444;">
        <h2>الرادار في وضع السكون 🛰️</h2>
        <p>لا توجد طفرات مكتملة الشروط حالياً. النظام يراقب الإغلاقات لحظة بلحظة.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"<div style='text-align:center; color:#222; padding:40px;'>Wahba Ultimate v8.0 | {now.strftime('%Y')}</div>", unsafe_allow_html=True)
