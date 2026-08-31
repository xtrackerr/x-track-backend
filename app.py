from flask import Flask, jsonify
from flask_cors import CORS
import twifork
import time

app = Flask(__name__)
CORS(app)  # Allow your frontend to call this

@app.route('/tweets/<username>')
def get_tweets(username):
    try:
        # twifork gets tweets without any API key
        print(f"Fetching tweets for @{username}")
        
        # Get tweets using twifork
        tweets_data = twifork.UserTweets(username, limit=10).tweets
        
        # Format the tweets
        result = []
        for tweet in tweets_data:
            result.append({
                'id': tweet['id'],
                'text': tweet['text'],
                'author_name': tweet['user']['name'],
                'author_username': tweet['user']['username'],
                'created_at': tweet['created_at'],
                'likes': tweet['favorite_count'],
                'retweets': tweet['retweet_count']
            })
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

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