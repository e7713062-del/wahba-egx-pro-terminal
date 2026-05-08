import streamlit as st
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import pytz
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# ==========================================
# 1. ماتور الذكاء الاصطناعي (Wahba AI Engine)
# ==========================================
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
        # الميزات الأساسية للتعلم
        features = ['Price', 'Score', 'S1', 'P', 'R1']
        df_clean = df.copy()
        for col in features:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        df_clean = df_clean.dropna(subset=features)
        return df_clean, features

    def train_engine(self, df):
        df_clean, features = self.prepare_data(df)
        if len(df_clean) < 5:
            return False
        
        X = df_clean[features].values
        # معادلة الهدف: السعر المتوقع بناءً على جودة السكور والمؤشرات
        y = df_clean['Price'] * (1 + (df_clean['Score'] / 100))
        
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True
        return True

    def get_predictions(self, df):
        if not self.is_trained:
            df['Target'] = df['Price'] * 1.03
            df['Confidence'] = "Low (Heuristic)"
            return df
            
        df_clean, features = self.prepare_data(df)
        if df_clean.empty: return df
        
        X_scaled = self.scaler.transform(df_clean[features].values)
        predictions = self.model.predict(X_scaled)
        
        df.loc[df_clean.index, 'Target'] = np.round(predictions, 2)
        df['Confidence'] = "High (AI Mode)"
        return df

# ==========================================
# 2. إعدادات الصفحة والتنسيق (UI)
# ==========================================
egypt_tz = pytz.timezone('Africa/Cairo')
now_egypt = datetime.now(egypt_tz)
today_key = now_egypt.strftime("%Y-%m-%d")

st.set_page_config(page_title="Wahba Intelligence AI", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * { font-family: 'Tajawal', sans-serif; }
    .stApp { background-color: #000000; color: #ffffff; }
    
    .nav-bar { text-align: center; padding: 30px; border-bottom: 2px solid #d4af37; margin-bottom: 20px; }
    .logo-text { font-size: 35px; font-weight: 900; color: #fff; letter-spacing: 2px; }
    .logo-text span { color: #d4af37; }
    
    .section-header { 
        color: #d4af37; border-right: 5px solid #d4af37; 
        padding-right: 15px; margin: 40px 0 20px 0; font-size: 24px; font-weight: bold; 
        text-align: right; direction: rtl;
    }
    
    .stock-card { 
        background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 15px; 
        padding: 20px; margin-bottom: 20px; border-top: 3px solid #d4af37; 
        direction: rtl; transition: 0.3s;
    }
    .stock-card:hover { border-color: #d4af37; background: #0f0f0f; }
    
    .symbol-name { font-size: 26px; font-weight: 900; color: #d4af37; }
    
    .target-box { 
        background: #1a1a00; border: 1px dashed #d4af37; 
        padding: 12px; border-radius: 8px; margin-top: 15px; text-align: center; 
    }
    .target-price { font-size: 22px; color: #00ff00; font-weight: bold; }
    
    .levels-grid { 
        display: flex; justify-content: space-around; margin-top: 15px; 
        background: #050505; padding: 10px; border-radius: 8px; border: 1px solid #111;
    }
    .level-item { text-align: center; }
    .label { font-size: 11px; color: #666; display: block; }
    .num { font-size: 14px; font-weight: bold; color: #d4af37; font-family: monospace; }
    
    .stButton>button { 
        background: linear-gradient(45deg, #d4af37, #f4cf67) !important; 
        color: #000 !important; font-weight: 900 !important; 
        border-radius: 10px !important; height: 55px !important; width: 100% !important;
        border: none !important; font-size: 18px !important;
    }
    </style>
    
    <div class="nav-bar">
        <div class="logo-text">WAHBA <span>INTELLIGENCE AI</span></div>
        <p style="color:#444; font-size:12px;">PREDICTIVE ENGINE • INSTITUTIONAL GRADE</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 3. وظائف جلب البيانات والتحليل
# ==========================================
@st.cache_data(ttl=86400)
def fetch_egx_list(date_key):
    try:
        url = "https://scanner.tradingview.com/egypt/scan"
        res = requests.post(url, json={"filter": [{"left": "market_cap_basic", "operation": "nempty"}], "markets": ["egypt"], "columns": ["name"]}, timeout=15).json()
        return [item['s'].split(':')[1] for item in res['data'] if not item['s'].split(':')[1].isdigit()]
    except:
        return ["COMI", "FWRY", "TMGH", "SWDY", "EKHO", "ABUK", "ETEL", "HELI"]

def run_strategic_scan():
    symbols = fetch_egx_list(today_key)
    raw_data = []
    p_bar = st.progress(0)
    status_text = st.empty()

    for i, sym in enumerate(symbols):
        status_text.text(f"تحليل ذكي للسهم: {sym}...")
        try:
            handler = TA_Handler(
                symbol=sym, screener="egypt", exchange="EGX", 
                interval=Interval.INTERVAL_1_DAY, timeout=10
            )
            analysis = handler.get_analysis()
            ind = analysis.indicators
            rec = analysis.summary["RECOMMENDATION"]
            
            # حساب سكور وهبة (Wahba Score)
            score = 0
            if "STRONG_BUY" in rec: score += 5
            elif "BUY" in rec: score += 3
            if ind.get("RSI") and 45 <= ind.get("RSI") <= 65: score += 3
            if ind.get("close") > ind.get("Pivot.M.Classic.Middle"): score += 2

            raw_data.append({
                "Symbol": sym, "Price": round(ind.get("close"), 2), "Score": score,
                "S1": round(ind.get("Pivot.M.Classic.S1"), 2),
                "P": round(ind.get("Pivot.M.Classic.Middle"), 2),
                "R1": round(ind.get("Pivot.M.Classic.R1"), 2),
                "RSI": round(ind.get("RSI"), 1)
            })
        except: continue
        p_bar.progress((i + 1) / len(symbols))
    
    df = pd.DataFrame(raw_data)
    
    # تدريب وتشغيل الماتور
    if not df.empty:
        status_text.text("جاري تدريب العقل الاصطناعي على بيانات السوق...")
        engine = WahbaAIEngine()
        if engine.train_engine(df):
            df = engine.get_predictions(df)
    
    status_text.empty()
    p_bar.empty()
    return df

# ==========================================
# 4. العرض النهائي للنتائج
# ==========================================
if st.button("تشغيل الماتور واستخراج الفرص"):
    results_df = run_strategic_scan()
    
    if not results_df.empty:
        st.markdown('<div class="section-header">أفضل الفرص بناءً على توقعات AI</div>', unsafe_allow_html=True)
        
        # عرض أعلى 12 سهم من حيث السكور
        top_stocks = results_df.sort_values(by="Score", ascending=False).head(12)
        
        rows = [top_stocks.iloc[i:i+3] for i in range(0, len(top_stocks), 3)]
        
        for row_data in rows:
            cols = st.columns(3)
            for i, (idx, row) in enumerate(row_data.iterrows()):
                with cols[i]:
                    st.markdown(f"""
                        <div class="stock-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span class="symbol-name">{row['Symbol']}</span>
                                <span style="color: #d4af37; font-weight: bold;">Score: {row['Score']}/10</span>
                            </div>
                            <div style="margin-top:10px; color:#bbb;">السعر الحالي: <span style="color:#fff; font-weight:bold;">{row['Price']} ج.م</span></div>
                            
                            <div class="target-box">
                                <div style="font-size: 11px; color: #d4af37; margin-bottom:5px;">السعر المستهدف (توقع AI)</div>
                                <div class="target-price">{row['Target']}</div>
                                <div style="font-size: 9px; color: #444; margin-top:5px;">Mode: {row['Confidence']}</div>
                            </div>

                            <div class="levels-grid">
                                <div class="level-item"><span class="label">دعم</span><span class="num">{row['S1']}</span></div>
                                <div class="level-item"><span class="label">ارتكاز</span><span class="num">{row['P']}</span></div>
                                <div class="level-item"><span class="label">مقاومة</span><span class="num">{row['R1']}</span></div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
    else:
        st.error("لم يتم العثور على بيانات كافية.")
