import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from model.llm import FollowUpGenerator
from important_functions.scoring import compute_priority_score, score_label
from important_functions.tools import init_state,enrich, followup_bucket

# Page config
st.set_page_config(page_title="FollowUp AI", page_icon="🤖", layout="wide")

today = date.today()

STATUSES  = ["New", "Interested", "Follow-up Needed", "Closed"]
INTERESTS = ["Low", "Medium", "High"]
TONES     = ["professional", "friendly", "polite", "persuasive"]

EXPORT_COLS = ["name", "contact", "company", "last_interaction",
               "next_followup", "status", "interest_level", "notes",
               "priority_score", "priority_label"]

# Initialising Session state

init_state()


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    cols = [c for c in EXPORT_COLS if c in df.columns]
    return df[cols].to_csv(index=False).encode()


def has_data() -> bool:
    return st.session_state.df is not None and not st.session_state.df.empty



#  UPLOAD GATE — every session starts here; nothing else is shown until a CSV
#  is loaded. Each browser session is completely independent.

if not has_data():
    st.title("🤖 AI Follow-Up Assistant")
    st.markdown("### Upload your leads CSV to get started")
    st.info(
        "Your data stays **only in your browser session** — "
        "it is never shared with or visible to other users.",
        icon="🔒",
    )

    col_up, col_tmpl = st.columns([3, 2])

    with col_up:
        uploaded = st.file_uploader("Upload your CSV", type=["csv"])
        if uploaded:
            file_key = f"{uploaded.name}_{uploaded.size}"
            if file_key != st.session_state.last_file_key:
                try:
                    raw = pd.read_csv(uploaded)
                    if not {"name", "contact"}.issubset(set(raw.columns.str.lower().str.strip())):
                        st.error("CSV must contain at least a **name** and **contact** column.")
                    else:
                        st.session_state.df            = enrich(raw)
                        st.session_state.file_name     = uploaded.name
                        st.session_state.last_file_key = file_key
                        st.rerun()
                except Exception as e:
                    st.error(f"Could not read file: {e}")

    with col_tmpl:
        st.markdown("**No CSV yet? Download a template:**")
        template = pd.DataFrame([{
            "name": "Priya Sharma",
            "contact": "priya@example.com",
            "company": "TechCorp",
            "status": "Interested",
            "interest_level": "High",
            "notes": "Wants a demo next week",
            "last_interaction": str(today),
            "next_followup": str(today),
        }])
        st.download_button(
            "📥 Download template CSV",
            template.to_csv(index=False).encode(),
            "followup_template.csv",
            "text/csv",
        )

    st.stop()   # Nothing below runs until a CSV is loaded


#  MAIN APP — only reached after a CSV is uploaded

df = st.session_state.df

# Top bar 
col_title, col_export, col_reset = st.columns([4, 2, 1])
col_title.title("🤖 AI Follow-Up Assistant")
col_title.caption(
    f"📄 **{st.session_state.file_name}** · {len(df)} customers  "
    f"·  🔒 Your private session"
)
col_export.download_button(
    label="📤 Download updated CSV",
    data=to_csv_bytes(df),
    file_name=st.session_state.file_name or "followup_updated.csv",
    mime="text/csv",
    use_container_width=True,
    help="Downloads your full list with all edits and priority scores applied.",
)
if col_reset.button("🔄 New file", use_container_width=True,
                    help="Clear this session and upload a different CSV"):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

st.divider()

# Sidebar — Add a new customer 
with st.sidebar:
    st.header("➕ Add Customer")
    with st.form("add_form", clear_on_submit=True):
        f_name    = st.text_input("Name *")
        f_contact = st.text_input("Contact *")
        f_company = st.text_input("Company")
        f_last    = st.date_input("Last Interaction", value=today)
        f_next    = st.date_input("Next Follow-Up",   value=today)
        f_status  = st.selectbox("Status",         STATUSES)# defined a list above
        f_int     = st.selectbox("Interest Level", INTERESTS)
        f_notes   = st.text_area("Notes")
        add_btn   = st.form_submit_button("💾 Save")

    if add_btn:
        if f_name and f_contact:
            new_row = pd.DataFrame([{               #neccessory
                "name": f_name, "contact": f_contact, "company": f_company,
                "last_interaction": str(f_last), "next_followup": str(f_next),
                "status": f_status, "interest_level": f_int, "notes": f_notes,
            }])
            st.session_state.df = enrich(
                pd.concat([df, new_row], ignore_index=True)
            )
            st.success(f"✅ {f_name} added!")
            st.rerun()
        else:
            st.warning("Name and Contact are required.")

    st.divider()
    st.caption(
        "All changes (add / edit / delete) are held in memory.\n\n"
        "Use **Download updated CSV** at the top to save your work."
    )

    st.header("⚙️ Groq Settings")
    api_key = st.text_input(
        "Groq API Key", 
        type="password", 
        value="", # can be setted in .env file or can be directly setted in web
        help="Get a free key at console.groq.com"
    )
    st.header("📧 Gmail Settings")
    gmail_sender = st.text_input(
        "Gmail_address",
        value="",
        help="The Gmail account you'll send from"
    )
    gmail_password = st.text_input(
        "Gmail app password",
        type="password",
        value="",
        help="Google Account -> Security -> 2-Step Verification ->App passwords"
    )
    

    

# Tabs 
tab_dash, tab_all, tab_edit, tab_ai, tab_analytics, tab_agent = st.tabs([
    "📊 Dashboard", "👥 All Customers", "✏️ Edit / Delete",
    "✍️ AI Messages", "📈 Analytics","🦾 Agent_Dev"
])


# TAB 1 — DASHBOARD

with tab_dash:
    overdue   = (df["bucket"] == "Overdue").sum()
    due_today = (df["bucket"] == "Due Today").sum()
    upcoming  = (df["bucket"] == "Upcoming").sum()
    hot       = (df["priority_label"] == "🔴 Hot").sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔴 Overdue",    int(overdue))
    c2.metric("📅 Due Today",  int(due_today))
    c3.metric("⏳ Upcoming",   int(upcoming))
    c4.metric("🔥 Hot Leads",  int(hot))

    st.subheader("Top Priority Leads")
    top_cols = ["name", "company", "next_followup", "status",
                "interest_level", "priority_score", "priority_label", "bucket"]
    st.dataframe(
        df[top_cols].head(10),
        use_container_width=True, hide_index=True,
    )

    sub_over, sub_today, sub_up = st.tabs(["Overdue", "Due Today", "Upcoming"])
    show_cols = ["name", "company", "status", "interest_level", "priority_score", "priority_label"]
    with sub_over:
        st.dataframe(df[df["bucket"] == "Overdue"][show_cols],
                     use_container_width=True, hide_index=True)
    with sub_today:
        st.dataframe(df[df["bucket"] == "Due Today"][show_cols],
                     use_container_width=True, hide_index=True)
    with sub_up:
        st.dataframe(df[df["bucket"] == "Upcoming"][show_cols],
                     use_container_width=True, hide_index=True)


# TAB 2 — ALL CUSTOMERS + EXPORT

with tab_all:
    st.subheader(f"All Customers ({len(df)})")

    cs, ci, cb = st.columns(3) # remove that if it not really matters
    s_filter = cs.multiselect("Filter by Status",   df["status"].unique().tolist())
    i_filter = ci.multiselect("Filter by Interest", df["interest_level"].unique().tolist())
    b_filter = cb.multiselect("Filter by Bucket",   df["bucket"].unique().tolist())

    filtered = df.copy()
    if s_filter: filtered = filtered[filtered["status"].isin(s_filter)]
    if i_filter: filtered = filtered[filtered["interest_level"].isin(i_filter)]
    if b_filter: filtered = filtered[filtered["bucket"].isin(b_filter)]

    st.dataframe(filtered, use_container_width=True, hide_index=True)

    st.download_button(
        "📤 Export filtered list as CSV",
        filtered.to_csv(index=False).encode(),
        f"filtered_{st.session_state.file_name or 'export.csv'}",
        "text/csv",
    )

# TAB 3 — EDIT / DELETE

with tab_edit:
    st.subheader("Edit or Delete a Customer")

    options ={}
    for idx, row in df.iterrows():
        display_text = row['name'] + "  (" + str(row['contact']) + ")"
        options[display_text] = idx

    selected_label = st.selectbox("Select customer", list(options.keys()), key="edit_sel")
    sel_idx        = options[selected_label]
    row            = df.loc[sel_idx]

    with st.form("edit_form"):
        e_name    = st.text_input("Name",    value=row["name"])
        e_contact = st.text_input("Contact", value=row["contact"])
        e_company = st.text_input("Company", value=row["company"])

        try:   e_last_val = pd.to_datetime(row["last_interaction"]).date() # I converted it to string earlier
        except: e_last_val = today
        try:   e_next_val = pd.to_datetime(row["next_followup"]).date()
        except: e_next_val = today

        e_last   = st.date_input("Last Interaction", value=e_last_val)
        e_next   = st.date_input("Next Follow-Up",   value=e_next_val)
        e_status = st.selectbox("Status", STATUSES,
                                index=STATUSES.index(row["status"])
                                      if row["status"] in STATUSES else 0) # fallback to idx 0 if current value not in list for some reason
        e_int    = st.selectbox("Interest Level", INTERESTS,
                                index=INTERESTS.index(row["interest_level"])
                                      if row["interest_level"] in INTERESTS else 1)
        e_notes  = st.text_area("Notes", value=row["notes"])

        col_s, col_d = st.columns([3, 1])
        save_btn   = col_s.form_submit_button("💾 Save Changes")
        delete_btn = col_d.form_submit_button("🗑️ Delete", type="secondary")

    if save_btn:
        updated = st.session_state.df.copy()
        updated.loc[sel_idx, "name"]             = e_name
        updated.loc[sel_idx, "contact"]          = e_contact
        updated.loc[sel_idx, "company"]          = e_company
        updated.loc[sel_idx, "last_interaction"] = str(e_last)
        updated.loc[sel_idx, "next_followup"]    = str(e_next)
        updated.loc[sel_idx, "status"]           = e_status
        updated.loc[sel_idx, "interest_level"]   = e_int
        updated.loc[sel_idx, "notes"]            = e_notes
        st.session_state.df = enrich(updated)
        st.success(f"✅ {e_name} updated.")
        st.rerun()

    if delete_btn:
        name_del = df.loc[sel_idx, "name"]
        updated  = st.session_state.df.drop(index=sel_idx).reset_index(drop=True)
        # Shifting message log keys after the deleted index
        new_log  = {}
        for k, v in st.session_state.msg_log.items():
            if k < sel_idx:   new_log[k]     = v
            elif k > sel_idx: new_log[k - 1] = v
        st.session_state.msg_log = new_log
        st.session_state.df      = enrich(updated)
        st.success(f"🗑️ {name_del} removed.")
        st.rerun()


# TAB 4 — AI MESSAGES

with tab_ai:
    st.subheader("Generate Follow-Up Message")
    st.info("Make sure to set your Groq API key in the sidebar before generating messages.", icon="💡")
    col_l, col_r = st.columns([1, 1])

    with col_l:
        ai_opts  = {
            f"{r['name']}  —  {r['company']}  {r['priority_label']}": idx
            for idx, r in df.iterrows()
        }
        ai_label = st.selectbox("Select customer", list(ai_opts.keys()), key="ai_sel")
        ai_idx   = ai_opts[ai_label]
        ai_row   = df.loc[ai_idx]
        tone     = st.selectbox("Tone", TONES)
        st.caption(
            f"**Status:** {ai_row['status']} · "
            f"**Interest:** {ai_row['interest_level']} · "
            f"**Bucket:** {ai_row['bucket']}"
        )
        gen_btn = st.button("✨ Generate Message", type="primary")

    with col_r:
        if gen_btn:
            # Instantiate once per session; reuse on every generation
            if st.session_state.llm is None:
                try:
                    st.session_state.llm = FollowUpGenerator(api_key)
                except Exception as e:
                    st.error(str(e))
                    st.stop()

                with st.spinner("Generating…"):
                    message = st.session_state.llm.generate({
                        "name":             ai_row["name"],
                        "contact":          ai_row["contact"],
                        "company":          ai_row["company"],
                        "last_interaction": str(ai_row["last_interaction"]),
                        "next_followup":    str(ai_row["next_followup"]),
                        "status":           ai_row["status"],
                        "interest_level":   ai_row["interest_level"],
                        "notes":            ai_row["notes"],
                    }, tone=tone)


                st.text_area("Generated Message", message, height=220)
                entry = {
                    "tone":    tone,
                    "message": message,
                    "ts":      pd.Timestamp.now().strftime("%d %b %Y, %H:%M"),
                }
                st.session_state.msg_log.setdefault(ai_idx, []).append(entry)
            

# TAB 5 — ANALYTICS 

with tab_analytics:
    st.subheader("Lead Analytics")
    r1l, r1r = st.columns(2)

    with r1l:
        

        sc = df["status"].value_counts()
        st.subheader("Leads by Status")
        st.bar_chart(sc)
    with r1r:
        st.subheader("Interest Level Breakdown")

        interest_counts = df["interest_level"].value_counts()

        st.bar_chart(interest_counts)

  
    bc = df["bucket"].value_counts().reset_index()
    bc.columns = ["Bucket", "Count"]
    
    st.subheader("Follow-Up Urgency")
    
    st.bar_chart(
    bc.set_index("Bucket")["Count"],
    use_container_width=True
        )
    
with tab_agent:
    st.subheader("📧 AI Email Agent")
    st.info("Generates follow-up emails for overdue customers, lets you review and edit them, then sends them via Gmail.", icon="🤖")

    # Step 1: Customer selection
    overdue_df = df[df["bucket"] == "Overdue"]

    if overdue_df.empty:
        st.success("No overdue customers right now!")
        st.stop()

    selected_names = st.multiselect(
        "Select customers to follow up with",
        options=overdue_df["name"].tolist(),
        default=overdue_df["name"].tolist(),
    )

    selected_df = overdue_df[overdue_df["name"].isin(selected_names)]

    # Step 2: Run agent
    run_btn = st.button("🚀 Run Agent", type="primary",
                        disabled=not selected_names)

    if run_btn:
        if not api_key:
            st.error("Please enter your Groq API key in the sidebar first.")
            st.stop()
        if not gmail_sender or not gmail_password:
            st.error("Please enter your Gmail address and app password in the sidebar.")
            st.stop()
        # Instantiate LLM if not already done
        if st.session_state.llm is None:
            try:
                st.session_state.llm = FollowUpGenerator(api_key)
            except Exception as e:
                st.error(f"LLM error: {e}")
                st.stop()

        # Build graph
        from agent.graph import build_graph
        graph = build_graph(st.session_state.llm, gmail_sender, gmail_password) #^^
        thread = {"configurable": {"thread_id": "crm-agent-7"}}

        # Prepare customer list from selected dataframe
        customers = selected_df.to_dict(orient="records")

        with st.spinner("Generating emails..."):
            result = graph.invoke(
                {"customers": customers},
                config=thread,
            )

        # Store graph + thread in session for resume step
        st.session_state["agent_graph"]  = graph
        st.session_state["agent_thread"] = thread
        st.session_state["agent_emails"] = result["__interrupt__"][0].value["emails"]
        st.rerun()

    # Step 3: Review & Edit
    if "agent_emails" in st.session_state:
        st.divider()
        st.subheader("📝 Review & Edit Emails")
        st.caption("Edit any email below. Uncheck to skip sending.")

        edited_emails = []

        for i, email in enumerate(st.session_state["agent_emails"]):  #^^^^^^^^^^
            with st.expander(
                f"{'✅' if email.get('approved', True) else '❌'} " # ^^^
                f"{email['name']} — {email['company']} ({email['email']})",
                expanded=True
            ):
                approved = st.checkbox("Approve for sending", value=True, key=f"approve_{i}")
                subject  = st.text_input("Subject", value=email["subject"], key=f"subject_{i}")
                body     = st.text_area("Email body", value=email["body"], height=180, key=f"body_{i}")

                edited_emails.append({
                    **email,
                    "approved": approved,
                    "subject":  subject,
                    "body":     body,
                })

        st.divider()
        send_btn = st.button("📤 Approve & Send", type="primary")

        if send_btn:
            from langgraph.types import Command

            graph  = st.session_state["agent_graph"]
            thread = st.session_state["agent_thread"]

            with st.spinner("Sending emails..."):
                final = graph.invoke(
                    Command(resume=edited_emails),
                    config=thread,
                )

            # Step 4: Results
            st.divider()
            st.subheader("📊 Send Results")

            sent    = [r for r in final["sent_results"] if r["status"] == "sent"]
            skipped = [r for r in final["sent_results"] if r["status"] == "skipped"]
            failed  = [r for r in final["sent_results"] if r["status"] == "failed"]

            c1, c2, c3 = st.columns(3)
            c1.metric("✅ Sent",    len(sent))
            c2.metric("⏭️ Skipped", len(skipped))
            c3.metric("❌ Failed",  len(failed))

            for r in final["sent_results"]:
                if r["status"] == "sent":
                    st.success(f"✅ Sent to {r['name']} ({r['email']})")
                elif r["status"] == "skipped":
                    st.info(f"⏭️ Skipped {r['name']}")
                elif r["status"] == "failed":
                    st.error(f"❌ Failed for {r['name']}: {r['error']}")

            # Clearing agent state after sending mial
            for key in ["agent_graph", "agent_thread", "agent_emails"]:
                del st.session_state[key]
