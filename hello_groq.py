import urllib.request
import json
import os
from dotenv import load_dotenv

load_dotenv()

print("Sending 'hlo' to Groq...")

url = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
data = {
    "model": "gpt-oss-120b-cloud",  # Using a fast, standard model on Groq
    "messages": [{"role": "user", "content": "hlo"}]
}

req = urllib.request.Request(
    url, 
    data=json.dumps(data).encode('utf-8'), 
    headers=headers, 
    method='POST'
)

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        print("\n--- Groq Replied ---")
        print(result['choices'][0]['message']['content'])
        print("--------------------")
except urllib.error.HTTPError as e:
    print(f"\nHTTP Error {e.code}: {e.reason}")
    print(f"Details: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"\nError communicating with Groq: {e}")
