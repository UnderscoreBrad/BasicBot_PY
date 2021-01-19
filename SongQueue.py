class SongQueue:
    
    guild_id = None
    channel_id = None
    queue = []
    length = 0
    
    def __init__(self, guild):
        self.guild_id = guild
        

    def upon_join(self, channel):
        self.channel_id = channel
        
        
    def add_queue(self, url):
        self.length += 1
        self.queue.append(url)
        
        
    def remove_queue(self, url):
        self.queue.remove(url)
        self.length -= 1
        
        
    def next_song(self):
        if length > 0:
            self.queue.pop(0)
            self.length -= 1
            return self.queue[0]
        elif length == 0:
            return None
        
        
    def is_occupied(self):
        return (self.length > 0)
        
        
    def get_queue_length(self):
        return self.length
        
        
    def reset_queue(self):
        self.length = 0
        self.queue = []
