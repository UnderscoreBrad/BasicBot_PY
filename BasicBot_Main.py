#BasicBot_Main.py

import os
import discord
from discord.ext.commands import Bot
import random
import string
import sys
import youtube_dl
import SongQueue as sq
from dotenv import load_dotenv
from youtube_search import YoutubeSearch

#Globals setup
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
OWNER_ID = int(os.getenv('OWNER_ID'))
OWNER_DM = int(os.getenv('OWNER_DM'))
KEYWORDS_RH = None
ABOUT = None
song_queues = []
yt_guilds = []
extra_ban_message = False


#Read data from about.txt
try:
    f = open('about.txt')
    ABOUT = f.readline()
except:
    print('No about.txt found')
    ABOUT = 'About command not configured'
finally:
    f.close()

#Read data from global-censored.txt
try:
    with open('global-censored.txt') as gcensor:
        KEYWORDS_RH = [ln.lower().rstrip() for ln in gcensor]
except:
    print('Could not read from global-censored.txt')
finally:
    #KEYWORDS_RH = KEYWORDS_RH.remove('Racsism/Homophobia Keywords, 1 Term/Phrase Per Line:'.lower())
    pass #Trying to make this phrase removal work, until then, this phrase is ignored every time.
    
opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'YTCache/%(id)s.mp3',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
        }],
    }

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
#DMs owner with a startup message, reacts to it with the emojis STOP_SIGN and ARROWS_COUNTERCLOCKWISE
@bot.event
async def on_ready():
    global OWNER_ID
    global song_queue
    print(f'{bot.user} is online. Terminate with OTP: {terminateCode}')
    for guild in bot.guilds:
        print(f'{bot.user} joined server: {guild.name} ID: {guild.id}')
        song_queues.append(sq.SongQueue(guild.id))
    print(f'{bot.get_user(OWNER_ID)} detected as Bot Owner. Change in .env')
    await bot.get_user(OWNER_ID).create_dm()
    msg = await bot.get_user(OWNER_ID).dm_channel.send(f'{bot.user} is online. Terminate with OTP: {terminateCode} or react to this message.\n\
Use: \U0001F6D1 to Shut down |  \U0001F504 to Restart |  \U0000274C to Delete audio cache |  \U0001F565 to Notify before restart')
    await msg.add_reaction('\U0001F6D1')
    await msg.add_reaction('\U0001F504')
    await msg.add_reaction('\U0000274C')
    await msg.add_reaction('\U0001F565')	
    await msg.add_reaction('\U00002754')
    
    
#ON GUILD JOIN
#Creates a song queue for that guild, so the bot doesnt need a restart    
@bot.event
async def on_guild_join(ctx):
    global song_queues
    global OWNER_ID
    song_queues.append(sq.SongQueue(guild.id))
    print(f'{bot.user} joined server: {guild.name} ID: {guild.id}')
    await bot.get_user(OWNER_ID).create_dm()
    msg = await bot.get_user(OWNER_ID).dm_channel.send(f'{bot.user} Has joined a new server: {guild.name} ID: {guild.id}.')
    
    
#=========================================================
#       REACTION AND MESSAGE PROCESSING
#=========================================================
    
    
#ON DM REACTION:
#If the message reacted to is in owner DMs:
#Bot must be message sender, owner reacted to DM, reacted with STOP_SIGN
#Bot is gracefully terminated
@bot.event
async def on_reaction_add(reaction, user):
    global extra_ban_message
    if reaction.message.channel.id == OWNER_DM:
        if reaction.message.author.name == bot.user.name and user.id == OWNER_ID:
            if reaction.emoji == '\U0001F6D1':
                await reaction.message.channel.send(f'{bot.user} is shutting down!')
                for vc in bot.voice_clients:
                    await vc.disconnect()
                print(f'{bot.user} shut down via owner DM reaction\n')
                #clean_up_audio()
                await bot.close()
            elif reaction.emoji == '\U0001F504':
                await reaction.message.channel.send(f'{bot.user} is restarting!')
                for vc in bot.voice_clients:
                    await vc.disconnect()
                print(f'{bot.user} restarted via owner DM reaction\n')
                #clean_up_audio()
                await bot.close()
                os.execl(sys.executable, sys.executable, *sys.argv)
            elif reaction.emoji == '\U0000274C':
                await reaction.message.channel.send(f'{bot.user} is deleting the audio cache.')
                clean_up_audio()
                print(f'{bot.user} audio cache deleted.')
            elif reaction.emoji == '\U0001F565':
                for g in bot.guilds:
                    for c in g.channels:
                        if c.name.startswith('bot') or c.name == 'basicbot':
                            await c.send(f'{bot.user} will restart for an update soon!')
                            break
            elif reaction.emoji == '\U00002754':
                extra_ban_message = not extra_ban_message


#ON MESSAGE:
#Bot checks which channel the message is in, force-deleting message in specific channels
#Attempts to command-check
#If not a command, but starts with !basic
@bot.event
async def on_message(message):
    if type(message.channel) == (discord.TextChannel):
        if message.channel.name == 'official-complaints':
            await message.delete()  #messages in these channels are deleted without question
            return
                                    #ch_bool is used to determine if the channel is a command channel
    if type(message.channel) == (discord.TextChannel):
        ch_bool = message.channel.name.startswith('bot') or message.channel.name == 'basicbot'
    else:    
        ch_bool = message.guild == None
    try:
        if ch_bool:                 #the command will only be interpreted in specific channels 
            await bot.process_commands(message)
    finally:
        await censor_check(message, ch_bool)

            
#Child of ON MESSAGE
#Automatically censors keywords in global-censored.txt
async def censor_check(message, ch_bool):
    global OWNER_ID
    global KEYWORDS_RH
    global extra_ban_message
    if message.author == bot.user or KEYWORDS_RH == None or KEYWORDS_RH == 'Racsism/Homophobia Keywords, 1 Term/Phrase Per Line:':
        return
    kwd = False
    for k in KEYWORDS_RH:
        if k != 'Racsism/Homophobia Keywords, 1 Term/Phrase Per Line:'.lower() and k in message.content.lower():
            kwd = True
            break
    if kwd:
        try:
            await message.delete()
            await message.author.create_dm()
            await message.author.dm_channel.send(f'You sent a message including a banned keyword in {message.guild.name}: {message.channel}. Your message: "{message.content}"\nReason: Offensive Language\nIf you believe this was an error, please contact {bot.get_user(OWNER_ID)}')
            if extra_ban_message:
                await message.author.dm_channel.send(f'For an explanation of this removal: https://www.youtube.com/watch?v=55-mHgUjZfY')
            print(f'Deleted message "{message.id}" from {message.author} in {message.channel.id}')
        except:
            print(f'Failed to delete message {message.id} from {message.author} in {message.channel.id}.')
    elif message.content.lower().startswith('noot'):
        await _noot(message, ch_bool) 

#Child of ON MESSAGE
#replies with noot-noot if nothing's already playing.
async def _noot(message, ch_bool):
    voice_client = None
    if message.guild.id not in yt_guilds:
        if(message.author.voice and ch_bool):
            voice_client = discord.VoiceClient = discord.utils.get(bot.voice_clients, guild=message.guild)
            if voice_client and not voice_client.is_playing():
                player = discord.FFmpegPCMAudio('AudioBin/NootSound.mp3')
                voice_client.play(player,after=None)
                voice_client.source = discord.PCMVolumeTransformer(player,volume=0.7)


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
    {bot.command_prefix}server_info: Lists information about the current server\n\
    {bot.command_prefix}add_role @[User] [Role]: Gives role for the specified user\n\
    {bot.command_prefix}remove_role @[User] [Role]: Removes role from the specified user\n\
    **Voice Channel Commands:**\n\
    {bot.command_prefix}join: Have the bot join your current voice channel\n\
    {bot.command_prefix}leave: Have the bot leave your current voice channel\n\
    **Youtube Audio Commands**\n\
    {bot.command_prefix}yt [Search/URL]: Have the bot play the video at the provided URL immediately\n\
    {bot.command_prefix}queue [Search/URL]: Add the Youtube video to the audio queue\n\
    {bot.command_prefix}play: Play songs from the first in the queue\n\
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
    await ctx.send(f'About {bot.user}:\n' + ABOUT)
    
    
#{bot.command_prefix}pingme
#Pings the user, for testing.
@bot.command(name='pingme', help = f'Sends the user a test ping')
async def pingme(ctx):
    await ctx.send(f'<@!{ctx.author.id}> here is your test ping')
    
    
#{bot.command_prefix}add_role [USER] [Role]
#Gives the mentioned user the role specified
@bot.command(name='add_role')
async def add_role(ctx, member_id, *, role):
    for r in ctx.guild.roles:
        if r.name == role:
            role = r
            break
    if not role:
        await ctx.send('Invalid role.')
        return
    member_id = int(member_id.replace('<@!','').replace('>',''))
    member = ctx.guild.get_member(member_id)
    if not member:
        await ctx.send('Invalid member.')
        return
    if role in member.roles:
        await ctx.send('User already has that role!')
        return
    if ctx.author.top_role > role:
        await _role_manager(ctx, member, role, True)
    else:
        await ctx.send(f'You do not have a high enough role to do that!')
        
        
#{bot.command_prefix}remove_role [USER] [Role]
#Removes the specified role from the mentioned user
@bot.command(name='remove_role')
async def remove_role(ctx, member_id, *, role):
    for r in ctx.guild.roles:
        if r.name == role:
            role = r
            break
    if not role:
        await ctx.send('Invalid role.')
        return
    member_id = int(member_id.replace('<@!','').replace('>',''))
    member = ctx.guild.get_member(member_id)
    if not member:
        await ctx.send('Invalid member.')
        return
    if role not in member.roles:
        await ctx.send('User does not have that role!')
        return
    if ctx.author.top_role > role:
        await _role_manager(ctx, member, role, False)
    else:
        await ctx.send(f'You do not have a high enough role to do that!')
        
        
#{bot.command_prefix}server_info
#Sends Guild info in the text channel
@bot.command(name='server_info')
async def server_info(ctx):
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
    await ctx.send(f'<@!{ctx.author.id}> no :)')
    if(ctx.author.voice):
        voice_client = discord.VoiceClient = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if not voice_client:
            await join(ctx,audio=False)    
            voice_client = discord.VoiceClient = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice_client and not voice_client.is_playing():
            player = discord.FFmpegPCMAudio('AudioBin/copypasta01.mp3') #Plays this audio clip at half volume upon command
            voice_client.play(player,after=None)
            voice_client.source = discord.PCMVolumeTransformer(player,volume=0.5)
            
            
#Internal use role manager function
async def _role_manager(ctx, member, role, add):
    if add:
        await member.add_roles(role, reason=f'{ctx.author} added role: {role.name} to {member.name}')
        await ctx.send(f'{role.name} added to {member.name}')
    else:
        await member.remove_roles(role, reason=f'{ctx.author} removed the role: {role.name} from {member.name}')
        await ctx.send(f'{role.name} removed from {member.name}')
        
        
#=========================================================
#       VOICE CHANNEL COMMANDS
#=========================================================        
        
#{bot.command_prefix}join
#Bot joins the voice channel of the command author
#Static command, no customization
@bot.command(name='join',help=f'Calls the bot into voice chat')
async def join(ctx,audio=True):
    try:
        if ctx.author.voice == None:
            await ctx.send(f'Join a voice channel before inviting me.')
            return
        channel = ctx.author.voice.channel
        voice_client = await channel.connect()
        if audio:
            player = discord.FFmpegPCMAudio('AudioBin/HelloThere.mp3')
            voice_client.play(player,after=None)
            voice_client.source = discord.PCMVolumeTransformer(player,volume=2.0)
        await ctx.send(f'Joining voice channel {ctx.author.voice.channel}')
    except:
        await ctx.send(f'Unable to join {ctx.author.voice.channel} (Bot already in another channel or other error)')
    
    
#{bot.command_prefix}leave
#Bot leaves the voice channel of the command author, if it was in one.
#Static command, no customization
@bot.command(name='leave',help=f'Asks {bot.user} to leave voice chat')
async def leave(ctx):
    global yt_guilds
    if not ctx.author.voice:
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
    args = _find_yt_url(args)
    await _yt(ctx, args)


#{bot.command_prefix}stop
#Stops any audio being played by the bot
@bot.command(name='stop', help = f'Asks the bot to stop its current audio playback.')
async def stop(ctx):
    global song_queues
    if not ctx.author.voice:
        await ctx.send(f'You must be in a voice channel to do that!')
        return
    voice_client = discord.VoiceClient = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_connected() and voice_client.is_playing():
        voice_client.stop()
        for s in song_queues:
            if s.get_guild() == ctx.guild.id:
                s.reset_queue()
                break
        await ctx.send(f'Youtube audio stopped, play queue cleared.')


#{bot.command_prefix}pause
#Pauses any audio being played by the bot
@bot.command(name='pause', help = f'Asks {bot.user} to pause its current audio playback.')
async def pause(ctx):
    if not ctx.author.voice:
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
    if not ctx.author.voice:
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
    args = _find_yt_url(args)
    await _queue(ctx, args)
    
    
#{bot.command_prefix}add
#calls {bot.command_prefix}queue (command alias)
@bot.command(name='add', help = f'Alias for {bot.command_prefix}queue')
async def add(ctx, *, args):
    args = _find_yt_url(args)
    await _queue(ctx, args)
    
            
#{bot.command_prefix}skip
#Stops playback then skips to the next song
@bot.command(name= 'skip',help = f'Skips to the next song in the play queue')
async def skip(ctx):
    if not ctx.author.voice:
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
    for s in song_queues:
        if s.get_guild()==ctx.guild.id:
            try:
                s.reset_queue()
                await ctx.send(f'Play queue cleared!')
                _reset_guild_playback(ctx)
            except:
                print(f'Error in clearing play queue from ctx.guild.id')
            #clean_server_audio_cache(ctx)
            break


#{bot.command_prefix}play
#Joins VC with the user if not already in a channel with them
#Plays the first audio file in the queue
#Calls _next_player() for all subsequent plays
@bot.command(name='play',help=f'Plays the songs in the queue from the start or where the bot left off.')
async def play(ctx, *, args=None):
    global song_queues
    if not ctx.author.voice:
        await ctx.send(f'You must be in a voice channel to do that!')
        return
    if args:
        args = _find_yt_url(args)
        await _yt(ctx, args)
        return     
    voice_client = discord.VoiceClient = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_client:
        await join(ctx,audio=False)
        voice_client = discord.VoiceClient = discord.utils.get(bot.voice_clients, guild=ctx.guild)   
    if voice_client.is_playing():
        voice_client.stop()
    for s in song_queues:
        if s.get_guild() == ctx.guild.id:
            if s.get_queue_length() > 0:
                _set_guild_playback(ctx)
                if not os.path.exists(f'YTCache/{s.get_song_id()}.mp3'):
                    with youtube_dl.YoutubeDL(opts) as ydl: 
                            ydl.extract_info(s.get_song(), download=True) #Extract Info must be used here, otherwise the download fails
                player = discord.FFmpegPCMAudio(f'YTCache/{s.get_song_id()}.mp3')
                await ctx.send(f'Now playing queued songs:\n{s.get_queue_items()}')
                s.next_song()
                voice_client.play(player, after= lambda e: _next_player(ctx,voice_client))
                voice_client.source = discord.PCMVolumeTransformer(player,volume=0.5)
            else:
                await ctx.send(f'Play queue is empty! Request with {bot.command_prefix}queue [URL]')
            break


#Internal use next-player function
#Used to play the next song in the queue
def _next_player(ctx, voice_client):
    for s in song_queues:
        if s.get_guild() == ctx.guild.id:
            if s.get_queue_length() > 0:
                if not os.path.exists(f'YTCache/{s.get_song_id()}.mp3'):
                    with youtube_dl.YoutubeDL(opts) as ydl: 
                        ydl.extract_info(s.get_song(), download=True) #Extract Info must be used here, otherwise the download fails
                player = discord.FFmpegPCMAudio(f'YTCache/{s.get_song_id()}.mp3')
                s.next_song()
                voice_client.play(player, after= lambda e: _next_player(ctx,voice_client))
                voice_client.source = discord.PCMVolumeTransformer(player,volume=0.5)
                return None
            else:
                _reset_guild_playback(ctx)
                return None
    return None
    
    
#       Internal YouTube Playback Functions
    
#Internal YT playback function
async def _yt(ctx, args):
    if not ctx.author.voice:
        await ctx.send(f'You must be in a voice channel to do that!')
        return
    voice_client = discord.VoiceClient = discord.utils.get(bot.voice_clients, guild=ctx.guild) #VOICE CLIENT JOINING
    if not voice_client:
        await join(ctx,audio=False)
        voice_client = discord.VoiceClient = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    with youtube_dl.YoutubeDL(opts) as ydl:                     #YTDL PLAYBACK
        try:                                                    #Get info for the video
            vid_info = ydl.extract_info(args, download=False)
            vid_id = vid_info.get("id", None)
            vid_name = vid_info.get("title",None)
        except:                                                 #If video does not exist, notify.
            await ctx.send(f'{ctx.author} Please supply a valid youtube URL!')
            return
        if vid_info.get('duration',None) > 3660:               #If video is too long, notify.
            await ctx.send(f'{vid_info.get("name",None)} is too long! Max media duration: 1 Hour')
            return
    if not os.path.exists(f'YTCache/{vid_info.get("id",None)}.mp3'):
        ydl.extract_info(args, download=True) #Extract Info must be used here, otherwise the download fails  

    if voice_client.is_connected() and not voice_client.is_playing() and ctx.author.voice.channel == voice_client.channel:
        player = discord.FFmpegPCMAudio(f'YTCache/{vid_id}.mp3')
        _set_guild_playback(ctx)
        voice_client.play(player, after= lambda e: _next_player(ctx, voice_client))
        voice_client.source = discord.PCMVolumeTransformer(player,volume=0.5)
        await ctx.send(f'Now playing: {vid_name}')     
    elif voice_client.is_playing():
        await ctx.send(f'Currently playing audio. Wait for it to end or use {bot.command_prefix}stop before requesting.')
    else:
        await ctx.send('Error in connecting to audio.')
    
    
#Internal use queue function
async def _queue(ctx, args):
    global song_queues
    with youtube_dl.YoutubeDL(opts) as ydl: 
        try:
            vid_info = ydl.extract_info(args, download=False)
            if vid_info.get('duration',None) > 3660:
                await ctx.send(f'{vid_info.get("name",None)} is too long! Max media duration: 1 Hour')
                return
            if not os.path.exists(f'YTCache/{vid_info.get("id",None)}.mp3'):
                ydl.extract_info(args, download=True) #Extract Info must be used here, otherwise the download fails
            for s in song_queues:
                if s.get_guild() == ctx.guild.id:
                    s.add_queue(args, vid_info.get("id", None), vid_info.get("title", None))
                    await ctx.send(f'{vid_info.get("title",None)} added to your play queue in position {s.get_queue_length()}')
                    break
        except:
            await ctx.send(f'Please supply a valid youtube URL!')
            
            
#Internal use URL finder
def _find_yt_url(args):
    if 'youtube.com/' not in args and 'youtu.be/' not in args:
        search_result = YoutubeSearch(args,max_results=1).to_dict() #adds delay but it's safer this way
        args = 'https://youtu.be/'+(search_result[0].get("id", None))   #better strategy in progress... but I'm not smart.
    args = args.replace('app=desktop&','')  #URL pattern santitization
    args = args.split('&', 1)[0]            #Know other URL patterns? Tell me on Discord @_Brad#7436!
    return args
    
    
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
        #clean_up_audio()
        await bot.close()
    else:
        await ctx.send(f'Wrong password! {bot.user} will not shut down.')
        print(f'{ctx.author} attempted to shutdown {bot.user} but provided incorrect password: {args}')


#{bot.command_prefix}announce [PASSCODE] "[MESSAGE]"
#Bot shuts down if the correct OTP is given
#Incorrect attempts will be ignored, the bot will continue to function.
#Static command, no customization
@bot.command(name='announce', help=f'Asks the bot to announce in all applicable channels with the provided message')
async def announce(ctx, args, message):
    global terminateCode
    if args == terminateCode:
        await ctx.send(f'{bot.user} is announcing {message}')
        print(f'{bot.user} announced {message} from {ctx.author} with code {args}\n')
        for g in bot.guilds:
                    for c in g.channels:
                        if c.name.startswith('bot') or c.name == 'basicbot':
                            await c.send(f'{bot.user} announcement from {ctx.author.name}: {message}')
                            break
    else:
        await ctx.send(f'Wrong password! {bot.user} will not send your announcement.')
        print(f'{ctx.author} attempted to send an announcement through {bot.user} but provided incorrect password: {args}')


#ON COMMAND ERROR
#Any errors with commands will direct the user to the Help command
#Generic command error message is sent to user, terminal gets details
@bot.event
async def on_command_error(ctx, error):
    if not isinstance(error, discord.ext.commands.CheckFailure):
        await ctx.send(f'Invalid command, use {bot.command_prefix}help for a list of commands. Make sure to supply an argument for commands such as {bot.command_prefix}yt [URL]')
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
        if before.channel != after.channel:
            for vc in bot.voice_clients:
                if vc.is_connected():
                    if vc.channel == before.channel:
                        player = discord.FFmpegPCMAudio('AudioBin/LeaveSound.mp3')
                        if len(vc.channel.members) == 1:
                            await vc.disconnect()
                            continue
                        if vc.guild.id not in yt_guilds:
                            if vc.is_playing():
                                vc.stop()
                            vc.play(player, after=None)
                            vc.source = discord.PCMVolumeTransformer(player, volume=1.0)
                    elif vc.channel == after.channel:
                        player = discord.FFmpegPCMAudio('AudioBin/JoinSound.mp3')
                        if vc.guild.id not in yt_guilds:
                            if vc.is_playing():
                                vc.stop()
                            vc.play(player, after=None)
                            vc.source = discord.PCMVolumeTransformer(player, volume=1.0)


#Cleans up the merged audio queues
#Only occurs on shutdown/restart (for now)
def clean_up_audio():
    try:
        for guild in bot.guilds:
            for f in os.listdir(f'YTCache/'):
                if not f.endswith(".mp3"):
                    continue
                os.remove(os.path.join('YTCache/', f))
    except:
        print(f'Cache deletion error')
          
           
try:
    bot.run(TOKEN)
except:
    print("Error running your bot. Check BOT_TOKEN in .env")
finally:
    print("Thank you for using BasicBot_PY.\n")
