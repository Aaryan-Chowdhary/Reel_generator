from flask import Flask, render_template, request
import logic # Importing the file we just made
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    topic = request.form.get('topic')
    
    # Run the magic function from logic.py
    script_text = logic.make_reel(topic)
    
    return render_template('index.html', video_ready=True, script=script_text)

if __name__ == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(debug=True)