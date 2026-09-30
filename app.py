import os, sys, subprocess, pandas as pd, streamlit as st
from nirman_drishti import synthetic
from nirman_drishti.pipeline import handle
st.set_page_config(page_title="Nirman Drishti",layout="wide")
st.title("Nirman Drishti")
st.caption("Voice/text road requests -> habitation (HAB_ID) -> equity-weighted priority. DEMO DATA IS SYNTHETIC.")
habs,_,_=synthetic.make(); bids={k:v[0] for k,v in synthetic.BLOCKS.items()}
st.sidebar.write("AI engine: **%s**"%("Gemini" if os.getenv("GEMINI_API_KEY") else "offline fallback (set GEMINI_API_KEY)"))
t1,t2=st.tabs(["Resolve a request","Priority ranking"])
with t1:
    txt=st.text_area("Request (any language)",placeholder="Naugarh block, Ramdih ka khadanja dhans gaya hai")
    aud=st.file_uploader("or voice note",type=["ogg","mp3","wav","m4a"])
    if st.button("Resolve"):
        mime="audio/"+(aud.name.split(".")[-1] if aud else "ogg")
        out=handle(txt or None,aud.read() if aud else None,mime,habs,bids); st.json(out)
with t2:
    if not os.path.exists("data/priorities_demo.csv"): subprocess.run([sys.executable,"scripts/build_demo.py"],check=True)
    p=pd.read_csv("data/priorities_demo.csv")
    st.dataframe(p[["priority","HAB_NAME","block","TOT_POPULA","requests","dist_road_m","sanctioned"]].head(40),use_container_width=True)
    st.scatter_chart(p,x="requests",y="priority",color="block")
    st.caption("Quiet, remote, deprived habitations outrank loud, well-connected ones.")
