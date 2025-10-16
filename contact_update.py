#This python file is used to:
#Generate mock contacts for newsletter subscribers
#Upload the mock contacts to Hubspot

from faker import Faker
import random
fake = Faker()

def main():
    HUBSPOT_TOKEN = "pat-na2-8f4f0028-e21b-40e1-9457-fd8a61d026d9"

    contacts = generate_mock_contacts(10)
    upload_contacts_to_hubspot(contacts, HUBSPOT_TOKEN)


def generate_mock_contacts(n=10):
    personas = ["founders", "creatives", "operations"]
    contacts = [
        {
            "email": fake.email(),
            "first_name": fake.first_name(),
            "company": fake.company(),
            "persona": random.choice(personas)
        }
        for _ in range(n)
    ]
    return contacts

import requests

def upload_contacts_to_hubspot(contacts, hubspot_token):
    url = "https://api.hubapi.com/crm/v3/objects/contacts"
    headers = {
        "Authorization": f"Bearer {hubspot_token}",
        "Content-Type": "application/json"
    }

    for contact in contacts:
        data = {
            "properties": {
                "email": contact["email"],
                "firstname": contact["first_name"],
                "company": contact["company"],
                "persona": contact["persona"]
            }
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 201:
            print(f"✅ Created contact: {contact['email']}")
        else:
            print(f"⚠️ Failed to create {contact['email']}: {response.text}")



if __name__ == '__main__':
    main()