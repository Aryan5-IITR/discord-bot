import discord
from discord.ext import commands, tasks
import requests
from random import choice,randint
import os
from dotenv import load_dotenv

current_language = "en"
load_dotenv('.env')

client=commands.Bot(command_prefix='$')

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    await client.change_presence(activity=discord.Game("GTA 6"))

@client.command(name='hello', help='This command greets the bot')
async def hello(ctx):
    await ctx.send(choice(['Hello, how are you?', 'Hi', '**Wasssuup!**','Hey there!','Yo! nice to see u','***Ahem Ahem!*** Why have you come here?','Hey! **Wubba Lubba Dub Dub**']))

@client.command(name='ping', help='This command returns the latency')
async def ping(ctx):
    await ctx.send(f'**Pong!** Latency: {round(client.latency * 1000)}ms')

@client.command(name='bitch',hidden=True)
async def lang(ctx):
    await ctx.send('You bitch! stfu 😠')

@client.command(name='meme',help='The bot will share a dank meme.')
async def meme(ctx):
    b=True
    while b:
        r=requests.get("https://memes.blademaker.tv/api?lang=en")
        rj=r.json()
        if rj['subreddit']=='dankmemes':
            b=False
    author=rj["author"]
    url=rj["image"]
    embed=discord.Embed(title=f'Author: {author}')
    embed.set_image(url=url)
    await ctx.send(embed=embed)


from Wikipedia_cog import Wikipedia
from music_cog import Music
from movie_cog import Movies

client.add_cog(Wikipedia(client))
client.add_cog(Music(client))
client.add_cog(Movies(client))

client.run(os.getenv('TOKEN'))
