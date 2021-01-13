#BasicBot_Main.py

import os
import discord
import random
import string
import sys
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER = os.getenv('DISCORD_GUILD')
client = discord.Client()
terminateCode = '!basicbot_terminate '+''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == SERVER:
            break
 
    print(f'{client.user} is online. Terminate with OTP: {terminateCode}')

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

client.run(TOKEN)
