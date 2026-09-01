from flask import Flask, jsonify
from flask_cors import CORS
import requests
import re

app = Flask(__name__)
CORS(app)

# === USE YOUR FRESH AUTH_TOKEN HERE ===
AUTH_TOKEN = "8d5d2c87f31c36e910e98d98789d0a30a5c80cd9"  # ← replace with fresh one if needed

# Standard bearer token (works for all)
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"

def fetch_tweets(username, limit=10):
    try:
        session = requests.Session()
        session.headers.update({
            'authorization': f'Bearer {BEARER_TOKEN}',
            'cookie': f'auth_token={AUTH_TOKEN}',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'x-twitter-active-user': 'yes',
            'x-twitter-auth-type': 'OAuth2Session',
            'x-twitter-client-language': 'en'
        })

        # Step 1: Get user info (REST endpoint)
        user_resp = session.get(
            'https://x.com/i/api/1.1/users/show.json',
            params={'screen_name': username},
            timeout=10
        )
        if user_resp.status_code != 200:
            return [{'error': f'User lookup failed: {user_resp.status_code} - {user_resp.text}'}]
        
        user_data = user_resp.json()
        user_id = user_data.get('id_str')
        if not user_id:
            return [{'error': 'User ID not found'}]

        # Step 2: Get tweets (REST endpoint)
        tweets_resp = session.get(
            'https://x.com/i/api/1.1/statuses/user_timeline.json',
            params={
                'user_id': user_id,
                'count': limit,
                'tweet_mode': 'extended',
                'include_rts': False
            },
            timeout=10
        )
        if tweets_resp.status_code != 200:
            return [{'error': f'Tweet fetch failed: {tweets_resp.status_code} - {tweets_resp.text}'}]

        tweets_data = tweets_resp.json()
        if not tweets_data:
            return [{'error': 'No tweets found'}]

        tweets = []
        for tweet in tweets_data:
            text = tweet.get('full_text', tweet.get('text', ''))
            text = re.sub(r'https?://\S+', '', text).strip()
            tweets.append({
                'id': tweet.get('id_str', ''),
                'text': text,
                'author_name': tweet.get('user', {}).get('name', username),
                'author_username': tweet.get('user', {}).get('screen_name', username),
                'created_at': tweet.get('created_at', ''),
                'likes': tweet.get('favorite_count', 0),
                'retweets': tweet.get('retweet_count', 0)
            })

        return tweets

    except Exception as e:
        return [{'error': f'Error: {str(e)}'}]

@app.route('/tweets/<username>')
def get_tweets(username):
    return jsonify(fetch_tweets(username))

@app.route('/')
def home():
    return jsonify({'status': 'online', 'message': 'X Track Pro using REST API'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)