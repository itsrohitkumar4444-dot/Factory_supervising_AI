import os
import json
import urllib.request
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

# Import our mock Hindsight Memory
from hindsight import HindsightMemory

app = Flask(__name__, static_folder='ui')
CORS(app)

HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

hindsight = HindsightMemory(api_key=HINDSIGHT_API_KEY, storage_path="./hindsight_db")

# Serve the beautiful UI UI built earlier
@app.route('/')
def index():
    return send_from_directory('ui', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('ui', path)

# Main chat endpoint utilizing Hindsight
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    messages = data.get('messages', [])
    if not messages:
        return jsonify({'error': 'No messages provided'}), 400

    last_user_msg = [m for m in messages if m['role'] == 'user'][-1]['content']
    
    # 1. HINDSIGHT RECALL: augment context with "Tribal Knowledge"
    past_knowledge = hindsight.recall(query=last_user_msg, search_mode="temporal+graph", top_k=2)
    
    system_prompt = (
        "You are the Shadow Floor Engineer, an expert AI assistant monitoring sensors and helping with factory operations.\n"
        "Maintain a middle-ground tone: neither overly clinical nor overly friendly. Do NOT use bullet points or explicitly label 'Generic' or 'Specific' solutions.\n"
        "When diagnosing an issue using the provided context, weave your answer to follow this exact natural flow:\n"
        "'The problem you are talking about can be solved by [state the generic textbook method], but before that try to check the following as [Technician Name] had mentioned it earlier: [state the specific real-world fix]'\n"
        "CRITICAL EDGE CASE: If the context below explicitly says '[No historical data...]' OR if it refers to a completely different machine, do NOT hallucinate. Just say: 'The problem can be solved by [generic method], but please let me know if you discover a different physical fix on the floor so I can remember it.'\n"
        "Keep it concise.\n"
        "Here is the relevant factory floor context:\n"
        f"{past_knowledge}"
    )

    # Inject the hindsight knowledge into the system prompt
    api_messages = [{'role': 'system', 'content': system_prompt}]
    for msg in messages:
        if msg['role'] != 'system':  # filter out the client's dummy system prompt
            api_messages.append(msg)

    # 2. CALL GROQ
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    payload = {
        "model": "gpt-oss-120b-cloud",
        "messages": api_messages
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            ai_text = result['choices'][0]['message']['content']
            
            # 3. HINDSIGHT RETAIN: remember this interaction
            hindsight.retain(
                content=f"User Issue: {last_user_msg} | Solution provided: {ai_text[:100]}...",
                tags=["ui_chat", "maintenance"],
                metadata={}
            )
            
            return jsonify({'response': ai_text})
    except urllib.error.HTTPError as e:
        error_info = e.read().decode('utf-8')
        print(f"HTTP Error {e.code}: {e.reason} \n{error_info}")
        return jsonify({'error': error_info}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Shadow Floor Engineer backend running on http://127.0.0.1:5000")
    app.run(port=5000, debug=True)
