#This python file is used to:
#Simulate performance data
#Generate strategy suggestions using OpenAI API
import random
import pandas as pd
from datetime import datetime, timedelta
from openai import OpenAI
# import the existing function to get contacts
from content_generation import get_contacts

def main():
    time_week=input('How many weeks has this newsletter been going out?')
    df = simulate_newsletter_performance(int(time_week))

    # Save both detailed and summary data
    df.to_csv("newsletter_performance_detailed.csv", index=False)
    print("💾 Data saved: newsletter_performance_detailed.csv and newsletter_performance_summary.csv")

    api_key = "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"

    summary = performance_analysis(df, api_key)
    print(summary)

def generate_base_probabilities():
    #Generate base probabilities for open/click/unsubscribe rates.
    base_open = random.uniform(0.3, 0.7)         # 30%–70% open rate
    base_click = random.uniform(0.05, 0.25)      # 5%–25% click rate
    base_unsub = random.uniform(0.005, 0.02)     # 0.5%–2% unsubscribe rate
    return base_open, base_click, base_unsub

def simulate_newsletter_performance(num_weeks):

    # weekly newsletter performance for each contact.
    # Metrics: open, click, unsubscribe.
    open, click, unsub = generate_base_probabilities()

    contacts = get_contacts()
    print(f"📇 Retrieved {len(contacts)} contacts from HubSpot for simulation.")

    data = []
    start_date = datetime(2025, 1, 1)  # arbitrary start date

    for contact in contacts:
        email = contact.get("properties", {}).get("email", "")
        persona = contact.get("properties", {}).get("persona", "unknown")

        for week in range(num_weeks):
            week_date = start_date + timedelta(weeks=week)
            week_label = week + 1

            # Simulate open/click/unsubscribe probabilities by persona
            if persona == "founders":

                open_rate = random.random()>open
                click_rate = open_rate and (random.random()>click)
                unsubscribe = random.random()>unsub
            elif persona == "creatives":

                open_rate = random.random()>open
                click_rate = open_rate and (random.random()>click )
                unsubscribe = random.random()>unsub
            elif persona == "operations":
                open_rate = random.random()>open
                click_rate = open_rate and (random.random()>click)
                unsubscribe = random.random()>unsub
            else:
                open_rate = random.random()>open
                click_rate = open_rate and (random.random()>click)
                unsubscribe = random.random()>unsub

            data.append({
                "email": email,
                "persona": persona,
                "week": week_label,
                "send_date": week_date.strftime("%Y-%m-%d"),
                "opened": int(open_rate),
                "clicked": int(click_rate),
                "unsubscribed": int(unsubscribe),
            })

    df = pd.DataFrame(data)
    print("✅ Simulated newsletter performance data created.")
    return df



def performance_analysis(df,key):
    data_summary = df.to_markdown(index=False)

    # Ask GPT to summarize

    client = OpenAI(api_key=key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a data analyst writing marketing insights."},
            {"role": "user",
             "content": f"Here's our newsletter performance data:\n\n{data_summary}\n\nSummarize key trends and suggest strategies to improve performance."}
        ]
    )

    print(response.choices[0].message.content)


if __name__ == '__main__':
    main()