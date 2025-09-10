from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful trainer SaaS assistant."},
        {"role": "user", "content": "Generate a motivational message for a fitness client."}
    ]
)

print(response.choices[0].message.content)
