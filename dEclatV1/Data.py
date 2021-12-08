import re, tweepy, os


class Data:

    def __init__(self, user):
        self.data_path = Data.get_twitts(user)  # This may be divided into two steps: 1 - get tweets, 2 - load from file
        self.database = self.create_database()
        self.unique_words = self.get_unique_words()
        self.discretized_data = self.disc_data()
        self.unique_numbers = self.get_unique_numbers()
        self.dictionary = self.disc_words()

    def create_database(self):
        with open(self.data_path, "r", encoding='utf-8') as file:
            tweets = file.readlines()
        data = list()
        id = 0
        for tweet in tweets:
            temp_tweet = list()
            tweet = tweet.strip()
            tweet = tweet.split()
            for i in range(len(tweet)):
                tweet[i] = tweet[i].strip("!#$%^&*(){}[];:\"\\,./<>?|“")
            for word in tweet:
                if re.match("^[a-zA-Z’-]+$", word):
                    if word not in temp_tweet and len(word) > 1:    # How long the single word should be
                        temp_tweet.append(word.lower())
            if len(temp_tweet) >= 2: # Accept tweets composed of at least 2 words
                id = id + 1
                data.append([id, sorted(temp_tweet, reverse=False)])

        return data

    def get_unique_words(self):
        data = self.database
        unique_data = list()
        for tweet in data:
            for word in tweet[1]:
                if word not in unique_data:
                    unique_data.append(word)
        return unique_data

    def get_unique_numbers(self):
        data = self.discretized_data
        unique_data = list()
        for tweet in data:
            for number in tweet[1]:
                number = int(number)
                if number not in unique_data:
                    unique_data.append(number)
        return unique_data

    def disc_words(self):
        unique_words = self.unique_words
        dictionary = dict()
        i = 1
        for word in unique_words:
            dictionary[f"{word}"] = i
            i += 1
        return dictionary

    def disc_data(self):
        data = self.database
        dictionary = self.disc_words()

        d_data = list()
        for tweet in data:
            new_tweet = set()
            for word in tweet[1]:
                new_tweet.add(dictionary[word])
            d_data.append([tweet[0], new_tweet])

        return d_data

    def save_db_in_standard_format(self):
        """
        Save data in standard format to test with spmf

        Data will be saved to the file, example:
        1 3 5 7
        1 2 4 5
        1 5 6
        """
        db = self.discretized_data

        with open("std_db.txt", 'w', encoding='utf-8') as file:
            for tweet in db:
                for word in tweet[1]:
                    file.write(str(word) + " ")
                file.write("\n")

    # This method need to be adjusted in a way, that we can fetch more than 200 tweets
    # We should also consider to fetch data before running algorithm and then load data
    # from text file.
    @staticmethod
    def get_twitts(user):
        # You have to export environment variables to authenticate to the API
        consumer_key = os.environ["CONSUMER_KEY"]
        consumer_secret = os.environ["CONSUMER_SECRET"]
        bearer_token = os.environ["BEARER_TOKEN"]
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
