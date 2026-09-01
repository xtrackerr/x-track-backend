from flask import Flask, jsonify
from flask_cors import CORS
from twikit import Client  # twifork imports as twikit
import asyncio

app = Flask(__name__)
CORS(app)

async def fetch_tweets_async(username, limit=10):
    try:
        # 1. Create a client and perform guest authentication
        client = Client('en-US')
        await client.guest_auth()  # CRITICAL: This creates a guest session

        # 2. Get user by screen name
        user = await client.get_user_by_screen_name(username)
        user_id = user.id

        # 3. Get tweets using the user's numeric ID
        tweets = await client.get_user_tweets(user_id, 'Tweets', count=limit)

        # 4. Format the response
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
        # Return the error message as a JSON-friendly dict
        return [{'error': f'Error: {str(e)}'}]

def fetch_tweets_sync(username, limit=10):
    """Synchronous wrapper for the async function."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(fetch_tweets_async(username, limit))
        loop.close()
        return result
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