import youtube_dl
from youtube_search import YoutubeSearch
import os

#Easy container class for youtube searching and downloading

class YtDownloader:
    opts = None
    max_duration = 0;
    cache_folder = ""
    
    def __init__(self,max_dur=3660,folder="YTCache"):
        self.cache_folder = folder
        self.opts = {
                'quiet' : True,
                'format': 'bestaudio/best',
                'outtmpl': f'{self.cache_folder}/%(id)s.mp3',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '128',
                }],
            }
        self.max_duration = max_dur
        
    
    #URL Finder
    #Returns a youtube url
    #Searches if not already url,
    #Passes url through if already url
    def find_yt_url(self, args):
        if 'youtube.com/' not in args and 'youtu.be/' not in args:
            search_result = YoutubeSearch(args,max_results=1).to_dict()
            args = 'https://youtu.be/'+(search_result[0].get("id", None))
        args = args.replace('app=desktop&','')  #URL pattern santitization
        args = args.replace('m.youtube','youtube')
        args = args.split('&', 1)[0]            #Know other URL patterns? Tell me on Discord @_Brad#7436!
        return args
    
    
    #MP3 Downloader, downloads from specified url
    #Returns 2 element array with the id and title if under max_duration, regardless of whether or not the video was redownloaded
    def download(self, args):
        args = self.find_yt_url(args)
        with youtube_dl.YoutubeDL(self.opts) as ydl:
            vid_info = ydl.extract_info(args, download=False)
            if vid_info.get('duration',None) > self.max_duration:
                return ["Too long", vid_info.get("title",None)]
            if not os.path.exists(f'{self.cache_folder}/{vid_info.get("id",None)}.mp3'):
                ydl.extract_info(args, download=True) #Extract Info must be used here, otherwise the download fails
                return [vid_info.get("id",None),vid_info.get("title",None)]
            else:#Passes on downloading if file already exists
                return [vid_info.get("id",None),vid_info.get("title",None)]
            
        
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
            
    
    #Cleans up the merged audio queues
    #Only occurs on shutdown/restart (for now)
    def clean_cache():
        try:
            for guild in bot.guilds:
                for f in os.listdir(f'{self.cache_folder}/'):
                    if not f.endswith(".mp3"):
                        continue
                    os.remove(os.path.join('{self.cache_folder}/', f))
        except:
            print(f'Cache deletion error')
            
            
        
            
            
        
        
        
        
        
