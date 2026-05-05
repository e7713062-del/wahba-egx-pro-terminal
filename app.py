import streamlit as st
from tradingview_ta import TA_Handler, Interval
import requests
import pandas as pd
from datetime import datetime
import pytz
import time

# ==========================================
# 1. الإعدادات الجوهرية (CORE SETTINGS)
# ==========================================
egypt_tz = pytz.timezone('Africa/Cairo')
now = datetime.now(egypt_tz)
today_str = now.strftime("%Y-%m-%d")

st.set_page_config(
    page_title="Wahba Intelligence Terminal",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. نظام التنسيق البصري (ADVANCED CSS)
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&family=Tajawal:wght@400;700;900&display=swap');
    
    :root {
        --primary-gold: #d4af37;
        --spike-red: #ff4b4b;
        --bg-dark: #050505;
    }
    
    * { font-family: 'Tajawal', sans-serif; }
    .stApp { background-color: var(--bg-dark); color: #ffffff; }
    
    /* Header Style */
    .main-terminal-header {
        text-align: center; padding: 50px 20px;
        background: linear-gradient(180deg, #111 0%, #000 100%);
        border-bottom: 2px solid var(--primary-gold);
        margin-bottom: 40px; border-radius: 0 0 30px 30px;
    }
    
    /* Card System */
    .elite-card {
        background: #0d0d0d; border: 1px solid #1a1a1a;
        border-radius: 15px; padding: 25px; margin-bottom: 20px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .elite-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(212, 175, 55, 0.1);
        border-color: var(--primary-gold);
    }
    
    /* Status Badges */
    .badge-spike { background: var(--spike-red); color: white; padding: 5px 15px; border-radius: 5px; font-weight: bold; font-size: 12px; }
    .badge-elite { background: var(--primary-gold); color: black; padding: 5px 15px; border-radius: 5px; font-weight: bold; font-size: 12px; }
    
    .price-large { font-family: 'Roboto Mono', monospace; font-size: 38px; font-weight: 700; color: #fff; }
    .target-box { background: rgba(0,255,0,0.05); padding: 10px; border-radius: 8px; border: 1px dashed #00ff00; color: #00ff00; font-weight: bold; }
    
    /* Animation */
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
    .live-dot { height: 10px; width: 10px; background-color: #00ff00; border-radius: 50%; display: inline-block; animation: pulse 2s infinite; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. محرك جلب البيانات الضخم (HEAVY DATA ENGINE)
# ==========================================

class MarketAnalyzer:
    def __init__(self):
        self.symbols = []
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.scan_url = "https://scanner.tradingview.com/egypt/scan"

    def get_all_symbols(self):
        """جلب كل الرموز النشطة من السوق المصري"""
        try:
            payload = {
                "filter": [{"left": "market_cap_basic", "operation": "nempty"}],
                "options": {"lang": "en"},
                "markets": ["egypt"],
                "symbols": {"query": {"types": []}, "tickers": []},
                "columns": ["name", "close", "volume", "change"],
                "sort": {"sortBy": "name", "sortOrder": "asc"}
            }
            response = requests.post(self.scan_url, json=payload, timeout=15)
            data = response.json()
            return [item['s'].split(':')[1] for item in data['data'] if not item['s'].split(':')[1].isdigit()]
        except Exception as e:
            st.error(f"خطأ في جلب بيانات السوق: {e}")
            return []

    @st.cache_data(ttl=86400)
    def run_full_analysis(_self, date_trigger):
        """المحرك الرئيسي لتحليل كل سهم على حدة"""
        symbols = _self.get_all_symbols()
        spike_results = []
        elite_results = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, sym in enumerate(symbols):
            try:
                status_text.text(f"🔍 فحص السهم {idx+1}/{len(symbols)}: {sym}")
                progress_bar.progress((idx + 1) / len(symbols))
                
                handler = TA_Handler(
                    symbol=sym,
                    screener="egypt",
                    exchange="EGX",
                    interval=Interval.INTERVAL_1_DAY,
                    timeout=5
                )
                analysis = handler.get_analysis()
                ind = analysis.indicators
                
                # --- البيانات الفنية ---
                data = {
                    "sym": sym,
                    "price": round(ind.get("close"), 2),
                    "vol_ratio": round(ind.get("volume") / ind.get("average_volume_10d"), 2) if ind.get("average_volume_10d") else 0,
                    "mfi": round(ind.get("MoneyFlow"), 1),
                    "rsi": round(ind.get("RSI"), 1),
                    "adx": round(ind.get("ADX"), 1),
                    "target_r1": round(ind.get("Pivot.M.Classic.R1"), 2),
                    "target_r2": round(ind.get("Pivot.M.Classic.R2"), 2),
                    "sma20": ind.get("SMA20"),
                    "bb_upper": ind.get("BB.upper")
                }

                # --- منطق التصنيف الاستراتيجي ---
                
                # 1. فلتر الطفرات (Spike) - شروط قوية جداً
                if data['vol_ratio'] > 1.5 and data['price'] > data['bb_upper'] and data['mfi'] > 60:
                    spike_results.append(data)
                
                # 2. فلتر نخبة النخبة (Elite) - شروط استقرار واتجاه صاعد
                elif data['price'] > data['sma20'] and 50 < data['rsi'] < 70 and data['adx'] > 25:
                    elite_results.append(data)
                    
            except:
                continue
                
        status_text.empty()
        progress_bar.empty()
        return spike_results, elite_results

# ==========================================
# 4. واجهة العرض النهائية (THE TERMINAL)
# ==========================================

# الهيدر
st.markdown(f"""
    <div class="main-terminal-header">
        <h2 style="color:var(--primary-gold); margin:0; letter-spacing:5px;">WAHBA INTELLIGENCE</h2>
        <h1 style="font-size:50px; margin:10px 0;">STRATEGIC <span style="color:var(--primary-gold);">TERMINAL</span></h1>
        <div style="font-size:14px; color:#666;">
            <span class="live-dot"></span> نظام الرصد الموحد | تحديث الإغلاق اليومي: {today_str}
        </div>
    </div>
""", unsafe_allow_html=True)

analyzer = MarketAnalyzer()
spikes, elites = analyzer.run_full_analysis(today_str)

# --- عرض النتائج ---

# الجزء الأول: الطفرات
st.markdown("### 🚨 رادار الطفرات السعرية (High Liquidity)")
if spikes:
    cols = st.columns(2)
    for idx, s in enumerate(spikes):
        with cols[idx % 2]:
            st.markdown(f"""
            <div class="elite-card" style="border-right: 8px solid var(--spike-red);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="symbol-name" style="color:var(--spike-red); font-size:28px; font-weight:900;">{s['sym']}</span>
                    <span class="badge-spike">طفرة مؤكدة</span>
                </div>
                <div class="price-large">{s['price']} <span style="font-size:14px; color:#444;">EGP</span></div>
                <div style="margin:15px 0;" class="target-box">🎯 الهدف الانفجاري: {s['target_r2']}</div>
                <div style="display:flex; justify-content:space-between; font-size:12px; color:#555; border-top:1px solid #1a1a1a; padding-top:10px;">
                    <span>مضاعف السيولة: x{s['vol_ratio']}</span>
                    <span>قوة التدفق MFI: {s['mfi']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("⚠️ لا يوجد أسهم طفرات حالياً طبقت المعايير الانفجارية. النظام في وضع المراقبة.")

st.write("")
st.write("---")
st.write("")

# الجزء الثاني: نخبة النخبة
st.markdown("### ⭐ قائمة نخبة النخبة (Stable Growth)")
if elites:
    cols = st.columns(3)
    for idx, e in enumerate(elites):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="elite-card" style="border-right: 8px solid var(--primary-gold);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <span style="font-weight:900; color:var(--primary-gold);">{e['sym']}</span>
                    <span class="badge-elite">نخبة</span>
                </div>
                <div style="font-size:24px; font-weight:bold;">{e['price']} EGP</div>
                <div style="color:#00ff00; font-size:14px; margin:10px 0;">الهدف الفني: {e['target_r1']}</div>
                <div style="font-size:11px; color:#444;">قوة الاتجاه ADX: {e['adx']}</div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.warning("حتى أسهم النخبة في حالة انتظار حالياً.")

# السايدبار
st.sidebar.title("🛠️ تحكم النظام")
st.sidebar.write("هذا النظام مصمم للاستقرار العالي ومعالجة البيانات الضخمة.")
if st.sidebar.button("🔄 إعادة تحليل السوق بالكامل"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.write("---")
st.sidebar.caption("Wahba Enterprise v9.0")
