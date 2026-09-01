from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)
CORS(app)  # Allow frontend to call this

def get_tweets_from_nitter(username):
    """
    Fetch tweets using public Nitter instances.
    Nitter is a privacy-friendly frontend for X/Twitter.
    """
    tweets = []
    
    # List of public Nitter instances (some may be down)
    instances = [
        f'https://nitter.net/{username}',
        f'https://nitter.poast.org/{username}',
        f'https://nitter.1d4.us/{username}',
        f'https://nitter.esmailelbob.xyz/{username}',
        f'https://nitter.kavin.rocks/{username}'
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    for instance_url in instances:
        try:
            response = requests.get(instance_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Nitter uses div.timeline-item for each tweet
            timeline_items = soup.find_all('div', class_='timeline-item')
            
            if not timeline_items:
                continue
            
            for item in timeline_items[:10]:  # Get up to 10 tweets
                try:
                    # Tweet content
                    content_div = item.find('div', class_='tweet-content')
                    if not content_div:
                        continue
                    text = content_div.get_text(strip=True)
                    
                    # Tweet time
                    time_elem = item.find('span', class_='tweet-date')
                    created_at = time_elem.get_text(strip=True) if time_elem else 'Just now'
                    
                    # Stats (likes, retweets) - Nitter may have these
                    stats = item.find_all('span', class_='tweet-stat')
                    likes = 0
                    retweets = 0
                    # We'll keep it simple, but you can parse stats if needed
                    
                    tweets.append({
                        'id': f'tweet_{len(tweets)}',
                        'text': text,
                        'author_name': username,
                        'author_username': username,
                        'created_at': created_at,
                        'likes': likes,
                        'retweets': retweets
                    })
                except Exception:
                    continue
            
            # If we got tweets, break out of the instance loop
            if tweets:
                break
        
        except Exception:
            continue  # Try next instance
    
    if not tweets:
        return [{'error': f'Could not fetch tweets for @{username}. All instances may be blocked.'}]
    
    return tweets

@app.route('/tweets/<username>')
def get_tweets(username):
    result = get_tweets_from_nitter(username)
    return jsonify(result)

@app.route('/')
def home():
    return jsonify({
        'status': 'online',
        'message': 'X Track Pro Backend is running!',
        'endpoints': {
            '/tweets/<username>': 'Get recent tweets for a user'
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)