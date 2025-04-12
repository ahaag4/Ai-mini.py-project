from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import time

app = Flask(__name__)
CORS(app)  # Fixes frontend-backend connection issues

# Reliable free AI endpoints (no keys required)
API_ENDPOINTS = [
    {
        "url": "https://api.deepinfra.com/v1/inference/meta-llama/Meta-Llama-3-70B-Instruct",
        "method": lambda text: {"input": text},
        "parse": lambda r: r.json()['results'][0]['generated_text']
    },
    {
        "url": "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1", 
        "method": lambda text: {"inputs": text},
        "parse": lambda r: r.json()[0]['generated_text']
    }
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
                endpoint["url"],
                json=endpoint["method"](user_message),
                headers={"Content-Type": "application/json"},
                timeout=10  # Prevents hanging
            )
            
            if response.status_code == 200:
                return jsonify({
                    "response": endpoint["parse"](response),
                    "status": "success"
                })
                
        except requests.exceptions.RequestException as e:
            print(f"API error ({endpoint['url']}): {str(e)}")
            continue  # Try next endpoint
    
    return jsonify({
        "response": "All AI services are currently busy. Please try again in a moment.",
        "status": "error"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
