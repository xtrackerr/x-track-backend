from flask import Flask, jsonify
from flask_cors import CORS
import asyncio
import os

app = Flask(__name__)
CORS(app)

# Read credentials from environment variables
X_USERNAME = os.environ.get('X_USERNAME')
X_PASSWORD = os.environ.get('X_PASSWORD')

async def fetch_tweets(username, limit=10):
    try:
        from twikit import Client
        
        if not X_USERNAME or not X_PASSWORD:
            return [{'error': 'Missing X credentials on server'}]
        
        # ✅ CORRECT: No 'proxies' argument
        client = Client('en-US')
        
        # Login with credentials
        await client.login(
            auth_info_1=X_USERNAME,
            password=X_PASSWORD
        )
        
        # Get user
        user = await client.get_user_by_screen_name(username)
        
        # Get tweets
        tweets = await client.get_user_tweets(user.id, 'Tweets', count=limit)
        
        result = []
        for tweet in tweets:
            result.append({
                'id': tweet.id,
                'text': tweet.text,
                'author_name': tweet.user.name,
                'author_username': tweet.user.screen_name,
                'created_at': str(tweet.created_at),
                'likes': tweet.favorite_count,
                'retweets': tweet.retweet_count
            })
        return result
        
    except Exception as e:
        return [{'error': str(e)}]

@app.route('/tweets/<username>')
def get_tweets(username):
    return jsonify(asyncio.run(fetch_tweets(username)))

@app.route('/')
def home():
    return jsonify({
        'status': 'online',
        'message': 'X Track Pro Backend is running!'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)