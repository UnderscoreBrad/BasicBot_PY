# BasicBot_PY
A basic, Python-based bot for Discord channels.

View the website here: https://sites.google.com/view/discord-basicbot

**Important Setup Information:**

BasicBot requires you install the following Python packages: discord.py, python-dotenv, youtube-dl, youtube-search

If on Linux, run ./setup to install these packages as needed. You may need to use "chmod 755 setup" first.

BasicBot requires Server Members Intent to function. This is how it DMs and mentions users.

Environment Variables (.env) must contain the proper IDs for the bot token, owner's user ID, and owner's DM channel, site URL should be filled out with your website, or the site listed above. See sample in dotenv

global-censored.txt can contain no keywords, but ensure there are no blank lines in the file

about.txt is optional, fill it out (on one line) for an "about" command message

**Supported Features**

Bot responds to commands only in channels starting with 'basic' or 'bot'

'User Joined Your Channel' and 'User Left Your Channel' messages

Youtube audio playback with queue and search

Suppression of all new messages in channels named 'official-complaints'

Keyword-censoring for racism and homophobia as the owner specifies in global-censored-RH.txt

**General Commands:**

--about: Information about the bot

--help: List of bot commands

--pingme: Sends you a test ping

--serverinfo: Lists information about the server

--addrole @[User] @[Role]: Adds [Role] to [User]

--giverole @[User] @[Role]: Adds [Role] to [User]

--removerole @[User] @[Role]: Removes [Role] from [User]

**Voice Channel Commands:**

--join: Have the bot join your current voice channel

--leave: Have the bot leave your current voice channel

noot

**Youtube Audio Commands**

--yt [YouTube URL/Search]: Play audio from YouTube, or add to audio queue
    
--queue [YouTube URL/Search]: Add the Youtube video to the audio queue

--add [YouTube URL/Search]: Alias for --queue
    
--play: Play songs from the first in the queue

--play [YouTube URL/Search]: Alias for --yt (when arguments are given)
    
--pause: Have the bot pause audio playback
    
--resume: Have the bot resume audio playback after pausing
    
--skip: Skip to the next song in the play queue

--next: Alias for --skip
    
--stop: Have the bot stop audio playback

**Administrative Features**

--terminate [PASSCODE]: Shuts down the bot if the correct one-time passcode was provided

--announce [PASSCODE] [MESSAGE]: Sends the specified message in all bot-command enabled servers

Shutdown via owner DM reaction

Restart via owner DM reaction

Delete audio cache via owner DM reaction

Announce restart via owner DM reaction

