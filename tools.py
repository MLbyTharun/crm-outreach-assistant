import streamlit as st

def init_state():
    for k, v in {
        "df":            None,   # working DataFrame — only this user's data
        "file_name":     None,   # original filename so export keeps the same name
        "msg_log":       {},     # {row_idx: [{"tone":..,"message":..,"ts":..}]}
        "last_file_key": None,   # prevent re-import
        "llm":           None,   # FollowUpGenerator instance — created once per session
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v