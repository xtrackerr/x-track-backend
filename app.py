from flask import Flask, jsonify
from flask_cors import CORS
from twikit import Client  # twifork still imports as twikit
import asyncio

app = Flask(__name__)
CORS(app)

def fetch_tweets_sync(username, limit=10):
    """Fetch tweets using twifork (no API key needed)."""
    try:
        async def fetch():
            client = Client('en-US')
            
            # 1. Get the user's numeric ID from their username
            user = await client.get_user_by_screen_name(username)
            user_id = user.id
            
            # 2. Get the user's tweets using their numeric ID
            #    The second parameter can be 'Tweets' or 'Replies' or 'Media'
            tweets = await client.get_user_tweets(user_id, 'Tweets', count=limit)
            
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

        # Run the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            tweets_data = loop.run_until_complete(fetch())
        finally:
            loop.close()
        return tweets_data

    except Exception as e:
        return [{'error': f'Error: {str(e)}'}]

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