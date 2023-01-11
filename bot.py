import os
import vlc
import discord
import pafy

from dotenv import load_dotenv
from discord.ext import commands
from youtubeIntegration import songRequest

#load discord bot token from environment variable
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#set discord intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command(name = 'play', help = "Search youtube for the phrase given, play first result")
async def play(ctx, song):

    #get author voice channel
    voiceChannel = ctx.author.voice.channel

    #check that author voice channel exists
    if voiceChannel is None:
        await ctx.send("Please join a voice channel first!")
        return

    video = songRequest(song)
    await ctx.send("Now playing: " + video["items"][0]["snippet"]["title"])
    ''' 
    videourl = pafy.new("https://www.youtube.com/watch?v=" + video["items"][0]["id"]["videoId"])
    best = videourl.getbest()
    playurl = best.url '''

    link = ("https://www.youtube.com/watch?v=" + video["items"][0]["id"]["videoId"])

    ''' Instance = vlc.Instance()
    player = Instance.media_player_new()
    Media = Instance.media_new("https://www.youtube.com/watch?v=" + video["items"][0]["id"]["videoId"])
    Media.get_mrl()
    player.set_media(Media)
    player.play() '''

    media = vlc.MediaPlayer(link)
    media.play()

@bot.command(name = 'playUrl', help = "Play the given url")
async def playUrl(ctx, url):

    #get author voice channel
    voiceChannel = ctx.author.voice.channel

    #check that author voice channel exists
    if voiceChannel is None:
        await ctx.send("Please join a voice channel first!")
        return

    s

#start bot
bot.run(TOKEN)
