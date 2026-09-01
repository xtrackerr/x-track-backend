from flask import Flask, jsonify
from flask_cors import CORS
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)
CORS(app)

def get_tweets_from_rss(username):
    """Get tweets from RSS feed (no API key)"""
    try:
        # Use nitter RSS (if any instance is working)
        # Or use a service like twiiit.com
        url = f"https://nitter.net/{username}/rss"
        
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return [{'error': f'Could not fetch RSS for @{username}'}]
        
        root = ET.fromstring(response.content)
        items = root.findall('.//item')
        
        tweets = []
        for item in items[:10]:
            title = item.find('title')
            pub_date = item.find('pubDate')
            link = item.find('link')
            
            tweets.append({
                'id': link.text.split('/')[-1] if link else '',
                'text': title.text if title is not None else '',
                'author_name': username,
                'author_username': username,
                'created_at': pub_date.text if pub_date is not None else '',
                'likes': 0,
                'retweets': 0
            })
        
        return tweets if tweets else [{'error': f'No tweets found for @{username}'}]
        
    except Exception as e:
        return [{'error': f'Error: {str(e)}'}]

@app.route('/tweets/<username>')
def get_tweets(username):
    return jsonify(get_tweets_from_rss(username))

@app.route('/')
def home():
    return jsonify({'status': 'online', 'message': 'X Track Pro Backend is running!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)