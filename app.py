from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import pytz
import urllib.parse

app = Flask(__name__)

# --- STEP 1: DATABASE CONNECTION (Error Fixed) ---
password = urllib.parse.quote_plus("Bobby@21nov2001")
MONGO_URI = f"mongodb+srv://RRBHARDWAJ:{password}@cluster0.qyk1df2.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(MONGO_URI)
db = client['github_tracker']
collection = db['events']

@app.route('/webhook', methods=['POST'])
def handle_github_webhook():
    data = request.json
    event_type = request.headers.get('X-GitHub-Event', 'push').upper()

    try:
        # TechStaX Requirements: request_id, author, action, timestamp
        payload = {
            "request_id": data.get('after') if event_type == 'PUSH' else str(data.get('pull_request', {}).get('id', '')),
            "author": data['sender']['login'],
            "action": event_type,
            "from_branch": data.get('pull_request', {}).get('head', {}).get('ref', '') if event_type != 'PUSH' else '',
            "to_branch": data.get('ref', '').split('/')[-1] if event_type == 'PUSH' else data.get('pull_request', {}).get('base', {}).get('ref', ''),
            "timestamp": datetime.now(pytz.utc).strftime('%d %B %Y - %I:%M %p UTC')
        }

        collection.insert_one(payload)
        print(f"✅ Data Saved: {event_type} by {payload['author']}")
        return jsonify({"message": "Data saved successfully"}), 200

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)