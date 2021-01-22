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

#Globals setup
load_dotenv()
intents = discord.Intents.default()
intents.members = True
bot = Bot(command_prefix='!basic', intents=intents)
bot.remove_command('help') #To override the standard Help
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
OWNER_ID = int(os.getenv('OWNER_ID'))
OWNER_DM = int(os.getenv('OWNER_DM'))
KEYWORDS_RH = None
ABOUT = None
FORCE_DELETE = None
song_queues = []
yt_guilds = []


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
    with open('forced-delete-ids.txt') as gcensor:
        FORCE_DELETE = [int(ln.strip()) for ln in gcensor]
except:
    print('Could not read from forced-delete-ids.txt')

    
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
        'format': 'bestaudio/good',
        'outtmpl': f'YTCache/%(id)s.mp3',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
        }],
    }

#Generate a unique termination code for this session
terminateCode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

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
    msg = await bot.get_user(OWNER_ID).dm_channel.send(f'{bot.user} is online. Terminate with OTP: {terminateCode} or react to this message.')
    await msg.add_reaction('\U0001F6D1')
    await msg.add_reaction('\U0001F504')
    
    
#ON GUILD JOIN
#Creates a song queue for that guild, so the bot doesnt need a restart    
@bot.event
async def on_guild_join(ctx):
    global song_queues
    song_queues.append(sq.SongQueue(guild.id))
    print(f'{bot.user} joined server: {guild.name} ID: {guild.id}')
    
    
#ON DM REACTION:
#If the message reacted to is in owner DMs:
#Bot must be message sender, owner reacted to DM, reacted with STOP_SIGN
#Bot is gracefully terminated
@bot.event
async def on_reaction_add(reaction, user):
    if reaction.message.channel.id == OWNER_DM:
        if reaction.message.author.name == bot.user.name and user.id == OWNER_ID:
            if reaction.emoji == '\U0001F6D1':
                await reaction.message.channel.send(f'{bot.user} is shutting down!')
                for vc in bot.voice_clients:
                    await vc.disconnect()
                print(f'{bot.user} shut down via owner DM reaction\n')
                clean_up_audio()
                await bot.close()
            elif reaction.emoji == '\U0001F504':
                await reaction.message.channel.send(f'{bot.user} is restarting!')
                for vc in bot.voice_clients:
                    await vc.disconnect()
                print(f'{bot.user} restarted via owner DM reaction\n')
                clean_up_audio()
                await bot.close()
                os.execl(sys.executable, sys.executable, *sys.argv)


#!basic_help:
#Responds with list of available commands and their functions.
#Effectively overrides the built-in Help command (formatting is better)
@bot.command(name = '_help',help = f'A list of commands and functions for {bot.user}', category='General')
async def _help(ctx):
    response = (f'**{bot.user} has the following commands:**\n \
    **General Commands:**\n \
    !basic_about: Information about the bot\n \
    !basic_help: List of bot commands\n \
    !basic_pingme: Sends you a test ping\n \
    **Voice Channel Commands:**\n \
    !basic_join: Have the bot join your current voice channel\n \
    !basic_leave: Have the bot leave your current voice channel\n \
    **Youtube Audio Commands**\n \
    !basic_yt [YouTube URL]: Have the bot play the video at the provided URL immediately\n \
    !basic_queue [YouTube URL]: Add the Youtube video to the audio queue\n \
    !basic_play: Play songs from the first in the queue\n \
    !basic_pause: Have the bot pause audio playback\n \
    !basic_resume: Have the bot resume audio playback after pausing\n \
    !basic_skip: Skip to the next song in the play queue\n \
    !basic_stop: Have the bot stop audio playback\n \
    !basic_clearqueue: Clear the media queue')
    await ctx.send(response)


#!basic_about
#Responds with info about the bot
#Message customizable in about.txt
@bot.command(name = '_about', help = f'Information about {bot.user}')
async def _about(ctx):
    global ABOUT
    response = (f'About {bot.user}:\n' + ABOUT)
    await ctx.send(response)
    
    
#!basic_join
#Bot joins the voice channel of the command author
#Static command, no customization
@bot.command(name='_join',help=f'Calls the bot into voice chat')
async def _join(ctx,audio=True):
    try:
        if ctx.author.voice == None:
            await ctx.send(f'Join a voice channel before inviting me.')
            return
        channel = ctx.author.voice.channel
        response = f'Joining voice channel {ctx.author.voice.channel}'
        voice_client = await channel.connect()
        if audio:
            player = discord.FFmpegPCMAudio('AudioBin/HelloThere.mp3')
            player.volume = 1.3
            voice_client.play(player,after=None)
        await ctx.send(response)
    except:
        response = f'Unable to join {ctx.author.voice.channel} (Bot already in another channel or other error)'
        await ctx.send(response)
    
    
#!basic_leave
#Bot leaves the voice channel of the command author, if it was in one.
#Static command, no customization
@bot.command(name='_leave',help=f'Asks {bot.user} to leave voice chat')
async def _leave(ctx):
    if not ctx.author.voice:
        await ctx.send(f'You must be in a voice channel to do that!')
        return
    response = f'Leaving voice channel {ctx.author.voice.channel}'
    vcID = ctx.guild.voice_client
    await vcID.disconnect()
    await ctx.send(response)


#!basic_pingme
#Pings the user, for testing.
@bot.command(name='_pingme', help = f'Sends the user a test ping')
async def _pingme(ctx):
    response = f'<@!{ctx.author.id}> here is your test ping'
    await ctx.send(response)
    
    
#!basic_yt
#Uses Youtube-DL to download an MP3 of the selected video
#Plays that audio file via FFmpeg PCM
#Cuts off any currently playing audio.
#Audio queue planned
@bot.command(name='_yt', help = f'Plays the youtube audio through the bot. Video blacklist planned.')
async def _yt(ctx, args):
    if not ctx.author.voice:
        await ctx.send(f'You must be in a voice channel to do that!')
        return
    args = args.replace('app=desktop&','')
    args = args.split('&', 1)[0]
    
    #VOICE CLIENT JOINING
    voice_client = None
    for vc in bot.voice_clients:
        if vc.channel == ctx.author.voice.channel:
            voice_client = vc
            break
    if not voice_client:
        await _join(ctx,audio=False)
        for vc in bot.voice_clients:
            if vc.channel == ctx.author.voice.channel:
                voice_client = vc
                break

    #YTDL PLAYBACK
    with youtube_dl.YoutubeDL(opts) as ydl: 
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

    if voice_client.is_connected() and not voice_client.is_playing() and ctx.author.voice.channel == voice_client.channel :
        player = discord.FFmpegPCMAudio(f'YTCache/{vid_id}.mp3')
        set_guild_playback(ctx)
        voice_client.play(player, after= lambda e: reset_guild_playback(ctx))
        await ctx.send(f'Now playing: {vid_name}')     
    elif voice_client.is_playing():
        await ctx.send('Currently playing audio. Wait for it to end or use !basic_stop before requesting.')
    else:
        await ctx.send('Error in playing audio. Use !basic_join before requesting a song, and make sure you are in the voice chat.')



#!basic_stop
#Stops any audio being played by the bot
@bot.command(name='_stop', help = f'Asks the bot to stop its current audio playback.')
async def _stop(ctx):
    global song_queues
    if not ctx.author.voice:
        await ctx.send(f'You must be in a voice channel to do that!')
        return
    voice_client = None
    for vc in bot.voice_clients:
        if vc.channel == ctx.author.voice.channel:
            voice_client = vc
            break
    if voice_client and voice_client.is_connected() and voice_client.is_playing():
        voice_client.stop()
        for s in song_queues:
            if s.get_guild() == ctx.guild.id:
                s.reset_queue()
                break
        await ctx.send(f'Youtube audio stopped, play queue cleared.')


#!basic_pause
#Pauses any audio being played by the bot
@bot.command(name='_pause', help = f'Asks {bot.user} to pause its current audio playback.')
async def _pause(ctx):
    if not ctx.author.voice:
        await ctx.send(f'You must be in a voice channel to do that!')
        return
    voice_client = None
    for vc in bot.voice_clients:
        if vc.channel == ctx.author.voice.channel:
            voice_client = vc
            break
    if voice_client and voice_client.is_connected() and voice_client.is_playing():
        voice_client.pause()
        await ctx.send(f'Youtube audio paused.')
        


#!basic_resume
#Resumes any audio being played by the bot
@bot.command(name='_resume',help = f'Asks {bot.user} to resume paused audio payback.')
async def _resume(ctx):
    if not ctx.author.voice:
        await ctx.send(f'You must be in a voice channel to do that!')
        return
    voice_client = None
    for vc in bot.voice_clients:
        if vc.channel == ctx.author.voice.channel:
            voice_client = vc
            break
    if voice_client and voice_client.is_connected() and voice_client.is_paused():
        voice_client.resume()
        await ctx.send(f'Resuming youtube audio playback.')


#!basic_queue
#adds the song given as url to the queue
@bot.command(name='_queue',help = f'Adds the song at the URL to the play queue for the server')
async def _queue(ctx, args):
    global song_queues
    args = args.replace('app=desktop&','')
    args = args.split('&', 1)[0]
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
    
            
#!basic_skip
#Stops playback then skips to the next song
@bot.command(name= '_skip',help = f'Skips to the next song in the play queue')
async def _skip(ctx):
    if not ctx.author.voice:
        await ctx.send(f'You must be in a voice channel to do that!')
        return
    voice_client = None
    for vc in bot.voice_clients:
        if vc.channel == ctx.author.voice.channel:
            voice_client = vc
            break
    if voice_client and voice_client.is_connected() and voice_client.is_playing():
        voice_client.stop()
        await ctx.send(f'Skipping to next audio track.')
    
    
#!basic_clearqueue
#Clears the youtube play queue
@bot.command(name='_clearqueue',help=f'Clears the media queue')
async def _clearqueue(ctx):
    global song_queues
    for s in song_queues:
        if s.get_guild()==ctx.guild.id:
            s.reset_queue()
            await ctx.send(f'Play queue cleared!')
            reset_guild_playback(ctx)
            #clean_server_audio_cache(ctx)
            break


#!basic_play
#Joins VC with the user if not already in a channel with them
#Plays the first audio file in the queue
#Calls next_player() for all subsequent plays
@bot.command(name='_play',help=f'Plays the songs in the queue from the start or where the bot left off.')
async def _play(ctx):
    global song_queues
    if not ctx.author.voice:
        await ctx.send(f'You must be in a voice channel to do that!')
        return
    voice_client = None
    for vc in bot.voice_clients:
        if vc.channel == ctx.author.voice.channel:
            voice_client = vc
            break
    if not voice_client:
        await _join(ctx,audio=False)
        if(ctx.author.voice):
            for vc in bot.voice_clients:
                if vc.channel == ctx.author.voice.channel:
                    voice_client = vc
                    break
    if voice_client.is_playing():
        voice_client.stop()
    for s in song_queues:
        if s.get_guild() == ctx.guild.id:
            if s.get_queue_length() > 0:
                set_guild_playback(ctx)
                try:
                    player = discord.FFmpegPCMAudio(f'YTCache/{s.get_song_id()}.mp3')
                except:
                    with youtube_dl.YoutubeDL(opts) as ydl: 
                        ydl.download(s.get_queue())
                    player = discord.FFmpegPCMAudio(f'YTCache/{s.get_song_id()}.mp3')
                await ctx.send(f'Now playing queued songs:\n{s.get_queue_items()}')
                s.next_song()
                voice_client.play(player, after= lambda e: next_player(ctx,voice_client))
            else:
                await ctx.send(f'Play queue is empty! Request with !basic_queue [URL]')
            break


#CHILD OF !basic_play
#Used to play the next song in the queue
def next_player(ctx, voice_client):
    for s in song_queues:
        if s.get_guild() == ctx.guild.id:
            if s.get_queue_length() > 0:
                try:
                    player = discord.FFmpegPCMAudio(f'YTCache/{s.get_song_id()}.mp3')
                except:
                    with youtube_dl.YoutubeDL(ydl_opts) as ydl: 
                        ydl.download(s.get_queue())
                    player = discord.FFmpegPCMAudio(f'YTCache/{s.get_song_id()}.mp3')
                s.next_song()
                voice_client.play(player, after= lambda e: next_player(ctx,voice_client))
                return None
            else:
                #clean_server_audio_cache(ctx)
                reset_guild_playback(ctx)
                return None
    return None
    
    
#Removes the guild from the list of guilds playing songs    
def reset_guild_playback(ctx):
    global yt_guilds
    yt_guilds.remove(ctx.guild.id)
    return None
    
#Adds the guild to the list of guilds playing songs
def set_guild_playback(ctx):
    global yt_guilds
    yt_guilds.append(ctx.guild.id)
    return None

    
#!basic_go_to_hell
#A suggestion from a user
@bot.command(name='_go_to_hell')
async def _go_to_hell(ctx):
    voice_client = None
    await ctx.send(f'<@!{ctx.author.id}> no :)')
    if(ctx.author.voice):
        for vc in bot.voice_clients:
            if vc.channel == ctx.author.voice.channel:
                voice_client = vc
        if voice_client and not voice_client.is_playing():
            player = discord.FFmpegPCMAudio('AudioBin/copypasta01.mp3')
            voice_client.play(player,after=None)
    
#!basicbot_terminate [PASSCODE]
#Bot shuts down if the correct OTP is given
#Incorrect attempts will be ignored, the bot will continue to function.
#Static command, no customization
@bot.command(name='bot_terminate', help=f'Asks the bot to terminate, requires 16-character OTP')
async def bot_terminate(ctx, args):
    global terminateCode
    if args == terminateCode:
        await ctx.send(f'{bot.user} is shutting down!')
        print(f'{bot.user} shut down by {ctx.author} with code {args}\n')
        for vc in bot.voice_clients:
            await vc.disconnect()
        clean_up_audio()
        await bot.close()
    else:
        await ctx.send(f'Wrong password! {bot.user} will not shut down.')
        print(f'{ctx.author} attempted to shutdown {bot.user} but provided incorrect password: {args}')


#ON MESSAGE:
#Bot checks which channel the message is in, force-deleting message in specific channels
#Attempts to command-check
#If not a command, but starts with !basic
@bot.event
async def on_message(message):
    processed = False
    #ch_bool = False
    if message.channel.id in FORCE_DELETE:
        await message.delete()
        return
    try:
        ch_bool = message.channel.name.startswith('bot') or message.channel.name.startswith('basic')
    except:    
        ch_bool = message.guild == None
    try:
        if ch_bool:
            await bot.process_commands(message)
    except:
        processed = True
        await censor_check(message, ch_bool)
    if not processed:
        await censor_check(message, ch_bool)
            
#Child of ON MESSAGE
#Automatically censors keywords in global-censor-RH.txt
async def censor_check(message, ch_bool):
    global OWNER_ID
    global KEYWORDS_RH
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
            print(f'Deleted message "{message.id}" from {message.author} in {message.channel.id}')
        except:
            print(f'Failed to delete message {message.id} from {message.author} in {message.channel.id}.')
    elif message.content.lower().startswith('noot'):
        await noot(message, ch_bool) 

#Child of ON MESSAGE
#replies with noot-noot if nothing's already playing.
async def noot(message, ch_bool):
    voice_client = None
    if(message.author.voice and ch_bool):
        for vc in bot.voice_clients:
            if vc.channel == message.author.voice.channel:
                voice_client = vc
        if voice_client and not voice_client.is_playing():
            player = discord.FFmpegPCMAudio('AudioBin/NootSound.mp3')
            voice_client.play(player,after=None)


#ON COMMAND ERROR
#Any errors with commands will direct the user to the Help command
@bot.event
async def on_command_error(ctx, error):
    if not isinstance(error, discord.ext.commands.CheckFailure):
        await ctx.send(f'Invalid command, use !basic_help for a list of commands. Make sure to supply an argument for commands such as !basic_yt [URL]')
        print(f'Command Error from {ctx.author} in {ctx.channel.id}: {error}\nMessage ID: {ctx.message.id}\nMessage content: {ctx.message.content}') 


#ON VOICE STATE UPDATE:
#If the bot is in a voice chat, compare that voice chat to the join or leave
#If the voice client the user left is the same as the bot is in, play LeaveSound.mp3
#If the voice client the user joined is the same as the bot is in, play JoinSound.mp3
#Simulates the Teamspeak Experience (TM)
@bot.event
async def on_voice_state_update(member, before, after):
    global yt_guilds
    if bot.voice_clients:
        if before.channel != after.channel:
            for vc in bot.voice_clients:
                if vc.is_connected():
                    if vc.guild.id not in yt_guilds:
                        if vc.is_playing():
                            vc.stop()
                        if vc.channel == before.channel:
                            player = discord.FFmpegPCMAudio('AudioBin/LeaveSound.mp3')
                            vc.play(player, after=None)
                        elif vc.channel == after.channel:
                            player = discord.FFmpegPCMAudio('AudioBin/JoinSound.mp3')
                            vc.play(player, after=None)


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
        
 
#DEPRECATED CLEANUP FUNCTION:
#The queues are now merged, this doesn't work.    
#def clean_server_audio_cache(ctx):
#    try:
#        for f in os.listdir(f'YTCache/'):
#            if not f.endswith(".mp3"):
#                continue
#            os.remove(os.path.join(f'YTCache/', f))
#    except:
#        print(f'No cache for {ctx.guild.id}')
        
        
        
           
try:
    bot.run(TOKEN)
except:
    print("Error running your bot. Check BOT_TOKEN in .env")
finally:
    print("Thank you for using BasicBot_PY.\n")
    
    
