from flask import Flask, render_template, request, jsonify
import wikipedia

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    query = request.form['query']
    
    try:
        # Try to fetch a summary from Wikipedia
        summary = wikipedia.summary(query, sentences=2)
        return jsonify({'response': summary})
    
    except wikipedia.exceptions.DisambiguationError as e:
        # If it's ambiguous, return the options
        response = "That’s a bit ambiguous. Here are some options you can choose from:\n" + "\n".join(e.options)
        return jsonify({'response': response})
    
    except wikipedia.exceptions.PageError:
        # If no page is found for the query
        return jsonify({'response': "I couldn’t find a page on that. Please try asking something else."})
    
    except wikipedia.exceptions.RedirectError:
        # If there's a redirect error
        return jsonify({'response': "That page is redirected. Trying to find the related page."})
    
    except Exception as e:
        # Catching any other unexpected errors
        return jsonify({'response': f"Something went wrong: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
