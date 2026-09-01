from flask import Flask, jsonify
from flask_cors import CORS
from twifork import Client
import asyncio

app = Flask(__name__)
CORS(app)

def get_tweets_sync(username, limit=10):
    """Get tweets using twifork (no API key needed)"""
    try:
        # Create client and get tweets
        client = Client('en-US')
        tweets = asyncio.run(client.get_user_tweets_by_username(username, limit))
        
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
        return [{'error': f'Error: {str(e)}'}]

@app.route('/tweets/<username>')
def get_tweets(username):
    return jsonify(get_tweets_sync(username))

@app.route('/')
def home():
    return jsonify({'status': 'online', 'message': 'X Track Pro Backend is running!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)