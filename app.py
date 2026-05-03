import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
from datetime import datetime
import pytz

# --- 1. إعدادات الوقت والصفحة ---
egypt_tz = pytz.timezone('Africa/Cairo')
now_alex = datetime.now(egypt_tz)
today_key = now_alex.strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba Intelligence | Pro Terminal", layout="wide")

# --- 2. التصميم (Black & Gold Elite Design) ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    .main-header { 
        text-align: center; padding: 25px; border-bottom: 2px solid #ffd700; 
        background: linear-gradient(to bottom, #000, #111); margin-bottom: 30px;
    }
    .gold-box { 
        background: rgba(255, 215, 0, 0.05); border: 1px solid #ffd700; 
        padding: 20px; border-radius: 15px; margin-bottom: 20px;
    }
    .disclaimer {
        font-size: 13px; color: #888; text-align: justify;
        background: #0a0a0a; padding: 20px; border-radius: 15px;
        margin-top: 50px; border: 1px solid #222;
    }
    .star-rating { color: #ffd700; font-size: 20px; font-weight: bold; }
    .footer-name {
        color: #ffd700; font-size: 24px; font-weight: bold; 
        text-transform: uppercase; letter-spacing: 2px;
        margin-top: 10px; display: block;
    }
    </style>
    <div class="main-header">
        <h1 style="color:#ffd700; font-size: 40px; margin-bottom: 5px;">WAHBA <span style="color:#fff;">INTELLIGENCE</span> PRO</h1>
        <p style="color:#888; font-size: 16px;">Advanced Support & Resistance Analysis Terminal</p>
    </div>
""", unsafe_allow_html=True)

# --- 3. محرك التحليل الذكي (نخبة النخبة) ---

@st.cache_data(ttl=14400) # تحديث كل 4 ساعات لحماية البيانات
def run_full_market_scan(date_key):
    # قائمة الأسهم القيادية والنشطة في البورصة المصرية
    symbols = [
        "COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK", "MFOT", "ETEL", 
        "BTEL", "ESRS", "HELI", "ORAS", "AMOC", "CCAP", "SKPC", "PHDC"
    ] 
    results = []
    
    progress_text = "جاري فحص رادار نخبة النخبة... يرجى الانتظار"
    progress_bar = st.progress(0, text=progress_text)
    
    for i, symbol in enumerate(symbols):
        try:
            handler = TA_Handler(
                symbol=symbol,
                screener="egypt",
                exchange="EGX",
                interval=Interval.INTERVAL_1_DAY,
                timeout=10
            )
            analysis = handler.get_analysis()
            
            # جلب البيانات السعرية والمؤشرات
            close = analysis.indicators["close"]
            high = analysis.indicators["high"]
            low = analysis.indicators["low"]
            rsi = analysis.indicators["RSI"]
            rec = analysis.summary["RECOMMENDATION"]
            
            # حساب مستويات الدعم والمقاومة (Pivot Points)
            pivot = (high + low + close) / 3
            r1 = (2 * pivot) - low
            s1 = (2 * pivot) - high
            
            # خوارزمية النجوم (نخبة النخبة)
            score = 0
            if "BUY" in rec: score += 1
            if "STRONG_BUY" in rec: score += 1
            if 40 <= rsi <= 55: score += 2  # المنطقة الذهبية للدخول
            if close > s1: score += 1      # تأكيد الارتكاز فوق الدعم
            
            stars = "⭐" * score if score > 0 else "🌑"
            
            results.append({
                "السهم": symbol,
                "السعر الحالي": round(close, 2),
                "الدعم (S1)": round(s1, 2),
                "المقاومة (R1)": round(r1, 2),
                "التقييم": stars,
                "RSI": round(rsi, 2),
                "التوصية": rec,
                "score_num": score
            })
        except Exception as e:
            continue
        finally:
            progress_bar.progress((i + 1) / len(symbols))
            
    progress_bar.empty()
    return pd.DataFrame(results)

# --- 4. واجهة المستخدم والتنفيذ ---

if st.button('🚀 إطلاق رادار نخبة النخبة وتحديد الأهداف', use_container_width=True):
    df = run_full_market_scan(today_key)
    
    if not df.empty:
        # استخراج أفضل سهمين (النخبة)
        golden = df.sort_values(by="score_num", ascending=False).head(2)
        
        st.markdown("<div class='gold-box'><h2>💎 ترشيحات نخبة النخبة لجلسة الغد</h2></div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        for col, (_, row) in zip([col1, col2], golden.iterrows()):
            with col:
                st.markdown(f"""
                    <div style="background:#111; padding:25px; border-radius:15px; border:2px solid #ffd700; position:relative;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h2 style="color:#ffd700; margin:0;">{row['السهم']}</h2>
                            <span class="star-rating">{row['التقييم']}</span>
                        </div>
                        <h3 style="color:#fff; margin-top:10px;">السعر الحالي: {row['السعر الحالي']} ج.م</h3>
                        <hr style="border-color:#222; margin:15px 0;">
                        <p style="color:#00ff00; font-size:18px; margin-bottom:5px;"><b>🟢 نقطة الدخول (دعم): {row['الدعم (S1)']}</b></p>
                        <p style="color:#ff4b4b; font-size:18px; margin-bottom:5px;"><b>🔴 نقطة الهدف (مقاومة): {row['المقاومة (R1)']}</b></p>
                        <p style="font-size:14px; color:#666;">مؤشر القوة النسبية RSI: {row['RSI']}</p>
                    </div>
                """, unsafe_allow_html=True)

        st.divider()
        st.markdown("### 📊 جدول التحليل الفني الشامل")
        st.dataframe(
            df[['السهم', 'السعر الحالي', 'الدعم (S1)', 'المقاومة (R1)', 'التقييم', 'التوصية', 'RSI']], 
            use_container_width=True, 
            hide_index=True
        )
    else:
        st.error("فشل في جلب البيانات، يرجى المحاولة مرة أخرى لاحقاً.")

# --- 5. إخلاء المسؤولية وحقوق المطور (الاسم بالكامل) ---
st.markdown(f"""
    <div class="disclaimer">
        <strong>⚠️ إخلاء مسؤولية قانوني:</strong><br>
        هذا النظام أداة برمجية للتحليل الرقمي تعتمد على خوارزميات فنية (RSI, ADX, Pivot Points). 
        كل ما يظهر من أرقام وتوقعات هو لغرض الاسترشاد الفني فقط وليس توصية مباشرة بالشراء أو البيع. 
        البورصة تنطوي على مخاطر، وقرارك المالي هو مسؤوليتك الشخصية. المصمم غير مسؤول عن أي نتائج استثمارية.
        <br><br>
        <div style='text-align:center; border-top: 1px solid #333; padding-top: 20px;'>
            <span style='color:#888; font-size: 14px;'>تم التطوير والبرمجة بواسطة المهندس</span><br>
            <span class="footer-name">MOSTAFA TAMER WAHBA</span><br>
            <span style='color:#ffd700; font-size: 12px; opacity: 0.8;'>WAHBA INTELLIGENCE SYSTEMS © 2026</span>
        </div>
    </div>
""", unsafe_allow_html=True)
