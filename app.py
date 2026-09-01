from flask import Flask, jsonify
from flask_cors import CORS
from twikit import Client  # twifork still imports as twikit
import asyncio
import nest_asyncio

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

app = Flask(__name__)
CORS(app)

def get_tweets_sync(username, limit=10):
    """Get tweets using twifork (no API key needed)"""
    try:
        # Create client with impersonation to bypass 403 blocks
        client = Client('en-US')
        
        # Run the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tweets = loop.run_until_complete(
            client.get_user_tweets_by_username(username, limit)
        )
        loop.close()
        
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
    return jsonify({
        'status': 'online',
        'message': 'X Track Pro Backend is running!'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)