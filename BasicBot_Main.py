#BasicBot_Main.py

import os
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER = os.getenv('DISCORD_GUILD')

client = discord.Client()

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == SERVER:
            break

    print(f'{client.user} is in ' f'{guild.name}(id: {guild.id})')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content == '!basic_help':
        response = 'Basic Bot PY has the following commands: !basic_help, !basic_about, !basic_joinVC'
        print(f'{message.author} asked {client.user} for commands help using !basic_help')
        await message.channel.send(response)
    if message.content == '!basic_about':
        response = ('Basic Bot PY is an open-source, Python-based Discord bot with basic functionality inlcuding role management, nickname management, Teamspeak-style VC join messages, and keyword-based censorship options! More features are planned. The source code can be found at [GITHUB LINK] and the bot is hosted with Heroku.')
        print(f'{message.author} asked {client.user} for the bot details using !basic_about')
        await message.channel.send(response)
client.run(TOKEN)
