import googleapiclient.discovery
import os
from dotenv import load_dotenv

load_dotenv()

# Set up the YouTube API client
api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = os.getenv('DEVELOPER_KEY')

youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey = DEVELOPER_KEY)

def songRequest(name):
# Search for a video
    request = youtube.search().list(
        part="id,snippet",
        type='video',
        q=name,
        videoDefinition='high',
        maxResults=1,
        fields="items(id(videoId),snippet(publishedAt,channelId,channelTitle,title,description))"
    )

    response = request.execute()
    print("fetching video: " + response["items"][0]["id"]["videoId"])
    return response

