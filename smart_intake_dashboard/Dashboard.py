import streamlit as st
from backend_client import (
    add_incoming_webhook,
    add_outgoing_webhook,
    delete_outgoing_webhook,
    generate_api_token,
    get_api_tokens,
    get_dashboard_summary,
    get_incoming_webhooks,
    get_outgoing_webhooks,
    revoke_api_token,
    toggle_incoming_webhook,
)

st.set_page_config(page_title="Intake Agent Dashboard", layout="wide")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Settings"],
    format_func=lambda x: ("📊 Dashboard" if x == "Dashboard" else "⚙️ Settings"),
)

if page == "Dashboard":
    st.title("📊 Intake Agent Metrics")
    summary = get_dashboard_summary()
    if summary:
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric(label="Qualified Leads", value=summary["total_qualified_leads"])
        with col2:
            st.metric(label="Lead Reviews", value=summary["total_lead_reviews"])
        with col3:
            st.metric(label="Notifications Sent", value=summary["notifications_sent"])
        with col4:
            st.metric(label="Callbacks/Updates", value=summary["callbacks_or_updates"])
        with col5:
            st.metric(label="Practice Areas", value=len(summary["practice_area_chart"]))
        st.caption("Metrics reflect the current state of the Smart Intake backend.")
    else:
        st.error("Could not fetch dashboard summary from backend.")

elif page == "Settings":
    st.title("⚙️ API Tokens & Webhooks Management")
    tabs = st.tabs(["API Tokens", "Incoming Webhooks", "Outgoing Webhooks"])

    # --- API Tokens ---
    with tabs[0]:
        st.header("API Tokens")
        try:
            tokens = get_api_tokens()
            for t in tokens:
                st.write(
                    f"Token: `{t['token']}` | Status: {'Active' if t['active'] else 'Revoked'}"
                )
                if t["active"]:
                    if st.button(f"Revoke {t['token']}"):
                        revoke_api_token(t["token"])
                        st.success("Token revoked.")
                        st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
        if st.button("Generate New API Token"):
            r = generate_api_token()
            if r.ok:
                st.success("New API token generated.")
                st.rerun()
            else:
                st.error("Failed to generate token.")

    # --- Incoming Webhooks ---
    with tabs[1]:
        st.header("Incoming Webhooks")
        try:
            webhooks = get_incoming_webhooks()
            for wh in webhooks:
                st.write(
                    f"URL: `{wh['url']}` | Enabled: {'Yes' if wh['enabled'] else 'No'}"
                )
                if st.button(f"Toggle {wh['url']}"):
                    toggle_incoming_webhook(wh["url"])
                    st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
        if st.button("Add Incoming Webhook"):
            with st.form("add_incoming_webhook"):
                url = st.text_input("Webhook URL")
                enabled = st.checkbox("Enabled", value=True)
                submitted = st.form_submit_button("Create")
                if submitted:
                    r = add_incoming_webhook(url, enabled)
                    if r.ok:
                        st.success("Webhook added.")
                        st.rerun()
                    else:
                        st.error("Failed to add webhook.")

    # --- Outgoing Webhooks ---
    with tabs[2]:
        st.header("Outgoing Webhooks")
        try:
            webhooks = get_outgoing_webhooks()
            for wh in webhooks:
                st.write(
                    f"Name: {wh.get('name', wh['id'])} | URL: `{wh['url']}` | Events: {', '.join(wh.get('event_types', []))}"
                )
                if st.button(f"Delete {wh['id']}"):
                    del_resp = delete_outgoing_webhook(wh["id"])
                    if del_resp.ok:
                        st.success("Deleted!")
                        st.rerun()
                    else:
                        st.error("Delete failed.")
        except Exception as e:
            st.error(f"Error: {e}")
        if st.button("Add Outgoing Webhook"):
            with st.form("add_outgoing_webhook"):
                name = st.text_input("Integration Name")
                url = st.text_input("Webhook URL")
                event_types = st.text_input("Event Types (comma-separated)")
                submitted = st.form_submit_button("Register")
                if submitted:
                    r = add_outgoing_webhook(
                        name,
                        url,
                        [e.strip() for e in event_types.split(",") if e.strip()],
                    )
                    if r.ok:
                        st.success("Webhook registered.")
                        st.rerun()
                    else:
                        st.error("Failed to register webhook.")
