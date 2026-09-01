from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import json
import os

app = Flask(__name__)
CORS(app)

def fetch_tweets(username, limit=10):
    """Use x-tweet-fetcher CLI to get tweets."""
    try:
        # Run the xtf command
        cmd = [
            "xtf",
            "--user", username,
            "--limit", str(limit),
            "--backend", "auto"  # Auto-fallback between backends
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return [{'error': f'Command failed: {result.stderr}'}]
        
        # Parse the JSON output
        tweets = json.loads(result.stdout)
        
        # Format the response
        formatted = []
        for tweet in tweets:
            formatted.append({
                'id': tweet.get('id', ''),
                'text': tweet.get('text', ''),
                'author_name': tweet.get('author', {}).get('name', username),
                'author_username': tweet.get('author', {}).get('username', username),
                'created_at': tweet.get('created_at', ''),
                'likes': tweet.get('metrics', {}).get('likes', 0),
                'retweets': tweet.get('metrics', {}).get('retweets', 0)
            })
        
        return formatted
        
    except subprocess.TimeoutExpired:
        return [{'error': 'Request timed out'}]
    except Exception as e:
        return [{'error': f'Error: {str(e)}'}]

@app.route('/tweets/<username>')
def get_tweets(username):
    return jsonify(fetch_tweets(username))

@app.route('/')
def home():
    return jsonify({
        'status': 'online',
        'message': 'X Track Pro Backend is running!'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)