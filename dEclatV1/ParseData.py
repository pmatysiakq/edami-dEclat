import re
import tweepy, os

class Data:

    def __init__(self, user):
        self.data_path = Data.get_twitts(user)
        self.database = self.create_database()
        self.unique_words = self.get_unique_words()
        self.unique_numbers = self.get_unique_numbers()
        self.discretized_data = self.disc_data()
        self.dictionary = self.disc_words()
        self.tweet_count = len(self.database)

    def create_database(self):
        with open(self.data_path, "r", encoding='utf-8') as file:
            tweets = file.readlines()
        data = []
        id = 0
        for tweet in tweets:
            temp_tweet = []
            tweet = tweet.strip()
            tweet = tweet.split()
            for i in range(len(tweet)):
                tweet[i] = tweet[i].strip("!#$%^&*(){}[];:\"\\,./<>?|“")
            for word in tweet:
                if re.match("^[a-zA-Z’]+$", word):
                    if word not in temp_tweet and len(word) > 4:
                        temp_tweet.append(word.lower())
            if len(temp_tweet) >= 2:
                id = id + 1
                data.append([id, sorted(temp_tweet, reverse=False)])

        return data

    def get_unique_words(self):
        data = self.create_database()
        unique_data = []
        for tweet in data:
            for word in tweet[1]:
                if word not in unique_data:
                    unique_data.append(word)
        return unique_data

    def get_unique_numbers(self):
        data = self.disc_data()
        unique_data = []
        for tweet in data:
            for number in tweet[1]:
                number = int(number)
                if number not in unique_data:
                    unique_data.append(number)
        return unique_data

    def disc_words(self):
        unique_words = self.get_unique_words()
        dictionary = dict()
        i = 1
        for word in unique_words:
            dictionary[f"{word}"] = i
            i += 1
        return dictionary

    def disc_data(self):
        data = self.create_database()
        dictionary = self.disc_words()

        discretize_data = []
        for tweet in data:
            new_tweet = set()
            for word in tweet[1]:
                new_tweet.add(dictionary[word])
            discretize_data.append([tweet[0], new_tweet])

        return discretize_data

    @staticmethod
    def get_twitts(user):
        consumer_key = os.environ["CONSUMER_KEY"]
        consumer_secret = os.environ["CONSUMER_SECRET"]
        # bearer_token = os.environ["BEARER_TOKEN"]

        access_token = os.environ["ACCESS_TOKEN"]
        access_token_secret = os.environ["ACCESS_TOKEN_SECRET"]

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        api = tweepy.API(auth)

        while True:
            tweets = api.user_timeline(screen_name=user, count=200, tweet_mode='extended')
            file_name = f"data/tweets-{user}.txt"
            with open(file_name, "w", encoding='utf-8') as file:
                i = 1
                for tweet in tweets:
                    tweet_text = tweet.full_text.replace("\n", " ")
                    file.write(f"{tweet_text}\n")
                    i += 1
            if len(tweets) >= 200:
                print(f"LOG::GetTwitterData:: Tweets count: {len(tweets)}")
                break
        return file_name
