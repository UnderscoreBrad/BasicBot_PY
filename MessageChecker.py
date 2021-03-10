class MessageChecker:

    keywords = None
    
    def __init__(self):
        try:
            with open('global-censored.txt') as gcensor:
                self.keywords = [ln.lower().rstrip() for ln in gcensor]
        except:
            print('Could not read from global-censored.txt')
    
    
    def check_message(self, message):
        if not self.keywords:
            return False
        for k in self.keywords:
            if k in message.lower():
                return True
        return False
