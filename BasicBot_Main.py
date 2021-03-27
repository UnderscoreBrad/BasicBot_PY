#BasicBot_Main.py

import os
import discord
from discord.ext.commands import Bot
import string
import random
import sys
import MessageChecker
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
    guild_list = ""
    
    #Find all joined servers
    print(f'{bot.user} is online. Terminate with OTP: {terminateCode}')
    for guild in bot.guilds:
        print(f'Joined server: {guild.id}')
        guild_list = guild_list + f'Joined server: {guild.id}.\n'
    
    #Send startup info to the owner DMs
    await bot.get_user(OWNER_ID).create_dm()
    msg = await bot.get_user(OWNER_ID).dm_channel.send(f'{guild_list}{bot.user} is online. Terminate with OTP: {terminateCode} or react to this message.\n\
Use: \U0001F6D1 to Shut down |  \U0001F504 to Restart |  \U0001F565 to Notify before restart')
    OWNER_DM = bot.get_user(OWNER_ID).dm_channel.id
    #Add control emojis
    await msg.add_reaction('\U0001F6D1')
    await msg.add_reaction('\U0001F504')
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

    #Only honor reactions if from the owner
    if reaction.message.channel.id == OWNER_DM:
        if reaction.message.author.name == bot.user.name and user.id == OWNER_ID:
        
            #Shutdown bot gracefully
            if reaction.emoji == '\U0001F6D1':
                await reaction.message.channel.send(f'{bot.user} is shutting down!')
                await bot.change_presence(status=discord.Status.idle,activity=discord.Game("Shutting Down"))
                print(f'{bot.user} shut down.\n')
                await bot.close()
                
            #Shutdown bot gracefully, restart program to refresh variables/code    
            elif reaction.emoji == '\U0001F504':
                await reaction.message.channel.send(f'{bot.user} is restarting!')
                await bot.change_presence(status=discord.Status.idle,activity=discord.Game("Restarting"))
                print(f'{bot.user} restarting.\n')
                await bot.close()
                os.execl(sys.executable, sys.executable, *sys.argv)
                     
            #Notify all BasicBot-Enabled servers that there will be a restart
            elif reaction.emoji == '\U0001F565':
                for g in bot.guilds:
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
    if type(message.channel) == (discord.TextChannel):
        if message.channel.name == 'official-complaints':
            await message.delete()  #messages in these channels are deleted without question
            return
                                    #valid_channel is used to determine if the channel is a command channel
        valid_channel = message.channel.name.startswith('bot') or message.channel.name == 'basicbot'
    else:    
        valid_channel = message.guild == None
        if valid_channel and message.author != bot.user and "bug report" in message.content.lower() and BUG_REPORT_CHANNEL:
            bug_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            await bot.get_channel(BUG_REPORT_CHANNEL).send(f"Bug report {bug_id} from {message.author}:\n{message.content}")
            await bot.get_user(message.author.id).dm_channel.send(f"Your bug report has been submitted and will be addressed in the order it was recieved. We may ask for additional details regarding this issue.\nYour ticket ID is: {bug_id}\n Thank you.")
    try:
        if valid_channel:                 #the command will only be interpreted in specific channels 
            await bot.process_commands(message)
    finally:
        await _censor_check(message, valid_channel)

            
#Child of ON MESSAGE
#Automatically censors keywords in global-censored.txt
async def _censor_check(message, valid_channel):
    global OWNER_ID
    global SITE_URL
    if message.author == bot.user:
        return
    if message_checker.check_message(message.content):
        try:
            await message.delete()
            await message.author.create_dm()
            await message.author.dm_channel.send(f'You sent a message including a banned keyword in {message.guild.name}: {message.channel}.\n\
Your message: "{message.content}"\n\
Reason: Offensive Language\n\
If you believe this was an error, please send a ticket at {SITE_URL} or reply to this DM with "Bug Report" in your message.')
        except:
            pass



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
  {bot.command_prefix}removerole @[User] @[Role]: Removes role from the specified user\n"
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
                    
            
#Internal use role manager function
async def _role_manager(ctx, member, role, add):
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
        await ctx.send(f'{bot.user} is announcing "{message}"')
        print(f'{bot.user} announced {message} from {ctx.author} with code {args}\n')
        for g in bot.guilds:
                    for c in g.channels:
                        if c.name.startswith('bot') or c.name == 'basicbot':
                            await c.send(f'{bot.user.name} announcement from {ctx.author}:\n{message}')
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
        await ctx.send(f'Invalid command, use {bot.command_prefix}help for a list of commands.\nIf you believe this was an error, send {bot.user.name} a direct message with the text "Bug Report" and an explanation of the issue.')
        print(f'Command Error from {ctx.author} in {ctx.channel.id}: {error}\nMessage ID: {ctx.message.id}\nMessage content: {ctx.message.content}')
          
           
try:
    bot.run(TOKEN)
except:
    print("Error running your bot. Check your .env")
finally:
    print("Thank you for using BasicBot_PY.\n")
