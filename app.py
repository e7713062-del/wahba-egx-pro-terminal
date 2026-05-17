import requests
import pandas as pd
from tradingview_ta import TA_Handler, Interval

def get_all_egx_tickers():
    """سحب جميع رموز الأسهم المصرية المتاحة على تريدنج فيو حالياً"""
    url = "https://scanner.tradingview.com/egypt/scan"
    
    # طلب البيانات بصيغة يفهمها سيرفر تريدنج فيو
    payload = {
        "filter": [{"left": "exchange", "operation": "equal", "right": "EGX"}],
        "options": {"lang": "en"},
        "markets": ["egypt"],
        "symbols": {"query": {"types": []}, "tickers": []},
        "columns": ["name"],
        "sort": {"by": "name", "order": "asc"}
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        # استخراج الرموز (tickers) من النتيجة
        tickers = [item['d'][0] for item in data.get('data', [])]
        return tickers
    except Exception as e:
        print(f"⚠️ فشل في سحب قائمة الأسهم التلقائية: {e}")
        # قائمة احتياطية لأهم الأسهم في حال فشل الاتصال بالسيرفر
        return ['COMI', 'ABUK', 'FWRY', 'TMGH', 'SWDY', 'EKHO', 'ESRS', 'AMOC']

def scan_and_analyze_market():
    # 1. سحب كل الأسهم أوتوماتيكياً (القديم والجديد)
    all_tickers = get_all_egx_tickers()
    print(f"🚀 تم العثور على {len(all_tickers)} سهم مدرج في البورصة المصرية على TradingView.")
    print("⏳ جاري التحليل الفني الشامل... برجاء الانتظار")
    
    results = []
    
    # 2. عمل Loop لتحليل كل سهم
    for ticker in all_tickers:
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
            
            # تصفية: نريد فقط الأسهم التي بدأت تتحرك إيجابياً (Buy أو Strong Buy)
            if summary['RECOMMENDATION'] in ['BUY', 'STRONG_BUY']:
                results.append({
                    'السهم': ticker,
                    'التقييم': summary['RECOMMENDATION'],
                    'مؤشرات الشراء': summary['BUY'],
                    'مؤشرات البيع': summary['SELL'],
                    'RSI (14)': round(indicators.get('RSI', 0), 2),
                    'MACD': round(indicators.get('MACD.macd', 0), 4)
                })
        except:
            # تخطي أي سهم فيه مشكلة في البيانات أو بياناته غير مكتملة (مثل الأسهم حديثة الطرح جداً أول يومين)
            continue

    # 3. عرض النتائج وتنظيمها
    if results:
        df = pd.DataFrame(results)
        # ترتيب الأسهم حسب عدد مؤشرات الشراء (الأقوى في الأعلى)
        df_sorted = df.sort_values(by='مؤشرات الشراء', ascending=False)
        
        print("\n✅ الأسهم الجاهزة للتداول الآن (فرص السيولة الذكية):")
        print(df_sorted.to_string(index=False))
        
        # حفظ نسخة في ملف إكسيل أوتوماتيكياً لمتابعتها
        df_sorted.to_excel("EGX_Opportunities_Report.xlsx", index=False)
        print("\n💾 تم حفظ التقرير في ملف إكسيل باسم: EGX_Opportunities_Report.xlsx")
    else:
        print("\n❌ لا توجد إشارات شراء قوية في السوق حالياً.")

# تشغيل الأداة
scan_and_analyze_market()
