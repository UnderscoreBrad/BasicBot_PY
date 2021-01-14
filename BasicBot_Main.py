#BasicBot_Main.py

import os
import discord
from discord.ext.commands import Bot
import random
import string
import sys

intents = discord.Intents.default()
intents.members = True
bot = Bot(command_prefix='!', intents=intents)
OWNER_ID = None
TOKEN = None
try:
    fp = open('config.txt')
    TOKEN = fp.readline()
    TOKEN = TOKEN.replace('BOT_TOKEN:','')
    OWNER_ID = fp.readline()
    OWNER_ID = OWNER_ID.replace('OWNER_ID:','')
    print(f'config.txt lists bot token as {TOKEN}')
    print(f'config.txt lists UID as {OWNER_ID}')
    OWNER_ID = int(OWNER_ID)
except:
    print('Bot token not properly read! Edit your config.txt!')
finally:
    fp.close()
    print('Starting BasicBot.')
    
terminateCode = '!basicbot_terminate '+''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

@bot.event
async def on_ready():
    global OWNER_ID
    for guild in bot.guilds:
        print(f'BasicBot_PY joined server: {guild.name} ID: {guild.id}')
    print(f'{bot.user} is online. Terminate with OTP: {terminateCode}')
    print(f'{bot.get_user(OWNER_ID)} detected as Bot Owner. Change in BasicBot_Main.py')
    await bot.get_user(OWNER_ID).create_dm()
    await bot.get_user(OWNER_ID).dm_channel.send(f'{bot.user} is online. Terminate with OTP: {terminateCode}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith(f'!basic'):
        if message.content == '!basic_help':
            response = 'Basic Bot PY has the following commands: !basic_help, !basic_about, !basic_joinVC'
            print(f'{message.author} asked {bot.user} for commands help using !basic_help')
            await message.channel.send(response)
        elif message.content == '!basic_about':
            response = ('Basic Bot PY is an open-source, Python-based Discord bot with basic functionality inlcuding role management, nickname management, Teamspeak-style VC join messages, and keyword-based censorship options! More features are planned. The source code can be found at https://github.com/UnderscoreBrad/BasicBot_PY and the bot is hosted with locally for now.')
            print(f'{message.author} asked {bot.user} for the bot details using !basic_about')
            await message.channel.send(response)
        elif message.content == '!basic_joinVC':
            channel = message.author.voice.channel
            response = f'Joining voice channel {message.author.voice.channel}'
            print(f'{message.author} asked {bot.user} to join {message.author.voice.channel}')
            await channel.connect()
            await message.channel.send(response)
        elif message.content == '!basic_leaveVC':
            response = f'Leaving voice channel {message.author.voice.channel}'
            print(f'{message.author} asked {bot.user} to leave {message.author.voice.channel}')
            vcID = message.guild.voice_client
            await vcID.disconnect()
            await message.channel.send(response)
        elif message.content == terminateCode:
            await message.channel.send('BasicBot_PY is shutting down!')
            exit();

@bot.event
async def on_voice_state_update(member, before, after):
    voice_client: discord.VoiceClient = discord.utils.get(bot.voice_clients)
    channel = voice_client.channel
    if before.channel == channel and after.channel != channel:
        print("USER LEFT")
        player = discord.FFmpegPCMAudio('AudioBin/LeaveSound.mp3')
        voice_client.play(player, after=None)
    elif before.channel != channel and after.channel == channel:
        print("USER JOINED")
        player = discord.FFmpegPCMAudio('AudioBin/JoinSound.mp3')
        voice_client.play(player, after=None)
   
try:
    bot.run(TOKEN)
except:
    print("Error running your bot. Check BOT_TOKEN in config.txt")
finally:
    print("Thank you for using BasicBot_PY.")























