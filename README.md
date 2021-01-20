# BasicBot_PY
A basic, Python-based bot for Discord channels.

**Important Setup Information:**

BasicBot requires Server Members Intent to function. This is how it DMs and mentions users.

Environment Variables (.env) must contain the proper IDs for the bot token, owner's user ID, and owner's DM channel. See sample in dotenv

global-censored-RH.txt can contain no keywords, but ensure there are no blank lines in the file

forced-delete-ids.txt either must be populated or contain a negative value, ensure there are no blank lines in the file

about.txt is optional, fill it out (on one line) for an about command message

**Supported Features**

Bot starts and restarts via the owner's DM channel

'User Joined Your Channel' and 'User Left Your Channel' messages (in progress)

Youtube audio playback (queue in progress)

Suppression of all new messages in configured text channels

Keyword-censoring for racism and homophobia as the owner specifies in global-censored-RH.txt

Supported commands:

**General Commands:**

!basic_about: Information about the bot

!basic_help: List of bot commands

!basic_pingme: Sends you a test ping

**Voice Channel Commands:**

!basic_join: Have the bot join your current voice channel

!basic_leave: Have the bot leave your current voice channel

noot

**Youtube Audio Commands**

!basic_yt [YouTube URL]: Have the bot play the video at the provided URL immediately
    
!basic_queue [YouTube URL]: Add the Youtube video to the audio queue
    
!basic_play: Play songs from the first in the queue
    
!basic_pause: Have the bot pause audio playback
    
!basic_resume: Have the bot resume audio playback after pausing
    
!basic_skip: Skip to the next song in the play queue
    
!basic_stop: Have the bot stop audio playback
