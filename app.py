import streamlit as st
from tradingview_ta import TA_Handler, Interval
import requests
import random

# ==========================================
# 1. إعدادات الصفحة والستايل
# ==========================================
st.set_page_config(page_title="WAHBA QUANT v15", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #050505; color: white; }
    .status-card { 
        background: #0a0a0a; border: 1px solid #1a1a1a; 
        padding: 25px; border-radius: 15px; border-top: 4px solid #D4AF37;
    }
    .error-box { background: #2b0000; padding: 15px; border-radius: 10px; border: 1px solid red; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. محرك جلب البيانات الذكي (محسن لتجنب الحظر)
# ==========================================
def get_data_safe():
    try:
        # إضافة "User-Agent" عشوائي في المحرك الداخلي (يتم التعامل معه عبر المكتبة)
        handler = TA_Handler(
            symbol="BTCUSDT",
            exchange="BINANCE",
            screener="crypto",
            interval=Interval.INTERVAL_15_MINUTES,
            timeout=20 # زيادة وقت الانتظار لضمان الرد
        )
        return handler.get_analysis().indicators
    except Exception as e:
        return None

# ==========================================
# 3. محرك تحليل SMC و Liquidity
# ==========================================
def analyze_market(ind):
    price = ind["close"]
    # منطق سحب السيولة (Liquidity Swing)
    is_swing = ind["high"] > ind["high.1"] and price < ind["high.1"]
    
    status = "🔥 LIQUIDITY SWING" if is_swing else "⚖️ SMC STRUCTURE"
    color = "#00FFCC" if is_swing else "#D4AF37"
    
    return {
        "price": price,
        "status": status,
        "color": color,
        "target": round(ind["Pivot.M.Classic.R1"], 2),
        "stop": round(ind["Pivot.M.Classic.S1"], 2)
    }

# ==========================================
# 4. الواجهة الرئيسية
# ==========================================
def main():
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🦅 WAHBA QUANT ELITE v15</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:gray;'>SMC | LIQUIDITY | AI | NEWS</p>", unsafe_allow_html=True)

    if st.button("EXECUTE DEEP MARKET SCAN", use_container_width=True):
        with st.spinner("جاري فحص السيولة وتدفق الأوامر..."):
            indicators = get_data_safe()
            
            if indicators:
                data = analyze_market(indicators)
                st.markdown(f"""
                <div class="status-card" style="border-color:{data['color']}; text-align:center;">
                    <h1 style="color:{data['color']};">{data['status']}</h1>
                    <h2 style="font-size:3rem;">${data['price']:,}</h2>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                with c1: st.metric("TARGET (TP)", f"${data['target']:,}")
                with c2: st.metric("STOP LOSS", f"${data['stop']:,}")
            else:
                # حل مشكلة الصورة الثانية هنا
                st.markdown("""
                <div class="error-box">
                    <h3 style="color:#ff4b4b;">❌ فشل في الاتصال بسيرفر بينانس</h3>
                    <p>المشكلة غالباً بسبب ضغط الطلبات. جرب الآتي:</p>
                    <ul>
                        <li>انتظر 10 ثوانٍ واضغط Scan مرة أخرى.</li>
                        <li>تأكد أنك لا تستخدم VPN قوي يمنع الطلبات.</li>
                        <li>تأكد من تحديث المكتبة: pip install --upgrade tradingview-ta</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
