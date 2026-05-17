import streamlit as st
import requests
import pandas as pd
from tradingview_ta import TA_Handler, Interval

st.set_page_config(page_title="ماسح البورصة المصرية الشامل", layout="wide")
st.title("🚀 ماسح البورصة المصرية التلقائي (TradingView Live)")

def get_live_tradingview_tickers():
    """سحب جميع رموز الأسهم المصرية الحية مباشرة من سكرينر تريدنج فيو"""
    url = "https://scanner.tradingview.com/egypt/scan"
    
    # إضافة هيدرز حقيقية لخدع السيرفر وتجنب الحظر (User-Agent)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # الطلب الرسمي المتوافق مع تحديثات تريدنج فيو
    payload = {
        "filter": [
            {"left": "exchange", "operation": "equal", "right": "EGX"},
            {"left": "type", "operation": "in_range", "right": ["stock", "dr", "fund"]}
        ],
        "options": {"lang": "en"},
        "markets": ["egypt"],
        "symbols": {"query": {"types": []}, "tickers": []},
        "columns": ["name"],
        "sort": {"by": "name", "order": "asc"}
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            tickers = [item['d'][0] for item in data.get('data', [])]
            return tickers
        else:
            st.error(f"⚠️ سيرفر تريدنج فيو رد بكود خطأ: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"⚠️ فشل الاتصال التلقائي بالسيرفر: {e}")
        return None

# زر تشغيل الفحص
if st.button("ابدأ فحص البورصة بالكامل الآن"):
    all_tickers = get_live_tradingview_tickers()
    
    if all_tickers:
        st.success(f"🔥 تم سحب القائمة الحية بنجاح! تم العثور على {len(all_tickers)} سهم (بما فيها الجديد).")
        st.info("جاري التحليل الفني للمؤشرات حالياً... برجاء الانتظار")
        
        results = []
        progress_bar = st.progress(0)
        
        for index, ticker in enumerate(all_tickers):
            try:
                handler = TA_Handler(
                    symbol=ticker,
                    screener="egypt",
                    exchange="EGX",
                    interval=Interval.INTERVAL_1_DAY
                )
                analysis = handler.get_analysis()
                summary = analysis.summary
                indicators = analysis.indicators
                
                # تصفية الأسهم بناءً على استراتيجية التداول بتاعتك (شراء فقط)
                if summary['RECOMMENDATION'] in ['BUY', 'STRONG_BUY']:
                    results.append({
                        'السهم': ticker,
                        'التقييم': summary['RECOMMENDATION'],
                        'مؤشرات الشراء': summary['BUY'],
                        'RSI (14)': round(indicators.get('RSI', 0), 2)
                    })
            except:
                # تخطي أي سهم جديد جداً لسه ملوش بيانات كاملة على السيرفر
                continue
            
            # تحديث العداد
            progress_bar.progress((index + 1) / len(all_tickers))
            
        if results:
            df = pd.DataFrame(results).sort_values(by='مؤشرات الشراء', ascending=False)
            st.write("### 📊 الفرص المتاحة الآن للدخول بالـ 10 آلاف جنيه:")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("❌ تم فحص السوق بالكامل، ولا توجد أسهم معطية إشارة شراء واضحة حالياً.")
    else:
        st.error("❌ تعذر جلب الأسهم من تريدنج فيو. يرجى مراجعة الـ Logs في Streamlit.")
