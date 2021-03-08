import youtube_dl
from youtube_search import YoutubeSearch
import os

class YtDownloader:
    opts = {
            'quiet' : True,
            'format': 'bestaudio/best',
            'outtmpl': f'YTCache/%(id)s.mp3',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }],
        }
    
    def __init__(self):
        pass
    
    #URL Finder
    def find_yt_url(self, args):
        if 'youtube.com/' not in args and 'youtu.be/' not in args:
            search_result = YoutubeSearch(args,max_results=1).to_dict() #adds delay but it's safer this way
            args = 'https://youtu.be/'+(search_result[0].get("id", None))   #better strategy in progress... but I'm not smart.
        args = args.replace('app=desktop&','')  #URL pattern santitization
        args = args.replace('m.youtube','youtube')
        args = args.split('&', 1)[0]            #Know other URL patterns? Tell me on Discord @_Brad#7436!
        return args
    
    
    #MP3 Downloader, downloads from specified url
    def download(self, args):
        args = self.find_yt_url(args)
        with youtube_dl.YoutubeDL(self.opts) as ydl:
            vid_info = ydl.extract_info(args, download=False)
            if vid_info.get('duration',None) > 3660:
                return ["Too long", vid_info.get("title",None)]
            if not os.path.exists(f'YTCache/{vid_info.get("id",None)}.mp3'):
                ydl.extract_info(args, download=True) #Extract Info must be used here, otherwise the download fails
                return [vid_info.get("id",None),vid_info.get("title",None)];
            else:
                return [vid_info.get("id",None),vid_info.get("title",None)];
            
        
    #Return song name of song specified with args
    def get_song_name(self, args):
        args = self.find_yt_url(args)
        with youtube_dl.YoutubeDL(self.opts) as ydl:
            info = ydl.extract_info(args,download=False)
            return info.get('title',None)
        
        
    #Return the song id from specified args
    def get_song_id(self, args):
        args = self.find_yt_url(args)
        with youtube_dl.YoutubeDL(self.opts) as ydl:
            info = ydl.extract_info(args,download=False)
            return info.get('id',None)
    
        
        
        
        
        
        
        
        
        
        
