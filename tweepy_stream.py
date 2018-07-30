
# coding: utf-8

# In[1]:


from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
import sqlite3
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from unidecode import unidecode
import time
import googlemaps


# In[2]:


analyzer = SentimentIntensityAnalyzer()


# In[3]:


# Twitter consumer key, consumer secret, access token, access secret
ckey = "sMg1LorjGGb65gQj5pWttNwjf"
csecret = "GrYLOEZBM6Xd7VSZKg4jOj8TDznHeL6rrBdnj82lcstHglGNzT"
atoken = "67005096-78hw0Z5xlrPOR2eqxFuEjD2Epo6gaCx3FTZCLLLjO"
asecret = "pbTscQwId5E1LuvKK7d5JALzkANV5cdrYjH0lZYfPABOB"


# In[4]:


conn = sqlite3.connect('twitter.db')
c = conn.cursor()


# In[5]:


def create_table():
    try:
        c.execute(
            "CREATE TABLE IF NOT EXISTS sentiment(unix REAL, tweet TEXT, sentiment REAL,location TEXT ,lat FLOAT, lng FLOAT)")
        c.execute("CREATE INDEX fast_unix ON sentiment(unix)")
        c.execute("CREATE INDEX fast_tweet ON sentiment(tweet)")
        c.execute("CREATE INDEX fast_sentiment ON sentiment(sentiment)")
        conn.commit()
    except Exception as e:
        print(str(e))


create_table()


# In[6]:


gmaps_api_key = "AIzaSyDO54ayyPFCLklgiuwXu_LMaLVL2hYtS3o"


# In[7]:


def return_lat_lon(location_name):
    try:
        if location_name is not None:
            gmaps = googlemaps.Client(key=gmaps_api_key)
            geocode_result = gmaps.geocode(location_name)
            lat = geocode_result[0]['geometry']['location']['lat']
            lng = geocode_result[0]['geometry']['location']['lng']
            return lat, lng
        else:
            return None
    except Exception as e:
        print(e)
        pass


# In[13]:


class listener(StreamListener):
    def on_data(self, data):
        try:
            lat, lng = None, None
            data = json.loads(data)
            tweet = unidecode(data['text'])
            time_ms = data['timestamp_ms']
            vs = analyzer.polarity_scores(tweet)
            sentiment = vs['compound']
            location = data['user']['location']
            try:
                lat, lng = return_lat_lon(location)
            except Exception as e:
                pass
            print(time_ms, tweet, sentiment, location, lat, lng)
            c.execute("INSERT INTO sentiment(unix, tweet, sentiment, location, lat, lng) VALUES(?, ?, ?, ?, ?, ?)",
                      (time_ms, tweet, sentiment, location, lat, lng))
            conn.commit()

        except KeyError as e:
            print(str(e))
        return(True)

    def on_error(self, status):
        print(status)


# In[ ]:


while True:
    try:
        auth = OAuthHandler(ckey, csecret)
        auth.set_access_token(atoken, asecret)
        twitterStream = Stream(auth, listener())
        twitterStream.filter(track=["a, e, i, o, u"])
    except Exception as e:
        print(str(e))
        # time.sleep(5)
