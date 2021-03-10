#SongQueue objects with arrays of video ids, names, video urls
#Each song queue is guild specific with a queue length tracker

class SongQueue:
    
    guild_id = None
    queue = None    #video url
    names = None
    video_ids = None
    length = 0
    
    #Init new SongQueue for a Guild
    #Guild identified by guild.id from the API
    def __init__(self, guild):
        self.guild_id = guild
        self.queue = []
        self.names = []
        self.video_ids = []
        self.length = 0
        
    #Add new video to the queue
    #url: Youtube URL to fetch from
    #vid_id: 11 Character youtube ID pulled from YT-DL
    #name: video title pulled from YT-DL    
    def add_queue(self, url, vid_id, name):
        self.length += 1
        self.queue.append(url)
        self.video_ids.append(vid_id)
        self.names.append(name)
        
    
    #Currently Unused
    #Remove song by entry
    def remove_queue(self, url, vid_id, name):
        self.queue.remove(url)
        self.names.remove(name)
        self.video_ids.remove(vid_id)
        self.length -= 1
        
        
    #Move to next song, iterate through list
    #Boolean functionality intended for error checking, not needed
    def next_song(self):
        if self.length > 0:
            self.length -= 1
            del self.queue[0]
            del self.names[0]
            del self.video_ids[0]
        

    def get_song(self):
        if self.length > 0:
            return self.queue[0]  
        else:
            return None
            
            
    def get_song_id(self):
        if self.length > 0:
            return self.video_ids[0]
                
                
    def get_song_name(self):
        if self.length > 0:
            return self.names[0]
            
            
    def get_guild(self):
        return self.guild_id
        
    def get_queue_items(self):
        response = ''
        num = 1
        for name in self.names:
            response += f'#{num}: {name}\n'
            num+=1
        return response    
        
    def get_queue_length(self):
        return self.length
        
        
    def reset_queue(self):
        self.length = 0
        self.queue = []
        self.names = []

