import os
import discord
import pafy
from youtube_dl import YoutubeDL
import asyncio

from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get
from youtubeIntegration import songRequest
from time import sleep

#load discord bot token from environment variable
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#set discord intents
intents = discord.Intents.default()
intents.message_content = True

#audio options
FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

bot = commands.Bot(command_prefix='!', intents=intents)

#initialize playlist queue
playlist = []

@bot.command(name = 'play', help = "Search youtube for the phrase given, play first result")
async def play(ctx,*, song):

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
    
    #log video information
    print(video)
    
    #use pafy to get audio only stream of youtube video
    link = ("https://www.youtube.com/watch?v=" + video["items"][0]["id"]["videoId"])
    pafyVideo = pafy.new(link)
    stream = pafyVideo.getbestaudio()

    #add request to playlist if a song is already playing
    if (botVoice.is_playing()):
        print("queuing new song")
        playlist.append((video, stream))
        await ctx.send("Added " + video["items"][0]["snippet"]["title"] + " to queue")
        
    else
        #play video audio over voice channel
        botVoice.play(discord.FFmpegPCMAudio(stream.url, **FFMPEG_OPTS), after=lambda e: print('done', e))
        botVoice.is_playing()

        #inform user what song is playing
        await ctx.send("Now playing: " + video["items"][0]["snippet"]["title"])

    #call to aux function for playlist support
    await playNext(ctx, botVoice)

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

    video = {'items': [{'id': {'videoId': 'fecSD7CgxAI'}, 'snippet': {'publishedAt': '2023-01-23T07:43:18Z', 'channelId': 'UCeZoKzVi_FCb9a-96XqU5iQ', 'title': url, 'description': 'countrymusic #countrynews #topcountrysongs Top 100 Country Songs of 2023  Chris Lane, Morgan Wallen, Luke Combs, Chris ...', 'channelTitle': 'Country Music Collection'}}]}

    if (botVoice.is_playing()):
        print("queuing new song")
        playlist.append((video, stream))
        await ctx.send("Added " + video["items"][0]["snippet"]["title"] + " to queue")
    
    else
        #play video audio over voice channel
        botVoice.play(discord.FFmpegPCMAudio(stream.url, **FFMPEG_OPTS), after=lambda e: print('done', e))
        botVoice.is_playing()

        #inform user what song is playing
        await ctx.send("Now playing: " + video["items"][0]["snippet"]["title"])

    await playNext(ctx, botVoice)

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
    
    #deletes queue
    playlist = []

@bot.command(name = "skip", help = "skips current song and moves to next in queue")
async def skip(ctx):

    botVoice = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if playlist == []:
        await ctx.send("No other songs in queue")
    elif not botVoice.is_playing():
        await ctx.send("Not currently playing")
    else:
        video = playlist.pop(0)
        stream = video[1]
        video = video[0]

        await ctx.send("Skipped")

        botVoice.stop()
        botVoice.play(discord.FFmpegPCMAudio(stream.url, **FFMPEG_OPTS),after=lambda e: print('done', e))
        botVoice.is_playing()

        await ctx.send("Now playing: " + video["items"][0]["snippet"]["title"])

        await playNext(ctx, botVoice)


#internal function to allow playlist support
async def playNext(ctx, botVoice):

    while botVoice.is_playing():
        await asyncio.sleep(.1)

    #check if any songs are in queue, disconnect if not
    if playlist == []:
        await ctx.send("Queue finished!")
        #await botVoice.disconnect()
    else:
        #extract enqueued song
        video = playlist.pop(0)
        stream = video[1]
        video = video[0]
        
        print("playing next")

        #play video audio over voice channel
        botVoice.play(discord.FFmpegPCMAudio(stream.url, **FFMPEG_OPTS),after=lambda e: print('done', e))
        botVoice.is_playing()

        #inform user what song is playing
        await ctx.send("Now playing: " + video["items"][0]["snippet"]["title"])

        await playNext(ctx, botVoice)

#start bot
bot.run(TOKEN)
