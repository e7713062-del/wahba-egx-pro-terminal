import streamlit as st
from tradingview_ta import TA_Handler, Interval
import requests

# ==========================================
# 1. LIQUIDITY SWING ENGINE (The Hunt)
# ==========================================
def fetch_smc_liquidity_data():
    try:
        # فريم الـ 15 دقيقة هو الأفضل لرصد سحب السيولة اللحظي
        handler = TA_Handler(symbol="BTCUSDT", exchange="BINANCE", screener="crypto", interval=Interval.INTERVAL_15_MINUTES)
        analysis = handler.get_analysis()
        ind = analysis.indicators

        price = ind["close"]
        high = ind["high"]
        low = ind["low"]
        p_high = ind["high.1"] # القمة السابقة
        p_low = ind["low.1"]   # القاع السابق

        # --- خوارزمية رصد الـ Liquidity Swing ---
        liq_signal = "MARKET STABLE"
        liq_color = "#666"
        
        # 1. سحب سيولة القمم (Buy Side Liquidity Grab)
        if high > p_high and price < p_high:
            liq_signal = "🚨 LIQUIDITY SWEEP (TOP): Smart Money Hunting Sellers"
            liq_color = "#FF3131"
        
        # 2. سحب سيولة القيعان (Sell Side Liquidity Grab)
        elif low < p_low and price > p_low:
            liq_signal = "🔥 LIQUIDITY SWING (BOTTOM): Smart Money Hunting Buyers"
            liq_color = "#00FFCC"

        # مناطق الـ Order Block المؤسسية
        ob_zone = f"${ind['low.1']:,.2f}" if price > ind['high.1'] else f"${ind['high.1']:,.2f}"

        return {
            "price": price,
            "signal": liq_signal,
            "color": liq_color,
            "ob": ob_zone,
            "vol": ind["volume"],
            "target": round(ind["Pivot.M.Classic.R1"], 2)
        }
    except: return None

# ==========================================
# 2. SMART NEWS (AI SENTIMENT)
# ==========================================
def get_ai_news():
    try:
        url = "https://min-api.cryptocompare.com/data/v2/news/?lang=EN"
        response = requests.get(url).json()
        return [{"title": n['title'], "url": n['url']} for n in response['Data'][:3]]
    except: return []

# ==========================================
# 3. THE ULTIMATE SMC INTERFACE
# ==========================================
st.set_page_config(page_title="WAHBA LIQUIDITY QUANT", layout="wide")

st.markdown("""
<style>
    .stApp { background: #000; color: #fff; }
    .hunt-box { 
        background: #080808; border: 2px solid #1a1a1a; padding: 30px; 
        border-radius: 15px; text-align: center; margin-bottom: 20px;
    }
    .news-item { border-bottom: 1px solid #222; padding: 10px 0; }
    .target-box { background: #111; border-left: 4px solid #D4AF37; padding: 15px; }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown("<h1 style='text-align:center; color:#D4AF37; font-family:Orbitron;'>🦅 WAHBA QUANT: LIQUIDITY SWING RADAR</h1>", unsafe_allow_html=True)
    st.divider()

    if st.button("RUN DEEP LIQUIDITY SCAN", use_container_width=True):
        data = fetch_smc_liquidity_data()
        news = get_ai_news()

        if data:
            # عرض إشارة صيد السيولة
            st.markdown(f"""
            <div class="hunt-box" style="border-color:{data['color']};">
                <p style="color:#888; letter-spacing:2px;">LIQUIDITY STATUS</p>
                <h1 style="color:{data['color']};">{data['signal']}</h1>
                <p style="font-size:1.5rem;">Price: ${data['price']:,}</p>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"""
                <div class="target-box">
                    <h3 style="color:#D4AF37;">SMC INSTITUTIONAL TARGETS</h3>
                    <p>NEXT LIQUIDITY POOL (TP): <b style="color:#00FFCC;">${data['target']:,}</b></p>
                    <p>RE-ENTRY ZONE (OB): <b style="color:#D4AF37;">{data['ob']}</b></p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown("### 📰 LIVE MARKET NEWS")
                for n in news:
                    st.markdown(f"""
                    <div class="news-item">
                        <a href="{n['url']}" style="color:#eee; text-decoration:none; font-size:0.9rem;">{n['title']}</a>
                    </div>
                    """, unsafe_allow_html=True)
                
            st.caption("System focuses exclusively on Binance BTC/USDT Spot | No Classic Indicators Used.")

if __name__ == "__main__":
    main()
