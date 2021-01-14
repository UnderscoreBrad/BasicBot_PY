#BasicBot_Main.py

import os
import discord
from discord.ext.commands import Bot
import random
import string
import sys

intents = discord.Intents.default()
intents.members = True
bot = Bot(command_prefix='!basic_', intents=intents)
TOKEN = None
OWNER_ID = None
OWNER_DM = None
try:
    fp = open('config.txt')
    TOKEN = fp.readline()
    TOKEN = TOKEN.replace('BOT_TOKEN:','')
    OWNER_ID = fp.readline()
    OWNER_ID = OWNER_ID.replace('OWNER_ID:','')
    OWNER_DM = fp.readline()
    OWNER_DM = OWNER_DM.replace('OWNER_DM:','')
    print(f'config.txt lists bot token as {TOKEN}')
    OWNER_ID = int(OWNER_ID)
    OWNER_DM = int(OWNER_DM)
except:
    print('Bot token not properly read! Make sure your config.txt is properly formatted!')
finally:
    fp.close()
    
terminateCode = '!basicbot_terminate '+''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

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
    
@bot.event
async def on_reaction_add(reaction, user):
    if reaction.message.channel.id == OWNER_DM:
        if reaction.message.author.name == bot.user.name and user.id == OWNER_ID:
            await reaction.message.channel.send(f'{bot.user} is shutting down!')
            print(f'{bot.user} shut down via owner DM reaction')
            await bot.close()

#@bot.command
#async def help(ctx, 
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith(f'!basic'):
        if message.content == '!basic_help':
            response = '{bot.user} has the following commands: !basic_help, !basic_about, !basic_join, !basic_leave'
            print(f'{message.author} asked {bot.user} for commands help using !basic_help')
            await message.channel.send(response)
        elif message.content == '!basic_about':
            response = ('Basic Bot PY is an open-source, Python-based Discord bot with basic functionality inlcuding role management, nickname management, Teamspeak-style VC join messages, and keyword-based censorship options! More features are planned. The source code can be found at https://github.com/UnderscoreBrad/BasicBot_PY and the bot is hosted with locally for now.')
            print(f'{message.author} asked {bot.user} for the bot details using !basic_about')
            await message.channel.send(response)
        elif message.content == '!basic_join':
            channel = message.author.voice.channel
            response = f'Joining voice channel {message.author.voice.channel}'
            print(f'{message.author} asked {bot.user} to join {message.author.voice.channel}')
            await channel.connect()
            await message.channel.send(response)
        elif message.content == '!basic_leave':
            response = f'Leaving voice channel {message.author.voice.channel}'
            print(f'{message.author} asked {bot.user} to leave {message.author.voice.channel}')
            vcID = message.guild.voice_client
            await vcID.disconnect()
            await message.channel.send(response)
        elif message.content == terminateCode:
            await message.channel.send(f'{bot.user} is shutting down!')
            await bot.close()

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























