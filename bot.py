import os
import discord
import pafy
from youtube_dl import YoutubeDL

from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get
from youtubeIntegration import songRequest
#from requests import get

#load discord bot token from environment variable
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#set discord intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command(name = 'play', help = "Search youtube for the phrase given, play first result")
async def play(ctx, song):

    #check that author voice channel exists 
    if ctx.author.voice is None:
        await ctx.send("Please join a voice channel first!")
        print("User attempted play when not in voice channel")
        return
    else:
        voiceChannel = ctx.author.voice.channel

    #check if bot is already in a voice channel, join author voice channel if not
    botVoice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if botVoice and botVoice.is_connected():
        await botVoice.move_to(voiceChannel)
    else:
        botVoice = await voiceChannel.connect() 

    #get youtube video information
    video = songRequest(song)

    #inform user what song is playing
    await ctx.send("Now playing: " + video["items"][0]["snippet"]["title"])
    
    #use pafy to get audio only stream of youtube video
    link = ("https://www.youtube.com/watch?v=" + video["items"][0]["id"]["videoId"])
    pafyVideo = pafy.new(link)
    stream = pafyVideo.getbestaudio()

    #play video audio over voice channel
    FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    botVoice.play(discord.FFmpegPCMAudio(stream.url, **FFMPEG_OPTS), after=lambda e: print('done', e))
    botVoice.is_playing()

@bot.command(name = 'playUrl', help = "Play the given url")
async def playUrl(ctx, url):

    #check that author voice channel exists 
    if ctx.author.voice is None:
        await ctx.send("Please join a voice channel first!")
        print("User attempted play when not in voice channel")
        return
    else:
        voiceChannel = ctx.author.voice.channel

    #check if bot is already in a voice channel, join author voice channel if not
    botVoice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if botVoice and botVoice.is_connected():
        await botVoice.move_to(voiceChannel)
    else:
        botVoice = await voiceChannel.connect() 

#start bot
bot.run(TOKEN)
