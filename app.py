from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import time

app = Flask(__name__)
CORS(app)  # Enable cross-origin requests

# Free AI API endpoints with fallback
API_ENDPOINTS = [
    "https://api.deepinfra.com/v1/inference/meta-llama/Meta-Llama-3-70B-Instruct",
    "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
]

@app.route('/')
def home():
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    
    for endpoint in API_ENDPOINTS:
        try:
            response = requests.post(
                endpoint,
                json={"inputs": user_message},
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                reply = response.json()[0]['generated_text'] if 'generated_text' in response.json()[0] else response.json()['results'][0]['generated_text']
                return jsonify({
                    "response": reply,
                    "status": "success",
                    "timestamp": int(time.time())
                })
                
        except Exception as e:
            continue
    
    return jsonify({
        "response": "Our AI services are currently busy. Please try again shortly.",
        "status": "error"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
