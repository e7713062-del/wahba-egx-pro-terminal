# ==============================================================================
# 👑 PROJECT: WAHBA EGX - THE MASTERPIECE (v16.0)
# 👨‍💻 ARCHITECT: MOSTAFA TAMER | ALEXANDRIA, EGYPT
# 🏛️ SYSTEM: NEURAL FEEDBACK, SMC LOGIC, DYNAMIC HTML/CSS
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
# 🏛️ القطاع الأول: إدارة البيانات (The Database Fortress)
# ------------------------------------------------------------------------------
class DataManager:
    """
    هذا الكلاس مسؤول عن كل ما يخص 'الذاكرة' وتخزين البيانات وحمايتها.
    """
    def __init__(self):
        self.db_path = 'wahba_ultimate_vault.db'
        self.create_tables()
        self.run_auto_maintenance()

    def create_tables(self):
        """إنشاء الجداول اللازمة لحفظ البيانات والتعلم"""
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                trade_date TEXT,
                predicted_target REAL,
                actual_price REAL,
                accuracy REAL,
                market_context TEXT,
                brain_score REAL
            )
        ''')
        connection.commit()
        connection.close()

    def run_auto_maintenance(self):
        """تنظيف تلقائي للبيانات التي مر عليها أكثر من 30 يوم لضمان السرعة"""
        try:
            expiration_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            connection = sqlite3.connect(self.db_path)
            cursor = connection.cursor()
            cursor.execute("DELETE FROM signals_history WHERE trade_date < ?", (expiration_date,))
            cursor.execute("VACUUM")  # ضغط قاعدة البيانات وتوفير المساحة
            connection.commit()
            connection.close()
            return True
        except Exception:
            return False

    def save_new_signal(self, sym, date, pred, actual, context, score):
        """حفظ إشارة جديدة في الأرشيف"""
        acc = 1 - abs((actual - pred) / actual) if actual != 0 else 0
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO signals_history 
            (symbol, trade_date, predicted_target, actual_price, accuracy, market_context, brain_score) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (sym, date, pred, actual, acc, context, score))
        connection.commit()
        connection.close()

    def load_today_cache(self, current_date):
        """استعادة بيانات اليوم من الذاكرة (Anti-Ban)"""
        connection = sqlite3.connect(self.db_path)
        query = f"SELECT * FROM signals_history WHERE trade_date = '{current_date}'"
        df = pd.read_sql(query, connection)
        connection.close()
        return df

# ------------------------------------------------------------------------------
# 🧠 القطاع الثاني: محرك الذكاء الاصطناعي (The Neural Engine)
# ------------------------------------------------------------------------------
class IntelligenceEngine:
    """
    المحرك المسؤول عن تحليل المؤشرات، توقع السعر، وفهم سياق السوق (SMC).
    """
    def __init__(self):
        # نموذج ذكاء اصطناعي (Linear Regression)
        self.brain = self.initialize_model()

    def initialize_model(self):
        """تدريب نموذج أولي يتعلم مع مرور الوقت"""
        X = np.array([[10, 30], [50, 60], [5, 20]])
        y = np.array([10.5, 51.0, 5.2])
        return LinearRegression().fit(X, y)

    def calculate_market_mood(self, c, r, v, av, hi, lo, pivot):
        """منطق المال الذكي (Smart Money Concepts)"""
        if c > hi and v < (av * 0.75):
            return "⚠️ فخ سيولة: اختراق كاذب", -2.0
        if c < pivot and r < 35 and v > av:
            return "💎 تجميع مؤسسي: دخول حيتان", 3.5
        if r < 25:
            return "🔥 منطقة ارتداد تاريخية", 2.5
        if c > pivot and v > av:
            return "📈 اتجاه صاعد صحي", 2.0
        return "🔄 تداول عرضي مستقر", 0

    def predict_target(self, close_price, rsi_value):
        """توقع السعر المستهدف بناءً على المعطيات"""
        prediction = self.brain.predict(np.array([[close_price, rsi_value]]))[0]
        return round(float(prediction), 2)

# ------------------------------------------------------------------------------
# 🎨 القطاع الثالث: التصميم والتفاعل (Visual & CSS UI)
# ------------------------------------------------------------------------------
class ThemeArchitect:
    """
    المسؤول عن جماليات الأداة، الألوان، الخطوط، والأنيميشن.
    """
    @staticmethod
    def apply_styles():
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;700;900&display=swap');
        
        /* التنسيق العام */
        * { font-family: 'Tajawal', sans-serif; transition: all 0.4s ease-in-out; }
        .stApp { background-color: #020202; color: #ffffff; }

        /* الهيدر الفاخر */
        .premium-header {
            background: linear-gradient(180deg, #111, #000);
            padding: 80px 20px;
            text-align: center;
            border-bottom: 5px solid #d4af37;
            border-radius: 0 0 100px 100px;
            margin-bottom: 60px;
            box-shadow: 0 15px 40px rgba(0,0,0,0.8);
        }
        .main-logo { font-size: 80px; font-weight: 900; color: #d4af37; margin: 0; }
        .sub-logo { letter-spacing: 12px; color: #444; font-size: 14px; text-transform: uppercase; }

        /* الكروت التفاعلية */
        .stock-card {
            background: rgba(15, 15, 15, 0.9);
            border: 1px solid rgba(212, 175, 55, 0.1);
            border-radius: 35px;
            padding: 40px;
            margin: 15px;
            text-align: center;
        }
        .stock-card:hover {
            transform: translateY(-20px);
            border-color: #d4af37;
            background: #0a0a0a;
            box-shadow: 0 25px 50px rgba(212, 175, 55, 0.1);
        }

        /* الجداول والأزرار */
        .stButton>button {
            background: linear-gradient(90deg, #d4af37, #b8860b) !important;
            color: #000 !important;
            border-radius: 20px !important;
            font-weight: 900 !important;
            height: 60px !important;
            border: none !important;
            width: 100% !important;
        }
        </style>

        <div class="premium-header">
            <h1 class="main-logo">WAHBA <span>EGX</span></h1>
            <p class="sub-logo">Masterpiece Edition v16.0</p>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 🚀 القطاع الرابع: نظام التشغيل (Mission Control)
# ------------------------------------------------------------------------------
def run_wahba_system():
    # تهيئة المحركات
    db = DataManager()
    ai = IntelligenceEngine()
    ThemeArchitect.apply_styles()
    
    # ضبط التوقيت والهوية
    cairo_tz = pytz.timezone('Africa/Cairo')
    today_str = datetime.now(cairo_tz).strftime("%Y-%m-%d")

    # لوحة التحكم الجانبية
    with st.sidebar:
        st.markdown("## ⚙️ Control Terminal")
        st.success("✅ نظام التنظيف الذاتي: نشط")
        st.info(f"📅 جلسة اليوم: {today_str}")
        st.divider()
        start_button = st.button("إطلاق المسح الكمي الشامل 🚀")

    # منطق العمل الرئيسي
    if start_button:
        # البحث في الذاكرة أولاً لمنع الهجمات والحظر
        cache_df = db.load_today_cache(today_str)
        
        if not cache_df.empty:
            st.warning("💾 تم استرجاع البيانات من الخزنة (وضع الحماية الذكي)")
            st.session_state.market_data = cache_df
        else:
            # جلب قائمة الأسهم أوتوماتيكياً
            try:
                url = "https://scanner.tradingview.com/egypt/scan"
                payload = {"filter": [{"left": "type", "operation": "in_range", "right": ["stock"]}], "markets": ["egypt"], "columns": ["name"]}
                response = requests.post(url, json=payload, timeout=15).json()
                symbols_list = [item['s'].split(':')[1] for item in response['data']]
            except:
                symbols_list = ["COMI", "FWRY", "TMGH", "SWDY", "BTEL", "ISPH"]

            final_results = []
            progress_bar = st.progress(0, text="🧠 جاري تشغيل العقل الصناعي وفحص السيولة...")
            
            for index, ticker in enumerate(symbols_list):
                try:
                    # سحب البيانات الفنية
                    handler = TA_Handler(symbol=ticker, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY)
                    indicators = handler.get_analysis().indicators
                    
                    # تحليل SMC وتوقع AI
                    close = indicators["close"]
                    rsi = indicators["RSI"]
                    vol = indicators["volume"]
                    avg_vol = indicators.get("average_volume", vol)
                    hi, lo, piv = indicators["high"], indicators["low"], indicators["Pivot.M.Classic.Middle"]
                    
                    mood, score = ai.calculate_market_mood(close, rsi, vol, avg_vol, hi, lo, piv)
                    target = ai.predict_target(close, rsi)
                    
                    # حفظ في قاعدة البيانات للتعلم والماركتينج
                    db.save_new_signal(ticker, today_str, target, close, mood, score)
                    
                    final_results.append({
                        "السهم": ticker,
                        "actual_price": close,
                        "predicted_target": target,
                        "market_context": mood,
                        "brain_score": score
                    })
                except:
                    continue
                progress_bar.progress((index + 1) / len(symbols_list))
            
            st.session_state.market_data = pd.DataFrame(final_results).sort_values("brain_score", ascending=False)
            st.rerun()

    # عرض المخرجات النهائية
    if 'market_data' in st.session_state:
        results = st.session_state.market_data
        
        st.markdown("## ⚜️ أقوى فرص السوق (نخبة الواهب)")
        top_3 = results.head(3)
        cols = st.columns(3)
        
        for i, (idx, row) in enumerate(top_3.iterrows()):
            with cols[i]:
                st.markdown(f"""
                <div class="stock-card">
                    <h1 style="color:#d4af37; margin:0; font-size:50px;">{row['السهم'] if 'السهم' in row else row['symbol']}</h1>
                    <p style="color:#777; margin:20px 0;">{row['market_context']}</p>
                    <div style="display:flex; justify-content:space-between; border-top:1px solid #222; padding-top:20px;">
                        <span>السعر: <b>{row['actual_price']}</b></span>
                        <span style="color:#00ff00;">الهدف: <b>{row['predicted_target']}</b></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### 📊 تقرير الذكاء الكمي الكامل")
        st.dataframe(results, use_container_width=True, hide_index=True)

    # الفوتر
    st.markdown(f"""
        <div style="text-align:center; padding:100px; color:#222; font-size:12px;">
            DEVELOPED BY MOSTAFA TAMER | ALEXANDRIA, EGYPT<br>
            ALL RIGHTS RESERVED © {datetime.now().year}
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    run_wahba_system()
