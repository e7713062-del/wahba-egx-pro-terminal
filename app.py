import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import pytz
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# --- 1. محرك الذكاء الاصطناعي (Wahba AI Engine) ---
class WahbaAIEngine:
    def __init__(self, n_estimators=200):
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            criterion='squared_error',
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False

    def prepare_data(self, df):
        features = ['Price', 'Score', 'S1', 'P', 'R1']
        df_clean = df.copy()
        for col in features:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        df_clean = df_clean.dropna(subset=features)
        return df_clean, features

    def train_engine(self, df):
        df_clean, features = self.prepare_data(df)
        if len(df_clean) < 5: return False
        X = df_clean[features].values
        y = df_clean['Price'] * (1 + (df_clean['Score'] / 100))
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True
        return True

    def get_predictions(self, df):
        if not self.is_trained:
            df['Target'] = np.round(df['Price'] * 1.03, 2)
            df['Confidence'] = "Low (Heuristic)"
            return df
        df_clean, features = self.prepare_data(df)
        if df_clean.empty: return df
        X_scaled = self.scaler.transform(df_clean[features].values)
        predictions = self.model.predict(X_scaled)
        df.loc[df_clean.index, 'Target'] = np.round(predictions, 2)
        df['Confidence'] = "High (AI Mode)"
        return df

# --- 2. إعدادات الوقت والصفحة ---
egypt_tz = pytz.timezone('Africa/Cairo')
today_key = datetime.now(egypt_tz).strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba Intelligence AI", layout="wide")

# --- 3. تصميم الـ CSS الثابت ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif; }
    .stApp { background-color: #000000; color: #ffffff; }
    .nav-bar { text-align: center; padding: 20px; border-bottom: 2px solid #d4af37; margin-bottom: 20px; }
    .logo-text { font-size: 30px; font-weight: 900; color: #fff; }
    .logo-text span { color: #d4af37; }
    .section-header { color: #d4af37; border-right: 5px solid #d4af37; padding-right: 15px; margin: 30px 0; font-size: 24px; font-weight: bold; text-align: right; direction: rtl; }
    .stock-card { background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 15px; padding: 20px; margin-bottom: 20px; border-top: 3px solid #d4af37; direction: rtl; }
    .symbol-name { font-size: 24px; font-weight: 900; color: #d4af37; }
    .target-box { background: #1a1a00; border: 1px dashed #d4af37; padding: 12px; border-radius: 8px; margin-top: 15px; text-align: center; }
    .target-price { font-size: 22px; color: #00ff00; font-weight: bold; }
    .levels-grid { display: flex; justify-content: space-around; margin-top: 15px; background: #050505; padding: 10px; border-radius: 8px; }
    .level-item { text-align: center; }
    .label { font-size: 11px; color: #666; display: block; }
    .num { font-size: 14px; font-weight: bold; color: #d4af37; }
    .stButton>button { background: linear-gradient(45deg, #d4af37, #f4cf67) !important; color: #000 !important; font-weight: 900 !important; border-radius: 10px !important; height: 50px !important; width: 100% !important; border: none !important; }
    </style>
    <div class="nav-bar">
        <div class="logo-text">WAHBA <span>INTELLIGENCE AI</span></div>
    </div>
""", unsafe_allow_html=True)

# --- 4. جلب البيانات ---
@st.cache_data(ttl=86400)
def fetch_symbols(key):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=15).json()
        return [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except: return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO"]

def run_scan():
    symbols = fetch_symbols(today_key)
    data = []
    p_bar = st.progress(0)
    msg = st.empty()
    
    for i, sym in enumerate(symbols):
        msg.text(f"تحليل: {sym}")
        try:
            handler = TA_Handler(symbol=sym, screener="egypt", exchange="EGX", interval=Interval.INTERVAL_1_DAY, timeout=7)
            analysis = handler.get_analysis()
            ind = analysis.indicators
            rec = analysis.summary["RECOMMENDATION"]
            
            score = 0
            if "STRONG_BUY" in rec: score += 5
            elif "BUY" in rec: score += 3
            if ind.get("RSI") and 40 <= ind.get("RSI") <= 68: score += 3
            if ind.get("close") > ind.get("Pivot.M.Classic.Middle"): score += 2

            data.append({
                "Symbol": sym, "Price": round(ind.get("close"), 2), "Score": score,
                "S1": round(ind.get("Pivot.M.Classic.S1"), 2),
                "P": round(ind.get("Pivot.M.Classic.Middle"), 2),
                "R1": round(ind.get("Pivot.M.Classic.R1"), 2)
            })
        except: continue
        p_bar.progress((i + 1) / len(symbols))
    
    df = pd.DataFrame(data)
    if not df.empty:
        msg.text("جاري تشغيل محرك الذكاء الاصطناعي...")
        engine = WahbaAIEngine()
        engine.train_engine(df)
        df = engine.get_predictions(df)
    
    msg.empty()
    p_bar.empty()
    return df

# --- 5. العرض النهائي ---
if st.button("بدء تحليل السوق بواسطة AI"):
    results = run_scan()
    if not results.empty:
        st.markdown('<div class="section-header">نتائج فحص ماتور الذكاء الاصطناعي</div>', unsafe_allow_html=True)
        top_list = results.sort_values(by="Score", ascending=False).head(12)
        
        # تقسيم العرض لـ 3 أعمدة
        for i in range(0, len(top_list), 3):
            cols = st.columns(3)
            chunk = top_list.iloc[i:i+3]
            for j, (idx, row) in enumerate(chunk.iterrows()):
                with cols[j]:
                    # استخدام قالب نصي نظيف لتجنب أخطاء العرض
                    card_template = """
                    <div class="stock-card">
                        <div style="display: flex; justify-content: space-between;">
                            <span class="symbol-name">{sym}</span>
                            <span style="color:#d4af37;">Score: {sc}/10</span>
                        </div>
                        <div style="margin-top:10px;">السعر الحالي: <b>{pr}</b> ج.م</div>
                        <div class="target-box">
                            <div style="font-size:11px; color:#d4af37;">هدف AI المتوقع</div>
                            <div class="target-price">{trg}</div>
                            <div style="font-size:9px; color:#555;">{conf}</div>
                        </div>
                        <div class="levels-grid">
                            <div class="level-item"><span class="label">دعم</span><span class="num">{s1}</span></div>
                            <div class="level-item"><span class="label">ارتكاز</span><span class="num">{p}</span></div>
                            <div class="level-item"><span class="label">مقاومة</span><span class="num">{r1}</span></div>
                        </div>
                    </div>
                    """
                    st.markdown(card_template.format(
                        sym=row['Symbol'], sc=row['Score'], pr=row['Price'],
                        trg=row['Target'], conf=row['Confidence'],
                        s1=row['S1'], p=row['P'], r1=row['R1']
                    ), unsafe_allow_html=True)
