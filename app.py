from flask import Flask, jsonify
from flask_cors import CORS
import feedparser
import requests
import time

app = Flask(__name__)
CORS(app)

# Public RSSHub instances (working as of Sept 2026)
RSSHUB_INSTANCES = [
    "https://rsshub.app",
    "https://rsshub.rssforever.com",
    "https://rsshub.feeded.xyz",
    "https://rsshub.youxingk.com"
]

def get_tweets_from_rss(username, limit=10):
    """Fetch tweets using RSSHub public instances (no auth)."""
    
    for instance in RSSHUB_INSTANCES:
        try:
            feed_url = f"{instance}/twitter/user/{username}"
            
            # Add browser-like headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(feed_url, headers=headers, timeout=12)
            if response.status_code != 200:
                continue
            
            feed = feedparser.parse(response.content)
            
            if not feed.entries:
                continue
            
            tweets = []
            for entry in feed.entries[:limit]:
                # RSS title usually = "username: tweet text"
                text = entry.title if hasattr(entry, 'title') else ''
                if ': ' in text:
                    text = text.split(': ', 1)[1]
                
                # Extract published date
                published = entry.published if hasattr(entry, 'published') else ''
                
                # Extract tweet link and ID
                link = entry.link if hasattr(entry, 'link') else ''
                tweet_id = link.split('/')[-1] if link else ''
                
                tweets.append({
                    'id': tweet_id,
                    'text': text,
                    'author_name': username,
                    'author_username': username,
                    'created_at': published,
                    'likes': 0,
                    'retweets': 0
                })
            
            if tweets:
                return tweets
                
        except Exception:
            # Try next instance silently
            continue
    
    return [{'error': f'Could not fetch tweets for @{username} from any RSSHub instance. Try again later.'}]

@app.route('/tweets/<username>')
def get_tweets(username):
    return jsonify(get_tweets_from_rss(username))

@app.route('/')
def home():
    return jsonify({
        'status': 'online',
        'message': 'X Track Pro Backend running via RSSHub'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)