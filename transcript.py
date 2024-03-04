import requests
import getopt
import sys
from dotenv import load_dotenv
load_dotenv()
import os

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter


# YT Data Api v3
GAPI_Key = os.getenv('GOOGLE_DATA_API_KEY') 

youtube=build(
    'youtube',
    'v3',
    developerKey=GAPI_Key
    )

def YT_ChannelID_From_Name(name):

    request = youtube.search().list(
        part="id,snippet",
        type='channel',
        q=name,
        maxResults=1
    )

    response = request.execute()


    ChannelID = response["items"][0]["id"]["channelId"]
    return(ChannelID)

def YT_Videos_from_channelID(id, maxResults):
    request = youtube.search().list(
        part="id,snippet",
        type='video',
        order='date',
        channelId=id,
        maxResults=maxResults
    )
    response = request.execute()
    #print(response)
    res = []

    for item in response["items"]:
        #print(item["id"]["videoId"])
        res.append(item["id"]["videoId"])
    return(res)

def Get_Transcript_from_videoId(video_id, language):
    print(language)
    ts = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
    return(ts)

def Is_Short(video_id):
    r = requests.get("https://www.youtube.com/shorts/"+video_id)
    if (len(r.history) > 0):
        return(False)
    else:
        return(True)


#main function
def main():
    print("Get Transcripts From YT Channel")
    #lets fetch all the arguments from sys.argv except the script name
    argv = sys.argv[1:]

    channel=None
    maxResults='10'
    language='en'

    try:
        opts,argv = getopt.getopt(argv, "c:m:l:", ["channel=","maxResults=","language="])
        print("Argomenti: ")
        print(opts)

        for o,v in opts:
            if o=='-c' or o=='--channel':  
                channel = v
            elif o in ['-m','--maxResults']:
                maxResults = v
            elif o in ['-l','--language']:
                language = v

    except Exception:
        traceback.print_exc()
        print('Error: pass the arguments like -c <channelName> -m <maxResults> -l <language>')
        print('MaxResults example: 10, 15, 30, etc... Default: 10')
        print('Language example: it, en, de, etc... Default: en')

    if channel!=None:
        print("Channel: " + channel)
        print("Max Results: " + maxResults)

        chId=YT_ChannelID_From_Name(channel)

        videoList = YT_Videos_from_channelID(chId, maxResults)
        print("Video List:")
        print(videoList)

        for video in videoList:
            if (Is_Short(video) == False):
                transcript = Get_Transcript_from_videoId(video, language)
                formatter = TextFormatter()
                txt_formatted = formatter.format_transcript(transcript)
                print(txt_formatted)
            else:
                print("Short Skipped")
                print(video)

if __name__ == "__main__":
    main()