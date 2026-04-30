import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="وهبة للمحلل مصطفي تامر", layout="wide")

st.title("💎 منصة وهبة للتحليل المالي")
st.markdown("### 👨‍💼 تطوير: المحلل مصطفي تامر")
st.write("---")

symbols = [
    "ABUK.CA", "ACGC.CA", "ADCI.CA", "ADIB.CA", "AFMC.CA", "AIH.CA", "AIVC.CA", "AMER.CA", "AMOC.CA", 
    "ANFI.CA", "APME.CA", "ARAB.CA", "ASPI.CA", "ASRE.CA", "ASU.CA", "ATLC.CA", "ATWB.CA", "AUCC.CA", 
    "AXPH.CA", "BINP.CA", "BINV.CA", "BIOC.CA", "BLGN.CA", "BMOH.CA", "BTFH.CA", "CAED.CA", "CAFR.CA", 
    "CAPW.CA", "CCAP.CA", "CERA.CA", "CFGH.CA", "CHWP.CA", "CICH.CA", "CIRA.CA", "CLHO.CA", "CNCR.CA", 
    "CNFR.CA", "COMI.CA", "COPR.CA", "CSAG.CA", "CVLC.CA", "DAPH.CA", "DCRC.CA", "DCTL.CA", "DOMT.CA", 
    "EALR.CA", "EATM.CA", "EBSC.CA", "ECAP.CA", "ECHG.CA", "ECOS.CA", "EDAB.CA", "EDIN.CA", "EFID.CA", 
    "EGAS.CA", "EGBE.CA", "EGCH.CA", "EGDC.CA", "EGDH.CA", "EGFI.CA", "EGID.CA", "EGLI.CA", "EGSG.CA", 
    "EGTB.CA", "EHDR.CA", "EIMC.CA", "EIPC.CA", "EKHOA.CA", "ELKA.CA", "ELSH.CA", "EMFD.CA", "ENGC.CA", 
    "EPCO.CA", "ESIC.CA", "ESRS.CA", "ETEL.CA", "EXPA.CA", "FAHL.CA", "FAIT.CA", "FCIE.CA", "FIIT.CA", 
    "FWRY.CA", "GTHE.CA", "GZCC.CA", "HELI.CA", "HERO.CA", "HRHO.CA", "IFAP.CA", "IHCX.CA", "INFI.CA", 
    "IRGC.CA", "ISDI.CA", "ISPH.CA", "JUFO.CA", "KABO.CA", "KIMA.CA", "LREI.CA", "MACRO.CA", "MASR.CA", 
    "MDWA.CA", "MEPA.CA", "MFPC.CA", "MNHD.CA", "MPCO.CA", "MTIE.CA", "OBET.CA", "ODPD.CA", "ODIN.CA", 
    "OIH.CA", "OPAT.CA", "ORAS.CA", "ORHD.CA", "ORWE.CA", "PHDC.CA", "PIOH.CA", "PRDC.CA", "PSDC.CA", 
    "QNBA.CA", "RAFT.CA", "RMDA.CA", "RTVC.CA", "SAEI.CA", "SCFM.CA", "SEMO.CA", "SHAC.CA", "SIAG.CA", 
    "SKPC.CA", "SPHT.CA", "SVCP.CA", "SWDY.CA", "SYVI.CA", "TAQA.CA", "TMGH.CA", "TRGO.CA", "UEGC.CA", 
    "UNTR.CA", "UPLD.CA", "UTOP.CA", "VIRA.CA", "ZEIRA.CA"
]

results = []

st.info("نظام وهبة: تحميل مجمع وسريع (Batch Loading).")

if st.button("بدء المسح الآن"):
    with st.spinner('وهبة تقوم بتحميل بيانات السوق بالكامل...'):
        # تحميل البيانات دفعة واحدة (أسرع بكتير)
        data = yf.download(symbols, period="3mo", group_by='ticker', progress=False)
        
        for s in symbols:
            try:
                # سحب بيانات السهم من المصفوفة الكبيرة
                df = data[s]
                if len(df) > 50:
                    ma50 = df['Close'].rolling(50).mean().iloc[-1]
                    today_close = df['Close'].iloc[-1]
                    
                    if today_close > ma50:
                        results.append({
                            "السهم": s,
                            "السعر الحالي": round(float(today_close), 2),
                            "المتوسط (MA50)": round(float(ma50), 2),
                            "القرار": "صاعد 📈"
                        })
            except:
                continue

    if results:
        st.table(pd.DataFrame(results))
    else:
        st.warning("لا توجد أسهم مطابقة اليوم.")

st.markdown("""---
**⚠️ إخلاء مسؤولية:** هذه الأداة للتحليل التعليمي فقط، والقرار النهائي مسؤوليتك.
""")