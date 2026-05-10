import streamlit as st
import pandas as pd
import google.generativeai as genai
import yfinance as yf  # البديل الأقوى لبيانات تريدنج فيو
import time
from datetime import datetime

# =================================================================
# 1. إعدادات النظام (Wahba Sovereign - TradingView Data Style)
# =================================================================
CONFIG = {
    "GEMINI_KEY": "YOUR_GEMINI_API_KEY",
    "SYMBOLS": ["BTC-USD", "ETH-USD", "SOL-USD"], # تنسيق yfinance
    "TIMEFRAME": "15m"
}

# =================================================================
# 2. محرك جلب البيانات (The Data Scraper)
# =================================================================
class MarketData:
    @staticmethod
    def get_live_data(symbol):
        """جلب بيانات حقيقية من السوق (مثل تريدنج فيو) بدون API Keys"""
        try:
            # بنسحب بيانات آخر 24 ساعة بفاصل 15 دقيقة
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="1d", interval="15m")
            if df.empty: return None
            
            df = df.reset_index()
            df.columns = ['time', 'open', 'high', 'low', 'close', 'vol', 'div', 'split']
            return df
        except Exception as e:
            return None

    @staticmethod
    def detect_smc(df):
        """تحليل الـ SMC على البيانات الحقيقية"""
        lb = 20
        df['r_low'] = df['low'].shift(1).rolling(window=lb).min()
        df['r_high'] = df['high'].shift(1).rolling(window=lb).max()
        last = df.iloc[-1]
        
        if last['low'] < last['r_low'] and last['close'] > last['r_low']: return "BUY"
        if last['high'] > last['r_high'] and last['close'] < last['r_high']: return "SELL"
        return "WAIT"

# =================================================================
# 3. الواجهة الرسومية (The Dashboard)
# =================================================================
def main():
    st.set_page_config(page_title="Wahba Sovereign AI", layout="wide", page_icon="🦅")
    
    # تهيئة Gemini
    if "GEMINI_CLIENT" not in st.session_state:
        try:
            genai.configure(api_key=CONFIG["GEMINI_KEY"])
            st.session_state.gemini = genai.GenerativeModel('gemini-1.5-flash')
        except:
            st.session_state.gemini = None

    st.title("🦅 Wahba Sovereign AI")
    st.markdown("### نظام التحليل الذكي (بيانات حية من السوق)")

    with st.sidebar:
        st.header("⚙️ حالة الاتصال")
        st.success("✅ البيانات: Yahoo Finance (Live)")
        if not CONFIG["GEMINI_KEY"] or "YOUR" in CONFIG["GEMINI_KEY"]:
            st.warning("⚠️ يرجى إضافة مفتاح Gemini للتحليل")
        st.divider()
        st.write("الوضع: مراقبة وتحليل (Spot)")

    # شبكة العملات
    cols = st.columns(len(CONFIG["SYMBOLS"]))
    
    for i, sym in enumerate(CONFIG["SYMBOLS"]):
        with cols[i]:
            df = MarketData.get_live_data(sym)
            
            if df is not None:
                current_price = df.iloc[-1]['close']
                signal = MarketData.detect_smc(df)
                
                st.subheader(f"💎 {sym.replace('-USD', '')}")
                st.metric("Price", f"${current_price:,.2f}")
                
                if signal != "WAIT":
                    st.info(f"🔍 إشارة {signal} رصدت")
                    # استشارة Gemini لو المفتاح موجود
                    if st.session_state.gemini:
                        try:
                            prompt = f"Analyze {sym} {signal} at {current_price}. Is it a good liquidity sweep? Reply in Arabic (1 sentence)."
                            resp = st.session_state.gemini.generate_content(prompt)
                            st.success(f"🤖 ذكاء اصطناعي: {resp.text}")
                        except:
                            st.write("🤖 Gemini مشغول حالياً...")
                
                # رسم الشارت
                st.line_chart(df['close'].tail(40))
            else:
                st.error(f"❌ تعذر جلب {sym}")

    st.divider()
    st.caption("التحديث يتم تلقائياً كل دقيقة | البيانات مستمدة من سيرفرات السوق المفتوحة")
    
    time.sleep(60)
    st.rerun()

if __name__ == "__main__":
    main()
