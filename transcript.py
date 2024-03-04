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
from youtube_transcript_api.formatters import JSONFormatter


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

def YT_Videos_from_playlistId(playlistId, maxResults):
    request = youtube.playlistItems().list(
        part="id,snippet",
        maxResults=maxResults,
        playlistId=playlistId
    )

    response = request.execute()
    res = []

    for item in response["items"]:
        res.append(item['snippet']['resourceId']['videoId'])
    
    return(res)

def Get_Transcript_from_videoId(video_id, language):
    ts = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
    return(ts)

def Is_Short(video_id):
    r = requests.get("https://www.youtube.com/shorts/"+video_id)
    if (len(r.history) > 0):
        return(False)
    else:
        return(True)


def process_video(video, skip_shorts, language, formatter, file_name):
    if skip_shorts and Is_Short(video):
        print("Short Skipped")
        print(video)
        return

    transcript = Get_Transcript_from_videoId(video, language)

    if formatter == 'text':
        formatter = TextFormatter()
    else:
        formatter =JSONFormatter()

    txt_formatted = formatter.format_transcript(transcript)

    with open(file_name, 'a', encoding='utf-8') as file:
        file.write(txt_formatted)


#main function
def main():
    print("Get Transcripts From YT Channel (or Playlist)")
    #lets fetch all the arguments from sys.argv except the script name
    argv = sys.argv[1:]

    channel=None
    maxResults='10'
    language='en'
    isPlaylist=False
    videoList=[]
    skipShorts=True
    formatter='json'
    fileName='out.json'

    try:
        opts,argv = getopt.getopt(argv, "c:m:l:p:s:f:o:", ["channel=","maxResults=","language=","isPlaylist=","skipShorts=","formatter=","fileName="])
        print("Args: ")
        print(opts)

        for o,v in opts:
            if o=='-c' or o=='--channel':  
                channel = v
            elif o in ['-m','--maxResults']:
                maxResults = v
            elif o in ['-l','--language']:
                language = v
            elif o in ['-p','--isPlaylist']:
                isPlaylist = bool(v)
            elif o in ['-s','--skipShorts']:
                skipShorts = bool(v)
            elif o in ['-f','--formatter']:
                formatter = v
            elif o in ['-o','--fileName']:
                fileName = v

    except Exception:
        traceback.print_exc()
        print('Error: pass the arguments like -c <channelNameprint(isPlaylist)> -m <maxResults> -l <language> -p <isPlaylist> -f <fileName>')
        print('MaxResults example: 10, 15, 30, etc... Default: 10')
        print('Language example: it, en, de, etc... Default: en')
        print('isPlaylist example: true|false Default: False')
        print('skipShorts example: true|false Default: True')
        print('formatter example: json|text')
        print('fileName example: output.json')
    
    if channel!=None:
        #print(isPlaylist)
        if isPlaylist==True:
            videoList = YT_Videos_from_playlistId(channel, maxResults)
        elif isPlaylist==False:
            print("Channel: " + channel)
            print("Max Results: " + maxResults)

            chId=YT_ChannelID_From_Name(channel)

            videoList = YT_Videos_from_channelID(chId, maxResults)

        if(len(videoList) > 0):
            print("Video List:")
            print(videoList)

            for video in videoList:
                process_video(video, skipShorts, language, formatter, fileName)

if __name__ == "__main__":
    main()