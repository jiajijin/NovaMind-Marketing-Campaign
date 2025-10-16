#This python file is used to:
#Generate personalized contents for newsletters using OpenAI API
#Log contacts to the Hubspot
#Send newsletters through emails to contacts

import uuid
import pandas as pd

from openai import OpenAI

import json
import requests

def main():
    # Replace this with your actual key — or use an environment variable

    api_key="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"

    topic=input_topic()
    filename, blogs_data=generate(topic,api_key)


    if blogs_data:
        send_and_log_campaigns(blogs_data)
        print("✅ All campaigns processed.")

    contacts = get_contacts()
    print(f"📇 Retrieved {len(contacts)} contacts from HubSpot.")

    send_newsletters(blogs_data, contacts)


def input_topic():
    topic=input("What's your topic?")
    return topic


from datetime import datetime


def generate(topic, key):
    client = OpenAI(api_key=key)

    # Improved prompt for structured output
    user_prompt = f"""
You are a senior content strategist. 
Return ONLY a single JSON object in this exact format — no extra text, no markdown:

{{
  "topic": "{topic}",
  "generated_on": "{datetime.utcnow().isoformat()}Z",
  "blogs": [
    {{
      "audience": "Founders / Decision-Makers",
      "focus": "ROI, growth, efficiency",
      "title": Newsletter for KPI trends in {topic},
      "content": "<~400-600 word blog post here>"
    }},
    {{
      "audience": "Creative Professionals",
      "focus": "inspiration, time-saving tools",
      "title": Newsletter for new tools in {topic},
      "content": "<~400-600 word blog post here>"
    }},
    {{
      "audience": "Operations Managers",
      "focus": "workflows, integrations, reliability",
      "title": Newsletter for operational trends in {topic}
      "content": "<~400-600 word blog post here>"
    }}
  ]
}}

Constraints:
- Output must be VALID JSON.
- Use double quotes for all strings.
- Do not include any commentary or markdown formatting.
- Each 'content' field should be a full blog post (~400–600 words) about {topic}.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a precise assistant who outputs only valid JSON."},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3
    )

    content = response.choices[0].message.content.strip()

    # Try to parse into JSON (if valid)
    try:
        data = json.loads(content)
        filename = f"{topic.replace(' ', '_')}_blogs.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Blogs saved to {filename}")
        return filename, data
    except json.JSONDecodeError:
        print("⚠️ Model output was invalid JSON.")
        return None, None

HUBSPOT_TOKEN = "pat-na2-8f4f0028-e21b-40e1-9457-fd8a61d026d9"
HUBSPOT_API = "https://api.hubapi.com"

# --- Fetch contacts from HubSpot ---
def get_contacts():
    url = f"{HUBSPOT_API}/crm/v3/objects/contacts?properties=email,firstname,lastname,persona&limit=100"
    headers = {"Authorization": f"Bearer {HUBSPOT_TOKEN}"}
    contacts = []
    while url:
        resp = requests.get(url, headers=headers).json()
        contacts.extend(resp.get("results", []))
        # handle pagination
        url = resp.get("paging", {}).get("next", {}).get("link")
    for c in contacts:
        persona = c.get("properties", {}).get("persona")
        print(f"{c.get('properties', {}).get('email')}: persona = {persona}")

    return contacts


import time
from datetime import datetime
import random
import requests

def log_campaign_to_crm(title, audience, newsletter_id):
    """Logs campaign metadata and mock performance to HubSpot as a Note."""
    url = f"{HUBSPOT_API}/crm/v3/objects/notes"
    headers = {
        "Authorization": f"Bearer {HUBSPOT_TOKEN}",
        "Content-Type": "application/json"
    }

    # HubSpot expects timestamp in milliseconds
    timestamp_ms = int(time.time() * 1000)

    # Generate mock performance data
    open_rate = round(random.uniform(20, 50), 1)       # e.g., 20%–50%
    click_rate = round(random.uniform(5, 20), 1)       # e.g., 5%–20%
    unsubscribe_rate = round(random.uniform(0, 2), 2)  # e.g., 0%–2%

    data = {
        "properties": {
            "hs_note_body": (
                f"Newsletter '{title}' sent to {audience} on {datetime.utcnow().isoformat()}Z. "
                f"Newsletter ID: {newsletter_id}\n\n"
                f"📊 Performance (mock): Open rate: {open_rate}%, "
                f"Click rate: {click_rate}%, Unsubscribe rate: {unsubscribe_rate}%"
            ),
            "hs_timestamp": timestamp_ms
        }
    }

    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code == 201:
        print(f"📝 Logged campaign '{title}' for {audience} in HubSpot with mock metrics.")
    else:
        print(f"❌ Failed to log campaign: {resp.status_code}, {resp.text}")


def send_and_log_campaigns(blogs_data):
    contacts = get_contacts()
    print(f"📇 Retrieved {len(contacts)} contacts from HubSpot.")

    for blog in blogs_data.get("blogs", []):
        audience = blog["audience"]
        title = blog.get("title", "Untitled Campaign")
        newsletter_id = str(uuid.uuid4())[:8]

        # Filter recipients by persona (case-insensitive match)
        recipients = [
            c for c in contacts
            if c.get("properties", {}).get("persona", "").lower() in audience.lower()
        ]
        print(f"📤 Simulating sending to {len(recipients)} recipients in {audience}...")

        # Log campaign
        log_campaign_to_crm(title, audience, newsletter_id)

import yagmail

GMAIL_USER = "jinjiaji20040228@gmail.com"
GMAIL_APP_PASSWORD = "qgfgxfpcflzucxfr"

def send_email(recipient, subject, body):
    """Send email via Gmail SMTP."""
    yag = yagmail.SMTP(GMAIL_USER, GMAIL_APP_PASSWORD)
    yag.send(to=recipient, subject=subject, contents=body)
    print(f"✉️ Email sent to {recipient}!")


def send_newsletters(blogs_data, contacts):
    AUDIENCE_TO_PERSONA = {
        "Founders / Decision-Makers": "founders",
        "Creative Professionals": "creatives",
        "Operations Managers": "operations"
    }

    for blog in blogs_data.get("blogs", []):
        audience = blog["audience"]
        persona_value = AUDIENCE_TO_PERSONA.get(audience)
        if not persona_value:
            print(f"⚠️ No persona mapping for audience '{audience}'")
            continue

        subject = blog.get("title", f"Newsletter for {blog.get('focus','General')}")
        body_content = blog["content"]

        # Filter contacts by mapped persona
        recipients = [
            c for c in contacts
            if c.get("properties", {}).get("persona", "").lower() == persona_value
        ]

        print(f"📤 Sending '{subject}' to {len(recipients)} recipients in {audience}...")

        for c in recipients:
            email = c.get("properties", {}).get("email")
            if email:
                send_email(email, subject, body_content)

if __name__ == '__main__':
    main()