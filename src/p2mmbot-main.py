from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands
import json
import logging
from logging import handlers
import asyncio
import os
import traceback
from datetime import datetime

basepath = os.getcwd()
if "src" not in basepath:
    basepath = basepath + os.sep + "src" + os.sep

if not os.path.exists(basepath + "Logs"):
    os.mkdir(basepath + "Logs")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename=basepath + "Logs/p2mmbot.log", # Log location
    encoding="utf-8", # Log encoding
    mode="w", # Make sure when ever the bot starts it starts fresh with logs
    maxBytes=32 * 1024 * 1024,  # 32 MiB will be the max size for log files
    backupCount=5,  # Rotate through 5 files
)
formatter = logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{")
handler.setFormatter(formatter)
logger.addHandler(handler)

def log(msg: str) -> None:
    now = datetime.now()
    print(f'[{now.strftime("%d/%m/%Y %H:%M:%S")}] {msg}')
    logging.info(msg)

testcommands = [
    "dm_test",
    "message_history_test",
    "test_modal"
]

log("Starting the P2MM bot...")

log("Grabbing config.json information...")

# Get config.json
if not os.path.exists(basepath + "config.json"):
    print("ERROR: config.json not found! config.json contains info the Discord bot needs to start! Shutting down...")
    logging.error("config.json not found! config.json contains info the Discord bot needs to start! Shutting down...")
    exit(1)

try:
    with open(basepath + "config.json", "r") as config:
        cfg = json.load(config)

        # Check if the user wants to use a test bot id
        if (not cfg.get("testing") is None) and (cfg["testing"]):
            token = cfg["token_testing"] # Test Bot Token
            testing_guild_id = int(cfg["testing_guild_id"]) # Testing guild id
            log('"testing" is set to True, will use test bot token...')
        else:
            token = cfg["token"] # Bot Token
        debug_prefix = cfg["debug_prefix"] # Bot Debug Command Prefix, Default "!"

        # P2MM Discord Server specific channel ids
        bot_test_channel_id = int(cfg["bot_test_channel_id"])
        mod_help_channel_id = int(cfg["mod_help_channel_id"])
except KeyError as key:
    # Should only except is the P2MM Discord Server ids error, this is assuming that this bot is not the offical P2MM Bot
    print(f"WARNING: {key} not found! Assuming this is not the offical P2MM Bot being run! Setting all offical ids to None...")
    logging.warning(f"{key} not found! Assuming this is not the offical P2MM Bot being run! Setting all offical ids to None...")
    bot_test_channel_id = None
    mod_help_channel_id = None

class P2MMBot(discord.Client):
    def __init__(self, *, intents: discord.Intents, command_prefix):
        super().__init__(intents=intents, command_prefix=debug_prefix)
        self.tree = app_commands.CommandTree(self)

    # Runs when the bot is being setup
    async def setup_hook(self):
        log("Setting up bot hook...")
        if not cfg["testing"]:
            # Copy all commands to test guild, including test commands
            
            try:
                for testcommand in testcommands:
                    self.tree.add_command(globals()[testcommand])
                    log(f'Added test command: {testcommand}')
            except discord.app_commands.errors.CommandAlreadyRegistered:
                pass
            
            self.tree.copy_global_to(guild=discord.Object(id=testing_guild_id))
            log(f'Copied all slash commands to test guild "{await discord.utils.get(self.fetch_guilds(), id=testing_guild_id)}"...')
        else:
            # Remove test commands so there are not used by the general public
            for testcommand in testcommands:
                self.tree.remove_command(testcommand)
                log(f'Removed test command: {testcommand}')
                
        log("Syncing slash commands to all guilds...")
        for command in await self.tree.sync():
            log(f'Command "{command}" was synced...')
        
        log("Finished setting up bot hook...")
    
    # Runs when the bot has finished setting up
    async def on_ready(self):
        log("Almost ready...")
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.custom, name="Portal 2: Multiplayer Mod"))
        #await client.get_channel(bot_test_channel_id).send("I AM ALIVE!!!")
        log(f'Logged on as {self.user}!')
        log("----------------------------")

class Test_Modal(discord.ui.Modal, title='Test Modal'):
    # Our modal classes MUST subclass `discord.ui.Modal`,
    # but the title can be whatever you want.

    # This will be a short input, where the user can enter their name
    # It will also have a placeholder, as denoted by the `placeholder` kwarg.
    # By default, it is required and is a short-style input which is exactly
    # what we want.
    name = discord.ui.TextInput(
        label='Name',
        placeholder='Type your name here... ',
    )

    # This is a longer, paragraph style input, where user can submit feedback
    # Unlike the name, it is not required. If filled out, however, it will
    # only accept a maximum of 300 characters, as denoted by the
    # `max_length=300` kwarg.
    feedback = discord.ui.TextInput(
        label='This is the text for a textinput',
        style=discord.TextStyle.long,
        placeholder='Type your text here...',
        required=False,
        max_length=300,
    )

    async def on_submit(self, interaction: discord.Interaction):
        log("Submitted info for the Test Modal...")
        await interaction.response.send_message(f'Thanks for your feedback, {self.name.value}!', ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        log("ERROR: Something went wrong with the Test Modal...")

        # Make sure we know what the error actually is
        log(traceback.print_exception(type(error), error, error.__traceback__))
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
client = P2MMBot(intents=intents, command_prefix=debug_prefix)

def check_admin(target_member: discord.Member) -> bool:
    """Checks if Orsell is the one to execute the command.

    Args:
        target_member (discord.Member): Member/User to target.

    Returns:
        bool: Returns True if the user is Orsell.
    """
    if target_member.id == 217027527602995200:
        return True
    return False

async def message_history_count(target_channel_id: int, target_member_id: int, limit: int = None, output: bool = False) -> int:
    """Get the total message count of a member.

    Args:
        target_channel_id (int): Target channel id.
        target_member_id (int): Target member id.
        limit (int): The limit of how many messages you want to grab. Defaults to None which is all messages.
        output (bool, optional): Output message contents to the console and log. Defaults to False.

    Returns:
        int: Total number of users message in that channel.
    """
    log("MESSAGE HISTORY COUNT:")
    log(f'Checking message count in channel {client.get_channel(target_channel_id)}')
    log(f'Target user {client.get_user(target_member_id)}')
    log(f'With limit {limit} and will print out in both console and log {output}')
    
    message_count = 0
    async for message in client.get_channel(target_channel_id).history(limit=limit):
        if message.author.id == target_member_id:
            if output:
                log(message.content)
            message_count += 1
    return message_count

# Simply responds with hello back to the user who issued the command
@client.tree.command(description="Says hello back")
async def hello(interaction: discord.Interaction):
    """Says hello!"""

    log("Hello command executed...")
    await interaction.response.send_message(f'Hi, {interaction.user.mention}')

# Reponds back with when a member joinned the server
@client.tree.command(description="Get when a user joinned the server")
@app_commands.describe(member="The user you want to get the joined date from; defaults to the user who uses the command")
async def date_joined(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    """Get when a user joinned the server"""

    # If no member is explicitly provided then we use the command user here
    member = member or interaction.user

    # The format_dt function formats the date time into a human readable representation in the official client
    log("Join data grabbed via slash command:")
    log(f'{member} joined at {discord.utils.format_dt(member.joined_at)}')
    await interaction.response.send_message(f'{member} joined {discord.utils.format_dt(member.joined_at)}')

@client.tree.context_menu(name="Show Join Date")
async def show_join_date(interaction: discord.Interaction, member: discord.Member):

    # The format_dt function formats the date time into a human readable representation in the official client
    log("Join data grabbed via context menu:")
    log(f'{member} joined at {discord.utils.format_dt(member.joined_at)}')
    await interaction.response.send_message(f'{member} joined at {discord.utils.format_dt(member.joined_at)}', ephemeral=True)

@client.tree.command(description="Turns off the P2MM bot")
async def shutdown(interaction: discord.Interaction):
    """Shutsdown the P2MM bot"""

    # Check if user is Orsell
    if not check_admin(interaction.user):
        await interaction.response.send_message("You do not have permission to run this command!", ephemeral=True)
        return

    await interaction.response.send_message("Shutting down, good bye!")
    log("The P2MM Bot Has been shutdown...")
    await asyncio.sleep(1)
    await client.close()

@client.tree.command(description="Pings the bot")
async def ping(interaction: discord.Interaction):
    """Pings the bot"""

    embed = discord.Embed(title="Ping", description=f'Pong! {round((client.latency * 1000), 2)} ms', colour=discord.Colour.brand_green())
    log("Bot has been pinged...")
    await interaction.response.send_message(embed=embed)

@client.tree.command(description="Test DMing using the bot")
@app_commands.describe(member="The specified user to DM; defaults to the user who uses the command")
async def dm_test(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    """Test DMing using the bot"""

    # Check if user is Orsell
    if not check_admin(interaction.user):
        await interaction.response.send_message("You do not have permission to run this command!", ephemeral=True)
        return

    # If no member is explicitly provided then we use the command user here
    member = member or interaction.user
    
    # Send the DM to the specified user
    try:
        await member.send("Hello from the P2MM Bot!")
        log((f'Sent DM message to {member}'))
        await interaction.response.send_message(f'Sent DM message to {member}')
    except discord.Forbidden:
        log(f"Failed to DM message to {member} as they have blocked the bot or have server DM's disabled.")
        await interaction.response.send_message(f"Failed to DM message to {member} as they have blocked the bot or have server DM's disabled.")

@client.tree.command(description="Grab the specified users last 50 messages or how many there are if less than 50 are present.")
@app_commands.describe(
    channel="The specified channel to grab messages from; this needs to be specified.",
    member="The specified user to get the last 50 messages; defaults to the user who uses the command."
)
async def message_history_test(interaction: discord.Interaction, channel: str, member: Optional[discord.Member] = None):
    """Get specified users last 50 messages, if there is less it will return how many there actually are.

    Parameters
    ----------
        channel str: 
            "The specified channel to grab messages from; this needs to be specified."
        member (Optional[discord.Member], optional): 
            "The specified user to get the last 50 messages; defaults to the user who uses the command."
    """

    # Check if user is Orsell
    if not check_admin(interaction.user):
        await interaction.response.send_message("You do not have permission to run this command!", ephemeral=True)
        return

    # If no member is explicitly provided then we use the command user here
    member = member or interaction.user
    
    log(f'Grabbing messages of user: {member}')

    # Check to make sure the specified channel is valid/exists
    target_channel = discord.utils.get(client.get_all_channels(), name=channel)
    if target_channel == None:
        log(f'Failed to grab the messages of "{member}" in the specified channel "{channel}" as it doesn\'t exist.')
        await interaction.response.send_message(f'Failed to grab the messages of "{member}" in the specified channel "{channel}" as it doesn\'t exist.')
        return  
    
    # Count up the number of messages the author sent
    message_count = await message_history_count(target_channel.id, member.id, 50, True)
    
    # If there are 0 messages in the channel it will report as so
    if message_count == 0:
        log(f'No messages of user "{member}" were found in "{channel}"')
        await interaction.response.send_message(f'No messages of user "{member}" were found in "{channel}"')
        return
    
    log(f'Grabbed last {message_count} messages of "{member}" in "{channel}", check console for history.')
    await interaction.response.send_message(f'Grabbed last {message_count} messages of "{member}" in "{channel}", check console for history.')

@client.tree.command(description="Test the Test Modal")
async def test_modal(interaction: discord.Interaction):

    # Check if user is Orsell
    if not check_admin(interaction.user):
        await interaction.response.send_message("You do not have permission to run this command!", ephemeral=True)
        return

    log("Test Modal was tested...")
    await interaction.response.send_modal(Test_Modal())

# Called whenever someone sends a message
@client.event
async def on_message(message: discord.Message, interaction: discord.Interaction):
    if (message.author.id == client.user.id):
        return
    
    #log(f'Message from id {message.author.id}, author name {message.author}, in channel {message.channel}, with id {message.channel.id}: {message.content}")
    if (message.channel.id == mod_help_channel_id) and (await message_history_count(mod_help_channel_id, message.author.id, output=None) == 1) and (not message.author.bot):
        log(f'New comer in #mod-help! User: {message.author} ID: {message.author.id}')
        await interaction.response.send_message(
            "Hey there! It appears it's your first time messaging in <#839751998445846568>!\nMake sure to check out the <#1027963220851429387>, your answer might be there!", 
            ephemeral=True)
        return
    
    if not message.content.startswith(debug_prefix):
        return
    
    if "hello" in message.content:
        log("Hello command executed...")
        await message.reply("Hello!", mention_author=True)

# @client.event
# async def on_guild_join(self, guild:discord.Guild):
#     client.get_channel(discord.utils.get(predicate, iterable))

@client.event
async def on_error(self, interaction: discord.Interaction, error: Exception, event:str):
    log(f'An non-fatal error occured! With event: {event}')
    log(traceback.print_exception(type(error), error, error.__traceback__))
    await client.get_channel(1062430492558888980).send("<@217027527602995200> ERROR: An error occured with the bot! Check the console!")

# START THE BOT!!!
client.run(token, log_handler=None, root_logger=True)