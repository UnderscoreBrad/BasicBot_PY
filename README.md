# BasicBot_PY
A basic, Python-based bot for Discord channels.

**Important Setup Information:**

config.txt must contain the proper IDs for the bot token, owner's user ID, and owner's DM channel

global-censored-RH.txt can contain no keywords, but ensure there are no blank lines in the file

forced-delete-ids.txt either must be populated or contain a negative value, ensure there are no blank lines in the file

about.txt is optional, fill it out (on one line) for an about command message

**Supported Features**

'User Joined Your Channel' and 'User Left Your Channel' messages (in progress)

Youtube audio playback (queue in progress)

Suppression of all new messages in configured text channels

Keyword-censoring for racism and homophobia as the owner specifies in global-censored-RH.txt

Supported commands:

!basic_help

!basic_about

!basic_join

!basic_leave

!basic_yt [YOUTUBE URL]

!basic_stop

!basic_pause

!basic_resume

!basicbot_terminate [PASSCODE]

noot
