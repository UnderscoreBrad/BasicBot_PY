#BasicBot_Main.py

import os
import discord
import random
import string
import sys
from dotenv import load_dotenv


    
load_dotenv()
OWNER = 210455720137588737
TOKEN = None
try:
    fp = open('config.txt')
    TOKEN = fp.readline()
    TOKEN = TOKEN.replace('BOT_TOKEN:','')
    print(f'config.txt lists bot token as {TOKEN}')
except:
    print('Bot token not properly read! Edit your config.txt!')
finally:
    fp.close()
    print('Starting BasicBot.')

client = discord.Client()
terminateCode = '!basicbot_terminate '+''.join(random.choices(string.ascii_uppercase + string.digits, k=16))


@client.event
async def on_ready():
    #OWNER_USER = get_user(210455720137588737)
    print(f'{client.user} is online. Terminate with OTP: {terminateCode}')
    #print(f'{OWNER_USER.name} detected as Bot Owner. Change in BasicBot_Main.py')
    #await OWNER_USER.create_dm()
    #await OWNER_USER.dm_channel.send(f'{client.user} is online. Terminate with OTP: {terminateCode}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith(f'!basic'):
        if message.content == '!basic_help':
            response = 'Basic Bot PY has the following commands: !basic_help, !basic_about, !basic_joinVC'
            print(f'{message.author} asked {client.user} for commands help using !basic_help')
            await message.channel.send(response)
        elif message.content == '!basic_about':
            response = ('Basic Bot PY is an open-source, Python-based Discord bot with basic functionality inlcuding role management, nickname management, Teamspeak-style VC join messages, and keyword-based censorship options! More features are planned. The source code can be found at https://github.com/UnderscoreBrad/BasicBot_PY and the bot is hosted with locally for now.')
            print(f'{message.author} asked {client.user} for the bot details using !basic_about')
            await message.channel.send(response)
        elif message.content == '!basic_joinVC':
            channel = message.author.voice.channel
            response = f'Joining voice channel {message.author.voice.channel}'
            print(f'{message.author} asked {client.user} to join {message.author.voice.channel}')
            await channel.connect()
            await message.channel.send(response)
        elif message.content == '!basic_leaveVC':
            response = f'Leaving voice channel {message.author.voice.channel}'
            print(f'{message.author} asked {client.user} to leave {message.author.voice.channel}')
            vcID = message.guild.voice_client
            await vcID.disconnect()
            await message.channel.send(response)
        elif message.content == terminateCode:
            exit();

@client.event
async def on_voice_state_update(member, before, after):
    get_user(798647715473915924)
    if before.channel != None and after.channel == None:
        print("USER LEFT")
        player = discord.FFmpegPCMAudio('AudioBin/LeaveSound.mp3')
        voice_client.play(player, after=None)
    elif before.channel == None and after.channel != None:
        print("USER JOINED")
        player = discord.FFmpegPCMAudio('AudioBin/JoinSound.mp3')
        voice_client.play(player, after=None)
   
try:
    client.run(TOKEN)
except:
    print("Error running your bot. Check BOT_TOKEN in config.txt")
finally:
    print("Thank you for using BasicBot_PY.")























