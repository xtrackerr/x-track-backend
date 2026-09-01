from flask import Flask, jsonify
from flask_cors import CORS
from twikit import Client
import asyncio

app = Flask(__name__)
CORS(app)

async def get_tweets_async(username, limit=10):
    try:
        # Create client – guest authentication happens automatically
        client = Client('en-US')
        
        # Get user by screen name
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
    # Use asyncio.run() – simple and works in Flask
    return jsonify(asyncio.run(get_tweets_async(username)))

@app.route('/')
def home():
    return jsonify({
        'status': 'online',
        'message': 'X Track Pro Backend is running!'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)