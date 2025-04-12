from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
import openai
import os
import requests
import json
import time
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Database simulation (replace with real DB in production)
users_db = {
    "admin": generate_password_hash("admin123"),
    "student": generate_password_hash("student123")
}

conversation_history = {}

# Initialize OpenAI (if API key available)
try:
    openai.api_key = os.getenv("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", "")
    OPENAI_AVAILABLE = True
except:
    OPENAI_AVAILABLE = False

class AdvancedChatbot:
    def __init__(self):
        self.models = {
            "free": "https://api.deepinfra.com/v1/inference/meta-llama/Llama-2-70b-chat-hf",
            "paid": "gpt-3.5-turbo" if OPENAI_AVAILABLE else None
        }
        self.knowledge_graph = self._build_knowledge_graph()
        
    def _build_knowledge_graph(self):
        """Semantic knowledge base for fallback"""
        return {
            "computer_science": {
                "algorithms": {
                    "definition": "Step-by-step procedures for calculations",
                    "examples": ["Sorting", "Searching", "Graph traversal"],
                    "complexity": {
                        "bubble_sort": "O(n²)",
                        "quick_sort": "O(n log n) average"
                    }
                },
                "databases": {
                    "types": ["Relational", "NoSQL", "Graph"],
                    "sql": "Structured Query Language"
                }
            },
            "math": {
                "calculus": {
                    "derivatives": "Rate of change",
                    "integrals": "Accumulation of quantities"
                }
            }
        }

    def _query_knowledge_graph(self, topic):
        """Semantic search through local knowledge"""
        topic = topic.lower()
        for domain in self.knowledge_graph:
            if topic in domain.lower():
                return json.dumps(self.knowledge_graph[domain], indent=2)
            for subtopic in self.knowledge_graph[domain]:
                if topic in subtopic.lower():
                    return json.dumps(self.knowledge_graph[domain][subtopic], indent=2)
        return None

    def generate_response(self, user_input, user_id):
        """Advanced response generation with multiple fallbacks"""
        # Track conversation context
        if user_id not in conversation_history:
            conversation_history[user_id] = []
        
        # Try OpenAI first if available
        if OPENAI_AVAILABLE:
            try:
                response = openai.ChatCompletion.create(
                    model=self.models["paid"],
                    messages=[
                        {"role": "system", "content": "You are an advanced AI tutor for computer science students."},
                        *conversation_history[user_id],
                        {"role": "user", "content": user_input}
                    ],
                    temperature=0.7,
                    max_tokens=150
                )
                reply = response.choices[0].message.content
                conversation_history[user_id].append({"role": "assistant", "content": reply})
                return reply
            except Exception as e:
                print(f"OpenAI error: {e}")

        # Fallback to free API
        try:
            payload = {
                "input": user_input,
                "context": str(conversation_history.get(user_id, []))
            }
            response = requests.post(
                self.models["free"],
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=10
            )
            if response.status_code == 200:
                reply = response.json()['results'][0]['generated_text']
                conversation_history[user_id].append({"role": "assistant", "content": reply})
                return reply
        except Exception as e:
            print(f"Free API error: {e}")

        # Final fallback to knowledge graph
        knowledge = self._query_knowledge_graph(user_input)
        if knowledge:
            return f"From knowledge base:\n{knowledge}"
        
        return "I couldn't generate a response. Please try rephrasing your question."

@app.route("/")
def index():
    if "user_id" not in session:
        return render_template("login.html")
    return render_template("chat.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    
    if username in users_db and check_password_hash(users_db[username], password):
        session["user_id"] = username
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return jsonify({"status": "success"})

@app.route("/api/chat", methods=["POST"])
def chat_api():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "Empty message"}), 400
    
    bot = AdvancedChatbot()
    response = bot.generate_response(user_input, session["user_id"])
    
    return jsonify({
        "response": response,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "model": "Llama2-70B" if not OPENAI_AVAILABLE else "GPT-3.5"
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
