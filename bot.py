from ast import alias
import os
import discord
import pafy
import asyncio

from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get
from youtubeIntegration import songRequest

#load discord bot token from environment variable
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#set discord intents
intents = discord.Intents.default()
intents.message_content = True

#audio options
FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

#initiate bot
bot = commands.Bot(command_prefix='!', intents=intents)

#initiate global playlist queue
playlist = []

#primary command, user requests a song by search term or link
@bot.command(name = 'play', help = "Search youtube for the phrase given, play first result", aliases = ["p", "Play", "PLAY"])
async def play(ctx,*, song):

    #check that author voice channel exists, try to join if so
    if ctx.author.voice.channel is None:
        await ctx.send("Please join a voice channel first!")
        print("User attempted play when not in voice channel")
        return
    else:
        voiceChannel = ctx.message.author.voice.channel
        try:
        #try creates voice client, except moves voice client if already created on server but in different channel
            botVoice = await voiceChannel.connect()
        except:
            botVoice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
            if botVoice.channel != voiceChannel:
                await botVoice.move_to(voiceChannel)

        #Queue video given, different functions for search term vs url
        if song.startswith("http"):
            await queueUrl(song, ctx)
        else:
            await queueString(song, ctx)

        if not botVoice.is_playing():
            skipInvoke = 0
            await playSong(botVoice, ctx, skipInvoke)
            
async def queueUrl(song, ctx):
#auxillary function to queue song from a link

    #check if url is a youtube short, convert to video if so
    if song.startswith("https://www.youtube.com/shorts/"):
        urlSplit = song.split("/")
        id = urlSplit[4]
        print(id)
        song = "https://www.youtube.com/watch?v=" + id

    #extract audio stream from youtube link
    pafyVideo = pafy.new(song)
    stream = pafyVideo.getbestaudio()
    video = {'items': [{'id': {'videoId': 'fecSD7CgxAI'}, 'snippet': {'publishedAt': '2023-01-23T07:43:18Z', 'channelId': 'UCeZoKzVi_FCb9a-96XqU5iQ', 'title': song, 'description': 'countrymusic #countrynews #topcountrysongs Top 100 Country Songs of 2023  Chris Lane, Morgan Wallen, Luke Combs, Chris ...', 'channelTitle': 'Country Music Collection'}}]}
    duration = pafyVideo.length

    print("Queued Url: " + song)

    #add video information and stream to playlist queue
    playlist.append((song, stream, duration))

    await ctx.send("Added " + song + " to queue")

async def queueString(song, ctx):
#auxillary function to queue song from a search term

    #search for request on Youtube
    video = songRequest(song)

    #extract audio stream from youtube page
    link = ("https://www.youtube.com/watch?v=" + video["items"][0]["id"]["videoId"])
    pafyVideo = pafy.new(link)
    stream = pafyVideo.getbestaudio()
    duration = pafyVideo.length

    print("Queueing: " + video["items"][0]["snippet"]["title"])

    #add video information and stream to playlist queue
    playlist.append((video["items"][0]["snippet"]["title"], stream, duration))

    await ctx.send("Added " + video["items"][0]["snippet"]["title"] + " to queue")

async def playSong(botVoice, ctx, skipInvoke):
#auxillary function that manages song plays and playlist support

    if (skipInvoke == 1):
    #causes function to play next song in queue
        botVoice.stop()

        #extract song information from playlist queue
        song = playlist.pop(0)
        title = song[0]
        stream = song[1]
        duration = song[2]

        #play song
        botVoice.play(discord.FFmpegPCMAudio(stream.url, **FFMPEG_OPTS),after=lambda e: print('done', e))
        botVoice.is_playing()

        await ctx.send("Skipped! Now playing: " + title)

        #play next song, without skipping, after sleeping currenmt songs duration
        await asyncio.sleep(duration + 1)
        skipInvoke = 0
        await playSong(botVoice, ctx, skipInvoke)
        return

    elif playlist != []:
    #default function behaviour, starts playlist and continues until empty

        botVoice.stop()

        #extract song information from playlist
        song = playlist.pop(0)
        title = song[0]
        stream = song[1]
        duration = song[2]

        #play song
        botVoice.play(discord.FFmpegPCMAudio(stream.url, **FFMPEG_OPTS),after=lambda e: print('done', e))
        botVoice.is_playing()

        await ctx.send("Now playing: " + title)

        #sleep for song duration, play next
        await asyncio.sleep(duration + 1)
        await playSong(botVoice, ctx, skipInvoke)
        return
    
    else:
        await ctx.send("Playlist empty")
        return

@bot.command(name = "stop", help = "stop current song and deletes queue")
async def stop(ctx):

    #Check if voice client exists, stops playback if currently playing
    try:
        botVoice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    except:
        await ctx.send("I'm not playing anything!")
    else:
        if (botVoice.is_playing()):
            botVoice.stop()
            await ctx.send(ctx.message.author.name + " has stopped the music :(")
    
    #deletes queue
    playlist = []

@bot.command(name = "skip", help = "skips current song and moves to next in queue. Aliases: !next", aliases = ["next"])
async def skip(ctx):

    try:
        botVoice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    except:
        await ctx.send("Not currently playing")
    else:
        if playlist == []:
            await ctx.send("No other songs in queue")
        else:
            skipInvoke = 1
            await playSong(botVoice, ctx, skipInvoke)

@bot.command(name = "Diagnostics", help = "Display bot metrics to users")
async def diagnostics(ctx):
#function to allow for bot diagnostics by server users

    botVoice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    await ctx.send("Voice connection: ") 
    await ctx.send(botVoice.is_connected())
    await ctx.send("Voice channel: " + botVoice.channel)
    await ctx.send("Current Queue length: " + playlist.count)
    await ctx.send("Currently playing: ")
    await ctx.send(botVoice.is_playing())

#start bot
bot.run(TOKEN)
