import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import numpy as np
import requests
import os
from datetime import datetime
import pytz

# --- الإعدادات الفنية (الطبخة السرية v4.0) ---
egypt_tz = pytz.timezone('Africa/Cairo')
today_date = datetime.now(egypt_tz).strftime("%Y-%m-%d")
INTERNAL_DB = f"w_egx_gold_{today_date}.log"

# تخصيص واجهة ستريمليت وتعيين الثيم الداكن افتراضياً
st.set_page_config(page_title="WAHBA EGX GOLD", layout="wide", initial_sidebar_state="collapsed")

class WahbaEngineGold:
    @staticmethod
    def calculate_logic(df):
        # حساب الهدف بناءً على امتداد فيبوناتشي الذهبي 1.618
        df['Target'] = np.round(df['P'] + (df['R1'] - df['P']) * 1.618, 2)
        # وقف الخسارة الديناميكي (أسفل الدعم الأول بـ 1%)
        df['StopLoss'] = np.round(df['S1'] * 0.99, 2)
        # حساب العائد المتوقع
        df['ROI'] = np.round(((df['Target'] - df['Price']) / df['Price']) * 100, 1)
        return df

def run_wahba_engine():
    # التحقق من وجود بيانات مخزنة لليوم
    if os.path.exists(INTERNAL_DB):
        try:
            return pd.read_csv(INTERNAL_DB)
        except:
            pass

    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=10).json()
        all_syms = [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except:
        return pd.DataFrame()

    results = []
    # التركيز على أول 20 سهم لسرعة التحميل وضمان جودة الفرص
    for s in all_syms[:20]:
        try:
            h = TA_Handler(symbol=s, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=7)
            analysis = h.get_analysis()
            ind = analysis.indicators
            
            sc = 0
            rec = analysis.summary["RECOMMENDATION"]
            rsi = ind.get("RSI", 50)
            mfi = ind.get("MFI", 50)
            
            # نظام تقييم احترافي (الخلاصة)
            if "STRONG_BUY" in rec: sc += 5
            elif "BUY" in rec: sc += 3
            
            if 45 <= rsi <= 60: sc += 3 # منطقة ارتداد ذهبية
            if mfi > 60: sc += 2 # دخول سيولة
            
            results.append({
                "Symbol": s, 
                "Price": round(ind.get("close"), 2), 
                "Score": sc,
                "S1": round(ind.get("Pivot.M.Classic.S1"), 2),
                "P": round(ind.get("Pivot.M.Classic.Middle"), 2),
                "R1": round(ind.get("Pivot.M.Classic.R1"), 2)
            })
        except: continue
    
    df = pd.DataFrame(results)
    if not df.empty:
        df = WahbaEngineGold.calculate_logic(df)
        df.to_csv(INTERNAL_DB, index=False)
    return df

# --- تصميم الواجهة الذهبية الملكية (CSS) ---
# يجب وضع صورة خلفية باسم bkg.png في نفس المجلد للحصول على النقش الفرعوني
bkg_img = "bkg.png"
if os.path.exists(bkg_img):
    bkg_css = f"url(data:image/png;base64,{st.image(bkg_img).base64}) repeat"
else:
    bkg_css = "#000" # بديل أسود سادة إذا لم توجد الصورة

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    
    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* الخلفية المنقوشة وتصفير الهوامش */
    .stApp {{
        background: {bkg_css};
        background-size: 200px;
        color: #fff;
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
    }}
    
    /* حاوية المحتوى الرئيسي لجعلها بحدود واضحة */
    .main .block-container {{
        padding: 10px;
        max-width: 500px; /* تضييق المساحة لتشبه الموبايل في الصورة */
        margin: auto;
    }}

    /* ترويسة الصفحة */
    .header-bar {{
        text-align: center;
        background: rgba(0,0,0,0.8);
        padding: 15px;
        border-bottom: 2px solid #d4af37;
        margin-bottom: 15px;
        border-radius: 0 0 15px 15px;
    }}
    .brand {{
        font-size: 24px;
        font-weight: 900;
        letter-spacing: 2px;
        color: #fff;
    }}
    .gold-text {{ color: #d4af37; }}
    
    /* الزر الذهبي الكبير */
    .stButton>button {{
        background: linear-gradient(180deg, #fceabb 0%, #fccd4d 50%, #f8b500 100%) !important;
        color: #000 !important;
        font-weight: 900 !important;
        width: 100% !important;
        border: 2px solid #b8860b !important;
        height: 55px !important;
        font-size: 18px !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.5);
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 10px rgba(212, 175, 55, 0.4);
    }}

    /* تصميم الكارت الذهبي */
    .card-gold {{
        background: #000;
        border: 2px solid #d4af37;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 20px;
        position: relative;
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.2);
    }}
    /* الإطار المزدوج الداخلي */
    .card-gold::after {{
        content: '';
        position: absolute;
        top: 5px; left: 5px; right: 5px; bottom: 5px;
        border: 1px solid #d4af37;
        border-radius: 10px;
        pointer-events: none;
    }}
    
    /* ترويسة الكارت (الرمز وحالة الشراء) */
    .card-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
        border-bottom: 1px solid rgba(212, 175, 55, 0.3);
        padding-bottom: 5px;
    }}
    .sym-box {{
        font-size: 22px;
        font-weight: 900;
        color: #d4af37;
        background: rgba(212,175,55,0.1);
        padding: 2px 10px;
        border-radius: 5px;
    }}
    .rec-buy {{
        color: #00ff00;
        font-weight: bold;
        font-size: 14px;
        text-transform: uppercase;
    }}

    /* عداد التقييم النصف دائري */
    .score-gauge-container {{
        text-align: center;
        position: relative;
        height: 60px;
        margin-bottom: 10px;
    }}
    .gauge-bg {{
        position: absolute;
        width: 100px; height: 50px;
        border-radius: 50px 50px 0 0;
        background: #222;
        left: 50%; transform: translateX(-50%);
        border: 2px solid #333;
    }}
    .gauge-fill {{
        position: absolute;
        width: 100px; height: 50px;
        border-radius: 50px 50px 0 0;
        background: linear-gradient(180deg, #fccd4d, #f8b500);
        left: 50%; transform: translateX(-50%);
        clip-path: polygon(0 50%, 100% 50%, 100% 100%, 0 100%); /* البداية */
    }}
    .score-text {{
        position: absolute;
        bottom: 0; left: 50%;
        transform: translateX(-50%);
        font-size: 20px; font-weight: bold; color: #fff;
    }}

    /* صندوق الهدف الذهبي اللامع */
    .target-box-gold {{
        background: linear-gradient(135deg, #fceabb 0%, #fccd4d 30%, #f8b500 60%, #b8860b 100%);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
        border: 1px solid #fff;
        box-shadow: inset 0 0 10px rgba(255,255,255,0.5);
    }}
    .target-label {{
        font-size: 14px;
        color: #000;
        font-weight: bold;
        margin-bottom: 5px;
    }}
    .target-value {{
        font-size: 36px;
        font-weight: 900;
        color: #008000; /* أخضر غامق واضح كما في الصورة */
        text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
    }}
    .roi-tag {{
        color: #008000;
        font-weight: bold;
        font-size: 14px;
    }}

    /* جدول النقاط الفنية (S1, P, R1) */
    .tech-table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
        background: #111;
        border-radius: 8px;
        overflow: hidden;
    }}
    .tech-table td {{
        border: 1px solid rgba(212, 175, 55, 0.2);
        padding: 8px;
        text-align: center;
    }}
    .label-tech {{ font-size: 10px; color: #aaa; }}
    .value-tech {{ font-size: 14px; color: #d4af37; font-weight: bold; }}

    /* وقف الخسارة */
    .sl-box {{
        text-align: left;
        margin-top: 10px;
        color: #ff4b4b;
        font-size: 14px;
        font-weight: bold;
        padding-left: 5px;
    }}
    
    /* تحسين شكل الـ Loading */
    .stSpinner>div>div {{ border-top-color: #d4af37 !important; }}

</style>
""", unsafe_allow_html=True)

# --- محتوى الصفحة ---
# الترويسة
st.markdown("""
<div class="header-bar">
    <div class="brand">WAHBA <span class="gold-text">EGX</span> | <span style="font-size:16px;">النسخة الذهبية</span></div>
</div>
""", unsafe_allow_html=True)

# زر التحديث
calc_btn = st.button("تحديث المسح الشامل للسوق")

if calc_btn:
    with st.spinner("جاري استخلاص الفرص الذهبية..."):
        # حذف الملف القديم لضمان جلب بيانات لحظية جديدة
        if os.path.exists(INTERNAL_DB):
            try: os.remove(INTERNAL_DB)
            except: pass
        market_df = run_wahba_engine()
    
    if not market_df.empty:
        # عرض الوقت الحالي للجلسة
        st.markdown(f"<p style='text-align:center; color:#666; font-size:10px;'>SESSION ID: {datetime.now(egypt_tz).strftime('%Y-%m-%d %H:%M')}</p>", unsafe_allow_html=True)
        
        # تصفية الأسهم بناءً على سكور قوي (6 فما فوق) لتطابق الفرص المتميزة في الصورة
        gold_picks = market_df[market_df['Score'] >= 6].sort_values(by="Score", ascending=False)
        
        if gold_picks.empty:
            st.warning("لا توجد فرص قوية تحقق المعايير الذهبية حالياً. جرب التحديث وقت الجلسة.")
        else:
            for _, row in gold_picks.iterrows():
                # حساب زاوية العداد النصف دائري (بناءً على سكور من 10)
                gauge_angle = 180 - (min(row['Score'], 10) * 18)
                rec_text = "STRONG BUY" if row['Score'] >= 7 else "BUY"
                
                # إنشاء كارت الذهب لكل سهم
                st.markdown(f"""
                <div class="card-gold">
                    <div class="card-header">
                        <div class="sym-box">{row['Symbol']}</div>
                        <div class="rec-buy">{rec_text}</div>
                    </div>
                    
                    <div class="score-gauge-container">
                        <div class="gauge-bg"></div>
                        <div class="gauge-fill" style="clip-path: polygon(0 0, 100% 0, 100% 100%, 0 100%) ; transform: translateX(-50%) rotate({gauge_angle}deg); transform-origin: bottom center;"></div>
                        <div class="score-text">{row['Score']}<span style="font-size:10px; color:#aaa;">/10</span></div>
                        <div style="font-size:10px; color:#aaa; position:absolute; bottom:25px; left:50%; transform:translateX(-50%);">SCORE</div>
                    </div>
                    
                    <div class="target-box-gold">
                        <div class="target-label">الهدف المستهدف (Fib 1.618)</div>
                        <div class="target-value">{row['Target']}</div>
                        <div class="roi-tag">+ العائد المتوقع: {row['ROI']}%</div>
                    </div>
                    
                    <table class="tech-table">
                        <tr>
                            <td><div class="label-tech">S1</div><div class="value-tech">{row['S1']}</div></td>
                            <td><div class="label-tech">P</div><div class="value-tech">{row['P']}</div></td>
                            <td><div class="label-tech">R1</div><div class="value-tech">{row['R1']}</div></td>
                        </tr>
                    </table>
                    
                    <div class="sl-box">! وقف الخسارة: {row['StopLoss']}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.error("فشل الاتصال بـ TradingView. تأكد من الإنترنت وحاول مرة أخرى.")
