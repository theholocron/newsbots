import os
import json
import twitter
import requests
from time import time
from traders import screen_names


def handle(event, context):
    """
    Lambda handler
    """

    periodicity = int(os.getenv('BOT_PERIODICITY', 15))
    offset = int(os.getenv('BOT_OFFSET', 5))
    retweet_threshold = int(os.getenv('TWITTER_RETWEET_THRESHOLD', 10))

    twitter_client = twitter.Api(
                         consumer_key=os.getenv('TWITTER_CONSUMERKEY'),
                         consumer_secret=os.getenv('TWITTER_CONSUMERSECRET'),
                         access_token_key=os.getenv('TWITTER_APP_ACCESSTOKEN'),
                         access_token_secret=os.getenv('TWITTER_APP_ACCESSSECRET')
                         )
    slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    slack_channel = os.getenv('SLACK_CHANNEL')

    for screen_name in screen_names:
        current_time = time()
        stream = twitter_client.GetUserTimeline(screen_name=screen_name,
                                                include_rts=True,
                                                exclude_replies=True)

        for msg in stream:
            msg_time = msg.created_at_in_seconds

            if current_time - msg_time > (periodicity  + offset) * 60: # periodicity param is in minutes
                break

            if current_time - msg_time < offset * 60: # periodicity param is in minutes
                break

            if msg.retweet_count < retweet_threshold:
                continue

            twitter_status_url = 'https://twitter.com/{handle}/status/{status_id}'
            slack_payload = {'unfurl_links': True, 'channel': slack_channel}

            msg_text = msg.text
            if 'RT @' in msg_text:
                orig_user = msg.text.split(':')[0].replace('RT @', '')
                twitter_status_url = twitter_status_url.format(handle=orig_user, status_id=msg.id_str)
                slack_payload['text'] = '*ReTweeted by {t}*.\n{url}'.format(t=screen_name, url=twitter_status_url)
            else:
                twitter_status_url = twitter_status_url.format(handle=screen_name, status_id=msg.id_str)
                slack_payload['text'] = '*Tweeted by {t}*.\n{url}'.format(t=screen_name, url=twitter_status_url)

            requests.post(slack_webhook_url, json=slack_payload)
    return event
