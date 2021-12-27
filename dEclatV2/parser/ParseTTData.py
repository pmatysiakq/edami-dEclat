import re, json, tweepy, os

class Parser:
    def __init__(self, input_file, output_file):
        self.data_path = input_file
        self.database = self.create_transactions_of_words()
        self.unique_words = self.get_unique_words()
        self.discretized_data = self.disc_data()
        self.dictionary = self.disc_words()
        self.save_db_in_standard_format(output_file)


    def create_transactions_of_words(self):
        """
        Use `data_path` parameter to parse Tweets into transactions.

        `data_path` file should be a *.txt file where 1 line is
        equal to single tweet.
        :return: List of transactions [[tid1, T1],[tid2, T2],...,[tidN, TN]]
        """
        with open(self.data_path, "r", encoding='utf-8') as file:
            tweets = file.readlines()
        data = list()
        id = 0
        for tweet in tweets:
            temp_tweet = list()
            tweet = tweet.strip()
            tweet = tweet.split()
            for i in range(len(tweet)):
                tweet[i] = tweet[i].strip("!#$%^&*(){}[];:\"\\,./<>?|")
            for word in tweet:
                if re.match("^[a-zA-Z]|$[a-zA-Z]", word):
                    # How long the single word should be - we don't find len(word) =< 3 interesting
                    if word not in temp_tweet and len(word) > 3:
                        if "http" not in word:
                            temp_tweet.append(word.lower())
            # Accept tweets composed of at least 2 words
            if len(temp_tweet) >= 2:
                id = id + 1
                data.append([id, sorted(temp_tweet, reverse=False)])

        return data


    def get_unique_words(self):
        """
        Search unique words in parsed database.
        :return: List of unique words, [word1, word2,..., wordN]
        """
        data = self.database
        unique_data = list()
        for tweet in data:
            for word in tweet[1]:
                if word not in unique_data:
                    unique_data.append(word)
        print(unique_data)
        return unique_data

    def disc_words(self):
        """
        Translate words into integers.

        Creates dictionary where the `key` is a word and
        value is corresponding integer value.
        :return: Dictionary {word1: int1, word2: int2,..., wordN, intN}
        """
        unique_words = self.unique_words
        dictionary = dict()
        i = 1
        for word in unique_words:
            dictionary[f"{word}"] = i
            i += 1
        print(dictionary)
        return dictionary

    def create_dict(self):
        """
        Translate words into integers.

        Creates dictionary where the `key` is a word and
        value is corresponding integer value.
        :return: Dictionary {word1: int1, word2: int2,..., wordN, intN}
        """
        unique_words = self.unique_words
        dictionary = dict()
        i = 1
        for word in unique_words:
            dictionary[f"{i}"] = word
            i += 1
        print(dictionary)
        return dictionary

    def disc_data(self):
        """
        Creates database where words are replaced by integers.

        Takes initial database and discritizizes data.
        :return: [[tid1, {items as ints}], [tid2, {items as ints}],..., [tidN, items as ints]]
        """
        data = self.database
        dictionary = self.disc_words()

        d_data = list()
        for tweet in data:
            new_tweet = set()
            for word in tweet[1]:
                new_tweet.add(dictionary[word])
            d_data.append([tweet[0], new_tweet])
        print(d_data)
        return d_data

    def save_db_in_standard_format(self, file_name):
        """
        Save data in standard format to test with spmf

        Data will be saved to the file. Then dictionary will be given
        which is necessary to translate integer values to words. Example:
        1 3 5 7
        1 2 4 5
        1 5 6
        """
        db = self.discretized_data

        with open(file_name, 'w', encoding='utf-8') as file:
            for tweet in db:
                for word in tweet[1]:
                    file.write(str(word) + " ")
                file.write("\n")
            file.write(" ==== DICTIONARY ==== \n")
            dictionary = json.dumps(self.create_dict())
            file.write(dictionary)

    @staticmethod
    def parse_trump_dataset():
        """
        Static method which is used to parse trump.csv into raw tweets.

        This dataset is downloaded from Kaggle. Before translation into transactional
        database, we need to fetch only tweet's text from this dataset.
        :return: Text file with raw tweets fetch from trump.csv file.
        """
        with open("kaggle_csv/trump.csv", "r", encoding="utf-8") as trumpy:
            for line in trumpy.readlines():
                with open("tweets_raw/trump-tweets.txt", "a", encoding='utf-8') as file:
                    try:
                        file.write(line.split(",")[4].strip("\n"))
                        file.write("\n")
                    except Exception as e:
                        print(f"Couldn't save line. Exception: {e}")
    @staticmethod
    def tweepy_auth():
        """
        Method used to authenticate into twitter Developer API

        This method is using credentials which are exported as environment
        variables. Export your own credentials to use this method.
        :return: Returns tweepy authentication object.
        """
        # You have to export environment variables to authenticate to the API
        consumer_key = os.environ["CONSUMER_KEY"]
        consumer_secret = os.environ["CONSUMER_SECRET"]
        bearer_token = os.environ["BEARER_TOKEN"]
        access_token = os.environ["ACCESS_TOKEN"]
        access_token_secret = os.environ["ACCESS_TOKEN_SECRET"]

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)

        return api

    @staticmethod
    def get_200_tweets_by_user(user_name):
        """
        Used to fetch 200 latest tweets of Twitter user `user_name`
        :param user_name: The name of Twitter user
        :return: Text file with 200 raw tweets fetched directly from Twitter.
        """
        api = Parser.tweepy_auth()

        while True:
            tweets = api.user_timeline(screen_name=user_name, count=200, tweet_mode='extended')
            file_name = f"tweets_raw/tweets-{user_name}.txt"
            with open(file_name, "w", encoding='utf-8') as file:
                for tweet in tweets:
                    tweet_text = tweet.full_text.replace("\n", " ")
                    file.write(f"{tweet_text}\n")

            if len(tweets) >= 200:
                break
        print(f"{len(tweets)} Tweets saved to file: {file_name}")

    @staticmethod
    def search_tweets_by_tags(tag_list, db_name="tweets"):
        """
        Used to fetch more than 200 tweets.

        To fetch list of tags need to be provided and based on that
        tags, we will query live twitter data and found tweets to text file.
        :param tag_list: List of words based on which we will query Twitter
        :param db_name: Name of the file, where tweets will be saved
        :return: Text file with raw tweets fetched directly from Twitter.
        """

        api = Parser.tweepy_auth()

        database = []

        for tag in tag_list:
            tweets = api.search_tweets(q=tag, tweet_mode='extended', lang='en', result_type="mixed", count=100)
            for tweet in tweets:
                text = tweet.full_text.replace("\n", " ")
                if text not in database:
                    database.append(text)

        file_name = f"tweets_raw/db-{db_name}.txt"
        with open(file_name, 'w', encoding='utf-8') as file:
            for tweet in database:
                file.write(f"{tweet}\n")
        print(f"{len(database)} Tweets saved to file: {file_name}")


if __name__ == "__main__":
    pass
    # STEP 1
    # # Use tweepy to fetch 200 newest "elonmusk" tweets
    # Parser.get_200_tweets_by_user("elonmusk")

    # STEP 2
    # # Use tweepy to fetch some tweeter data
    # words = ["covid", "vaccine", "covid-19", "quarantine", "restrictions", "phizer", "moderna", "astrazeneca",
    #          "fake covid", "wuhan", "coronavirus", "health", "pandemic", "virus", "corona", "stayhome", "lockdown",
    #          "unvaccinated", "omicron", "sars-cov-2", "death", "antibodies", "plandemic"]
    #
    # Parser.search_tweets_by_tags(words, "covid")

    # STEP 3
    # # Parse trump tweets downloaded from Kaggle
    # Parser.parse_trump_dataset()

    # STEP 4
    # From raw tweets create databases which will be provided as input for declat algorithm
    # input_path = r"tweets_raw/db-covid.txt"
    # output_filename = "../input_data/covid-transactions.txt"
    # Parser(input_file=input_path, output_file=output_filename)
    #
    # input_path = r"tweets_raw/tweets-elonmusk.txt"
    # output_filename = "../input_data/elonmusk-transactions.txt"
    # Parser(input_file=input_path, output_file=output_filename)
    #
    # input_path = r"tweets_raw/trump-tweets.txt"
    # output_filename = "../input_data/trump-transactions.txt"
    # Parser(input_file=input_path, output_file=output_filename)