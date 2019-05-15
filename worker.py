from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream
import twitter
import os
import argparse
import urllib
import json
import datetime as dt
from dateutil import parser
import afinn
from time import sleep
import re
import subprocess

# twitter tokens, keys, secrets, and Twitter handle in the following variables
CONSUMER_KEY = ''
CONSUMER_SECRET =''
OAUTH_TOKEN = ''
OAUTH_TOKEN_SECRET = ''
TWITTER_HANDLE = ''  # your handle
TWITTER_ID = 0 # your id (int type)

# Handle input arguments
argparser = argparse.ArgumentParser()
argparser.add_argument('--langs')
argparser.add_argument('--tags')
args = argparser.parse_args()

langs = args.langs.split(",")
tags = args.tags.split(",")

# Sentiment models for `score_sentiment` function
sentiment_model = dict(
    (lang, afinn.Afinn(language=lang))
    for lang in langs
)
    
def score_sentiment(text, lang):
    return sentiment_model[lang].score(text) / len(text.split())
    
def search_tweets(q, count=100, result_type="recent", lang='en'):
    return t.search.tweets(q=q, result_type=result_type, count=count, lang=lang)['statuses']

def tweet_in_subject(text):
    for tag in tags:
        if tag in text.upper():
            return True
    return False

def get_user_links_likes(user):
    try:
        return [
            (
                user,
                tweet['user']['screen_name'],
                str(parser.parse(tweet['created_at'])),
                str(tweet['id'])
            )
            for tweet in t.favorites.list(screen_name=user, count=100)
            if tweet['user']['screen_name'] in users and tweet_in_subject(tweet['text'])
        ]
    except KeyError: # Using keyError as dummy, insert correct error type
        print("Warning: API fails for user %s" % user)
        return []

def update_users(new_users):
    with open('data/users.json', 'r') as fp:
        users = json.load(fp)
    with open('data/users.json', 'w') as fp:
        users = sorted(set(users) | set(new_users))
        json.dump(users, fp)
    return users
    
def update_tweets(new_tweets):
    with open('data/tweets.json', 'r') as fp:
        tweets = json.load(fp)
    with open('data/tweets.json', 'w') as fp:
        tweets.update(dict((tweet['id'], tweet) for tweet in new_tweets))
        json.dump(tweets, fp)

def update_links(new_links, filename):
    with open(filename, 'r') as fp:
        rows = fp.read().split("\n")
        header = rows[0]
        links = [tuple(l.split(",")) for l in rows[1:]]
    with open(filename, 'w') as fp:
        links = sorted(set(links) | set(new_links))
        fp.write(header + "\n")
        fp.write("\n".join([",".join(l) for l in links]))

t = Twitter(auth=OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET))

while True:
    # Get users that tweeted with #netsci2018 tag
    print("Searching for tweets with tags %r" % tags)
    collection_tweets = []
    for tag in tags:
        for lang in langs:
            collection_tweets += search_tweets(tag, lang=lang)
    print("Loaded %d tweets"  % len(collection_tweets), end=" ")

    print("from", end=" ")
    users = sorted(set(update_users([
        tweet['user']['screen_name']
        for tweet in collection_tweets
        if tweet['text'][:2] != "RT"
    ])))  # Everybody who has tweeted
    print("%d different users:" %len(users))

    print("\n".join(users))
    print("\n... saving users")
    print("... saving tweets")
    update_tweets(collection_tweets)

    # Get retweet links
    links_retweets = []
    for tweet in collection_tweets:
        if 'retweeted_status' in tweet and tweet['retweeted_status']['user']['screen_name'] in users:
            links_retweets.append(
                (
                    tweet['user']['screen_name'],
                    tweet['retweeted_status']['user']['screen_name'],
                    str(parser.parse(tweet['created_at'])),
                    str(tweet['id']),
                    str(score_sentiment(tweet['text'], tweet['lang']) if tweet['is_quote_status'] else 1)
                )
            )

    # Get mention links
    links_mentions = []
    for tweet in collection_tweets:
        if 'retweeted_status' not in tweet:
            sentiment = score_sentiment(tweet['text'], tweet['lang'])
            for mentioned_user in re.findall(r"(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9_]+)", tweet['text']):
                if mentioned_user:
                    links_mentions.append(
                        (
                            tweet['user']['screen_name'],
                            mentioned_user,
                            str(parser.parse(tweet['created_at'])),
                            str(tweet['id']),
                            str(sentiment)
                        )
                    )

    update_links(links_retweets, "data/retweets.csv")
    update_links(links_mentions, "data/mentions.csv")
    subprocess.call("bash sync.sh".split())

    # For each, produce links from their favorites
    print("\nGetting like-links for each user:")
    links_likes = []
    for user in users:
        try:
            links_user = get_user_links_likes(user)
        except twitter.TwitterHTTPError:
            print("Warning: Rate limit exceeded (user: %s), saving data and waiting 15 minutes" % user)
            update_links(links_likes, "data/likes.csv")
            links_likes = []
            subprocess.call("bash sync.sh".split())
            try:
                sleep(60 * 15)
            except KeyboardInterrupt:
                break
            try:
                links_user = get_user_links_likes(user)
            except: # Twiter Rate Limit Error
                continue
            continue

        print(user, len(links_user))
        links_likes.extend(links_user)

    print("\nTotal:", len(links_likes))


    print("\n... saving links")
    update_links(links_likes, "data/likes.csv")
    subprocess.call("bash sync.sh".split())

    print("Successfully updated data!")
        
