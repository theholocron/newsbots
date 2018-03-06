import json
import os
import pytz
import requests
from datetime import datetime, timedelta
from dateutil import parser
from time import time
from youtubeapi import YoutubeAPI 
from youtube_channels import LIST_OF_CHANNEL_IDS

def set_environment_variables():
	
	with open('config.json','rb') as f:
		environment_variables = json.loads(f.read())
		for key,value in environment_variables.iteritems():
			os.environ[key]=str(value)

	
def handle():
	
	set_environment_variables()
	
	YOUTUBE_KEY = os.getenv('YOUTUBE_KEY')
	NUMBER_OF_VIDEOS = int(os.getenv('NUMBER_OF_VIDEOS'))
	SLACK_CHANNEL_NAME = os.getenv('SLACK_CHANNEL_NAME')
	SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
	VIDEO_UPLOAD_TIME_CHECK = int(os.getenv('VIDEO_UPLOAD_TIME_CHECK'))
	YOUTUBE_STANDARD_URL = os.getenv('YOUTUBE_STANDARD_URL')
	client = YoutubeAPI({'key':YOUTUBE_KEY})    

	for channel_id in LIST_OF_CHANNEL_IDS:																					
		
		videos_list = client.search_channel_videos('', channel_id, NUMBER_OF_VIDEOS)

		for video in videos_list:

			upload_time = parser.parse(client.get_video_info(video['id']['videoId'])['snippet']['publishedAt'])
			current_time = datetime.now(pytz.utc)
		
			if (current_time - upload_time) > timedelta(seconds=VIDEO_UPLOAD_TIME_CHECK):
				continue

			url = YOUTUBE_STANDARD_URL + video['id']['videoId']
			slack_payload = {'unfurl_links': True, 'channel': SLACK_CHANNEL_NAME}
			slack_payload['text'] = url
			requests.post(SLACK_WEBHOOK_URL, json = slack_payload)

handle()



