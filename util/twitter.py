import numpy as np
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import re
from collections import Counter
import tweepy
import string
import json
import operator


class Twitter:

    def __init__(self, name, count=1):
        with open("../secret/twitter_key.json") as json_file:
            data = json.load(json_file)

        access_token_key = data["ACCESS_TOKEN_KEY"]
        access_token_secret = data["ACCESS_TOKEN_SECRET"]
        consumer_key = data["CONSUMER_KEY"]
        consumer_secret = data["CONSUMER_SECRET"]

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token_key, access_token_secret)
        self.api = tweepy.API(auth)

        self.c = count
        self.u = self.api.get_user(screen_name=name)

        self.d = {}
        self.d["name"] = self.u.name
        self.d["user_id"] = self.u.id_str
        self.d["description"] = self.u.description
        self.d["lang"] = self.u.lang
        self.d["account_created_at"] = self.u.created_at
        self.d["location"] = self.u.location
        self.d["time_zone"] = self.u.time_zone
        self.d["number_tweets"] = self.u.statuses_count
        self.d["number_followers"] = self.u.followers_count
        self.d["following"] = self.u.friends_count
        self.d["member_of"] = self.u.listed_count
        self.d["location"] = self.u.location
        self.d["tweet"] = {}

    def info(self):
        print(self.d["name"])
        print("Location: " + self.d["location"])
        print("Time zone: " + self.d["time_zone"])
        print("Number of tweets: " + str(self.d["member_tweets"]))

    def extract(self, sentence):
        """
        extracting list of hashtag, at and url
        """
        h_list, a_list, u_list = [], [], []
        for s in list(sentence):
            if re.match('#.*', s):
                h_list.append(s)
            elif re.match('@.*', s):
                a_list.append(s)
            elif re.match('http.*', s):
                u_list.append(s)
        return (h_list, a_list, u_list)

    def normalize(self, sentence):
        # TODO use beautifulsoup to convert html special char
        # http://stackoverflow.com/questions/2087370/decode-html-entities-in-python-string
        """
        - remove url and @
        - remove punctuation
        """
        for s in list(sentence):
            if re.match('@.*', s):
                sentence.remove(s)
            elif re.match('http.*', s):
                sentence.remove(s)
            elif re.match('&.*', s):
                sentence.remove(s)
            elif s == 'cc':
                sentence.remove(s)
        sentence_norm = [''.join(c for c in s if c not in string.punctuation)
                         for s in sentence]
        # remove blank in array
        sentence_norm = [s for s in sentence_norm if s]
        return sentence_norm

    def run(self):
        statuses = self.api.user_timeline(id=self.u.id, count=self.c)
        counts = Counter()
        for status in statuses:
            self.d["tweet"]["id"] = status.id_str
            self.d["tweet"]["retweet_count"] = status.retweet_count
            self.d["tweet"]["favorite_count"] = status.favorite_count
            self.d["tweet"]["created_at"] = status.created_at
            self.d["tweet"]["place"] = status.place
            self.d["tweet"]["source"] = status.source
            self.d["tweet"]["coordinates"] = status.coordinates
            self.d["tweet"]["content"] = {}
            self.d["tweet"]["content"]["text"] = status.text
            tw = status.text
            tw_list = str(status.text).split()
            self.extract(tw)
            (self.d["tweet"]["content"]["hashtag"],
             self.d["tweet"]["content"]["at"],
             self.d["tweet"]["content"]["url"]) = self.extract(tw_list)
            tw_norm = self.normalize(tw_list)
            tw_norm_tolower = [x.lower() for x in tw_norm]
            for words in tw_norm_tolower:
                for letters in set(words):
                    counts[letters] += 1

        counts = sorted(counts.items(), key=operator.itemgetter(1), reverse=True)
        tot = 0
        for k, v in counts:
            if not re.match('\W+', k):
                tot += v

        for k, v in counts:
            if not re.match('\W+', k):
                print("{:<10}{:.2f}%".format(k, 100 * v / tot))

    def get_tweets(self, handle):
        stock_tweets = self.api.search(handle)

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

    def follower_count(self, handle):
        url = "https://twitter.com/{}".format(handle)
        nav = 'ProfileNav-'
        soup = BeautifulSoup(requests.get(url).text, 'html.parser')
        followers = soup.find('li', {'class': nav + 'item--followers'}).find('span', {'class': nav + 'value'}).text
        return followers
