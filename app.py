import streamlit as st
import pandas as pd
from tools import enrich
st.set_page_config(page_title="FollowUp AI",page_icon="🤖",layout="wide")

st.title("AI Follow-Up Assistant")
st.markdown("### Upload your leads CSV to get started")
st.info("**Your data stays only in your browser session**-- it is never shared with or visible to other users.")

#creating upload and templete cols

col_up,col_temp =st.columns([3,2])

with col_up:
    uploaded = st.file_uploader("Upload your CSV",type=["csv"])
    if uploaded:
        file_key = f"{uploaded.name}_{uploaded.size}"
        if file_key != st.session_state.last_key:
            try:
                raw = pd.read_csv(uploaded)
                if not {"name", "contact"}.issubset(set(raw.columns.str.lower().str.strip())):
                    st.error("file must contain name and contact")
                else:
                    st.session_state.last_key = file_key
                    st.session_state.name     = uploaded.name
                    st.session_state.db       =enrich(raw)
                    st.rerun
            except Exception as e:
                st.error(f"{e}")

