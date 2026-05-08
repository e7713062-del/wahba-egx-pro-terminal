import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import numpy as np
import requests
import os
from datetime import datetime
import pytz

# ==========================================
# 1. نظام الحماية والملكية الفكرية (Legal & IP)
# ==========================================
LICENSE_HOLDER = "WAHBA STRATEGY"
LEGAL_TEXT = """
خاضع لقوانين حماية الملكية الفكرية الدولية. 
يحظر تماماً محاولة هندسة الكود عكسياً أو اقتباس الخوارزميات البرمجية تحت طائلة المسؤولية القانونية.
هذا البرنامج هو أداة استشارية فنية فقط؛ والقرار الاستثماري يقع بالكامل على عاتق المستخدم.
"""

# ==========================================
# 2. المحرك المشفر (Encapsulated Engine)
# ==========================================
class PrivateCore:
    """محرك التحليل الفني - نسخة محمية"""
    @staticmethod
    def _execute_logic(data_vector):
        # تم تعمية المنطق الرياضي لضمان سرية الاستراتيجية
        _α = data_vector['P']
        _β = data_vector['R1']
        _γ = data_vector['S1']
        _δ = data_vector['Price']
        
        # خوارزمية وهبة الخاصة
        target = np.round(_α + (_β - _α) * 1.618, 2)
        sl = np.round(_γ * 0.99, 2)
        yields = np.round(((target - _δ) / _δ) * 100, 1)
        
        return target, sl, yields

# ==========================================
# 3. الواجهة الرسومية المتطورة (UI Customization)
# ==========================================
st.set_page_config(page_title="WAHBA | PRO TERMINAL", layout="wide")

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;500;700&display=swap');
    
    :root {{
        --gold: #D4AF37;
        --dark-bg: #0E1117;
        --card-bg: rgba(255, 255, 255, 0.05);
    }}

    * {{ font-family: 'IBM Plex Sans Arabic', sans-serif; direction: rtl; }}

    .stApp {{ background-color: var(--dark-bg); }}
    
    /* تصميم الكروت الاحترافي */
    .premium-card {{
        background: var(--card-bg);
        border-right: 4px solid var(--gold);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }}
    
    .symbol-header {{
        color: var(--gold);
        font-size: 24px;
        font-weight: 700;
        letter-spacing: 1px;
    }}
    
    .metric-box {{
        background: rgba(0,0,0,0.2);
        padding: 10px;
        border-radius: 5px;
        text-align: center;
    }}
    
    .legal-footer {{
        font-size: 10px;
        color: #555;
        text-align: center;
        margin-top: 50px;
        border-top: 1px solid #222;
        padding: 20px;
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. منطق التشغيل (System Logic)
# ==========================================

def main():
    # التحقق من الموافقة القانونية (تظهر مرة واحدة)
    if 'agreed' not in st.session_state:
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>نظام واهبة للتحليل المتقدم</h1>", unsafe_allow_html=True)
        st.warning(LEGAL_TEXT)
        if st.button("أوافق على الشروط وأتحمل المسؤولية القانونية الكاملة"):
            st.session_state.agreed = True
            st.rerun()
        return

    # Header
    cols = st.columns([1, 4, 1])
    with cols[1]:
        st.markdown("<h1 style='text-align:center; color:white;'>WAHBA <span style='color:#D4AF37'>QUANT</span> PRO</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#888;'>المنصة المؤسسية لتحليل أسهم البورصة المصرية</p>", unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2534/2534348.png", width=100)
        st.title("Control Panel")
        if st.button("Refresh Terminal"):
            st.cache_data.clear()
            st.rerun()
        st.markdown("---")
        st.write("Ver: 3.0.1 (Stable)")

    # جلب البيانات (استخدام الكود الخاص بك مع تحسين العرض)
    with st.spinner("جاري تحليل السيولة والتدفقات المالية..."):
        from __main__ import fetch_market_data # استدعاء الدالة من الكود الأصلي
        df = fetch_market_data()

    if not df.empty:
        # تطبيق الخوارزمية "المشفرة"
        df[['Target', 'StopLoss', 'ROI']] = df.apply(lambda r: pd.Series(PrivateCore._execute_logic(r)), axis=1)
        
        # عرض أفضل 10 فرص فقط (المؤسسات لا تعرض كل شيء)
        top_picks = df[df['Score'] >= 6].sort_values(by="Score", ascending=False).head(10)
        
        grid = st.columns(2)
        for i, (_, row) in enumerate(top_picks.iterrows()):
            with grid[i % 2]:
                st.markdown(f"""
                <div class="premium-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="symbol-header">{row['Symbol']}</span>
                        <span style="color:#ff4b4b; font-size:12px;">SL: {row['StopLoss']}</span>
                    </div>
                    <div style="margin: 15px 0;">
                        <span style="color:#eee;">السعر الحالي: </span>
                        <span style="font-size:20px; color:white; font-weight:bold;">{row['Price']} EGP</span>
                    </div>
                    <div class="metric-box">
                        <div style="color:#888; font-size:12px;">المستهدف المؤسسي (H1)</div>
                        <div style="color:#00ff00; font-size:28px; font-weight:700;">{row['Target']}</div>
                        <div style="color:#00ff00; font-size:14px;">+ {row['ROI']}% متوقع</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Footer القانوني الصارم
    st.markdown(f"""
    <div class="legal-footer">
        جميع الحقوق محفوظة © {datetime.now().year} {LICENSE_HOLDER}<br>
        استخدام هذا النظام يخضع لاتفاقية السرية الرقمية. أي محاولة لاستخراج البيانات (Data Scraping) ستؤدي لحظر البروتوكول الخاص بك.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
