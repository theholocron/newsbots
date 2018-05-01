import json
import os
import praw
import requests
from subreddits import threads


def handle(event, context):
    """
    Lambda handler
    """

    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    NUMBER_OF_SUBMISSIONS = int(os.getenv('NUMBER_OF_SUBMISSIONS'))
    PASSWORD = os.getenv('PASSWORD')
    SLACK_WEBHOOK_URL= os.getenv('SLACK_WEBHOOK_URL')
    SLACK_CHANNEL = os.getenv('SLACK_CHANNEL')
    USER_AGENT = os.getenv('USER_AGENT')
    USERNAME = os.getenv('USERNAME')

    reddit = praw.Reddit(client_id=CLIENT_ID,client_secret=CLIENT_SECRET,username=USERNAME,password=PASSWORD,user_agent=USER_AGENT)
    for thread in threads:
        subreddit = reddit.subreddit(str(subreddit_name))
        submission = subreddit.hot(limit=NUMBER_OF_SUBMISSIONS)
        for sub in submission:
            url = sub.url
            slack_payload = {'unfurl_links': True, 'channel': SLACK_CHANNEL}
            slack_payload['text'] = url
            requests.post(SLACK_WEBHOOK_URL, json=slack_payload)
    return event
