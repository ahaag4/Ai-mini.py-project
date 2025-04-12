from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Fast Hugging Face model
API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-small"

@app.route('/')
def home():
    return render_template("chat.html")  # Your HTML must be named 'chat.html' and in 'templates/' folder

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form['user_input']

    payload = {
        "inputs": f"User: {user_input}\nAI:",
    }

    try:
        response = requests.post(API_URL, json=payload, timeout=20)
        data = response.json()

        # Debug output
        print("Model response:", data)

        if isinstance(data, list) and 'generated_text' in data[0]:
            reply = data[0]['generated_text'].replace("User:", "").replace("AI:", "").strip()
        elif 'error' in data:
            reply = f"Model error: {data['error']}"
        else:
            reply = "Sorry, I didn't get a valid response."

        return jsonify({"response": reply})
    except Exception as e:
        return jsonify({"response": f"Server error: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
