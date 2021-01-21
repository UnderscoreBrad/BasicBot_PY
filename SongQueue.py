class SongQueue:
    
    guild_id = None
    queue = None
    names = None
    video_ids = None
    length = 0
    
    def __init__(self, guild):
        self.guild_id = guild
        self.queue = []
        self.names = []
        self.video_ids = []
        self.length = 0
        
        
    def add_queue(self, url, vid_id, name):
        self.length += 1
        self.queue.append(url)
        self.video_ids.append(vid_id)
        self.names.append(name)
        
        
    def remove_queue(self, url, vid_id, name):
        self.queue.remove(url)
        self.names.remove(name)
        self.video_ids.remove(vid_id)
        self.length -= 1
        
        
    def next_song(self):
        if self.length > 0:
            self.length -= 1
            del self.queue[0]
            del self.names[0]
            del self.video_ids[0]
            return True
        elif self.length == 0:
            return False
        

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

