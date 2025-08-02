import requests

clio_token = "YOUR_OAUTH_TOKEN"
contact_id = "CONTACT_ID"
lead_tag_id = "LEAD_TAG_ID"

headers = {"Authorization": f"Bearer {clio_token}", "Content-Type": "application/json"}

# Step 1: Fetch existing tags for the contact
contact_resp = requests.get(
    f"https://app.clio.com/api/v4/contacts/{contact_id}", headers=headers
)
existing_tag_ids = contact_resp.json()["data"].get("tag_ids", [])

# Step 2: Add the "Lead" tag (avoid duplicates)
if lead_tag_id not in existing_tag_ids:
    updated_tags = existing_tag_ids + [lead_tag_id]
else:
    updated_tags = existing_tag_ids

# Step 3: Update the contact
requests.put(
    f"https://app.clio.com/api/v4/contacts/{contact_id}",
    headers=headers,
    json={"data": {"tag_ids": updated_tags}},
)
