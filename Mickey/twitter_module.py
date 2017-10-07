import tweepy
import numpy as np
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob


# API Authentification
# Gets User API keys
with open('secret/twitter_key', 'r') as f:
    auth_list = []
    for line in f:
        item = line.replace('\n', '')
        auth_list.append(item)
    auth = tweepy.OAuthHandler(auth_list[0], auth_list[1])
    auth.set_access_token(auth_list[2], auth_list[3])
    api = tweepy.API(auth)


#
def get_tweets(handle):
    stock_tweets = api.search(handle)

    subjectivity_avg = []
    polarity_avg = []

    for tweet in stock_tweets:
        print(tweet.text)
        analysis = TextBlob(tweet.text)
        subjectivity_avg.append(analysis.subjectivity)
        polarity_avg.append(analysis.polarity)
        print(analysis.sentiment)

        print(np.mean(subjectivity_avg))
        print(np.mean(polarity_avg))


# Get follower count by using HTML parser
def follower_count(handle):
    url = "https://twitter.com/{}".format(handle)
    nav = 'ProfileNav-'
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    followers = soup.find('li', {'class': nav + 'item--followers'}).find('span', {'class': nav + 'value'}).text
    return followers