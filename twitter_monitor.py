'''
@author: yung_messiah

'''

import json
import os
import re
import requests
import time

from tweepy import API
from tweepy import Cursor
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener


CONSUMER_KEY = os.environ["CONSUMER_KEY"]
CONSUMER_SECRET = os.environ["CONSUMER_SECRET"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
ACCESS_SECRET = os.environ["ACCESS_SECRET"]

WEBHOOK_ID = os.environ["WEBHOOK_ID"]
WEBHOOK_TOKEN = os.environ["WEBHOOK_TOKEN"]

class Client():
    def __init__(self):
        self.auth = TwitterAuthenticator().authenticate()
        
        # [cybersole, copped, coppedproxies, GhostAIO, dashe, astrobotio,
        #  aiomacbot, fogldn, kickmoji_io, Splashforcebot, oakbotnet, wopbot,
        #  dna_io, destroyerbots, dropclub_io, DiSolveIO, ycopp_com, VypernetworkIO,
        #  SoleSorcerer, EveAIO, trip_io, dotbotsio, sScoutApp, ftlcodes ]    
        self.user_ids = ['718857559403270144', '1537575638', '892949517598736384',
                        '940121522269691904', '897593602846728201', '970559950077480961',
                        '742793690838642688', '751173964119105537', '948158419957100544',
                        '910500300594786305', '950783872295362560', '907690249249185792',
                        '951498765701140480', '887790349699227650', '945724122369347585',
                        '956619435456024576', '768416589750345728', '952919889379053568',
                        '863006606124085248', '914897340280053763', '944071591201267712',
                        '936550436470800384', '852706122226176000', '941082441107853312', '796180892997873664']

class Management(object):
    
    def original_tweet(self, status):
    #     if hasattr(status, 'retweeted_status'):
    #         return False
        if status.in_reply_to_status_id != None:
            return False
        elif status.in_reply_to_screen_name != None:
            return False
        elif status.in_reply_to_user_id != None:
            return False
        else:
            return True
    
    def post_to_discord(self, author, text, profile_pic):
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "username": author,
            "avatar_url": profile_pic,
            "content": text
        }
        post_req = requests.post(f'https://discordapp.com/api/webhooks/{WEBHOOK_ID}/{WEBHOOK_TOKEN}', data=json.dumps(payload), headers=headers)
        if post_req.status_code != 200:
            print('Post failed with error', post_req.status_code, 'because', post_req.reason)
        else:
            print('Post successful!')
            
    def post_error_to_discord(self, error_code, error_message):
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "content": "An error has occurred",
            "embeds": [{
                "title": error_code,
                "description": error_message,
                "color": 0x76d6ff,
            }]
        }
        post_req = requests.post(f'https://discordapp.com/api/webhooks/{WEBHOOK_ID}/{WEBHOOK_TOKEN}', data=json.dumps(payload), headers=headers)
        if post_req.status_code != 200:
            print('Post failed with error', post_req.status_code, 'because', post_req.reason)
        else:
            print('Post successful!')


class TwitterAuthenticator():
    def authenticate(self):
        auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        return auth
    

class TwitterStream(StreamListener):
    # keywords = ['check for access', 'fta', 'ftl', 'champs',
    #            'check in', 'check-in', 'restock',
    #            'available', 'password', 'pw', 'pw:', 'password:',
    #            'copies', 'sold out', 'update']
    error_420 = 0
    error_others = 0
    management = Management()
        
    def on_status(self, status):
        if self.management.original_tweet(status):
            try:
                if status.user.id_str in client.user_ids:
                    text = ''
                    tweet_status = ''
                    if hasattr(status, 'retweeted_status'):
                        if status.user.id_str == client.user_ids[0]:
                            pass
                        else:
                            if status.retweeted_status.text.find(status.text):
                                text += status.text + f'\n[View on Twitter](https://www.twitter.com/{status.user.screen_name})\n'
                            else:
                                text += status.text + '\n\n'
                                text += status.retweeted_status.text + f'\n[View on Twitter](https://www.twitter.com/{status.user.screen_name})\n'
                    elif hasattr(status, 'extended_tweet'):
                        text += status.extended_tweet['full_text'] + f'\n[View on Twitter](https://www.twitter.com/{status.user.screen_name})\n'
                    else:
                        text += status.text + f'\n[View on Twitter](https://www.twitter.com/{status.user.screen_name})\n' 
                        
                    if re.search('check for access|fta|ftl|champs|check in|check-in|restock|available|password|pw|pw:|password:|copies|sold out|update', text, re.IGNORECASE):
                        username = ''
                        if status.user.screen_name[0] == '_':
                            username += status.user.screen_name
                        else:
                            username += status.user.screen_name
                        self.management.post_to_discord(username, text, status.user.profile_image_url_https)
            except BaseException as e:
                print("Error on_data %s" % str(e))        
        return True
    
    def on_error(self, status_code):
        print("ERROR: " + str(status_code))
        if status_code == 420:
            error_code = "Error: 420"
            sleep_time = 60 * (2 ** self.error_420)
            error_message = "Rate limit reached. Will attempt to reconnect in: " + str(sleep_time/60) + " minutes."
            self.management.post_error_to_discord(error_code, error_message)
            time.sleep(sleep_time)
            self.error_420 += 1
        else:
            error_code = "Error: " + str(status_code)
            sleep_time = 5 * (2 ** self.error_others)
            error_message = "An error has occured. Will attempt to reconnect in: " + str(sleep_time/60) + " minutes."
            self.management.post_error_to_discord(error_code, error_message)
            time.sleept(sleep_time)
            self.error_others += 1
        return True


if __name__ == "__main__":
    client = Client()
    stream_listener = TwitterStream()
    stream = Stream(auth = client.auth, listener=stream_listener)
    stream.filter(follow=client.user_ids)
