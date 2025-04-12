from flask import Flask, render_template, jsonify
import subprocess

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/start-server', methods=['POST'])
def start_server():
    try:
        subprocess.Popen(['bash', 'server_control.sh', 'start'])
        return jsonify({'status': 'started'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/stop-server', methods=['POST'])
def stop_server():
    try:
        subprocess.Popen(['bash', 'server_control.sh', 'stop'])
        return jsonify({'status': 'stopped'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
