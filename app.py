from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import json
import os
import urllib.request
import stat
import platform

app = Flask(__name__)
CORS(app)

def get_x_cli():
    """Download x-cli binary if not present."""
    bin_path = "/tmp/x-cli"
    if os.path.exists(bin_path):
        return bin_path
    
    # Detect OS/Arch
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    if system != "linux":
        return None
    
    if arch in ["x86_64", "amd64"]:
        url = "https://github.com/tamnd/x-cli/releases/latest/download/x-linux-amd64"
    elif arch in ["aarch64", "arm64"]:
        url = "https://github.com/tamnd/x-cli/releases/latest/download/x-linux-arm64"
    else:
        return None
    
    try:
        urllib.request.urlretrieve(url, bin_path)
        os.chmod(bin_path, os.stat(bin_path).st_mode | stat.S_IEXEC)
        return bin_path
    except:
        return None

def fetch_tweets(username, limit=10):
    try:
        x_bin = get_x_cli()
        if not x_bin:
            return [{'error': 'Unsupported platform'}]
        
        # Command: x-cli timeline username --guest -n limit
        cmd = [x_bin, "timeline", username, "--guest", "-n", str(limit)]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return [{'error': f'Failed: {result.stderr}'}]
        
        # Parse JSONL output
        tweets = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            try:
                data = json.loads(line)
                tweets.append({
                    'id': data.get('id', ''),
                    'text': data.get('text', ''),
                    'author_name': data.get('author', {}).get('name', username),
                    'author_username': data.get('author', {}).get('username', username),
                    'created_at': data.get('created_at', ''),
                    'likes': data.get('metrics', {}).get('likes', 0),
                    'retweets': data.get('metrics', {}).get('retweets', 0)
                })
            except json.JSONDecodeError:
                continue
        
        if not tweets:
            return [{'error': 'No tweets found'}]
        
        return tweets
        
    except subprocess.TimeoutExpired:
        return [{'error': 'Request timed out'}]
    except Exception as e:
        return [{'error': f'Error: {str(e)}'}]

@app.route('/tweets/<username>')
def get_tweets(username):
    return jsonify(fetch_tweets(username))

@app.route('/')
def home():
    return jsonify({'status': 'online', 'message': 'X Track Pro Backend is running!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)