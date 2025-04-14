from flask import Flask, render_template, request
import wikipedia

app = Flask(__name__)

# Store chat history
history = []

@app.route("/", methods=["GET", "POST"])
def index():
    response = ""
    if request.method == "POST":
        user_input = request.form.get("question", "").strip()
        if user_input:
            try:
                response = wikipedia.summary(user_input, sentences=2)
                history.append({"question": user_input, "answer": response})
            except wikipedia.exceptions.DisambiguationError as e:
                response = "That’s a bit ambiguous. Try one of: " + ", ".join(e.options[:5])
            except wikipedia.exceptions.PageError:
                response = "I couldn’t find a page on that. Please try something else."
            except Exception as e:
                response = f"Something went wrong: {str(e)}"
    return render_template("index.html", response=response, history=history)

@app.route("/clear")
def clear_history():
    history.clear()
    return render_template("index.html", response="Conversation history cleared.", history=[])

if __name__ == "__main__":
    app.run(debug=True)
