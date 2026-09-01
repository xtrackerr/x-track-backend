from flask import Flask, jsonify
from flask_cors import CORS
import asyncio
import nest_asyncio

nest_asyncio.apply()

app = Flask(__name__)
CORS(app)

async def fetch_tweets_async(username, limit=10):
    try:
        from twikit import Client
        
        # Create client with language
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
        return [{'error': f'Error: {str(e)}'}]

def fetch_tweets_sync(username, limit=10):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Create a new loop if one is already running
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            result = new_loop.run_until_complete(fetch_tweets_async(username, limit))
            new_loop.close()
            return result
        else:
            return loop.run_until_complete(fetch_tweets_async(username, limit))
    except RuntimeError:
        # Fallback to creating a new loop
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        result = new_loop.run_until_complete(fetch_tweets_async(username, limit))
        new_loop.close()
        return result

@app.route('/tweets/<username>')
def get_tweets(username):
    return jsonify(fetch_tweets_sync(username))

@app.route('/')
def home():
    return jsonify({
        'status': 'online',
        'message': 'X Track Pro Backend is running!'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)