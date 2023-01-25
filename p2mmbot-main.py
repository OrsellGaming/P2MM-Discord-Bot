from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands
import json
import logging

log_handler = logging.FileHandler(filename='Logs/p2mmbot.log', encoding='utf-8', mode='w')

print("Starting the P2MM bot...")

# Get configuration.json
with open("config.json", "r") as config:
    data = json.load(config)
    token = data["token"]
    debug_prefix = data["debug_prefix"]

p2mm_server_id = discord.Object(id=839651379034193920)

class P2MMBot(commands.Bot):
    def __init__(self, *, intents: discord.Intents, command_prefix):
        super().__init__(intents=intents, command_prefix=debug_prefix)
        # The command tree holds all the slash commands used for the P2MM Bot
        #self.tree = app_commands.CommandTree(self)

    # Runs when the bot is being setup
    async def setup_hook(self):
        print("Setting up bot hook...")
        self.tree.copy_global_to(guild=p2mm_server_id)
        await self.tree.sync(guild=p2mm_server_id)
        print("Finished setting up bot hook...")

intents = discord.Intents.default()
intents.message_content = True
client = P2MMBot(command_prefix=debug_prefix, intents=intents)


# Runs when the bot has finished setting up
@client.event
async def on_ready():
    global bot_test_channel
    print("Almost ready...")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name ="Portal 2: Multiplayer Mod"))
    print(f"Logged on as {client.user}!")
    print("----------------------------")
    bot_test_channel = client.get_channel(1062430492558888980)
    await bot_test_channel.send("I AM ALIVE!!!")

# Simply responds with hello back to the user who issued the command
@client.tree.command(description="Says hello back")
async def hello(interaction: discord.Interaction):
    """Says hello!"""
    await interaction.response.send_message(f'Hi, {interaction.user.mention}')

# Reponds back with when a member joinned the server
@client.tree.command(description="Get when a user joinned the server")
@app_commands.describe(member="The user you want to get the joined date from; defaults to the user who uses the command")
async def date_joined(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    """Says when a member joined."""
    # If no member is explicitly provided then we use the command user here
    member = member or interaction.user

    # The format_dt function formats the date time into a human readable representation in the official client
    await interaction.response.send_message(f'{member} joined {discord.utils.format_dt(member.joined_at)}')

@client.tree.command(description="Turns off the P2MM bot")
async def shutdown(interaction: discord.Interaction):
    """Shutsdown the P2MM bot"""
    await interaction.response.send_message("Shutting down, good bye!")
    await client.close()

# Called on whenever someone sends a message
@client.event
async def on_message(self, message):
    if message.author.id == self.user.id:
         return
    
    if message.content.startswith('!hello'):
         await message.reply('Hello!', mention_author=True)
    #await message.reply('I am replying to this message', mention_author=True)
    print(f'Message from id {message.author.id} author name {message.author}: {message.content}')

# Runs when someone joins the server
@client.command()
async def joined(ctx, member: discord.Member):
    """Says when a member joined."""
    await ctx.send(f'{member.name} joined {discord.utils.format_dt(member.joined_at)}')

client.run(token, log_handler=log_handler, log_level=logging.INFO)