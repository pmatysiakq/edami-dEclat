import tweepy, os, FI



def get_200_tweets(user):
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


def calc_difflists(set_A: FI, set_B: FI):
    return set_B.difflist.difference(set_A.difflist)

