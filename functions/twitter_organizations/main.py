import os
import pytz
import twitter
import requests
from time import time
from dateutil import parser
from datetime import datetime, timedelta
from organizations import screen_names


posted_urls = list()


def is_quality_post(msg):
    """
    checks to ensure that this reddit thread is a quality post
    """
    current_time = datetime.now(pytz.utc)
    msg_time = parser.parse(msg.created_at)
    periodicity = int(os.getenv('BOT_PERIODICITY', 15))
    offset = int(os.getenv('BOT_OFFSET', 5))

    is_in_time_window = current_time - msg_time < timedelta(minutes=(periodicity+offset)) # periodicity param is in minutes
    is_after_time_offset = current_time - msg_time > timedelta(minutes=offset) # periodicity param is in minutes
    has_enuf_upvotes = msg.retweet_count > int(os.getenv('TWITTER_RETWEET_THRESHOLD', 10))
    return has_enuf_upvotes and is_in_time_window and is_after_time_offset


def is_being_reposted(url):
    """
    checks if the current thread is a url which has been previously posted on the current iteration
    """
    url = url.strip()
    is_being_reposted = url in posted_urls
    posted_urls.append(url)
    return is_being_reposted


def handle(event, context):
    """
    Lambda handler
    """
    twitter_client = twitter.Api(consumer_key=os.getenv('TWITTER_CONSUMERKEY'),
                                 consumer_secret=os.getenv('TWITTER_CONSUMERSECRET'),
                                 access_token_key=os.getenv('TWITTER_APP_ACCESSTOKEN'),
                                 access_token_secret=os.getenv('TWITTER_APP_ACCESSSECRET'))

    for screen_name in screen_names:
        current_time = time()
        stream = twitter_client.GetUserTimeline(screen_name=screen_name,
                                                include_rts=True,
                                                exclude_replies=True)

        for msg in stream:
            if not is_quality_post(msg):
                continue

            twitter_status_url = 'https://twitter.com/{handle}/status/{status_id}'
            slack_payload = {'unfurl_links': True, 'channel': os.getenv('SLACK_CHANNEL')}

            msg_text = msg.text
            if 'RT @' in msg_text:
                orig_user = msg.text.split(':')[0].replace('RT @', '')
                twitter_status_url = twitter_status_url.format(handle=orig_user, status_id=msg.id_str)
                slack_payload['text'] = '*ReTweeted by {t}*.\n{url}'.format(t=screen_name, url=twitter_status_url)
            else:
                twitter_status_url = twitter_status_url.format(handle=screen_name, status_id=msg.id_str)
                slack_payload['text'] = '*Tweeted by {t}*.\n{url}'.format(t=screen_name, url=twitter_status_url)

            if is_being_reposted(twitter_status_url):
                continue

            requests.post(os.getenv('SLACK_WEBHOOK_URL'), json=slack_payload)
    return event
