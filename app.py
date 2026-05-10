import streamlit as st
import pandas as pd
import sqlite3
import threading
import time
from datetime import datetime
from binance.client import Client
from tradingview_ta import TA_Handler, Interval

# =================================================================
# الإعدادات الأساسية
# =================================================================
DB_NAME = "wahba_live_pnl.db"
SYMBOL = "BTCUSDT"
STOP_LOSS_LIMIT = 190.0 # صمام الأمان النهائي

# =================================================================
# إدارة البيانات (الربح والخسارة الفعلي)
# =================================================================
class TradeAccountant:
    @staticmethod
    def init_db():
        with sqlite3.connect(DB_NAME) as conn:
            # سجل الصفقات لحساب الأرباح والخسائر
            conn.execute("""
                CREATE TABLE IF NOT EXISTS journal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entry_time TEXT,
                    entry_price REAL,
                    exit_price REAL,
                    pnl REAL,
                    final_balance REAL
                )
            """)
            conn.commit()

    @staticmethod
    def record_trade(entry_p, exit_p, pnl, current_bal):
        with sqlite3.connect(DB_NAME) as conn:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute("""
                INSERT INTO journal (entry_time, entry_price, exit_price, pnl, final_balance)
                VALUES (?, ?, ?, ?, ?)
            """, (now, entry_p, exit_p, pnl, current_bal))
            conn.commit()

# =================================================================
# العقل المدبر (المراقب المالي)
# =================================================================
def brain_worker(api_key, api_secret, testnet):
    client = Client(api_key, api_secret, testnet=testnet)
    TradeAccountant.init_db()
    
    # متغيرات لمتابعة الصفقة المفتوحة
    in_position = False
    entry_price = 0.0

    while True:
        try:
            # 1. جلب الرصيد الحالي من المنصة
            asset = client.get_asset_balance(asset='USDT')
            current_balance = float(asset['free']) if asset else 0.0

            # 🛡️ شرط الأمان: لو الرصيد نزل لـ 190$، اقفل فوراً
            if current_balance <= STOP_LOSS_LIMIT:
                st.session_state.is_running = False
                break

            # 2. تحليل السوق (فريم 5 دقائق للنمو السريع)
            handler = TA_Handler(symbol=SYMBOL, exchange="BINANCE", screener="crypto", 
                                interval=Interval.INTERVAL_5_MINUTES, timeout=10)
            analysis = handler.get_analysis().summary['RECOMMENDATION']
            live_price = float(client.get_symbol_ticker(symbol=SYMBOL)['price'])

            # 3. منطق التداول الحقيقي (شراء وبيع وحساب المكسب)
            if not in_position and analysis == "STRONG_BUY":
                # دخول صفقة شراء
                client.create_order(symbol=SYMBOL, side='BUY', type='MARKET', quantity=0.001)
                entry_price = live_price
                in_position = True
            
            elif in_position and analysis == "STRONG_SELL":
                # خروج من الصفقة (بيع)
                client.create_order(symbol=SYMBOL, side='SELL', type='MARKET', quantity=0.001)
                pnl = (live_price - entry_price) * 0.001 # حساب الربح أو الخسارة من هذه الصفقة
                
                # تسجيل النتيجة في "كشف الحساب"
                TradeAccountant.record_trade(entry_price, live_price, pnl, current_balance + pnl)
                in_position = False

        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(60) # تحديث كل دقيقة

# =================================================================
# الواجهة (عداد الأرباح والخسائر اللحظي)
# =================================================================
def main():
    st.set_page_config(page_title="Wahba Live PnL", layout="wide")
    st.title("💸 مراقب الأرباح والخسائر اللحظي")

    with st.sidebar:
        ak = st.text_input("Binance API Key", type="password")
        as_key = st.text_input("Binance Secret Key", type="password")
        is_test = st.checkbox("وضع الاختبار (أموال وهمية)", value=True)
        if st.button("🚀 تشغيل المحرك"):
            threading.Thread(target=brain_worker, args=(ak, as_key, is_test), daemon=True).start()
            st.success("المحرك يعمل ويراقب المحفظة!")

    if ak and as_key:
        # عرض الرصيد والنمو
        with sqlite3.connect(DB_NAME) as conn:
            df = pd.read_sql_query("SELECT * FROM journal ORDER BY id DESC", conn)
            
            if not df.empty:
                last_bal = df.iloc[0]['final_balance']
                total_pnl = df['pnl'].sum()
                
                # عداد كبير يوضح "بتكثر ولا بتنزل"
                c1, c2 = st.columns(2)
                c1.metric("الرصيد الحالي", f"${last_bal:,.2f}", delta=f"{total_pnl:,.2f}")
                c2.metric("حالة الأمان", "آمن" if last_bal > STOP_LOSS_LIMIT else "خطر")

                st.subheader("📈 مسار نمو الصفقات")
                st.line_chart(df.set_index('entry_time')['final_balance'])
                
                st.subheader("📝 كشف حساب الصفقات")
                st.table(df[['entry_time', 'pnl', 'final_balance']].head(10))
            else:
                st.info("في انتظار تنفيذ أول صفقة لحساب النتائج...")

if __name__ == "__main__":
    main()
