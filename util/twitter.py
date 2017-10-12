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
import os


class Twitter:

    def __init__(self, name, count=1):
        """
        Twitter class consttuctor

        :param name: Account name
        :type name: str
        """
        file_path = os.path.dirname(os.path.realpath(__file__))
        with open(file_path + '/../secret/twitter_key.json') as json_file:
            data = json.load(json_file)

        access_token_key = data["ACCESS_TOKEN_KEY"]
        access_token_secret = data["ACCESS_TOKEN_SECRET"]
        consumer_key = data["CONSUMER_KEY"]
        consumer_secret = data["CONSUMER_SECRET"]

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token_key, access_token_secret)
        self.api = tweepy.API(auth)

        self.user = self.api.get_user(screen_name=name)

        self.account = {}
        self.account["name"] = self.user.name
        self.account["user_id"] = self.user.id_str
        self.account["description"] = self.user.description
        self.account["lang"] = self.user.lang
        self.account["account_created_at"] = self.user.created_at
        self.account["location"] = self.user.location
        self.account["time_zone"] = self.user.time_zone
        self.account["number_tweets"] = self.user.statuses_count
        self.account["number_followers"] = self.user.followers_count
        self.account["following"] = self.user.friends_count
        self.account["member_of"] = self.user.listed_count
        self.account["location"] = self.user.location
        self.account["tweet"] = {}

    def rate_limit_status(self):
        return self.api.rate_limit_status()

    def info(self):
        """
        Print account info
        """
        print("Comapany:", self.account["name"])
        print("Number of tweets:", self.user.statuses_count)

    def extract(self, tweet):
        """
        Extracting hashtag, at, url and mail address from tweet

        :param tweet: tweet message
        :type tweet: str
        :return: hashtag, at and url
        :rtype: tuple
        """
        hashtag_list, mail_address_list, at_list, url_list = [], [], [], []
        for s in list(tweet):
            if re.match('^#.*', s):
                hashtag_list.append(s)
            elif re.match('^@.*', s):
                at_list.append(s)
            elif re.match('.*@.*', s):
                mail_address_list.append(s)
            elif re.match('^http.*', s):
                url_list.append(s)
        return (hashtag_list, mail_address_list, at_list, url_list)

    def normalize(self, tweet):
        """
        Remove url punctuation, url and , mail address from tweet

        :param tweet: tweet message
        :type tweet: str
        :return: clean up tweet message
        :rtype: str
        """
        # TODO use beautifulsoup to convert html special char
        # http://stackoverflow.com/questions/2087370/decode-html-entities-in-python-string
        for s in list(tweet):
            if re.match('^@.*', s):
                tweet.remove(s)
            elif re.match('.*@.*', s):
                tweet.remove(s)
            elif re.match('^#.*', s):
                tweet.remove(s)
            elif re.match('^http.*', s):
                tweet.remove(s)
            elif re.match('&.*', s):
                tweet.remove(s)
            elif s == 'cc':
                tweet.remove(s)
        tweet_norm = [''.join(c for c in s if c not in string.punctuation)
                      for s in tweet]
        # remove blank in array
        tweet_norm = [s for s in tweet_norm if s]
        return tweet_norm

    def get_tweet_info(self, tweet):
        """
        Save tweet info

        :param tweet: tweet message
        :type tweet: str
        """
        self.account["tweet"]["id"] = tweet.id_str
        self.account["tweet"]["retweet_count"] = tweet.retweet_count
        self.account["tweet"]["favorite_count"] = tweet.favorite_count
        self.account["tweet"]["created_at"] = tweet.created_at
        self.account["tweet"]["place"] = tweet.place
        self.account["tweet"]["source"] = tweet.source
        self.account["tweet"]["coordinates"] = tweet.coordinates
        self.account["tweet"]["content"] = {}
        self.account["tweet"]["content"]["text"] = tweet.text
        tw_list = str(tweet.text).split()
        (self.account["tweet"]["content"]["hashtag"],
         self.account["tweet"]["content"]["at"],
         self.account["tweet"]["content"]["url"]) = self.extract(tw_list)
        return self.account

    def get_timeline(self, count):
        return self.api.user_timeline(id=self.user.id, count=count)

    def get_company_letter_percentage(self, count):
        """
        Get percentage of letter in a company's tweets

        :param count: number of tweets to retrieve
        :type count: int
        """
        tweets = self.get_timeline(count)
        count_letter = Counter()
        for tweet in tweets:
            print(tweet.text)
            lower_tweet = [x.lower() for x in self.normalize(tweet.text.split())]
            print(lower_tweet)
            for words in lower_tweet:
                for letters in set(words):
                    count_letter[letters] += 1

        count_letter = sorted(count_letter.items(),
                              key=operator.itemgetter(1),
                              reverse=True)
        tot = 0
        for k, v in count_letter:
            if not re.match('\W+', k):
                tot += v

        for k, v in count_letter:
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
