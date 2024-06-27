from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# MongoDB configuration
client = MongoClient('mongodb://localhost:27017/')
db = client['github_events']
collection = db['events']

@app.route('/ui', methods=['GET'])
def ui():
    return render_template('index.html')

@app.route('/')
def home():
    return "Webhook Receiver is running."

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        data = request.json
        event_type = request.headers.get('X-GitHub-Event')

        if event_type == 'push':
            author = data['pusher']['name']
            to_branch = data['ref'].split('/')[-1]
            timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

            event = {
                'type': 'push',
                'author': author,
                'to_branch': to_branch,
                'timestamp': timestamp
            }
            collection.insert_one(event)
            return jsonify({'msg': 'Push event received'}), 200

        elif event_type == 'pull_request':
            action = data['action']
            if action in ['opened', 'closed']:
                author = data['pull_request']['user']['login']
                from_branch = data['pull_request']['head']['ref']
                to_branch = data['pull_request']['base']['ref']
                timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

                event = {
                    'type': 'pull_request',
                    'action': action,
                    'author': author,
                    'from_branch': from_branch,
                    'to_branch': to_branch,
                    'timestamp': timestamp
                }
                collection.insert_one(event)
                return jsonify({'msg': 'Pull request event received'}), 200

        elif event_type == 'pull_request' and action == 'closed' and data['pull_request']['merged']:
            author = data['pull_request']['user']['login']
            from_branch = data['pull_request']['head']['ref']
            to_branch = data['pull_request']['base']['ref']
            timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

            event = {
                'type': 'merge',
                'author': author,
                'from_branch': from_branch,
                'to_branch': to_branch,
                'timestamp': timestamp
            }
            collection.insert_one(event)
            return jsonify({'msg': 'Merge event received'}), 200

        return jsonify({'msg': 'Event type not handled'}), 400

@app.route('/events', methods=['GET'])
def get_events():
    events = list(collection.find().sort('timestamp', -1))
    for event in events:
        event['_id'] = str(event['_id'])
    return jsonify(events)

@app.route('/ui', methods=['GET'])
def ui():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
