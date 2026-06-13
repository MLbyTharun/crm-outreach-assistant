import streamlit as st

st.set_page_config(page_title="FollowUp AI",page_icon="🤖",layout="wide")

st.title("AI Follow-Up Assistant")
st.markdown("### Upload your leads CSV to get started")
st.info("**Your data stays only in your browser session**-- it is never shared with or visible to other users.")

#creating upload and templete cols

col_up,col_temp =st.columns([3,2])

with col_up:
    uploaded = st.file_uploader("Upload your CSV",type=["csv"])
    if uploaded:


with col_temp:
    temp =st.download_button("download template CSV")
    if temp:
        # add a sampl csv kinda here