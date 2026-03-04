from flask import Flask, jsonify, render_template
from flask_cors import CORS
from scheduler import RouteScheduler

app = Flask(__name__)
CORS(app)
scheduler = RouteScheduler()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/distribute', methods=['POST'])
def distribute():
    schedule = scheduler.distribute()
    return jsonify({'schedule': schedule})

@app.route('/api/reset', methods=['POST'])
def reset():
    schedule = scheduler.reset()
    return jsonify({'schedule': schedule})

@app.route('/api/current')
def current():
    schedule = scheduler.original_schedule
    return jsonify({'schedule': schedule})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
