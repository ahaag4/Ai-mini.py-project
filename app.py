from flask import Flask, request, session, redirect, render_template_string
import wikipedia

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key in production

# HTML + CSS Template
template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Wikipedia ChatBot | AI Assistant</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="A smart AI chatbot powered by Wikipedia">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f4f6f9; }
        .container { max-width: 800px; margin-top: 50px; }
        .chat-box { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 12px rgba(0,0,0,0.08); }
        .chat-entry { margin-bottom: 15px; }
        .chat-question { background: #d1e7dd; padding: 12px; border-radius: 8px; }
        .chat-answer { background: #e2e3e5; padding: 12px; border-radius: 8px; }
        footer { margin-top: 60px; text-align: center; font-size: 13px; color: #6c757d; }
    </style>
</head>
<body>
<div class="container">
    <div class="chat-box">
        <h2 class="text-center mb-4">Wikipedia AI ChatBot</h2>
        <form method="POST" class="input-group mb-4">
            <input type="text" name="question" class="form-control" placeholder="Ask me anything..." required>
            <button class="btn btn-primary" type="submit">Ask</button>
        </form>

        {% for item in history|reverse %}
            <div class="chat-entry">
                <div class="chat-question"><strong>You:</strong> {{ item.question }}</div>
                <div class="chat-answer"><strong>AI:</strong> {{ item.answer }}</div>
            </div>
        {% endfor %}

        <div class="text-end">
            <a href="/clear" class="btn btn-outline-danger btn-sm mt-3">Clear History</a>
        </div>
    </div>
</div>

<footer>&copy; 2025 Wikipedia AI ChatBot. Built with Flask & Wikipedia API.</footer>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if "history" not in session:
        session["history"] = []

    if request.method == "POST":
        question = request.form.get("question", "").strip()
        if question:
            try:
                answer = wikipedia.summary(question, sentences=2)
            except wikipedia.exceptions.DisambiguationError as e:
                answer = "That’s a bit ambiguous. Please try one of these: " + ", ".join(e.options[:5])
            except wikipedia.exceptions.PageError:
                answer = "No results found. Please ask about something else."
            except Exception as e:
                answer = f"Error: {str(e)}"

            # Save question and answer to history
            session["history"].append({"question": question, "answer": answer})
            session.modified = True

    return render_template_string(template, history=session.get("history", []))

@app.route("/clear")
def clear():
    session["history"] = []
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
