import streamlit as st
import requests
import pandas as pd
from tradingview_ta import TA_Handler, Interval

st.set_page_config(page_title="ماسح البورصة المصرية", layout="wide")
st.title("🚀 ماسح البورصة المصرية التلقائي (150 ألف سيولة)")

def get_all_egx_tickers():
    url = "https://scanner.tradingview.com/egypt/scan"
    payload = {
        "filter": [{"left": "exchange", "operation": "equal", "right": "EGX"}],
        "options": {"lang": "en"},
        "markets": ["egypt"],
        "symbols": {"query": {"types": []}, "tickers": []},
        "columns": ["name"],
        "sort": {"by": "name", "order": "asc"}
    }
    try:
        response = requests.post(url, json=payload, timeout=15)
        data = response.json()
        return [item['d'][0] for item in data.get('data', [])]
    except Exception as e:
        st.error(f"⚠️ فشل الاتصال التلقائي بالسيرفر: {e}")
        # قائمة احتياطية لأهم الأسهم حتى لا يتوقف التطبيق
        return ['COMI', 'ABUK', 'FWRY', 'TMGH', 'SWDY', 'EKHO', 'ESRS', 'AMOC', 'HELI', 'ORAS']

# زر لتشغيل الفحص
if st.button("ابدأ فحص السوق الآن"):
    all_tickers = get_all_egx_tickers()
    
    if all_tickers:
        st.info(f"تم العثور على {len(all_tickers)} سهم. جاري التحليل الفني...")
        results = []
        
        # شريط تقدم للمستخدم
        progress_bar = st.progress(0)
        
        for index, ticker in enumerate(all_tickers):
            try:
                handler = TA_Handler(
                    symbol=ticker, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY
                )
                analysis = handler.get_analysis()
                summary = analysis.summary
                indicators = analysis.indicators
                
                if summary['RECOMMENDATION'] in ['BUY', 'STRONG_BUY']:
                    results.append({
                        'السهم': ticker,
                        'التقييم': summary['RECOMMENDATION'],
                        'إشارات الشراء': summary['BUY'],
                        'RSI': round(indicators.get('RSI', 0), 2)
                    })
            except:
                continue
            
            # تحديث شريط التقدم
            progress_bar.progress((index + 1) / len(all_tickers))
            
        if results:
            df = pd.DataFrame(results).sort_values(by='إشارات الشراء', ascending=False)
            st.success("✅ تم الفحص بنجاح! إليك الفرص المتاحة:")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("❌ لا توجد إشارات شراء قوية حالياً في السوق.")
