import streamlit as st
from tradingview_ta import TA_Handler, Interval
import requests

# ==========================================
# 1. إعدادات الواجهة
# ==========================================
st.set_page_config(page_title="WAHBA QUANT PRO", layout="wide")
st.markdown("<style>.stApp { background-color: #050505; color: white; }</style>", unsafe_allow_html=True)

# ==========================================
# 2. جلب البيانات بطريقة آمنة (Safe Fetch)
# ==========================================
def fetch_safe_data():
    try:
        handler = TA_Handler(
            symbol="BTCUSDT",
            exchange="BINANCE",
            screener="crypto",
            interval=Interval.INTERVAL_15_MINUTES,
            timeout=15
        )
        analysis = handler.get_analysis()
        return analysis.indicators
    except Exception as e:
        return None

# ==========================================
# 3. محرك تحليل السيولة (Fixed KeyError)
# ==========================================
def analyze_market_safe(ind):
    # استخدام .get() يمنع حدوث KeyError إذا كانت القيمة ناقصة
    price = ind.get("close", 0)
    high = ind.get("high", 0)
    p_high = ind.get("high.1", 0)
    low = ind.get("low", 0)
    p_low = ind.get("low.1", 0)
    
    # منطق SMC Liquidity Swing
    status = "⚖️ STRUCTURE STABLE"
    color = "#D4AF37"
    
    if high > p_high and price < p_high and p_high != 0:
        status = "🚨 LIQUIDITY SWEEP (TOP)"
        color = "#FF3131"
    elif low < p_low and price > p_low and p_low != 0:
        status = "🔥 LIQUIDITY SWING (BOTTOM)"
        color = "#00FFCC"
        
    return {
        "price": price,
        "status": status,
        "color": color,
        "target": round(ind.get("Pivot.M.Classic.R1", price * 1.02), 2),
        "stop": round(ind.get("Pivot.M.Classic.S1", price * 0.98), 2)
    }

# ==========================================
# 4. التطبيق الرئيسي
# ==========================================
def main():
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🦅 WAHBA QUANT ELITE</h1>", unsafe_allow_html=True)

    if st.button("EXECUTE DEEP MARKET SCAN", use_container_width=True):
        indicators = fetch_safe_data()
        
        if indicators:
            # هنا تم حل المشكلة اللي في الصورة
            data = analyze_market_safe(indicators)
            
            st.markdown(f"""
            <div style="background:#0a0a0a; border:2px solid {data['color']}; padding:30px; border-radius:15px; text-align:center;">
                <h1 style="color:{data['color']};">{data['status']}</h1>
                <h2 style="font-size:3rem;">BTC: ${data['price']:,}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            c1.metric("TARGET", f"${data['target']:,}")
            c2.metric("STOP", f"${data['stop']:,}")
        else:
            st.error("فشل في الاتصال. تأكد من جودة الإنترنت وحاول مجدداً.")

if __name__ == "__main__":
    main()
