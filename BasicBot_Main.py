#BasicBot_Main.py

import os
import discord
from discord.ext.commands import Bot
import string
import random
import sys
import MessageChecker
import YtDownloader
import SongQueue
from dotenv import load_dotenv

#Globals setup
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
OWNER_ID = int(os.getenv('OWNER_ID'))
OWNER_DM = None
try:
    SITE_URL = os.getenv('SITE_URL')
except:
    SITE_URL = 'Site URL not set'
if SITE_URL == "0":
    SITE_URL = 'Site URL not set'
try:
    BUG_REPORT_CHANNEL = int(os.getenv('BUG_REPORT_CHANNEL'))
except:
    BUG_REPORT_CHANNEL = None
if BUG_REPORT_CHANNEL == 0:
    BUG_REPORT_CHANNEL = None
ABOUT = None
song_queues = []
yt_guilds = []
downloader = YtDownloader.YtDownloader()
message_checker = MessageChecker.MessageChecker()


#Read data from about.txt
try:
    f = open('about.txt')
    ABOUT = f.readline()
except:
    print('No about.txt found')
    ABOUT = 'Not Configured.'
finally:
    f.close()
    

#Generate a unique termination code for this session
terminateCode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

#Initialize bot w/ intents
intents = discord.Intents.default()
intents.members = True
bot = Bot(command_prefix='--', intents=intents)
bot.remove_command('help') #To override the standard Help


#=========================================================
#       STARTUP & JOIN SETUP
#=========================================================

#ON READY:
#Bot establishes connection to discord, notifies terminal with the stop code
#Prints out a list of connected servers to terminal (Owner DM planned, low priority)
#Prints owner user, as found in .env
#DMs owner with a startup message, reacts to it with the bot control emojis
@bot.event
async def on_ready():
    global OWNER_ID
    global OWNER_DM
    global song_queue
    guild_list = ""
    
    #Find all joined servers
    print(f'{bot.user} is online. Terminate with OTP: {terminateCode}')
    for guild in bot.guilds:
        print(f'Joined server: {guild.id}')
        guild_list = guild_list + f'Joined server: {guild.id}.\n'
        song_queues.append(SongQueue.SongQueue(guild.id))
    
    #Send startup info to the owner DMs
    await bot.get_user(OWNER_ID).create_dm()
    msg = await bot.get_user(OWNER_ID).dm_channel.send(f'{guild_list}{bot.user} is online. Terminate with OTP: {terminateCode} or react to this message.\n\
Use: \U0001F6D1 to Shut down |  \U0001F504 to Restart |  \U0000274C to Delete audio cache |  \U0001F565 to Notify before restart')
    OWNER_DM = bot.get_user(OWNER_ID).dm_channel.id
    #Add control emojis
    await msg.add_reaction('\U0001F6D1')
    await msg.add_reaction('\U0001F504')
    await msg.add_reaction('\U0000274C')
    await msg.add_reaction('\U0001F565')	
    await bot.change_presence(status=discord.Status.online,activity=discord.Game(f"{bot.command_prefix}about | {bot.command_prefix}help"))
    
    
#ON GUILD JOIN
#Creates a song queue for the new guild, so the bot doesnt need a restart
#Notifies in DMs: Bot owner
#Notifies in DMS: Guild Owner   
@bot.event
async def on_guild_join(guild):
    global song_queues
    global OWNER_ID
    global SITE_URL
    song_queues.append(sq.SongQueue(guild.id))
    print(f'Joined server: {guild.id}')
    
    #DM Bot Owner
    #await bot.get_user(OWNER_ID).create_dm()
    await bot.get_user(OWNER_ID).dm_channel.send(f'Joined a new server {guild.id}.')
    
    #DM Guild Owner
    #await guild.owner.create_dm()
    await guild.owner.dm_channel.send(f"{bot.user.name} was just invited to your server by you or an administrator!\n\
Get started with {bot.user.name} by typing --help\n\
Didn't invite {bot.user.name}? Contact us at {SITE_URL}")
    
    
#=========================================================
#       REACTION AND MESSAGE PROCESSING
#=========================================================
    
    
#ON REACTION: (Administrative actions)
#If the message reacted to is in owner DMs:
#Bot must be message sender, owner reacted to DM, reacted with U0001F6D1 (Shut Down)
#Bot must be message sender, owner reacted to DM, reacted with U0001F504 (Restart)
#Bot must be message sender, owner reacted to DM, reacted with U0000274C (Delete Cache)
#Bot must be message sender, owner reacted to DM, reacted with U0001F565 (Restart Soon)
@bot.event
async def on_reaction_add(reaction, user):
    global terminateCode
    #Only honor reactions if from the owner
    if reaction.message.channel.id == OWNER_DM:
        if reaction.message.author.name == bot.user.name and user.id == OWNER_ID:
        
            #Shutdown bot gracefully
            if reaction.emoji == '\U0001F6D1':
                await reaction.message.channel.send(f'{bot.user} is shutting down!')
                for vc in bot.voice_clients:
                    await vc.disconnect()
                await bot.change_presence(status=discord.Status.idle,activity=discord.Game("Shutting Down"))
                print(f'{bot.user} shut down.\n')
                await bot.close()
                
            #Shutdown bot gracefully, restart program to refresh variables/code    
            elif reaction.emoji == '\U0001F504':
                await reaction.message.channel.send(f'{bot.user} is restarting!')
                for vc in bot.voice_clients:
                    await vc.disconnect()
                await bot.change_presence(status=discord.Status.idle,activity=discord.Game("Restarting"))
                print(f'{bot.user} restarting.\n')
                await bot.close()
                os.execl(sys.executable, sys.executable, *sys.argv)
                
            #Delete all .mp3 files from YTCache
            elif reaction.emoji == '\U0000274C':
                await reaction.message.channel.send(f'{bot.user} is deleting the audio cache.')
                downloader.clean_cache()
                print(f'{bot.user} audio cache deleted.')
                
            #Notify all BasicBot-Enabled servers that there will be a restart
            elif reaction.emoji == '\U0001F565':    #This was reverted, announce command cannot be called
                for g in bot.guilds:                #Reaction has no object "ctx"
                    for c in g.channels:
                        if c.name.startswith('bot') or c.name == 'basicbot':
                            await c.send(f'{bot.user} will restart for an update soon!')
                            break


#ON MESSAGE:
#Bot checks which channel the message is in, force-deleting message in specific channels
#Attempts to command-check
#If not a command, but starts with !basic
@bot.event
async def on_message(message):
    global BUG_REPORT_CHANNEL
    if(message.author == bot.user): #do not censor process messages from the bot itself
        return
    if type(message.channel) == (discord.TextChannel):
        if message.channel.name == 'official-complaints':
            await message.delete()  #messages in these channels are deleted without question
            return
                                    #valid_channel is used to determine if the channel is a command channel
        valid_channel = message.channel.name.startswith('bot') or message.channel.name == 'basicbot'
    else:    
        valid_channel = message.guild == None
        if valid_channel and "bug report" in message.content.lower() and BUG_REPORT_CHANNEL:
            bug_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            await bot.get_channel(BUG_REPORT_CHANNEL).send(f"Bug report {bug_id} from {message.author}:\n{message.content}")
            await bot.get_user(message.author.id).dm_channel.send(f"Your bug report has been submitted and will be addressed in the order it was recieved. We may ask for additional details regarding this issue.\nYour ticket ID is: {bug_id}")
    try:                                                #Try-catch might not be necessary.   
        if valid_channel:                               #the command will only be interpreted in specific channels 
            if bot.user.mentioned_in(message) and 'go to hell' in message.content.lower():  #Allows for a call to "@{bot.user} go to hell" for an easter egg.
                message.content = '--go_to_hell'        #the lack of private data members in Python is a nightmare
            await bot.process_commands(message)         
    finally:
        await _censor_check(message, valid_channel)     #censor checking will be reworked with a return type such that it can come first

            
#Child of ON MESSAGE
#Automatically censors keywords in global-censored.txt
#Uses message_checker as defined in the MessageChecker class
async def _censor_check(message, valid_channel):
    global OWNER_ID
    global SITE_URL
    if message_checker.check_message(message.content):
        try:                                            #Message deletion is not always possible for a variety of reasons, try-catch is used as a result :/
            await message.delete()
            await message.author.create_dm()
            await message.author.dm_channel.send(f'You sent a message including a banned keyword in {message.guild.name}: {message.channel}.\n\
Your message: "{message.content}"\n\
Reason: Offensive Language\n\
If you believe this was an error, please send a ticket at {SITE_URL} or reply to this DM with "Bug Report" in your message.')
        except:
            pass
    elif message.content.lower().startswith('noot') and valid_channel:
        await _noot(message) 

#Child of ON MESSAGE
#replies with noot-noot if nothing's already playing.
async def _noot(message):
    voice_client = None
    if message.guild.id not in yt_guilds:   #If the bot is in a voice channel, nothing is playing, and the author is in voice channel
        if(message.author.voice):
            voice_client = discord.VoiceClient = discord.utils.get(bot.voice_clients, guild=message.guild)
            if voice_client and not voice_client.is_playing():
                player = discord.FFmpegPCMAudio('AudioBin/NootSound.mp3')   #Play noot-noot
                voice_client.play(player,after=None)
                voice_client.source = discord.PCMVolumeTransformer(player,volume=0.7)   #Volume adjusted, clip was too loud.


#=========================================================
#       GENERAL COMMANDS
#=========================================================

#{bot.command_prefix}help:
#Responds with list of available commands and their functions.
#Effectively overrides the built-in Help command (formatting is better)
@bot.command(name = 'help',help = f'A list of commands and functions for {bot.user}', category='General')
async def help(ctx):
    response = (f'**{bot.user} has the following commands:**\n\
  **General Commands:**\n\
  {bot.command_prefix}about: Information about the bot\n\
  {bot.command_prefix}help: List of bot commands\n\
  {bot.command_prefix}pingme: Sends you a test ping\n\
  {bot.command_prefix}serverinfo: Lists information about the current server\n\
  {bot.command_prefix}addrole @[User] @[Role]: Gives role for the specified user\n\
  {bot.command_prefix}removerole @[User] @[Role]: Removes role from the specified user\n\
  **Voice Channel Commands:**\n\
  {bot.command_prefix}join: Have the bot join your current voice channel\n\
  {bot.command_prefix}leave: Have the bot leave your current voice channel\n\
  **Youtube Audio Commands**\n\
  {bot.command_prefix}yt [Search/URL]: Play YouTube audio immediately or add to queue\n\
  {bot.command_prefix}queue [Search/URL]: Add the Youtube video to the audio queue\n\
  {bot.command_prefix}play: Play songs from the first in the queue\n\
  {bot.command_prefix}loop [URL][Count]: Loop the song a given number of times\n\
  {bot.command_prefix}pause: Have the bot pause audio playback\n\
  {bot.command_prefix}resume: Have the bot resume audio playback after pausing\n\
  {bot.command_prefix}skip: Skip to the next song in the play queue\n\
  {bot.command_prefix}stop: Have the bot stop audio playback\n\
  {bot.command_prefix}clearqueue: Clear the media queue')
    await ctx.send(response)


#{bot.command_prefix}about
#Responds with info about the bot
#Message customizable in about.txt
@bot.command(name = 'about', help = f'Information about {bot.user}')
async def about(ctx):
    global ABOUT
    global SITE_URL
    await ctx.send(f'About {bot.user}:\n' + ABOUT + f' \nFind out more at {SITE_URL}.')
    
    
#{bot.command_prefix}pingme
#Pings the user, for testing.
@bot.command(name='pingme', help = f'Sends the user a test ping')
async def pingme(ctx):
    await ctx.send(f'<@!{ctx.author.id}> here is your test ping')
    
    
#{bot.command_prefix}add_role [USER] [Role]
#Gives the mentioned user the role specified
@bot.command(name='addrole')
async def addrole(ctx, member_id, *, role):
    role_id = 0
    if '<@&' in role and '>' in role:
        role_id = int(role.replace('<@&','').replace('>',''))
        role = ctx.guild.get_role(role_id)
    else:
        for r in ctx.guild.roles:
            if r.name == role:
                role = r
                break
    if not role:
        await ctx.send('Invalid role.')
        return
    member_id = int(member_id.replace('<@!','').replace('>',''))
    member = ctx.guild.get_member(member_id)
    await _role_manager(ctx, member, role, True)
        
        
#{bot.command_prefix}give_role [USER] [Role]
#Gives the mentioned user the role specified
@bot.command(name='giverole')
async def giverole(ctx, member_id, *, role):
    role_id = 0
    if '<@&' in role and '>' in role:
        role_id = int(role.replace('<@&','').replace('>',''))
        role = ctx.guild.get_role(role_id)
    else:
        for r in ctx.guild.roles:
            if r.name == role:
                role = r
                break
    if not role:
        await ctx.send('Invalid role.')
        return
    member_id = int(member_id.replace('<@!','').replace('>',''))
    member = ctx.guild.get_member(member_id)
    await _role_manager(ctx, member, role, True)

        
#{bot.command_prefix}remove_role [USER] [Role]
#Removes the specified role from the mentioned user
@bot.command(name='removerole')
async def removerole(ctx, member_id, *, role):
    role_id = 0
    if '<@&' in role and '>' in role:
        role_id = int(role.replace('<@&','').replace('>',''))
        role = ctx.guild.get_role(role_id)
    else:
        for r in ctx.guild.roles:
            if r.name == role:
                role = r
                break
    if not role:
        await ctx.send('Invalid role.')
        return
    member_id = int(member_id.replace('<@!','').replace('>',''))
    member = ctx.guild.get_member(member_id)
    await _role_manager(ctx, member, role, False)

        
        
#{bot.command_prefix}server_info
#Sends Guild info in the text channel
@bot.command(name='serverinfo')
async def serverinfo(ctx):
    if ctx.guild:
        response =  f'Server Name: {ctx.guild.name}\n'
        response += f'Member Count: {ctx.guild.member_count}\n'
        response += f'Channel Count: {len(ctx.guild.text_channels)}\n'
        response += f'Voice Channels: {len(ctx.guild.voice_channels)}\n'
        response += f'Server Tier: {ctx.guild.premium_tier}\n'  
        response += f'Creation Date: {ctx.guild.created_at.date()}\n'  
        await ctx.send(response)
    else:
        await ctx.send('Cannot find server info (not a server or insufficient bot permissions)')
        
        
#{bot.command_prefix}go_to_hell
#A suggestion from a user
#This command performs little to no true function
@bot.command(name='go_to_hell')
async def go_to_hell(ctx):
    voice_client = None
    await ctx.send(f'<@!{ctx.author.id}> no :)')            #always respond with "no"
    if(ctx.guild and ctx.author.voice):
        voice_client = discord.VoiceClient = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if not voice_client:                                #Joins voice if not already active in a voice channel
            await join(ctx,audio=False)    
            voice_client = discord.VoiceClient = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice_client and not voice_client.is_playing():  #Does not interrupt music playback
            player = discord.FFmpegPCMAudio('AudioBin/copypasta01.mp3') #Plays this audio clip at half volume upon command
            voice_client.play(player,after=None)
            voice_client.source = discord.PCMVolumeTransformer(player,volume=0.5)
            
            
#Internal use role manager function
async def _role_manager(ctx, member, role, add):            #Internal function of adding or removing given roles
    if not member:                                                          
        await ctx.send('Invalid member.')
        return
    if ctx.author.top_role > role:
        if add:
            if role in member.roles:
                await ctx.send('User already has that role!')
                return
            await member.add_roles(role, reason=f'{ctx.author} added role: {role.name} to {member.name}')
            await ctx.send(f'{role.name} added to {member.name}')
        else:
            if role not in member.roles:
                await ctx.send('User does not have that role!')
                return
            await member.remove_roles(role, reason=f'{ctx.author} removed the role: {role.name} from {member.name}')
            await ctx.send(f'{role.name} removed from {member.name}')
    else:
        await ctx.send(f'You do not have a high enough role to do that!')
        
        
#=========================================================
#       VOICE CHANNEL COMMANDS
#=========================================================        
        
#{bot.command_prefix}join
#Bot joins the voice channel of the command author
#Static command, no customization
@bot.command(name='join',help=f'Calls the bot into voice chat')
async def join(ctx,audio=True):
    try:
        if not ctx.guild or not ctx.author.voice:
            await ctx.send(f'You must be in a voice channel to do that!')
            return
        channel = ctx.author.voice.channel
        voice_client = await channel.connect()
        if audio:
            player = discord.FFmpegPCMAudio('AudioBin/HelloThere.mp3')
            voice_client.play(player,after=None)
            voice_client.source = discord.PCMVolumeTransformer(player,volume=2.5)
        await ctx.send(f'Joining voice channel {ctx.author.voice.channel}')
    except:
        await ctx.send(f'Unable to join {ctx.author.voice.channel} (Bot already in another channel or other error)')
    
    
#{bot.command_prefix}leave
#Bot leaves the voice channel of the command author, if it was in one.
#Static command, no customization
@bot.command(name='leave',help=f'Asks {bot.user} to leave voice chat')
async def leave(ctx):
    global yt_guilds
    if not ctx.guild or not ctx.author.voice:
        await ctx.send(f'You must be in a voice channel to do that!')
        return
    vcID = ctx.guild.voice_client
    await vcID.disconnect()
    await ctx.send(f'Leaving voice channel {ctx.author.voice.channel}')
    if ctx.guild.id in yt_guilds:   #Resets guild YT playback if found
        _reset_guild_playback(ctx)
    

#=========================================================
#       YOUTUBE PLAYBACK COMMANDS
#=========================================================    
    
#{bot.command_prefix}yt
#Uses Youtube-DL to download an MP3 of the selected video
#Plays that audio file via FFmpeg Opus
#Cuts off any currently playing audio.
@bot.command(name='yt', help = f'Plays the youtube audio through the bot.')
async def yt(ctx, *, args):
    if args:
        await _play(ctx, args)
        return
    await _play(ctx)


#{bot.command_prefix}stop
#Stops any audio being played by the bot
@bot.command(name='stop', help = f'Asks the bot to stop its current audio playback.')
async def stop(ctx):
    global song_queues
    if not ctx.guild or not ctx.author.voice:
        await ctx.send(f'You must be in a voice channel to do that!')
        return
    voice_client = discord.VoiceClient = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_connected() and voice_client.is_playing():
        voice_client.stop()
        for s in song_queues:
            if s.get_guild() == ctx.guild.id:
                s.reset_queue()
                break
        await ctx.send(f'Audio stopped, play queue cleared.')
    else:
        await ctx.send(f'No audio to stop.')


#{bot.command_prefix}pause
#Pauses any audio being played by the bot
@bot.command(name='pause', help = f'Asks {bot.user} to pause its current audio playback.')
async def pause(ctx):
    if not ctx.guild or not ctx.author.voice:
        await ctx.send(f'You must be in a voice channel to do that!')
        return
    voice_client = discord.VoiceClient = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_connected() and voice_client.is_playing():
        voice_client.pause()
        await ctx.send(f'Youtube audio paused.')
        

#{bot.command_prefix}resume
#Resumes any audio being played by the bot
@bot.command(name='resume',help = f'Asks {bot.user} to resume paused audio payback.')
async def resume(ctx):
    if not ctx.guild or not ctx.author.voice:
        await ctx.send(f'You must be in a voice channel to do that!')
        return
    voice_client = discord.VoiceClient = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_connected() and voice_client.is_paused():
        voice_client.resume()
        await ctx.send(f'Resuming youtube audio playback.')


#{bot.command_prefix}queue
#adds the song given as url to the queue
@bot.command(name='queue',help = f'Adds the song at the URL to the play queue for the server')
async def queue(ctx, *, args):
    args = f"{args}"
    await _queue(ctx, args)
    
    
#{bot.command_prefix}add
#calls {bot.command_prefix}queue (command alias)
@bot.command(name='add', help = f'Alias for {bot.command_prefix}queue')
async def add(ctx, *, args):
    args = f"{args}"
    await _queue(ctx, args)
    
            
#{bot.command_prefix}skip
#Stops playback then skips to the next song
@bot.command(name= 'skip',help = f'Skips to the next song in the play queue')
async def skip(ctx):
    if not ctx.guild or not ctx.author.voice:
        await ctx.send(f'You must be in a voice channel to do that!')
        return
    voice_client = discord.VoiceClient = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_connected() and voice_client.is_playing():
        voice_client.stop()
        await ctx.send(f'Skipping to next audio track.')
        for s in song_queues:
            if s.get_guild() == ctx.guild.id:
                if s.get_queue_length() == 0:       #Resets the queue if this song was the last
                    s.reset_queue()
    
    
#{bot.command_prefix}next    
#alias of {bot.command_prefix}skip
@bot.command(name='next',help=f'Alias for {bot.command_prefix}skip')
async def next(ctx):
    await skip(ctx)


#{bot.command_prefix}clearqueue
#Clears the youtube play queue
@bot.command(name='clearqueue',help=f'Clears the media queue')
async def clearqueue(ctx):
    global song_queues
    if not ctx.guild or not ctx.author.voice:
        await ctx.send(f'You must be in a voice channel to do that!')
        return
    for s in song_queues:
        if s.get_guild()==ctx.guild.id:
            try:
                s.reset_queue()
                await ctx.send(f'Play queue cleared!')
                _reset_guild_playback(ctx)
            except:
                print(f'Error in clearing play queue from ctx.guild.id')
            break


#{bot.command_prefix}play
#Joins VC with the user if not already in a channel with them
#Plays the first audio file in the queue
#Calls _next_player() for all subsequent plays
@bot.command(name='play',help=f'Plays the songs in the queue from the start or where the bot left off.')
async def play(ctx, *, args=None):
    if args:
        await _play(ctx, args)
        return
    await _play(ctx)


#{bot.command_prefix}loop
#Downloads the audio, then queues it {num} times
#Then calls _play    
#ONLY WORKS WITH LINKS
#Because I'm lazy
@bot.command(name='loop',help=f'Loop the song specified by the URL')
async def loop(ctx, args, num=2):
    global song_queues
    if num < 2:
        num = 2
    info = downloader.download(args)
    if info[0] == "Too Long":
        await ctx.send(f'{info[1]} is too long! Max media duration: 1 Hour')
        return
    for i in range(int(num)):
        for s in song_queues:
            if s.get_guild() == ctx.guild.id:
                s.add_queue(args, info[0], info[1])
    await ctx.send(f'{info[1]} added to your play queue. It will play {num} times.')
    await _play(ctx)

    
#       Internal YouTube Playback Functions
    
#Internal use queue function
async def _queue(ctx, args):
    global song_queues
    info = downloader.download(args)
    if info[0] == "Too Long":
        await ctx.send(f'{info[1]} is too long! Max media duration: 1 Hour')
        return
    for s in song_queues:
        if s.get_guild() == ctx.guild.id:
            s.add_queue(args, info[0], info[1])
            await ctx.send(f'{info[1]} added to your play queue in position {s.get_queue_length()}')
            break
    
    
#Play from first in queue if there is a queue
#If no queue, notify user
#If already playing, notify user
async def _play(ctx, args=None):

    if not ctx.guild or not ctx.author.voice:
        await ctx.send(f'You must be in a voice channel to do that!')
        return
    voice_client = discord.VoiceClient = discord.utils.get(bot.voice_clients, guild=ctx.guild) #VOICE CLIENT JOINING
    if not voice_client:
        await join(ctx,audio=False)
        voice_client = discord.VoiceClient = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        
    #If a song is already playing, queue the request instead
    if args:
        await _queue(ctx, args)
        
    if ctx.guild.id not in yt_guilds:           #interrupt non-YT audio
        if voice_client.is_playing():
            voice_client.stop()   
        for s in song_queues:                   #find right song queue for the guild
            if s.get_guild() == ctx.guild.id:
                if s.get_queue_length() > 0:    #Add guild to YT guilds if there's at least 1 song
                    _set_guild_playback(ctx)
                    if not os.path.exists(f'YTCache/{s.get_song_id()}.mp3'):    #download if mp3 does not exist
                        downloader.download(f'https://youtu.be/{s.get_song_id()}')
                    player = discord.FFmpegPCMAudio(f'YTCache/{s.get_song_id()}.mp3')
                    await ctx.send(f'Now playing queued songs:\n{s.get_queue_items()}')
                    s.next_song()               #Increment through the song queue
                    voice_client.play(player, after= lambda e: _next_player(ctx,voice_client)) #silently move to next song in queue
                    voice_client.source = discord.PCMVolumeTransformer(player,volume=0.5)
                else:           #catch play command with no args and no queue
                    await ctx.send(f'Play queue is empty! Request with {bot.command_prefix}queue [URL]')
                break
    elif not voice_client.is_playing():
        voice_client.resume()   #double function as resume
        await resume(ctx)
    

#Internal use next-player function
#Used to play the next song in the queue
def _next_player(ctx, voice_client):
    if not voice_client.is_connected():
        return
    for s in song_queues:
        if s.get_guild() == ctx.guild.id:
            if s.get_queue_length() > 0:
                if not os.path.exists(f'YTCache/{s.get_song_id()}.mp3'):
                    downloader.download(f'https://youtu.be/{s.get_song_id()}')
                player = discord.FFmpegPCMAudio(f'YTCache/{s.get_song_id()}.mp3')
                s.next_song()
                voice_client.play(player, after= lambda e: _next_player(ctx,voice_client))
                voice_client.source = discord.PCMVolumeTransformer(player,volume=0.5)
                return None #Return None to be safe and avoid playback issues
            else:
                #Reset playback and return None to remove songs after
                _reset_guild_playback(ctx)
                return None
    return None    
    
    
#Removes the guild from the list of guilds playing songs    
def _reset_guild_playback(ctx):
    global yt_guilds
    yt_guilds.remove(ctx.guild.id)
    return None
    
    
#Adds the guild to the list of guilds playing songs
def _set_guild_playback(ctx):
    global yt_guilds
    yt_guilds.append(ctx.guild.id)
    return None
    

#========================================================= 
#       ADMINISTRATIVE COMMANDS
#========================================================= 
    

#{bot.command_prefix}terminate [PASSCODE]
#Bot shuts down if the correct OTP is given
#Incorrect attempts will be ignored, the bot will continue to function.
#Static command, no customization
@bot.command(name='terminate', help=f'Asks the bot to terminate, requires 16-character OTP')
async def terminate(ctx, args):
    global terminateCode
    if args == terminateCode:
        await ctx.send(f'{bot.user} is shutting down!')
        print(f'{bot.user} shut down by {ctx.author} with code {args}\n')
        for vc in bot.voice_clients:
            await vc.disconnect()
        await bot.change_presence(status=discord.Status.idle,activity=discord.Game("Shutting Down"))
        await bot.close()
    else:
        await ctx.send(f'Wrong password! {bot.user} will not shut down.')
        print(f'{ctx.author} attempted to shutdown {bot.user} but provided incorrect password: {args}')


#{bot.command_prefix}announce [PASSCODE] "[MESSAGE]"
#Bot shuts down if the correct OTP is given
#Incorrect attempts will be ignored, the bot will continue to function.
#Static command, no customization
@bot.command(name='announce', help=f'Asks the bot to announce in all applicable channels with the provided message')
async def announce(ctx, args, *, message):
    global terminateCode
    if args == terminateCode:
        await ctx.send(f'{bot.user} is announcing "{message}"')#notify and log to terminal
        print(f'{bot.user} announced {message} from {ctx.author} with code {args}\n')
        for g in bot.guilds:    #send the announcement message only once in each guild.
            for c in g.channels:
                if c.name == 'basicbot' or c.name.startswith('bot'):
                    await c.send(f'{bot.user.name} announcement from {ctx.author}:\n{message}')
                    break
    else:   #The OTP/terminate code provided was wrong for this session, the announcement is not sent and the interaction is logged to terminal
        await ctx.send(f'Wrong password! {bot.user} will not send your announcement.')
        print(f'{ctx.author} attempted to send an announcement through {bot.user} but provided incorrect password: {args}')


#ON COMMAND ERROR
#Any errors with commands will direct the user to the Help command
#Generic command error message is sent to user, terminal gets details
@bot.event
async def on_command_error(ctx, error):
    if not isinstance(error, discord.ext.commands.CheckFailure):
        await ctx.send(f'Invalid command, use {bot.command_prefix}help for a list of commands.\nIf you believe this was an error, send {bot.user.name} a direct message with the text "Bug Report" and an explanation of the issue.')
        print(f'Command Error from {ctx.author} in {ctx.channel.id}: {error}\nMessage ID: {ctx.message.id}\nMessage content: {ctx.message.content}')


#ON VOICE STATE UPDATE:
#If the bot is in a voice chat, compare that voice chat to the join or leave
#If the voice client the user left is the same as the bot is in, play LeaveSound.mp3
#If the voice client the user joined is the same as the bot is in, play JoinSound.mp3
#Simulates the Teamspeak Experience (TM)
#BasicBot leaves with the last VC member as well
@bot.event
async def on_voice_state_update(member, before, after):
    global yt_guilds
    if bot.voice_clients:
        if before.channel != after.channel:             #If the user changed channels
            for vc in bot.voice_clients:                #use of a for loop here means BasicBot will get bogged down if invited to enough servers
                if vc.is_connected():
                    if vc.channel == before.channel:    #If the channel before is the selected channel, user left this channel
                        player = discord.FFmpegPCMAudio('AudioBin/LeaveSound.mp3')
                        if len(vc.channel.members) == 1:#if only the bot is in the channel, leave silently.
                            await vc.disconnect()
                            continue
                        if vc.guild.id not in yt_guilds:#Do not interrupt youtube playback
                            if vc.is_playing():         #Interrupt audio for "noot-noot", "go to hell", or other voice state updates
                                vc.stop()
                            vc.play(player, after=None)#Play Leave sound with none after at default volume
                            vc.source = discord.PCMVolumeTransformer(player, volume=1.0)
                    elif vc.channel == after.channel:
                        player = discord.FFmpegPCMAudio('AudioBin/JoinSound.mp3')
                        if vc.guild.id not in yt_guilds:#Do not interrupt youtube playback
                            if vc.is_playing():         #Interrupt audio for "noot-noot", "go to hell", or other voice state updates
                                vc.stop()
                            vc.play(player, after=None)#Play join sound with none after at default volume
                            vc.source = discord.PCMVolumeTransformer(player, volume=1.0)
          
           
try:
    bot.run(TOKEN)
except:
    print("Error running your bot. Check your .env")
finally:
    print("Thank you for using BasicBot_PY.\n")
