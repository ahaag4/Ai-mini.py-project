from flask import Flask, request, jsonify, render_template
import requests
import time
from threading import Lock

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# Free AI API endpoints (no keys required)
API_PROVIDERS = [
    {
        "name": "DeepInfra-Llama3",
        "url": "https://api.deepinfra.com/v1/inference/meta-llama/Meta-Llama-3-70B-Instruct",
        "headers": {"Content-Type": "application/json"},
        "payload": lambda text: {"input": text},
        "parse": lambda r: r.json()['results'][0]['generated_text']
    },
    {
        "name": "HuggingFace-Mixtral",
        "url": "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1",
        "headers": {"Authorization": "Bearer hf_YourFreeTokenHere"},  # Optional
        "payload": lambda text: {"inputs": text},
        "parse": lambda r: r.json()[0]['generated_text']
    }
]

# Rate limiting and conversation history
conversation_lock = Lock()
user_sessions = {}

class AIChatEngine:
    def __init__(self):
        self.knowledge_base = {
            "current_date": time.strftime("%Y-%m-%d"),
            "capabilities": "I can discuss science, technology, history, and more"
        }

    def generate_response(self, user_input, user_id):
        with conversation_lock:
            # Maintain conversation context
            if user_id not in user_sessions:
                user_sessions[user_id] = {
                    "history": [],
                    "last_active": time.time()
                }

            session = user_sessions[user_id]
            session["history"].append({"role": "user", "content": user_input})
            session["last_active"] = time.time()

            # Try all available APIs
            for provider in API_PROVIDERS:
                try:
                    payload = provider["payload"](
                        f"Context: {self.knowledge_base}\n"
                        f"History: {session['history'][-5:]}\n"
                        f"User: {user_input}\nAssistant:"
                    )

                    response = requests.post(
                        provider["url"],
                        headers=provider["headers"],
                        json=payload,
                        timeout=15
                    )

                    if response.status_code == 200:
                        reply = provider["parse"](response)
                        session["history"].append({"role": "assistant", "content": reply})
                        return {
                            "response": reply,
                            "model": provider["name"],
                            "tokens": len(reply.split())
                        }

                except Exception as e:
                    print(f"API {provider['name']} failed: {str(e)}")

            # Fallback response if all APIs fail
            fallback_responses = [
                "I'm experiencing high demand. Please try again shortly.",
                "Let me think differently about that...",
                "Here's what I can tell you about this topic..."
            ]
            reply = random.choice(fallback_responses)
            session["history"].append({"role": "assistant", "content": reply})
            return {
                "response": reply,
                "model": "Fallback",
                "tokens": len(reply.split())
            }

@app.route('/')
def home():
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    user_id = request.remote_addr  # Simple user identification
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({"error": "Invalid request"}), 400

    engine = AIChatEngine()
    result = engine.generate_response(data['message'], user_id)
    
    return jsonify({
        "response": result["response"],
        "model": result["model"],
        "timestamp": int(time.time()),
        "tokens": result["tokens"]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
