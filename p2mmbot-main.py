from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands
import json
import logging
from logging import handlers
import asyncio
import os

if not os.path.exists("Logs"):
    os.mkdir("Logs")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename="Logs/p2mmbot.log", # Log location
    encoding="utf-8", # Log encoding
    mode="w", # Make sure when ever the bot starts it starts fresh with logs
    maxBytes=32 * 1024 * 1024,  # 32 MiB will be the max size for log files
    backupCount=5,  # Rotate through 5 files
)
formatter = logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{")
handler.setFormatter(formatter)
logger.addHandler(handler)

def check_admin(target_member: discord.Member) -> bool:
    """Check if the specified user has the Administrator role.

    Args:
        target_member (discord.Member): Member/User to target.

    Returns:
        bool: Returns True if the user has the Administrator role.
    """
    if discord.utils.get(target_member.roles, name="Administrator"):
        return True
    return False

def log(msg: str) -> None:
    print(msg)
    logging.info(msg)

log("Starting the P2MM bot...")

log("Grabbing config.json information...")

# Get config.json
if not os.path.exists("config.json"):
    print("ERROR: config.json contains info the Discord bot needs to start! Shutting down...")
    logging.error("ERROR: config.json contains info the Discord bot needs to start! Shutting down...")
    exit("config.json not found!")

with open("config.json", "r") as config:
    data = json.load(config)
    token = data["token"] # P2MM Bot Token
    debug_prefix = data["debug_prefix"] # P2MM Bot Debug Command Prefix, Default "!"
    bot_test_channel_id = data["bot_test_channel_id"]
    welcome_channel_id = data["welcome_channel_id"]

class P2MMBot(discord.Client):
    def __init__(self, *, intents: discord.Intents, command_prefix):
        super().__init__(intents=intents, command_prefix=debug_prefix)
        self.tree = app_commands.CommandTree(self)

    # Runs when the bot is being setup
    async def setup_hook(self):
        log("Setting up bot hook...")
        p2mm_guild = await discord.utils.get(self.fetch_guilds(), name="Portal 2: Multiplayer Mod")
        self.tree.copy_global_to(guild=p2mm_guild)
        await self.tree.sync()
        log("Finished setting up bot hook...")

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
client = P2MMBot(command_prefix=debug_prefix, intents=intents)

# Runs when the bot has finished setting up
@client.event
async def on_ready():
    log("Almost ready...")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.custom, name="Portal 2: Multiplayer Mod"))
    #await client.get_channel(bot_test_channel_id).send("I AM ALIVE!!!")
    log(f"Logged on as {client.user}!")
    log("----------------------------")

# Simply responds with hello back to the user who issued the command
@client.tree.command(description="Says hello back")
async def hello(interaction: discord.Interaction):
    """Says hello!"""
    await interaction.response.send_message(f"Hi, {interaction.user.mention}")

# Reponds back with when a member joinned the server
@client.tree.command(description="Get when a user joinned the server")
@app_commands.describe(member="The user you want to get the joined date from; defaults to the user who uses the command")
async def date_joined(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    """Get when a user joinned the server"""

    # If no member is explicitly provided then we use the command user here
    member = member or interaction.user

    # The format_dt function formats the date time into a human readable representation in the official client
    await interaction.response.send_message(f"{member} joined {discord.utils.format_dt(member.joined_at)}")

@client.tree.context_menu(name="Show Join Date")
async def show_join_date(interaction: discord.Interaction, member: discord.Member):
    # The format_dt function formats the date time into a human readable representation in the official client
    await interaction.response.send_message(f"{member} joined at {discord.utils.format_dt(member.joined_at)}", ephemeral=True)

@client.tree.command(description="Turns off the P2MM bot")
async def shutdown(interaction: discord.Interaction):
    """Shutsdown the P2MM bot"""

    # Check if user has the administrator role
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

    embed = discord.Embed(title="Ping", description=f"Pong! {round((client.latency * 1000), 2)} ms")
    await interaction.response.send_message(embed=embed)

@client.tree.command(description="Test DMing using the bot")
@app_commands.describe(member="The specified user to DM; defaults to the user who uses the command")
async def dm_test(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    """Test DMing using the bot"""

    # Check if user has the administrator role
    if not check_admin(interaction.user):
        await interaction.response.send_message("You do not have permission to run this command!", ephemeral=True)
        return

    # If no member is explicitly provided then we use the command user here
    member = member or interaction.user
    
    # Send the DM to the specified user
    await member.send("Hello from the P2MM Bot!")
    await interaction.response.send_message(f"Sent DM message to {member}")

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

    # Check if user has the administrator role
    if not check_admin(interaction.user):
        await interaction.response.send_message("You do not have permission to run this command!", ephemeral=True)
        return

    # If no member is explicitly provided then we use the command user here
    member = member or interaction.user
    
    # Check to make sure the specified channel is valid/exists
    target_channel = discord.utils.get(client.get_all_channels(), name=channel)
    if target_channel == None:
        await interaction.response.send_message(f"Failed to grab the messages of \"{member}\" in the specified channel \"{channel}\" as it doesn't exist.")
        return  
    target_channel = target_channel.id
    
    # Count up the number of messages the author sent
    message_count = 0
    async for message in client.get_channel(target_channel).history(limit=50):
        if message.author == member:
            print(message.content)
            message_count += 1
    
    # If there are 0 messages in the channel it will report as so
    if message_count == 0:
        await interaction.response.send_message(f"No messages of user \"{member}\" were found in \"{channel}\"")
        return
    
    await interaction.response.send_message(f"Grabbed last {message_count} messages of \"{member}\" in \"{channel}\", check console for history.")

# # All other Errors not returned come here. And we can just print the default TraceBack.
# print('Ignoring exception in command {}:'.format(ctx.command))
# traceback.print_exception(type(error), error, error.__traceback__)

# Called whenever someone sends a message
@client.event
async def on_message(message):
    if (message.author.id == client.user.id) or (not message.content.startswith(debug_prefix)):
         return
    
    if "hello" in message.content:
         await message.reply("Hello!", mention_author=True)
    log(f"Message from id {message.author.id} author name {message.author}: {message.content}")

# Runs when someone joins the server
# @client.event
# async def on_member_join(member: discord.Member):
#     """Says when a member joined."""
#     await client.get_channel(welcome_channel_id).send(f"{member.name} joined {discord.utils.format_dt(member.joined_at)}")
#     logging.info(f"{member.name} joined {discord.utils.format_dt(member.joined_at)}")

# @client.event
# async def on_guild_join(self, guild:discord.Guild):
#     client.get_channel(discord.utils.get(predicate, iterable))

client.run(token, log_handler=None)