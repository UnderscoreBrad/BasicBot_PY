#BasicBot_Main.py

import os
import discord
from discord.ext.commands import Bot
import random
import string
import sys
import youtube_dl
import SongQueue as sq
import time

#Globals setup
intents = discord.Intents.default()
intents.members = True
bot = Bot(command_prefix='!basic', intents=intents)
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")
OWNER_DM = os.getenv("OWNER_DM")
KEYWORDS_RH = None
ABOUT = None
FORCE_DELETE = None
song_queues = []


#Read data from config.txt
try:
    cfg = open('config.txt')
    TOKEN = cfg.readline()
    TOKEN = TOKEN.replace('BOT_TOKEN:','').strip()
    OWNER_ID = cfg.readline()
    OWNER_ID = OWNER_ID.replace('OWNER_ID:','').strip()
    OWNER_DM = cfg.readline()
    OWNER_DM = OWNER_DM.replace('OWNER_DM:','').strip()
    OWNER_ID = int(OWNER_ID)
    OWNER_DM = int(OWNER_DM)
except:
    print('Variables not taken from config.txt, trying .env')
finally:
    cfg.close()
    
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
    
#Setup Youtube-DL options
ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'YT-DLBin/%(id)s.mp3',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

#Generate a unique termination code for this session
terminateCode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

#ON READY:
#Bot establishes connection to discord, notifies terminal with the stop code
#Prints out a list of connected servers to terminal (Owner DM planned, low priority)
#Prints owner user, as found in config.txt
#DMs owner with a startup message, reacts to it with the emojis STOP_SIGN and ARROWS_COUNTERCLOCKWISE
@bot.event
async def on_ready():
    global OWNER_ID
    global song_queue
    print(f'{bot.user} is online. Terminate with OTP: {terminateCode}')
    for guild in bot.guilds:
        print(f'{bot.user} joined server: {guild.name} ID: {guild.id}')
        song_queues.append(sq.SongQueue(guild.id))
    print(f'{bot.get_user(OWNER_ID)} detected as Bot Owner. Change in config.txt')
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
                print(f'{bot.user} shut down via owner DM reaction')
                for vc in bot.voice_clients:
                    await vc.disconnect()
                await bot.close()
            elif reaction.emoji == '\U0001F504':
                await reaction.message.channel.send(f'{bot.user} is restarting!')
                print(f'{bot.user} restarted via owner DM reaction\n')
                for vc in bot.voice_clients:
                    await vc.disconnect()
                await bot.close()
                os.execl(sys.executable, sys.executable, *sys.argv)


#!basic_help:
#Responds with list of available commands and their functions.
#Logs to console as well
#Static command, no customization from config.txt
@bot.command(name = '_help',help = f'A list of commands and functions for {bot.user}')
async def _help(ctx):
    response = (f'**{bot.user} has the following commands:**\n!basic_help: List of bot commands\n!basic_about: Information about the bot\n!basic_join: Have the bot join your current voice channel\n!basic_leave: Have the bot leave your current voice channel\n!basic_yt [YouTube URL]: Have the bot play the video at the provided URL\n!basic_stop: Have the bot stop audio playback\n!basic_pause: Have the bot pause audio playback\n!basic_resume: Have the bot resume audio playback after pausing')
    print(f'{ctx.author} asked {bot.user} for commands help using !basic_help')
    await ctx.send(response)


#!basic_about
#Responds with info about the bot
#Logs to console as well
#Message customizable in about.txt
@bot.command(name = '_about', help = f'Information about {bot.user}')
async def _about(ctx):
    global ABOUT
    response = (f'About {bot.user}:\n' + ABOUT)
    print(f'{ctx.author} asked {bot.user} for the bot details using !basic_about')
    await ctx.send(response)
    
    
#!basic_join
#Bot joins the voice channel of the command author
#Logs to console as well
#Static command, no customization from config.txt
@bot.command(name='_join',help=f'Calls the bot into voice chat')
async def _join(ctx):
    try:
        if ctx.author.voice == None:
            await ctx.send(f'Join a voice channel before inviting me.')
            return
        channel = ctx.author.voice.channel
        response = f'Joining voice channel {ctx.author.voice.channel}'
        print(f'{ctx.author} asked {bot.user} to join {ctx.author.voice.channel}')
        await channel.connect()
        await ctx.send(response)
    except:
        response = f'Unable to join {ctx.author.voice.channel} (Bot already in another channel or other error)'
        await ctx.send(response)
    
    
#!basic_leave
#Bot leaves the voice channel of the command author, if it was in one.
#Logs to console as well
#Static command, no customization from config.txt
@bot.command(name='_leave',help=f'Asks {bot.user} to leave voice chat')
async def _leave(ctx):
    if not ctx.author.voice:
        await ctx.send(f'You must be in a voice channel to do that!')
        return
    response = f'Leaving voice channel {ctx.author.voice.channel}'
    print(f'{ctx.author} asked {bot.user} to leave {ctx.author.voice.channel}')
    vcID = ctx.guild.voice_client
    await vcID.disconnect()
    await ctx.send(response)


#!basic_pingme
#Pings the user, for testing.
@bot.command(name='_pingme')
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
    if os.path.exists("YT-DLBin/ytAudio.mp3"):
        os.remove("YT-DLBin/ytAudio.mp3")
        print("Cleaned YT-DLBin")
    else:
        print("No files to be deleted.")
    args = args.split('&', 1)[0]
    voice_client = None
    for vc in bot.voice_clients:
        if vc.channel == ctx.author.voice.channel:
            voice_client = vc
            break
    if voice_client:
        if voice_client.is_connected() and not voice_client.is_playing() and ctx.author.voice.channel == voice_client.channel :
            with youtube_dl.YoutubeDL(ydl_opts) as ydl: 
                try:
                    vid_info = ydl.extract_info(args, download=True)
                    vid_id = vid_info.get("id", None)
                    vid_name = vid_info.get("title",None)
                    player = discord.FFmpegPCMAudio(f'YT-DLBin/{vid_id}.mp3')
                    voice_client.play(player, after=None)
                    await ctx.send(f'Now playing: {vid_name}')
                except:
                    await ctx.send(f'{message.author} Please supply a valid youtube URL!')
        elif voice_client.is_playing():
            await ctx.send('Currently playing audio. Wait for it to end or use !basic_stop before requesting.')
        else:
            await ctx.send('Error in playing audio. Use !basic_join before requesting a song, and make sure you are in the voice chat.')
    else:
        await ctx.send('Error in playing audio. Use !basic_join before requesting a song, and make sure you are in the voice chat.')


#!basic_stop
#Stops any audio being played by the bot
@bot.command(name='_stop', help = f'Asks the bot to stop its current audio playback.')
async def _stop(ctx):
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
        await ctx.send(f'Youtube audio stopped.')


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
    args = args.split('&', 1)[0]
    with youtube_dl.YoutubeDL(ydl_opts) as ydl: 
                try:
                    vid_info = ydl.extract_info(args, download=True)
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
    for s in song_queues:
        if s.get_guild()==ctx.guild.id:
            s.reset_queue()
            await ctx.send(f'Play queue cleared!')
            break

#!basic_play
#calls !basic_yt on the next queue entry
@bot.command(name='_play',help=f'Plays the songs in the queue from the start or where the bot left off.')
async def _play(ctx):
    voice_client = None
    if(ctx.author.voice):
        for vc in bot.voice_clients:
            if vc.channel == ctx.author.voice.channel:
                voice_client = vc
                break
    for s in song_queues:
        if s.get_guild() == ctx.guild.id:
            if s.get_queue_length() > 0:
                player = discord.FFmpegPCMAudio(f'YT-DLBin/{s.get_song_id()}.mp3')
                await ctx.send(f'Now playing queued songs:\n{s.get_queue_items()}')
                s.next_song()
                voice_client.play(player, after= lambda e: next_player(ctx,voice_client))
            break

def next_player(ctx, voice_client):
    for s in song_queues:
        if s.get_guild() == ctx.guild.id:
            #await ctx.send(f'Now Playing: {s.get_song_name()}')
            if s.get_queue_length() > 1:
                player = discord.FFmpegPCMAudio(f'YT-DLBin/{s.get_song_id()}.mp3')
                s.next_song()
                if voice_client.is_playing():
                    voice_client.stop()
                    print('thing1')
                voice_client.play(player, after= lambda e: next_player(ctx,voice_client))
                return None
            elif s.get_queue_length() == 1:
                player = discord.FFmpegPCMAudio(f'YT-DLBin/{s.get_song_id()}.mp3')
                s.next_song()
                if voice_client.is_playing():
                    voice_client.stop()
                    print('thing2')
                voice_client.play(player, after=None)
                #return None
    return None

    
#!basicbot_terminate [PASSCODE]
#Bot shuts down if the correct OTP is given
#Incorrect attempts will be ignored, the bot will continue to function.
#Static command, no customization from config.txt
@bot.command(name='bot_terminate', help=f'Asks the bot to terminate, requires 16-character OTP')
async def bot_terminate(ctx, args):
    global terminateCode
    if args == terminateCode:
        await ctx.send(f'{bot.user} is shutting down!')
        print(f'{bot.user} shut down by {ctx.author} with code {args}')
        for vc in bot.voice_clients:
            await vc.disconnect()
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
    if message.channel.id in FORCE_DELETE:
        await message.delete()
        return
    try:
        await bot.process_commands(message)
    except:
        processed = True
        await censor_check(message)
    if not processed:
        await censor_check(message)
            
#Child of ON MESSAGE
#Automatically censors keywords in global-censor-RH.txt
async def censor_check(message):
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
        await noot(message) 

#Child of ON MESSAGE
#replies with noot-noot if nothing's already playing.
async def noot(message):
    voice_client = None
    if(message.author.voice):
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


#ON VOICE STATE UPDATE:
#If the bot is in a voice chat, compare that voice chat to the join or leave
#If the voice client the user left is the same as the bot is in, play LeaveSound.mp3
#If the voice client the user joined is the same as the bot is in, play JoinSound.mp3
#Simulates the Teamspeak Experience (TM)
@bot.event
async def on_voice_state_update(member, before, after):
    if bot.voice_clients:
        if before.channel != after.channel:
            for vc in bot.voice_clients:
                if vc.is_connected() and not vc.is_playing():
                    if vc.channel == before.channel:
                        print(f'User {member.name} left {vc.channel}')
                        player = discord.FFmpegPCMAudio('AudioBin/LeaveSound.mp3')
                        vc.play(player, after=None)
                    elif vc.channel == after.channel:
                        print(f'User {member.name} joined {vc.channel}')
                        player = discord.FFmpegPCMAudio('AudioBin/JoinSound.mp3')
                        vc.play(player, after=None)
   
try:
    bot.run(TOKEN)
except:
    print("Error running your bot. Check BOT_TOKEN in config.txt")
finally:
    print("Thank you for using BasicBot_PY.")























