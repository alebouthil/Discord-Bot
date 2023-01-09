import os

import discord
from dotenv import load_dotenv
from discord.ext import commands


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.message_content = True

#client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)

''' @client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!play'):
        voicename = discord.VoiceState.channel(message.author)
        

        await message.channel.send('Hello!') '''

@bot.command(name = 'play', help = "Searchs youtube for the phrase given, plays first result")
async def play(ctx, song):
    await ctx.send()

bot.run(TOKEN)
#client.run(TOKEN)