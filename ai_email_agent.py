import os

from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client =  OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("model_api_key")
)

CATEGORIES = ["Sales", "Support", "Feedback", "Other"]

def summarize_and_categorize_email(email_dict):
    subject = email_dict["subject"]
    sender = email_dict["from"]
    body = email_dict["body"][:4000]  # avoid huge prompts


    prompt = f"""
You are an assistant that summarizes corporate emails and classifies them.

Email:
From: {sender}
Subject: {subject}
Body:
\"\"\"
{body}
\"\"\"
                      

1. Give a concise summary in 2-3 sentences.
2. Classify the email into exactly one of these categories:
   - Sales
   - Support
   - Feedback
   - Other

Respond in JSON with keys: "summary" and "category" like the one below
{{"summary": "...","category": "..."}}

Important instruction points to note:
    0. Make sure the output which is the content to be in pure JSON format so that i can decode without an issue and need not put unnecessary newline or special characters and follow the respond method i said above.
    2.Do not add any  unnecessary newline or special characters in the output json as it will cause an error while i decode.

    """
    response = client.chat.completions.create(
        #model="x-ai/grok-4.1-fast",
        model="kwaipilot/kat-coder-pro:free",
        messages=[
            {"role": "system",
             "content": prompt},
            # {"role": "user", "content": user}
        ],
        response_format={"type": "json_object"}
    )
    # print("Response:- ",response)
    content = response.choices[0].message.content
    # print(content)# raw JSON string
    import json
    data = json.loads(content)
    print("Ai Agent response :",data)

    summary = data.get("summary", "").strip()
    category = data.get("category", "Other").strip()

    # Normalize category a bit
    if category not in CATEGORIES:
        category = "Other"
    print("Agent has summarized email")
    return summary, category