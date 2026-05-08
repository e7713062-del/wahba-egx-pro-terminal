import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import numpy as np
import requests
import os
from datetime import datetime
import pytz
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# --- 1. إعدادات الوقت والتخزين الذكي ---
egypt_tz = pytz.timezone('Africa/Cairo')
today_date = datetime.now(egypt_tz).strftime("%Y-%m-%d")
DB_FILE = f"wahba_swing_db_{today_date}.csv"

# --- 2. ماتور ذكاء اصطناعي مخصص للسوينج ---
class WahbaSwingEngine:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=300, max_depth=12, random_state=42)
        self.scaler = StandardScaler()

    def train_and_predict(self, df):
        try:
            features = ['Price', 'Score', 'S1', 'P', 'R1', 'RSI']
            X = df[features].values
            # في السوينج بنستهدف ربح من 5% لـ 15% بناءً على قوة السكور
            y = df['Price'] * (1 + (df['Score'] / 50)) 
            
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled, y)
            predictions = self.model.predict(X_scaled)
            
            df['Target'] = np.round(predictions, 2)
            df['Potential'] = np.round(((df['Target'] - df['Price']) / df['Price']) * 100, 1)
            df['Confidence'] = "High (Swing AI)"
            return df
        except:
            df['Target'] = np.round(df['Price'] * 1.07, 2)
            df['Potential'] = 7.0
            df['Confidence'] = "Standard"
            return df

# --- 3. محرك جلب البيانات وتجنب الحظر ---
def get_swing_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=10).json()
        symbols = [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except:
        symbols = ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK", "ETEL", "HELI", "ORAS", "ESRS"]

    data = []
    p_bar = st.progress(0)
    status = st.empty()
    
    for i, sym in enumerate(symbols):
        status.text(f"جاري فحص فرص السوينج: {sym}")
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=5)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            
            # فلتر السوينج: قوة الاتجاه + الـ RSI
            score = 0
            # 1. تقاطع المتوسطات أو التوصية العامة
            rec = analysis.summary["RECOMMENDATION"]
            if "STRONG_BUY" in rec: score += 4
            elif "BUY" in rec: score += 2
            
            # 2. مؤشر القوة النسبية (RSI) - السوينج بيحب الـ 40 لـ 60 (بداية انطلاق)
            rsi = ind.get("RSI", 50)
            if 45 <= rsi <= 65: score += 3
            
            # 3. السعر فوق الارتكاز الشهري (إشارة قوة)
            if ind.get("close") > ind.get("Pivot.M.Classic.Middle"): score += 3

            data.append({
                "Symbol": sym, "Price": round(ind.get("close"), 2), "Score": score,
                "S1": round(ind.get("Pivot.M.Classic.S1"), 2),
                "P": round(ind.get("Pivot.M.Classic.Middle"), 2),
                "R1": round(ind.get("Pivot.M.Classic.R1"), 2),
                "RSI": round(rsi, 1)
            })
        except: continue
        p_bar.progress((i + 1) / len(symbols))
    
    df = pd.DataFrame(data)
    if not df.empty:
        engine = WahbaSwingEngine()
        df = engine.train_and_predict(df)
        df.to_csv(DB_FILE, index=False)
    
    status.empty()
    p_bar.empty()
    return df

# --- 4. الواجهة (UI) ---
st.set_page_config(page_title="Wahba Swing AI", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif; direction: rtl; }
    .stApp { background-color: #000; color: #fff; }
    .header { text-align: center; padding: 30px; border-bottom: 2px solid #d4af37; }
    .gold { color: #d4af37; }
    .card { background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 15px; padding: 20px; border-top: 4px solid #d4af37; margin-bottom: 20px; }
    .target-box { background: #1a1a00; border: 1px dashed #d4af37; border-radius: 10px; padding: 15px; margin: 15px 0; text-align: center; }
    .potential { color: #00ff00; font-size: 18px; font-weight: bold; }
    .level-item { text-align: center; background: #050505; padding: 5px; border-radius: 5px; border: 1px solid #111; }
    .label { font-size: 10px; color: #666; }
    .num { font-size: 13px; color: #d4af37; font-family: monospace; }
    </style>
    <div class="header">
        <h1 class="gold">WAHBA SWING AI 💎</h1>
        <p>محرك الذكاء الاصطناعي لاقتناص الفرص الأسبوعية - EGX</p>
    </div>
""", unsafe_allow_html=True)

if st.button("تحديث وتحليل فرص السوينج لليوم"):
    df_final = get_swing_data()
    
    if not df_final.empty:
        # عرض الفرص اللي السكور بتاعها عالي (7 فما فوق)
        opportunities = df_final[df_final['Score'] >= 5].sort_values(by="Score", ascending=False)
        
        st.markdown(f"### 🎯 تم رصد {len(opportunities)} فرصة سوينج محتملة")
        
        for i in range(0, len(opportunities), 3):
            cols = st.columns(3)
            chunk = opportunities.iloc[i:i+3]
            for j, (idx, row) in enumerate(chunk.iterrows()):
                with cols[j]:
                    st.markdown(f"""
                    <div class="card">
                        <div style="display:flex; justify-content:space-between;">
                            <span style="font-size:24px; font-weight:900;" class="gold">{row['Symbol']}</span>
                            <span style="background:#d4af37; color:#000; padding:2px 8px; border-radius:5px; font-weight:bold;">Score: {row['Score']}</span>
                        </div>
                        <div style="margin:10px 0;">السعر الحالي: <b>{row['Price']} ج.م</b></div>
                        <div class="target-box">
                            <div style="font-size:12px;">الهدف السعري المتوقع (AI Target)</div>
                            <div style="font-size:22px; font-weight:bold; color:#00ff00;">{row['Target']}</div>
                            <div class="potential">ربح متوقع: {row['Potential']}% +</div>
                        </div>
                        <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:5px;">
                            <div class="level-item"><span class="label">دعم</span><br><span class="num">{row['S1']}</span></div>
                            <div class="level-item"><span class="label">ارتكاز</span><br><span class="num">{row['P']}</span></div>
                            <div class="level-item"><span class="label">مقاومة</span><br><span class="num">{row['R1']}</span></div>
                        </div>
                        <div style="font-size:9px; color:#444; margin-top:10px; text-align:center;">Mode: {row['Confidence']} | RSI: {row['RSI']}</div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.error("لا توجد بيانات متاحة حالياً.")
