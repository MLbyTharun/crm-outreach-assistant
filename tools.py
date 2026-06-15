import streamlit as st
from datetime import date
import pandas as pd
from scoring import compute_priority_score, score_label
today = date.today()

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


def followup_bucket(val):
    try:
        d = pd.to_datetime(val).date() if val else None
    except Exception:
        d = None
    if not d:         return "No Date"
    if d < today:     return "Overdue"
    if d == today:    return "Due Today"
    return "Upcoming"


def enrich(df: pd.DataFrame) -> pd.DataFrame: #  ^^^
    """Normalising columns and recomputing priority + bucket on the whole DataFrame."""
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Ensure all expected columns exist if not we create them 
    for col in ["name", "contact", "company", "status", "interest_level", "notes"]:
        if col not in df.columns:
            df[col] = ""
    for col in ["last_interaction", "next_followup"]:
        if col not in df.columns:
            df[col] = str(today)

    df["status"]         = df["status"].fillna("New")
    df["interest_level"] = df["interest_level"].fillna("Medium")
    df["notes"]          = df["notes"].fillna("")
    df["company"]        = df["company"].fillna("")

    df["priority_score"] = df.apply(lambda r: compute_priority_score(
        pd.to_datetime(r["next_followup"]).date() if r["next_followup"] else None,
        r["status"], r["interest_level"]
    ), axis=1)
    df["priority_label"] = df["priority_score"].apply(score_label) #it store colour rgy
    df["bucket"]         = df["next_followup"].apply(followup_bucket)
    return df.sort_values("priority_score", ascending=False).reset_index(drop=True)  #descending for top prior table in t1
