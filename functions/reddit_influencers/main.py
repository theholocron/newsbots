import json
import os
import praw
import requests
from list_of_subreddits import SUBREDDITS


def set_environment_variables():
		
	with open('config.json','rb') as f:
		environment_variables = json.loads(f.read())
		for key,value in environment_variables.iteritems():
			os.environ[key]=str(value)

def handle():

	set_environment_variables()

	CLIENT_ID = os.getenv('CLIENT_ID')
	CLIENT_SECRET = os.getenv('CLIENT_SECRET')
	NUMBER_OF_SUBMISSIONS = int(os.getenv('NUMBER_OF_SUBMISSIONS'))
	PASSWORD = os.getenv('PASSWORD')
	SLACK_WEBHOOK_URL= os.getenv('SLACK_WEBHOOK_URL')
	SLACK_CHANNEL = os.getenv('SLACK_CHANNEL')
	USER_AGENT = os.getenv('USER_AGENT')
	USERNAME = os.getenv('USERNAME')

	reddit = praw.Reddit(client_id=CLIENT_ID,client_secret=CLIENT_SECRET,username=USERNAME,password=PASSWORD,user_agent=USER_AGENT)
	for subreddit_name in SUBREDDITS:
		subreddit = reddit.subreddit(str(subreddit_name))
		submission = subreddit.hot(limit=NUMBER_OF_SUBMISSIONS)
		for sub in submission:
			url = sub.url 
			slack_payload = {'unfurl_links': True, 'channel': SLACK_CHANNEL}
			slack_payload['text'] = url
			requests.post(SLACK_WEBHOOK_URL, json=slack_payload)

handle()


