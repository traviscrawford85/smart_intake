import requests
import streamlit as st

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="Intake Agent Dashboard", layout="wide")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Settings"],
    format_func=lambda x: ("📊 Dashboard" if x == "Dashboard" else "⚙️ Settings"),
)

if page == "Dashboard":
    st.title("📊 Intake Agent Metrics")
    # Fetch metrics from backend
    try:
        resp = requests.get(f"{API_BASE}/metrics")
        if resp.ok:
            data = resp.json()
            qualified = data.get("qualified_leads", 0)
            needs_review = data.get("needs_review", 0)
            incomplete = data.get("incomplete", 0)
            capture_now = data.get("capture_now_agent_leads", 0)
            website = data.get("website_contact_form_leads", 0)
        else:
            qualified = needs_review = incomplete = capture_now = website = "-"
            st.warning("Could not fetch live metrics.")
    except Exception as e:
        qualified = needs_review = incomplete = capture_now = website = "-"
        st.error(f"Error fetching metrics: {e}")

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(label="Qualified Leads", value=qualified)
    with col2:
        st.metric(label="Needs Review", value=needs_review)
    with col3:
        st.metric(label="Incomplete", value=incomplete)
    with col4:
        st.metric(label="Capture Now Agent", value=capture_now)
    with col5:
        st.metric(label="Website Contact Form", value=website)

    st.caption("Metrics reflect the current state of the intake_agent backend.")

elif page == "Settings":
    st.title("⚙️ API Tokens & Webhooks Management")
    tabs = st.tabs(["API Tokens", "Incoming Webhooks", "Outgoing Webhooks"])

    # --- API Tokens ---
    with tabs[0]:
        st.header("API Tokens")
        try:
            resp = requests.get(f"{API_BASE}/settings/api_tokens")
            if resp.ok:
                tokens = resp.json().get("tokens", [])
                for t in tokens:
                    st.write(
                        f"Token: `{t['token']}` | Status: {'Active' if t['active'] else 'Revoked'}"
                    )
                    if t["active"]:
                        if st.button(f"Revoke {t['token']}"):
                            requests.post(
                                f"{API_BASE}/settings/api_tokens/revoke",
                                json={"token": t["token"]},
                            )
                            st.success("Token revoked.")
                            st.rerun()
            else:
                st.warning("Could not load API tokens.")
        except Exception as e:
            st.error(f"Error: {e}")
        if st.button("Generate New API Token"):
            r = requests.post(f"{API_BASE}/settings/api_tokens/generate")
            if r.ok:
                st.success("New API token generated.")
                st.rerun()
            else:
                st.error("Failed to generate token.")

    # --- Incoming Webhooks ---
    with tabs[1]:
        st.header("Incoming Webhooks")
        try:
            resp = requests.get(f"{API_BASE}/settings/webhooks/incoming")
            if resp.ok:
                webhooks = resp.json().get("webhooks", [])
                for wh in webhooks:
                    st.write(
                        f"URL: `{wh['url']}` | Enabled: {'Yes' if wh['enabled'] else 'No'}"
                    )
                    if st.button(f"Toggle {wh['url']}"):
                        requests.post(
                            f"{API_BASE}/settings/webhooks/incoming/toggle",
                            json={"url": wh["url"]},
                        )
                        st.rerun()
            else:
                st.warning("Could not load incoming webhooks.")
        except Exception as e:
            st.error(f"Error: {e}")
        if st.button("Add Incoming Webhook"):
            with st.form("add_incoming_webhook"):
                url = st.text_input("Webhook URL")
                enabled = st.checkbox("Enabled", value=True)
                submitted = st.form_submit_button("Create")
                if submitted:
                    r = requests.post(
                        f"{API_BASE}/settings/webhooks/incoming/add",
                        json={"url": url, "enabled": enabled},
                    )
                    if r.ok:
                        st.success("Webhook added.")
                        st.rerun()
                    else:
                        st.error("Failed to add webhook.")

    # --- Outgoing Webhooks ---
    with tabs[2]:
        st.header("Outgoing Webhooks")
        try:
            resp = requests.get(f"{API_BASE}/settings/webhooks/outgoing")
            if resp.ok:
                webhooks = resp.json().get("webhooks", [])
                for wh in webhooks:
                    st.write(
                        f"Name: {wh.get('name', wh['id'])} | URL: `{wh['url']}` | Events: {', '.join(wh.get('event_types', []))}"
                    )
                    if st.button(f"Delete {wh['id']}"):
                        del_resp = requests.delete(
                            f"{API_BASE}/settings/webhooks/outgoing/{wh['id']}/delete"
                        )
                        if del_resp.ok:
                            st.success("Deleted!")
                            st.rerun()
                        else:
                            st.error("Delete failed.")
            else:
                st.warning("Could not load outgoing webhooks.")
        except Exception as e:
            st.error(f"Error: {e}")
        if st.button("Add Outgoing Webhook"):
            with st.form("add_outgoing_webhook"):
                name = st.text_input("Integration Name")
                url = st.text_input("Webhook URL")
                event_types = st.text_input("Event Types (comma-separated)")
                submitted = st.form_submit_button("Register")
                if submitted:
                    payload = {
                        "name": name,
                        "url": url,
                        "event_types": [
                            e.strip() for e in event_types.split(",") if e.strip()
                        ],
                    }
                    r = requests.post(
                        f"{API_BASE}/settings/webhooks/outgoing/add", json=payload
                    )
                    if r.ok:
                        st.success("Webhook registered.")
                        st.rerun()
                    else:
                        st.error("Failed to register webhook.")
