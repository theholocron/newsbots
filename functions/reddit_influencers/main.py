import os
import praw
import json
import pytz
import requests
from datetime import timedelta, datetime
from subreddits import subreddit_handles


posted_urls = list()

def is_quality_post(thread):
    """
    checks to ensure that this reddit thread is a quality post
    """
    current_time = datetime.now(pytz.utc)
    msg_time = datetime.fromtimestamp(thread.created_utc, tz=pytz.utc)
    periodicity = int(os.getenv('BOT_PERIODICITY', 15))
    offset = int(os.getenv('BOT_OFFSET', 5))

    is_in_time_window = current_time - msg_time < timedelta(minutes=(periodicity+offset)) # periodicity param is in minutes
    is_after_time_offset = current_time - msg_time > timedelta(minutes=offset) # periodicity param is in minutes
    has_enuf_upvotes = thread.ups > int(os.getenv('UPVOTE_THRESHOLD', 5))
    return has_enuf_upvotes and is_in_time_window and is_after_time_offset


def is_being_reposted(thread):
    """
    checks if the current thread is a url which has been previously posted on the current iteration
    """
    url = thread.url.strip()
    is_being_reposted = url in posted_urls
    posted_urls.append(url)
    return is_being_reposted


def handle(event, context):
    """
    Lambda handler
    """
    reddit = praw.Reddit(client_id=os.getenv('CLIENT_ID'),
                         client_secret=os.getenv('CLIENT_SECRET'),
                         username=os.getenv('USERNAME'),
                         password=os.getenv('PASSWORD'),
                         user_agent=os.getenv('USER_AGENT'))

    for subreddit_handle in subreddit_handles:
        subreddit = reddit.subreddit(str(subreddit_handle))
        threads = subreddit.new(limit=100)

        for thread in threads:
            if not is_quality_post(thread):
                continue

            if is_being_reposted(thread):
                continue

            url = thread.url
            slack_payload = {'unfurl_links': True, 'channel': os.getenv('SLACK_CHANNEL')}
            slack_payload['text'] = '*Posted on r/{subreddit}*.\n {url}'.format(subreddit=subreddit_handle, url=url)
            requests.post(os.getenv('SLACK_WEBHOOK_URL'), json=slack_payload)
    return event
