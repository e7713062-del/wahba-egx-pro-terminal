# ==============================================================================
# 👑 PROJECT: WAHBA EGX - THE SUPREME QUANTUM ARCHITECT (v12.0)
# 👨‍💻 MASTER ARCHITECT: MOSTAFA TAMER | ALEXANDRIA, EGYPT
# 🏛️ SYSTEM: NEURAL FEEDBACK, SMC LOGIC & STRUCTURAL EVOLUTION
# ==============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import requests
import sqlite3
import pytz
import os
import time
from datetime import datetime
from sklearn.linear_model import LinearRegression
from tradingview_ta import TA_Handler, Interval

# ------------------------------------------------------------------------------
# 1. المنسق الإداري للبيانات (Database & Evolution Management)
# ------------------------------------------------------------------------------
class DatabaseManager:
    def __init__(self):
        self.db_path = 'wahba_supreme_memory.db'
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS evolution_vault 
                         (symbol TEXT, date TEXT, predicted REAL, actual REAL, accuracy REAL)''')
            conn.commit()

    def update_accuracy(self, symbol, current_price):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT rowid, predicted FROM evolution_vault WHERE symbol=? AND actual IS NULL", (symbol,))
            record = c.fetchone()
            if record:
                rowid, pred_price = record
                # منع القسمة على صفر في حالة الأسهم متناهية الصغر
                accuracy = 1 - abs((current_price - pred_price) / (pred_price if pred_price != 0 else 1))
                c.execute("UPDATE evolution_vault SET actual=?, accuracy=? WHERE rowid=?", (current_price, accuracy, rowid))
                conn.commit()

    def get_historical_trust(self, symbol):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT AVG(accuracy) FROM evolution_vault WHERE symbol=?", (symbol,))
            res = c.fetchone()[0]
            return res if res is not None else 0.75

    def store_prediction(self, symbol, date, predicted):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO evolution_vault (symbol, date, predicted) VALUES (?, ?, ?)", 
                      (symbol, date, predicted))
            conn.commit()

# ------------------------------------------------------------------------------
# 2. محرك الذكاء السياقي (Neural & Context Logic Engine)
# ------------------------------------------------------------------------------
class BrainEngine:
    def __init__(self, db_manager):
        self.db = db_manager
        self.model = self._train_initial_model()

    def _train_initial_model(self):
        # نموذج مبدئي للتدريب يعتمد على علاقة السعر بالزخم (RSI)
        model = LinearRegression()
        X = np.array([[10, 30], [50, 50], [5, 20], [100, 70], [30, 45]])
        y = np.array([10.8, 52.5, 5.6, 105.0, 31.5])
        model.fit(X, y)
        return model

    def analyze_scenarios(self, symbol, data):
        c, r, v = data['close'], data['rsi'], data['vol']
        av, pv, hi, lo = data['avg_vol'], data['pivot'], data['high'], data['low']
        
        trust = self.db.get_historical_trust(symbol)
        score = 0
        msg = "🔄 استقرار: السوق في منطقة توازن"

        # سيناريوهات SMC الاحترافية
        if c > hi and v < (av * 0.75):
            msg, score = "⚠️ فخ سيولة: اختراق كاذب (Fakeout)", -2.5
        elif c < pv and r < 35 and v > (av * 1.2):
            msg, score = "💎 تجميع حيتان: دخول سيولة ذكية (Accumulation)", 3.0
        elif r < 20:
            msg, score = "🔥 ذروة بيع: توقع ارتداد عنيف (Oversold)", 2.8
        elif c > pv and v > av:
            msg, score = "📈 صعود مؤسسي: اتجاه قوي مدعوم سيولياً", 1.8
        
        return msg, score * trust

    def predict_target(self, close, rsi):
        pred = self.model.predict(np.array([[close, rsi]]))[0]
        return round(float(pred), 2)

# ------------------------------------------------------------------------------
# 3. مدير الواجهة الرسومية (Premium UI Architecture)
# ------------------------------------------------------------------------------
class UIHandler:
    @staticmethod
    def inject_styles():
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;700;900&display=swap');
            * { font-family: 'Tajawal', sans-serif; }
            .stApp { background-color: #030303; color: #ffffff; }
            
            .main-header {
                background: linear-gradient(180deg, #121212 0%, #000 100%);
                padding: 80px 20px; text-align: center;
                border-bottom: 5px solid #d4af37; border-radius: 0 0 100px 100px;
                box-shadow: 0 20px 60px rgba(0,0,0,1); margin-bottom: 60px;
                animation: fadeIn 2s ease-in;
            }
            @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
            
            .logo-text { font-size: 90px; font-weight: 900; color: #fff; margin: 0; letter-spacing: -3px; }
            .logo-text span { color: #d4af37; text-shadow: 0 0 40px rgba(212,175,55,0.6); }
            
            .elite-card {
                background: linear-gradient(145deg, #111, #080808);
                border: 1px solid #d4af37; border-radius: 40px; padding: 45px;
                box-shadow: 10px 10px 30px rgba(0,0,0,0.5); transition: 0.6s;
            }
            .elite-card:hover { transform: scale(1.03) translateY(-10px); border-color: #fff; }
            
            .metric-box { border-left: 2px solid #d4af37; padding-left: 15px; margin: 10px 0; }
            </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def render_header():
        st.markdown("""
            <div class="main-header">
                <h1 class="logo-text">WAHBA <span>EGX</span></h1>
                <p style="color:#666; font-size:20px; letter-spacing:8px; font-weight:300;">THE SUPREME QUANTUM ARCHITECT v12.0</p>
                <p style="color:#333; margin-top:15px;">Designed by Mostafa Tamer | Alexandria, Egypt</p>
            </div>
        """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 4. التجميع والتشغيل النهائي (The Main Assembly)
# ------------------------------------------------------------------------------
def main():
    db = DatabaseManager()
    brain = BrainEngine(db)
    UIHandler.inject_styles()
    UIHandler.render_header()
    
    egypt_tz = pytz.timezone('Africa/Cairo')
    now = datetime.now(egypt_tz)

    with st.sidebar:
        st.markdown("### 🛠️ Terminal Control")
        st.info(f"📅 {now.strftime('%B %d, %Y')}")
        st.info(f"⏰ {now.strftime('%I:%M %p')} Cairo Time")
        st.divider()
        run_scan = st.button("RUN QUANTUM EVOLUTION SCAN 🚀")
        load_mem = st.button("RECALL HISTORICAL MEMORY 📁")

    if run_scan:
        try:
            url = "https://scanner.tradingview.com/egypt/scan"
            res = requests.post(url, json={"filter": [{"left": "type", "operation": "in_range", "right": ["stock"]}], "markets": ["egypt"], "columns": ["name"]}, timeout=15).json()
            symbols = [item['s'].split(':')[1] for item in res['data']]
        except:
            symbols = ["COMI", "FWRY", "TMGH", "SWDY", "BTEL", "ISPH", "EKHO", "JUFO"]

        results = []
        p_bar = st.progress(0, text="🧠 جارٍ تفعيل الخلايا العصبية وفحص السيولة المؤسسية...")
        
        for i, sym in enumerate(symbols):
            try:
                handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY)
                analysis = handler.get_analysis()
                ind = analysis.indicators
                
                # تحديث الدقة للهيكل البرمجي
                db.update_accuracy(sym, ind["close"])
                
                # التوقع والتحليل
                data_pack = {
                    'close': ind["close"], 'rsi': ind["RSI"], 'vol': ind["volume"],
                    'avg_vol': ind.get("average_volume", ind["volume"]),
                    'pivot': ind["Pivot.M.Classic.Middle"], 'high': ind["high"], 'low': ind["low"]
                }
                
                msg, score = brain.analyze_scenarios(sym, data_pack)
                target = brain.predict_target(data_pack['close'], data_pack['rsi'])
                
                # تخزين التوقع الجديد للمستقبل (Evolution Step)
                db.store_prediction(sym, now.strftime("%Y-%m-%d"), target)

                results.append({
                    "السهم": sym, "إغلاق": data_pack['close'], "هدف الـ AI": target,
                    "نمو %": round(((target - data_pack['close']) / data_pack['close']) * 100, 2),
                    "الرؤية السياقية": msg, "Brain Score": round(score, 2)
                })
            except: continue
            p_bar.progress((i + 1) / len(symbols))
        
        p_bar.empty()
        final_df = pd.DataFrame(results).sort_values(by=["Brain Score", "نمو %"], ascending=False)
        st.session_state.master_df = final_df

    if 'master_df' in st.session_state:
        df = st.session_state.master_df
        
        st.markdown("## ⚜️ THE ELITE SELECTIONS")
        top_cols = st.columns(3)
        for idx, row in enumerate(df.head(3).iterrows()):
            with top_cols[idx]:
                st.markdown(f"""
                    <div class="elite-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h1 style="color:#d4af37; margin:0; font-size:45px;">{row[1]['السهم']}</h1>
                            <span style="background:#d4af37; color:#000; padding:5px 15px; border-radius:50px; font-weight:900; font-size:12px;">SCORE: {row[1]['Brain Score']}</span>
                        </div>
                        <p style="color:#fff; font-size:16px; margin:25px 0; height:50px;">{row[1]['الرؤية السياقية']}</p>
                        <div class="metric-box">
                            <small style="color:#666;">Current Price</small><br>
                            <span style="font-size:24px; font-weight:900;">{row[1]['إغلاق']}</span>
                        </div>
                        <div class="metric-box" style="border-color:#00ff00;">
                            <small style="color:#666;">Quantum Target</small><br>
                            <span style="font-size:24px; font-weight:900; color:#00ff00;">{row[1]['هدف الـ AI']}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### 📊 FULL CONTEXTUAL INTELLIGENCE REPORT")
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown(f"""
        <div style="text-align:center; padding:100px 20px; border-top:1px solid #111; margin-top:100px;">
            <p style="color:#d4af37; font-weight:900; font-size:18px; margin-bottom:20px;">⚖️ OFFICIAL SUPREME DISCLAIMER</p>
            <p style="color:#444; font-size:13px; max-width:900px; margin: 0 auto; line-height:2;">
                تم تطوير هذا النظام بواسطة <b>مصطفى تامر</b> كأداة تحليلية متقدمة تعتمد على منطق SMC والذكاء الاصطناعي التطوري. 
                النظام يقوم بتطوير هيكله البرمجي بناءً على دقة التوقعات السابقة. المطور غير مسؤول عن أي قرارات استثمارية.
                <br><br>
                <b>ALL RIGHTS RESERVED © {now.year} | ARCHITECTED BY MOSTAFA TAMER</b>
            </p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
