#BasicBot_Main.py

import os
import discord
from discord.ext.commands import Bot
import random
import string
import sys

#Globals setup
intents = discord.Intents.default()
intents.members = True
bot = Bot(command_prefix='!basic', intents=intents)
TOKEN = None
OWNER_ID = None
OWNER_DM = None

#Read data from config.txt
try:
    fp = open('config.txt')
    TOKEN = fp.readline()
    TOKEN = TOKEN.replace('BOT_TOKEN:','')
    OWNER_ID = fp.readline()
    OWNER_ID = OWNER_ID.replace('OWNER_ID:','')
    OWNER_DM = fp.readline()
    OWNER_DM = OWNER_DM.replace('OWNER_DM:','')
    OWNER_ID = int(OWNER_ID)
    OWNER_DM = int(OWNER_DM)
except:
    print('Bot token not properly read! Make sure your config.txt is properly formatted!')
finally:
    fp.close()
    
#Generate a unique termination code for this session
terminateCode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

#ON READY:
#Bot establishes connection to discord, notifies terminal with the stop code
#Prints out a list of connected servers to terminal (Owner DM planned, low priority)
#Prints owner user, as found in config.txt
#DMs owner with a startup message, reacts to it with the stop-code emoji STOP_SIGN
@bot.event
async def on_ready():
    global OWNER_ID
    print(f'{bot.user} is online. Terminate with OTP: {terminateCode}')
    for guild in bot.guilds:
        print(f'{bot.user} joined server: {guild.name} ID: {guild.id}')
    print(f'{bot.get_user(OWNER_ID)} detected as Bot Owner. Change in config.txt')
    await bot.get_user(OWNER_ID).create_dm()
    msg = await bot.get_user(OWNER_ID).dm_channel.send(f'{bot.user} is online. Terminate with OTP: {terminateCode} or react to this message.')
    await msg.add_reaction('\U0001F6D1')
    
#ON DM REACTION:
#If the message reacted to is in owner DMs:
#Bot must be message sender, owner reacted to DM, reacted with STOP_SIGN
#Bot is gracefully terminated
@bot.event
async def on_reaction_add(reaction, user):
    if reaction.message.channel.id == OWNER_DM:
        if reaction.message.author.name == bot.user.name and user.id == OWNER_ID and reaction.emoji == '\U0001F6D1':
            await reaction.message.channel.send(f'{bot.user} is shutting down!')
            print(f'{bot.user} shut down via owner DM reaction')
            await bot.close()

#!basic_help:
#Responds with list of available commands and their functions.
#Logs to console as well
#Static command, no customization from config.txt
@bot.command(name = '_help',help = f'A list of commands and functions for {bot.user}')
async def _help(ctx):
    response = (f'{bot.user} has the following commands: !basic_help, !basic_about, !basic_join, !basic_leave')
    print(f'{ctx.author} asked {bot.user} for commands help using !basic_help')
    await ctx.send(response)

#!basic_about
#Responds with info about the bot
#Logs to console as well
#Static command, no customization from config.txt
@bot.command(name = '_about', help = f'Information about {bot.user}')
async def _about(ctx):
    response = (f'{bot.user} is an open-source, Python-based Discord bot with basic functionality inlcuding role management, nickname management, Teamspeak-style VC join messages, and keyword-based censorship options! More features are planned. The source code can be found at https://github.com/UnderscoreBrad/BasicBot_PY and the bot is hosted with locally for now.')
    print(f'{ctx.author} asked {bot.user} for the bot details using !basic_about')
    await ctx.send(response)
    
#!basic_join
#Bot joins the voice channel of the command author
#Logs to console as well
#Static command, no customization from config.txt
@bot.command(name='_join',help=f'Calls {bot.user} into voice chat')
async def _join(ctx):
    channel = ctx.author.voice.channel
    response = f'Joining voice channel {ctx.author.voice.channel}'
    print(f'{ctx.author} asked {bot.user} to join {ctx.author.voice.channel}')
    await channel.connect()
    await ctx.send(response)
    
#!basic_leave
#Bot leaves the voice channel of the command author, if it was in one.
#Logs to console as well
#Static command, no customization from config.txt
@bot.command(name='_leave',help=f'Asks {bot.user} to leave voice chat')
async def _leave(ctx):
    response = f'Leaving voice channel {ctx.author.voice.channel}'
    print(f'{ctx.author} asked {bot.user} to leave {ctx.author.voice.channel}')
    vcID = ctx.guild.voice_client
    await vcID.disconnect()
    await ctx.send(response)

#!basicbot_terminate [PASSCODE]
#Bot shuts down if the correct OTP is given
#Incorrect attempts will be ignored, the bot will continue to function.

@bot.command(name='bot_terminate', help=f'Asks {bot.user} to terminate, requires 16-character OTP')
async def bot_terminate(ctx, args):
    global terminateCode
    if args == terminateCode:
        await ctx.send(f'{bot.user} is shutting down!')
        print(f'{bot.user} shut down by {ctx.author} with code {args}')
        await bot.close()
    else:
        await ctx.send(f'Wrong password! {bot.user} will not shut down.')
        print(f'{ctx.author} attempted to shutdown {bot.user} but provided incorrect password: {args}')


#ON VOICE STATE UPDATE:
#If the bot is in a voice chat, compare that voice chat to the join or leave
#If the voice client the user left is the same as the bot is in, play LeaveSound.mp3
#If the voice client the user joined is the same as the bot is in, play JoinSound.mp3
#Simulates the Teamspeak Experience (TM)
#
#CURRENT ISSUE: ONLY WORKS FOR ONE VOICE CLIENT
#CURRENT ISSUE: REQUIRES BOT RESTART FOR NEW SERVERS
@bot.event
async def on_voice_state_update(member, before, after):
    print("Voice_update")
    voice_client: discord.VoiceClient = discord.utils.get(bot.voice_clients)
    if voice_client != None and voice_client.is_connected():
        channel = voice_client.channel
        if before.channel == channel and after.channel != channel:
            print(f'User {member.name} left {channel}')
            player = discord.FFmpegPCMAudio('AudioBin/LeaveSound.mp3')
            voice_client.play(player, after=None)
        elif before.channel != channel and after.channel == channel:
            print(f'User {member.name} joined {channel}')
            player = discord.FFmpegPCMAudio('AudioBin/JoinSound.mp3')
            voice_client.play(player, after=None)
   
try:
    bot.run(TOKEN)
except:
    print("Error running your bot. Check BOT_TOKEN in config.txt")
finally:
    print("Thank you for using BasicBot_PY.")























