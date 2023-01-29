from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands
import json
import logging
import asyncio

logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.FileHandler(
    filename = "Logs/p2mmbot.log", # Log location
    mode = "w", # Write mode, overides current log
    encoding = "utf-8", # Log format type
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

print("Starting the P2MM bot...")

# Get configuration.json
with open("config.json", "r") as config:
    data = json.load(config)
    token = data["token"] # P2MM Bot Token
    debug_prefix = data["debug_prefix"]
    bot_test_channel_id = int(data["bot_test_channel_id"])
    welcome_channel_id = int(data["welcome_channel_id"])

class P2MMBot(discord.Client):
    def __init__(self, *, intents: discord.Intents, command_prefix):
        super().__init__(intents=intents, command_prefix=debug_prefix)
        self.tree = app_commands.CommandTree(self)

    # Runs when the bot is being setup
    async def setup_hook(self):
        print("Setting up bot hook...")
        logging.info("Setting up bot hook...")
        guilds = [guild async for guild in self.fetch_guilds(limit=1)]
        print(guilds)
        self.tree.copy_global_to(guild=discord.Object(id=839651379034193920))
        await self.tree.sync(guild=None)
        print("Finished setting up bot hook...")
        logging.info("Finished setting up bot hook...")

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
client = P2MMBot(command_prefix=debug_prefix, intents=intents)

# Runs when the bot has finished setting up
@client.event
async def on_ready():
    print("Almost ready...")
    logging.info("Almost ready...")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.custom, name="Portal 2: Multiplayer Mod"))
    #await client.get_channel(bot_test_channel_id).send("I AM ALIVE!!!")
    print(f"Logged on as {client.user}!")
    print("----------------------------")
    logging.info(f"Logged on as {client.user}!")
    logging.info("----------------------------")

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

@client.tree.command(description="Turns off the P2MM bot")
async def shutdown(interaction: discord.Interaction):
    """Shutsdown the P2MM bot"""

    await interaction.response.send_message("Shutting down, good bye!")
    print("The P2MM Bot Has been shutdown...")
    logging.info("The P2MM Bot Has been shutdown...")
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

    # If no member is explicitly provided then we use the command user here
    member = member or interaction.user
    
    # Send the DM to the specified user
    await member.send("Hello from the P2MM Bot!")
    await interaction.response.send_message(f"Sent DM message to {member}")

# Called on whenever someone sends a message
@client.event
async def on_message(message):
    if (message.author.id == client.user.id) or (not message.content.startswith(debug_prefix)):
         return
    
    if "hello" in message.content:
         await message.reply("Hello!", mention_author=True)
    
    print(f"Message from id {message.author.id} author name {message.author}: {message.content}")
    logging.info(f"Message from id {message.author.id} author name {message.author}: {message.content}")

# Runs when someone joins the server
@client.event
async def on_member_join(member: discord.Member):
    """Says when a member joined."""
    await client.get_channel(welcome_channel_id).send(f"{member.name} joined {discord.utils.format_dt(member.joined_at)}")
    logging.info(f"{member.name} joined {discord.utils.format_dt(member.joined_at)}")

@client.event
async def on_guild_join(self, guild:discord.Guild):
    client.get_channel(discord.utils.get(predicate, iterable))

client.run(token, log_handler=None)