from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import time
import re

app = Flask(__name__)
CORS(app)

def get_tweets_from_x(username):
    """Scrape tweets without API key using a simple method"""
    tweets = []
    
    try:
        # Use the public mobile URL (easier to scrape)
        url = f"https://x.com/{username}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            return [{'error': f'Could not fetch tweets for @{username}'}]
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find tweet articles
        articles = soup.find_all('article')
        
        for article in articles[:5]:  # Get up to 5 tweets
            try:
                # Extract text
                text_elem = article.find('div', {'data-testid': 'tweetText'})
                if not text_elem:
                    continue
                text = text_elem.get_text(strip=True)
                
                # Extract time
                time_elem = article.find('time')
                created_at = time_elem.get('datetime') if time_elem else None
                
                # Extract stats
                stats = article.find_all('span', {'data-testid': 'like'})
                likes = 0
                retweets = 0
                
                if stats and len(stats) > 0:
                    try:
                        likes = int(stats[0].get_text().replace(',', ''))
                    except:
                        likes = 0
                
                tweets.append({
                    'id': f'tweet_{len(tweets)}',
                    'text': text,
                    'author_name': username,
                    'author_username': username,
                    'created_at': created_at or 'Just now',
                    'likes': likes,
                    'retweets': retweets
                })
            except Exception as e:
                continue
        
        if not tweets:
            return [{'error': f'No tweets found for @{username}'}]
            
        return tweets
        
    except Exception as e:
        return [{'error': f'Error: {str(e)}'}]

@app.route('/tweets/<username>')
def get_tweets(username):
    result = get_tweets_from_x(username)
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