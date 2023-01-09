import googleapiclient.discovery
import os
from dotenv import load_dotenv

load_dotenv()

# Set up the YouTube API client
api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = os.getenv('DEVELOPER_KEY')

youtube = googleapiclient.discovery.build(api_service_name, api_version, DEVELOPER_KEY)

# Search for a video
request = youtube.search().list(
    part="id,snippet",
    type='video',
    q='',
    videoDefinition='high',
    maxResults=1,
    fields="items(id(videoId),snippet(publishedAt,channelId,channelTitle,title,description))"
)
response = request.execute()

# Print the response
print(response)