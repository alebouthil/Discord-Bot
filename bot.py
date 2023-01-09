import os

import discord
from dotenv import load_dotenv
from discord.ext import commands
from youtubeIntegration import songRequest

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.message_content = True

#client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command(name = 'play', help = "Searchs youtube for the phrase given, plays first result")
async def play(ctx, song):
    video = songRequest(song)
    await ctx.send(video)

bot.run(TOKEN)
