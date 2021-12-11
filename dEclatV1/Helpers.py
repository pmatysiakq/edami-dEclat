import tweepy, os, FI


def tweepy_auth():
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


def get_200_tweets_by_user(user_name):

    api = tweepy_auth()

    while True:
        tweets = api.user_timeline(screen_name=user_name, count=200, tweet_mode='extended')
        file_name = f"data/tweets-{user_name}.txt"
        with open(file_name, "w", encoding='utf-8') as file:
            for tweet in tweets:
                tweet_text = tweet.full_text.replace("\n", " ")
                file.write(f"{tweet_text}\n")

        if len(tweets) >= 200:
            break
    print(f"{len(tweets)} Tweets saved to file: {file_name}")


def search_tweets_by_tags(tag_list, db_name="tweets"):

    api = tweepy_auth()

    database = []

    for tag in tag_list:
        tweets = api.search_tweets(q=tag, tweet_mode='extended', lang='en', result_type="mixed", count=100)
        for tweet in tweets:
            text = tweet.full_text.replace("\n", " ")
            if text not in database:
                database.append(text)

    file_name=f"data/db-{db_name}.txt"
    with open(file_name, 'w', encoding='utf-8') as file:
        for tweet in database:
            file.write(f"{tweet}\n")
    print(f"{len(database)} Tweets saved to file: {file_name}")


def calc_difflists(set_A: FI, set_B: FI):
    return set_B.difflist.difference(set_A.difflist)
