import json
import os
import pytz
import requests
from datetime import datetime, timedelta
from dateutil import parser
from time import time
from youtubeapi import YoutubeAPI
from youtube_channels import youtube_channel_ids


def is_quality_post(video, client):
    """
    checks to ensure that this youtube video is within required time window
    """
    current_time = datetime.now(pytz.utc)
    upload_time = parser.parse(client.get_video_info(video['id']['videoId'])['snippet']['publishedAt'])

    periodicity = int(os.getenv('BOT_PERIODICITY', 15))
    offset = int(os.getenv('BOT_OFFSET', 5))

    is_in_time_window = current_time - upload_time < timedelta(minutes=(periodicity+offset)) # periodicity param is in minutes
    is_after_time_offset = current_time - upload_time > timedelta(minutes=offset) # periodicity param is in minutes
    return is_in_time_window and is_after_time_offset


def handle(event, context):
    client = YoutubeAPI({'key': os.getenv('YOUTUBE_KEY')})
    VIDEOS_TO_QUERY_LIMIT = os.getenv('VIDEOS_TO_QUERY_LIMIT')

    for channel_id in youtube_channel_ids:
        videos_list = client.search_channel_videos('', channel_id, int(VIDEOS_TO_QUERY_LIMIT))

        for video in videos_list:

            if not is_quality_post(video, client):
                continue

            url = YOUTUBE_BASE_URL + video['id']['videoId']
            slack_payload = {'unfurl_links': True, 'channel': os.getenv('SLACK_CHANNEL')}
            slack_payload['text'] = '*Posted on Youtube*.\n {url}'.format(url=url)
            requests.post(os.getenv('SLACK_WEBHOOK_URL'), json=slack_payload)
    return event
