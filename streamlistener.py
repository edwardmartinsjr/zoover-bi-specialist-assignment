import tweepy
import pandas as pd
from dateutil import parser
import time
import store
import uuid
import json
import log
import store

# Tweepy class to access Twitter API
class Streamlistener(tweepy.StreamListener):
    
    def on_connect(self):
        # Get streamming for 60 seconds and exit
        self.start_time = time.time()
        self.limit = 60

        log.logger.info('You are connected to the Twitter API')

    def on_error(self, status):
        if status != 200:
            log.logger.error('error found: {}'.format(status) )
            # Returning false disconnects the stream
            return False

    # Reads in tweet data as Json and extracts the data we want.
    def on_data(self,data):	
        if (time.time() - self.start_time) < self.limit:
            try:
                raw_data = json.loads(data)

                if 'text' in raw_data:
                    username = raw_data['user']['screen_name']
                    created_at = parser.parse(raw_data['created_at'])
                    tweet = raw_data['text']
                    retweets = raw_data['retweet_count']
                    location = raw_data['user']['location']
                    
                    if raw_data['place'] is not None:
                        place = raw_data['place']['country']
                        log.logger.info(place)
                    else:
                        place = None
                        
                    log.logger.info('\n USERNAME: %s \n TWEET: %s \n RETWEET: %d \n LOCATION: %s',username, tweet, retweets, location)
                    log.logger.info(' Tweet colleted at: {} \n'.format(str(created_at)))
                    
                    # Prepares the data in a structured format
                    data = []
                    data.append({
                        'key':uuid.uuid4(),
                        'username':username,
                        'tweet':tweet,
                        'retweets':retweets,
                        'location':location,
                        'created_at':str(created_at)})
                    
                    # Transformation
                    # converting created_at to datetime
                    columns=['key', 'username', 'tweet', 'retweets', 'location', 'created_at']
                    df = pd.DataFrame(data, columns = columns)
                    df['created_at'] = pd.to_datetime(df['created_at'])
                    df['created_at'] = df['created_at'].dt.strftime('%Y-%m-%d %H:%M:S')
                    
                    # converting number of retweets to numeric
                    df['retweets'] = pd.to_numeric(df['retweets'])
                    
                    # Stores the data in a Database
                    store.save_data(df)
            
            except BaseException as e:
                log.logger.error(e)
        else:
            return False