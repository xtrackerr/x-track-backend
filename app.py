from flask import Flask, jsonify
from flask_cors import CORS
import requests
import json
import re
import os

app = Flask(__name__)
CORS(app)

# HARDCODED AUTH_TOKEN (Replace if it expires)
AUTH_TOKEN = "8d5d2c87f31c36e910e98d98789d0a30a5c80cd9"

def fetch_tweets(username, limit=10):
    """Direct GraphQL API using auth_token."""
    
    if not AUTH_TOKEN:
        return [{'error': 'Missing auth_token'}]
    
    headers = {
        'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
        'cookie': f'auth_token={AUTH_TOKEN}',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'x-twitter-active-user': 'yes',
        'x-twitter-auth-type': 'OAuth2Session',
        'x-twitter-client-language': 'en'
    }
    
    try:
        # Get user ID
        user_url = "https://x.com/i/api/graphql/-tV5-zb-lS3WDW34ppXrQg/UserByScreenName"
        user_params = {'variables': json.dumps({"screen_name": username, "withSafetyModeUserFields": True})}
        user_resp = requests.get(user_url, headers=headers, params=user_params, timeout=10)
        if user_resp.status_code != 200:
            return [{'error': f'User lookup failed: {user_resp.status_code}'}]
        user_data = user_resp.json()
        user_id = user_data['data']['user']['result']['id']
        
        # Get tweets
        tweets_url = "https://x.com/i/api/graphql/-tV5-zb-lS3WDW34ppXrQg/UserTweets"
        tweets_params = {'variables': json.dumps({
            "userId": user_id,
            "count": limit,
            "includePromotedContent": False,
            "withQuickPromoteEligibilityTweetFields": False,
            "withVoice": False,
            "withV2Timeline": True
        })}
        tweets_resp = requests.get(tweets_url, headers=headers, params=tweets_params, timeout=10)
        if tweets_resp.status_code != 200:
            return [{'error': f'Tweet fetch failed: {tweets_resp.status_code}'}]
        data = tweets_resp.json()
        
        tweets = []
        instructions = data['data']['user']['result']['timeline_v2']['timeline']['instructions']
        for instruction in instructions:
            if instruction.get('type') == 'TimelineAddEntries':
                for entry in instruction.get('entries', []):
                    try:
                        tweet_data = entry['content']['itemContent']['tweet_results']['result']
                        if tweet_data.get('retweeted_status_result'):
                            continue
                        legacy = tweet_data.get('legacy', {})
                        text = legacy.get('full_text', '')
                        text = re.sub(r'https?://\S+', '', text).strip()
                        tweets.append({
                            'id': tweet_data.get('rest_id', ''),
                            'text': text,
                            'author_name': username,
                            'author_username': username,
                            'created_at': legacy.get('created_at', ''),
                            'likes': legacy.get('favorite_count', 0),
                            'retweets': legacy.get('retweet_count', 0)
                        })
                        if len(tweets) >= limit:
                            break
                    except:
                        continue
                if len(tweets) >= limit:
                    break
        
        if not tweets:
            return [{'error': f'No tweets found for @{username}'}]
        return tweets
        
    except Exception as e:
        return [{'error': f'Error: {str(e)}'}]

@app.route('/tweets/<username>')
def get_tweets(username):
    return jsonify(fetch_tweets(username))

@app.route('/')
def home():
    return jsonify({'status': 'online', 'message': 'X Track Pro running'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)