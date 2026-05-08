# ==============================================================================
# 👑 PROJECT: WAHBA EGX - THE SUPREME QUANTUM ENTERPRISE (v13.5)
# 👨‍💻 MASTER ARCHITECT: MOSTAFA TAMER | ALEXANDRIA, EGYPT
# 🏛️ SYSTEM: NEURAL FEEDBACK, ANTI-BAN CACHE, & AUTO-PURGE ARCHITECTURE
# ==============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import requests
import sqlite3
import pytz
import os
import time
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from tradingview_ta import TA_Handler, Interval

# ------------------------------------------------------------------------------
# SECTION 1: DATABASE CONFIGURATION & SELF-CLEANING ENGINE
# ------------------------------------------------------------------------------
class DatabaseEngine:
    """
    هذا الكلاس مسؤول عن إدارة 'ذاكرة' النظام، بما في ذلك الحفظ، الاسترجاع، والتنظيف الذاتي.
    """
    def __init__(self):
        self.db_name = 'wahba_enterprise_vault.db'
        self.initialize_database()
        self.execute_auto_purge()

    def initialize_database(self):
        """إنشاء الجداول اللازمة إذا لم تكن موجودة"""
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evolution_vault (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                date TEXT,
                predicted_price REAL,
                actual_price REAL,
                accuracy_rate REAL,
                market_context TEXT,
                brain_score REAL
            )
        ''')
        connection.commit()
        connection.close()

    def execute_auto_purge(self):
        """
        مسح البيانات التي مضى عليها أكثر من 30 يوماً للحفاظ على سرعة النظام.
        """
        try:
            connection = sqlite3.connect(self.db_name)
            cursor = connection.cursor()
            
            # تحديد التاريخ الفاصل (منذ 30 يوم)
            threshold_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            
            # تنفيذ عملية المسح
            cursor.execute("DELETE FROM evolution_vault WHERE date < ?", (threshold_date,))
            
            # ضغط قاعدة البيانات لاستعادة المساحة المهدرة
            cursor.execute("VACUUM")
            
            connection.commit()
            connection.close()
            return True
        except Exception as e:
            print(f"Purge Error: {e}")
            return False

    def save_market_snapshot(self, symbol, date, predicted, actual, context, score):
        """حفظ نتائج التحليل اللحظي في القاعدة"""
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        
        # حساب الدقة اللحظية
        if actual != 0:
            accuracy = 1 - abs((actual - predicted) / actual)
        else:
            accuracy = 0
            
        cursor.execute('''
            INSERT INTO evolution_vault 
            (symbol, date, predicted_price, actual_price, accuracy_rate, market_context, brain_score) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, date, predicted, actual, accuracy, context, score))
        
        connection.commit()
        connection.close()

    def check_today_cache(self, current_date):
        """البحث عن بيانات اليوم لتوفير الموارد ومنع الحظر"""
        connection = sqlite3.connect(self.db_name)
        query = f"SELECT * FROM evolution_vault WHERE date = '{current_date}'"
        data_frame = pd.read_sql(query, connection)
        connection.close()
        return data_frame

    def get_success_metrics(self):
        """حساب متوسط الدقة لغرض الماركتينج"""
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        cursor.execute("SELECT AVG(accuracy_rate) FROM evolution_vault WHERE accuracy_rate IS NOT NULL")
        result = cursor.fetchone()[0]
        connection.close()
        
        if result:
            return round(result * 100, 2)
        return 0.0

# ------------------------------------------------------------------------------
# SECTION 2: ARTIFICIAL INTELLIGENCE & SMC LOGIC
# ------------------------------------------------------------------------------
class IntelligenceModule:
    """
    هذا الموديول يحتوي على 'عقل' الأداة، متمثلاً في نموذج الذكاء الاصطناعي ومنطق SMC.
    """
    def __init__(self):
        self.ai_model = self.bootstrap_ai_model()

    def bootstrap_ai_model(self):
        """تدريب نموذج مبدئي للتعامل مع التوقعات السعرية"""
        X_train = np.array([[10, 30], [50, 50], [5, 20], [100, 70]])
        y_train = np.array([10.5, 51.2, 5.3, 104.5])
        
        model = LinearRegression()
        model.fit(X_train, y_train)
        return model

    def calculate_brain_score(self, close, rsi, vol, avg_vol, hi, lo, pivot):
        """تحليل السيناريوهات السوقية بأسلوب يحاكي المتداول المحترف"""
        
        # 1. تحليل الاختراقات الكاذبة
        if close > hi and vol < (avg_vol * 0.8):
            return "⚠️ فخ سيولة: اختراق كاذب (Fake Breakout)", -2.5
        
        # 2. تحليل التجميع المؤسسي
        if close < pivot and rsi < 35 and vol > avg_vol:
            return "💎 تجميع مؤسسي: دخول سيولة ذكية (Accumulation)", 3.0
        
        # 3. تحليل مناطق الارتداد
        if rsi < 20:
            return "🔥 ذروة بيع: توقع ارتداد تقني عنيف", 2.8
        
        # 4. تحليل الاتجاه القوي
        if close > pivot and vol > avg_vol:
            return "📈 اتجاه صاعد: مدعوم بزخم مؤسسي", 2.0
            
        return "🔄 حالة توازن: تداول عرضي ممل", 0

    def generate_price_prediction(self, current_price, current_rsi):
        """استخدام الموديل لتوقع السعر القادم"""
        input_data = np.array([[current_price, current_rsi]])
        prediction = self.ai_model.predict(input_data)[0]
        return round(float(prediction), 2)

# ------------------------------------------------------------------------------
# SECTION 3: PREMIUM INTERFACE ARCHITECTURE
# ------------------------------------------------------------------------------
def render_custom_styles():
    """حقن أكواد CSS مخصصة لإعطاء مظهر المؤسسات الفاخر"""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;700;900&display=swap');
        
        /* إعدادات الخلفية العامة */
        .stApp { 
            background-color: #010101; 
            color: #ffffff; 
            font-family: 'Tajawal', sans-serif;
        }
        
        /* تصميم الهيدر الرئيسي */
        .main-header {
            background: linear-gradient(180deg, #121212 0%, #000 100%);
            padding: 80px 20px;
            text-align: center;
            border-bottom: 5px solid #d4af37;
            border-radius: 0 0 80px 80px;
            margin-bottom: 60px;
            box-shadow: 0 15px 50px rgba(0,0,0,0.8);
        }
        
        .logo-main { 
            font-size: 85px; 
            font-weight: 900; 
            color: #d4af37; 
            margin: 0;
            text-shadow: 0 0 30px rgba(212, 175, 55, 0.3);
        }
        
        .logo-sub { 
            letter-spacing: 12px; 
            color: #555; 
            font-size: 14px; 
            text-transform: uppercase;
        }

        /* تصميم كروت الأسهم المميزة */
        .premium-card {
            background: #080808;
            border: 1px solid #d4af37;
            border-radius: 35px;
            padding: 40px;
            margin: 15px;
            transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        
        .premium-card:hover {
            transform: scale(1.05) translateY(-15px);
            background: #111;
            box-shadow: 0 20px 40px rgba(212, 175, 55, 0.1);
        }

        /* أزرار التحكم */
        .stButton>button {
            background: linear-gradient(90deg, #d4af37 0%, #aa891e 100%) !important;
            color: #000 !important;
            border-radius: 20px !important;
            font-weight: 900 !important;
            height: 65px !important;
            border: none !important;
            transition: 0.4s !important;
        }
        </style>
        
        <div class="main-header">
            <h1 class="logo-main">WAHBA <span>EGX</span></h1>
            <p class="logo-sub">Enterprise Quantum System v13.5</p>
        </div>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# SECTION 4: SYSTEM ASSEMBLY & RUNTIME
# ------------------------------------------------------------------------------
def run_system():
    # 1. تهيئة المحركات
    db = DatabaseEngine()
    brain = IntelligenceModule()
    render_custom_styles()
    
    # 2. ضبط التوقيت المحلي
    cairo_tz = pytz.timezone('Africa/Cairo')
    today_date = datetime.now(cairo_tz).strftime("%Y-%m-%d")

    # 3. إعداد القائمة الجانبية (Sidebar)
    with st.sidebar:
        st.markdown("### 🛠️ Terminal Control")
        marketing_acc = db.get_success_metrics()
        st.metric("🎯 Global Accuracy Score", f"{marketing_acc}%")
        
        st.success("✅ Auto-Purge: Active")
        st.info(f"📅 Session: {today_date}")
        st.divider()
        
        initiate_scan = st.button("EXECUTE MARKET SCAN 🚀", use_container_width=True)

    # 4. منطق الفحص الرئيسي
    if initiate_scan:
        # فحص الكاش أولاً (Anti-Ban System)
        cached_data = db.check_today_cache(today_date)
        
        if not cached_data.empty:
            st.warning("💾 تم جلب البيانات من الخزنة اليومية (وضع الحماية نشط)")
            # معالجة البيانات المسجلة لتناسب العرض
            display_df = cached_data[['symbol', 'actual_price', 'predicted_price', 'market_context', 'brain_score']]
            display_df.columns = ['السهم', 'إغلاق', 'هدف الـ AI', 'الرؤية', 'Brain Score']
            st.session_state.current_results = display_df
        else:
            # جلب قائمة الأسهم أوتوماتيكياً
            try:
                scanner_url = "https://scanner.tradingview.com/egypt/scan"
                api_res = requests.post(scanner_url, json={"filter": [{"left": "type", "operation": "in_range", "right": ["stock"]}], "markets": ["egypt"], "columns": ["name"]}, timeout=15).json()
                market_symbols = [item['s'].split(':')[1] for item in api_res['data']]
            except:
                market_symbols = ["COMI", "FWRY", "TMGH", "SWDY", "BTEL", "ISPH", "EKHO", "JUFO"]

            final_analysis = []
            scan_progress = st.progress(0, text="🧠 جاري تشغيل المحرك الكمي وفحص السيولة...")
            
            for index, ticker in enumerate(market_symbols):
                try:
                    # سحب المؤشرات الفنية
                    handler = TA_Handler(symbol=ticker, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY)
                    tech_analysis = handler.get_analysis()
                    indicators = tech_analysis.indicators
                    
                    # استخلاص القيم الأساسية
                    price_close = indicators["close"]
                    rsi_value = indicators["RSI"]
                    volume_now = indicators["volume"]
                    vol_avg = indicators.get("average_volume", volume_now)
                    hi_val = indicators["high"]
                    lo_val = indicators["low"]
                    pivot_pt = indicators["Pivot.M.Classic.Middle"]
                    
                    # تشغيل منطق العقل الصناعي
                    context_msg, score_val = brain.calculate_brain_score(price_close, rsi_value, volume_now, vol_avg, hi_val, lo_val, pivot_pt)
                    future_target = brain.generate_price_prediction(price_close, rsi_value)
                    
                    # حفظ اللقطة في قاعدة البيانات (للمستقبل والماركتينج)
                    db.save_market_snapshot(ticker, today_date, future_target, price_close, context_msg, score_val)
                    
                    final_analysis.append({
                        "السهم": ticker, 
                        "إغلاق": price_close, 
                        "هدف الـ AI": future_target, 
                        "الرؤية": context_msg, 
                        "Brain Score": score_val
                    })
                except:
                    continue
                
                scan_progress.progress((index + 1) / len(market_symbols))
            
            # ترتيب النتائج وحفظها في جلسة العمل
            result_df = pd.DataFrame(final_analysis).sort_values("Brain Score", ascending=False)
            st.session_state.current_results = result_df
            st.rerun()

    # 5. عرض النتائج النهائية
    if 'current_results' in st.session_state:
        df_results = st.session_state.current_results
        
        st.markdown("## ⚜️ THE ELITE SELECTIONS")
        top_picks = df_results.head(3)
        ui_cols = st.columns(3)
        
        for i, (idx, row) in enumerate(top_picks.iterrows()):
            with ui_cols[i]:
                st.markdown(f"""
                <div class="premium-card">
                    <h1 style="color:#d4af37; margin:0; font-size:48px;">{row['السهم']}</h1>
                    <p style="color:#666; margin:20px 0; font-size:16px; line-height:1.6;">{row['الرؤية']}</p>
                    <div style="display:flex; justify-content:space-between; border-top:1px solid #1a1a1a; padding-top:20px;">
                        <div>
                            <small style="color:#444; font-weight:bold;">CURRENT</small><br>
                            <span style="font-size:22px; font-weight:900;">{row['إغلاق']}</span>
                        </div>
                        <div style="text-align:right;">
                            <small style="color:#d4af37; font-weight:bold;">TARGET</small><br>
                            <span style="font-size:22px; font-weight:900; color:#00ff00;">{row['هدف الـ AI']}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### 📊 FULL QUANTUM INTELLIGENCE REPORT")
        st.dataframe(df_results, use_container_width=True, hide_index=True)

    # 6. الفوتر النهائي (Legal Disclaimer)
    st.markdown(f"""
        <div style="text-align:center; padding:120px 20px 60px 20px; border-top:1px solid #080808; margin-top:100px;">
            <p style="color:#d4af37; font-weight:900; letter-spacing:5px; margin-bottom:20px;">WAHBA EGX SUPREME v13.5</p>
            <p style="color:#333; font-size:12px; max-width:800px; margin:0 auto; line-height:2;">
                هذا النظام هو ملكية فكرية لمصطفى تامر. جميع التحليلات مبنية على نماذج رياضية ومنطق السيولة المؤسسية. 
                النظام يقوم بعملية تنظيف ذاتي دورية للحفاظ على كفاءة الأداء. قرارات التداول هي مسؤوليتك الشخصية تماماً.
            </p>
            <p style="color:#222; font-size:10px; margin-top:30px;">ALL RIGHTS RESERVED © {datetime.now().year} | ALEXANDRIA, EGYPT</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    run_system()
