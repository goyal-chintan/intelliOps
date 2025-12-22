from openai import OpenAI
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama'
)

response = client.conversation
response = client.chat.completions.create(
    model="deepseek-r1:8b",
    messages=[
        {"role": "system", "content": "You are a indian doctor"},
        {"role": "user", "content": "Write a one-line Linux command to list all files."}
    ]
)

print("AI Reply:", response.choices[0].message.content)