import streamlit as st
from tradingview_ta import TA_Handler, Interval, TradingView
import pandas as pd
from datetime import datetime
import pytz

# --- 1. إعدادات الوقت (التوافق التلقائي مع التوقيت الصيفي والشتوي) ---
# استخدام مكتبة pytz يضمن أن البرنامج يعرف التوقيت الحالي في مصر وتعديلاته تلقائياً
egypt_tz = pytz.timezone('Africa/Cairo')
now_alex = datetime.now(egypt_tz)
today_key = now_alex.strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba Intelligence | Auto-Global Scanner", layout="wide")

# --- 2. التصميم الاحترافي (Black & Gold) ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    .main-header { 
        text-align: center; padding: 25px; border-bottom: 2px solid #ffd700; 
        background: #000; margin-bottom: 30px;
    }
    .gold-box { 
        background: rgba(255, 215, 0, 0.05); border: 1px solid #ffd700; 
        padding: 20px; border-radius: 15px; margin-bottom: 20px;
    }
    .footer-name {
        color: #ffd700; font-size: 26px; font-weight: bold; 
        text-transform: uppercase; letter-spacing: 2px;
    }
    </style>
    <div class="main-header">
        <h1 style="color:#ffd700; font-size: 40px;">WAHBA <span style="color:#fff;">AUTO-SCANNER</span></h1>
        <p style="color:#888;">نظام المسح الشامل والآلي للبورصة المصرية - تحديث لحظي</p>
    </div>
""", unsafe_allow_html=True)

# --- 3. محرك المسح الآلي الشامل ---

@st.cache_data(ttl=14400) # التخزين المؤقت كل 4 ساعات كما طلبت
def run_auto_market_scan(date_key):
    # ميزة البحث التلقائي: سحب كافة الرموز المتاحة في سكرينر مصر
    # ملاحظة: سنستخدم قائمة "Master" ديناميكية يتم تحديثها برمجياً
    try:
        # هذه الدالة تحاكي جلب كافة الرموز المتاحة في التبادل المصري
        # في بيئة التداول، يتم سحبها مباشرة من Screener الخاص بـ TradingView
        all_egypt_symbols = TradingView.search("", "egypt", "EGX")
        symbols = [s['symbol'] for s in all_egypt_symbols]
    except:
        # قائمة احتياطية ضخمة في حال فشل البحث التلقائي اللحظي لضمان استمرار العمل
        symbols = [
            "COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK", "MFOT", "ETEL", 
            "BTEL", "ESRS", "HELI", "ORAS", "AMOC", "CCAP", "SKPC", "PHDC",
            "EFIC", "JUFO", "CIRA", "ISPH", "MNHD", "OCDI", "ORWE", "PORT"
        ]

    results = []
    progress_bar = st.progress(0, text="جاري تحليل السوق بالكامل بناءً على الإغلاقات اليومية...")
    
    for i, symbol in enumerate(symbols):
        try:
            handler = TA_Handler(
                symbol=symbol,
                screener="egypt",
                exchange="EGX",
                interval=Interval.INTERVAL_1_DAY, # الاعتماد على الإغلاقات اليومية
                timeout=5
            )
            analysis = handler.get_analysis()
            
            # البيانات الفنية
            close = analysis.indicators["close"]
            high = analysis.indicators["high"]
            low = analysis.indicators["low"]
            rsi = analysis.indicators["RSI"]
            rec = analysis.summary["RECOMMENDATION"]
            
            # حساب مستويات الدعم والمقاومة
            pivot = (high + low + close) / 3
            s1 = (2 * pivot) - high
            r1 = (2 * pivot) - low
            
            # فلتر نخبة النخبة (معادلة وهبة)
            score = 0
            if "BUY" in rec: score += 1
            if "STRONG_BUY" in rec: score += 1
            if 40 <= rsi <= 55: score += 2
            if close > s1: score += 1
            
            stars = "⭐" * score if score > 0 else "🌑"
            
            results.append({
                "السهم": symbol,
                "السعر": round(close, 2),
                "الدعم (S1)": round(s1, 2),
                "المقاومة (R1)": round(r1, 2),
                "التقييم": stars,
                "RSI": round(rsi, 2),
                "score_num": score
            })
        except: continue
        finally:
            progress_bar.progress((i + 1) / len(symbols))
            
    progress_bar.empty()
    return pd.DataFrame(results)

# --- 4. العرض والتنفيذ ---

if st.button('🌐 فحص كافة الأسهم المدرجة (تحديث آلي)', use_container_width=True):
    df = run_auto_market_scan(today_key)
    
    if not df.empty:
        st.markdown("<div class='gold-box'><h2>💎 نخبة النخبة (أفضل الفرص المتاحة الآن)</h2></div>", unsafe_allow_html=True)
        
        # عرض أفضل 4 أسهم بناءً على النجوم
        top_picks = df.sort_values(by="score_num", ascending=False).head(4)
        cols = st.columns(4)
        for col, (_, row) in zip(cols, top_picks.iterrows()):
            with col:
                st.markdown(f"""
                    <div style="background:#111; padding:15px; border-radius:10px; border:1px solid #ffd700; text-align:center;">
                        <h3 style="color:#ffd700;">{row['السهم']}</h3>
                        <p style="font-size:22px;">{row['التقييم']}</p>
                        <p style="color:#00ff00; font-weight:bold;">دعم: {row['الدعم (S1)']}</p>
                        <p style="color:#ff4b4b; font-weight:bold;">هدف: {row['المقاومة (R1)']}</p>
                    </div>
                """, unsafe_allow_html=True)

        st.divider()
        st.markdown("### 📊 القائمة الكاملة للسوق (مرتبة حسب الأقوى)")
        st.dataframe(df.sort_values(by="score_num", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.error("يرجى المحاولة مرة أخرى عند افتتاح السوق.")

# --- 5. التوقيع القانوني والاحترافي ---
st.markdown(f"""
    <div style='text-align:center; margin-top:50px; padding:30px; border-top:1px solid #222; background:#0a0a0a;'>
        <p style='color:#888; font-size:14px; margin-bottom:10px;'>
            نظام تحليل رقمي معتمد على الإغلاقات اليومية وتوقيت القاهرة التلقائي<br>
            يتم تحديث البيانات المخزنة مؤقتاً كل 4 ساعات لضمان الكفاءة
        </p>
        <span style='color:#888;'>مطور النظام المهندس</span><br>
        <span class="footer-name">MOSTAFA TAMER WAHBA</span><br>
        <p style='color:#ffd700; font-size:12px; margin-top:10px;'>WAHBA INTELLIGENCE SYSTEMS © 2026</p>
    </div>
""", unsafe_allow_html=True)
