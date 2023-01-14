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

#audio options
FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

bot = commands.Bot(command_prefix='!', intents=intents)

playlist = []

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
    
    #use pafy to get audio only stream of youtube video
    link = ("https://www.youtube.com/watch?v=" + video["items"][0]["id"]["videoId"])
    pafyVideo = pafy.new(link)
    stream = pafyVideo.getbestaudio()

    if (botVoice.is_playing()):
        print("queuing new song")
        playlist.append((video, stream))
        await ctx.send("Added " + video["items"][0]["snippet"]["title"] + " to queue")

    #play video audio over voice channel
    botVoice.play(discord.FFmpegPCMAudio(stream.url, **FFMPEG_OPTS), after=lambda e: playNext(e, ctx, botVoice, playlist))
    botVoice.is_playing()

    #inform user what song is playing
    await ctx.send("Now playing: " + video["items"][0]["snippet"]["title"])

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
    
    #use pafy to get best audio stream from input url
    pafyVideo = pafy.new(url)
    stream = pafyVideo.getbestaudio()

    if (botVoice.is_playing()):
        #queue song request if one is already playing
        print("queuing new song")
        await ctx.send("Added " + url + " to queue")
    else:
        #play video audio over voice channel
        botVoice.play(discord.FFmpegPCMAudio(stream.url, **FFMPEG_OPTS), after=lambda e: playNext(e, ctx, botVoice, playlist))
        botVoice.is_playing()

        #inform user what song is playing
        await ctx.send("Now playing: " + url)

@bot.command(name = "stop", help = "stop current song and deletes queue")
async def stop(ctx):

    #get voice client
    botVoice = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    #check if playing, stop if true
    if not botVoice.is_playing():
        await ctx.send("I'm not playing anything!")
    else:
        await ctx.send("Party pooper")
        botVoice.stop()

@bot.command(name = "skip", help = "skips current song and moves to next in queue")
async def skip(ctx, playlist):

    botVoice = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if playlist == []:
        await ctx.send("No other songs in queue")
    elif not botVoice.is_playing():
        await ctx.send("Not currently playing")
    else:
        video = playlist.pop(0)
        stream = video[1]
        video = video[0]

        botVoice.stop()
        botVoice.play(discord.FFmpegPCMAudio(stream.url, **FFMPEG_OPTS),after=lambda e: playNext(e, ctx, botVoice, playlist))
        botVoice.is_playing()


#internal function to allow playlist support
async def playNext(e, ctx, botVoice, playlist):

    #log any errors from previous song
    print("errors: " + e)

    #check if any songs are in queue, disconnect if not
    if playlist == []:
        await ctx.send("Queue finished!")
        await botVoice.disconnect()
    else:
        #extract enqueued song
        video = playlist.pop(0)
        stream = video[1]
        video = video[0]
        
        print("playing next")

        #play video audio over voice channel
        botVoice.play(discord.FFmpegPCMAudio(stream.url, **FFMPEG_OPTS),after=lambda e: playNext(e, ctx, botVoice, playlist))
        botVoice.is_playing()

        #inform user what song is playing
        await ctx.send("Now playing: " + video["items"][0]["snippet"]["title"])

#start bot
bot.run(TOKEN)
