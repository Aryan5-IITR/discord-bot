import discord
from discord.ext import commands, tasks
from asyncio import sleep as s
import requests
from random import choice,randint
import wikipedia
from youtube_dl import YoutubeDL
import json
current_language = "en"

client=commands.Bot(command_prefix='$')

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    await client.change_presence(activity=discord.Game("VALORANT"))

@commands.Cog.listener()
async def on_member_join(self, member: discord.Member):
    channel = self.bot.get_channel(905141905283776605)
    if not channel:
        return

    await channel.send(f'Welcome {member.mention}!  Ready to jam out? See `$help` command for details!')
    #channel = discord.utils.get(member.guild.channels, name='general')
    #await channel.send(f'Welcome {member.mention}!  Ready to jam out? See `$help` command for details!')

@client.command(name='hello', help='This command greets the bot')
async def hello(ctx):
    await ctx.send(choice(['Hello, how are you?', 'Hi', '**Wasssuup!**','Hey there!','Yo! nice to see u','***Ahem Ahem!*** Why have you come here?','**Wubba Lubba Dub Dub**']))

@client.command(name='ping', help='This command returns the latency')
async def ping(ctx):
    await ctx.send(f'**Pong!** Latency: {round(client.latency * 1000)}ms')

@client.command(name='bitch',hidden=True)
async def lang(ctx):
    await ctx.send('You bitch! stfu 😠')

@client.command(name='meme',help='The bot will share a meme.')
async def meme(ctx):
    r=requests.get("https://memes.blademaker.tv/api?lang=en")
    rj=r.json()
    author=rj["author"]
    url=rj["image"]
    embed=discord.Embed(title=f'Author: {author}')
    embed.set_image(url=url)
    await ctx.send(embed=embed)


class Wikipedia(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(name='wiki',help='brings wikipedia search results')
    async def wiki(self,ctx):

        request = ctx.message.content[6:]

        wikicontent = wikipedia.search(request, results=10, suggestion=False)

        if not wikicontent:
            wikicontent ="Sorry, there are no search results for '{}'.".format(request)
            embed = discord.Embed(title="Wikipedia search results:", color=0xe74c3c, description=wikicontent)
            embed.set_thumbnail(url="https://www.wikipedia.org/static/images/project-logos/{}wiki.png".format(current_language))
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(title="Wikipedia search results:", color=0, description="\n".join(wikicontent))
            embed.set_thumbnail(url="https://www.wikipedia.org/static/images/project-logos/{}wiki.png".format(current_language))
            await ctx.send(embed=embed)


    @commands.command(name='display',help='This command displays wikipedia info')
    async def display(self,ctx):

        request = ctx.message.content[9:]

        try:
            pagecontent = wikipedia.page(request)
            pagetext = wikipedia.summary(request, sentences=5)


            try:
                thumbnail = pagecontent.images[randint(0, len(pagecontent.images))]
                #Trying to get random image from the article to display.

            except:
                thumbnail = "https://www.wikipedia.org/static/images/project-logos/enwiki.png"
                #If there are no pictures, it wil set it to the default wkikipedia picture


            embed = discord.Embed(title=request, color=0, description=pagetext + "\n\n[Read further]({})".format(pagecontent.url))
            embed.set_thumbnail(url=thumbnail)
            await ctx.send(embed=embed)

        except:
            ErrorMessage = "Sorry, I was unable to fetch the desired page. Please make sure that the page exists by using '$wiki'"
            embed = discord.Embed(title="Error", color=0xe74c3c, description=ErrorMessage)
            embed.set_thumbnail(url="https://www.wikipedia.org/static/images/project-logos/{}wiki.png".format(current_language))
            await ctx.send(embed=embed)

class Music(commands.Cog):

    def __init__(self, client):
        self.client = client

        self.is_playing = False

        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        self.vc = ""

    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception:
                return False

        return {'source': info['formats'][0]['url'], 'title': info['title']}

    def play_next(self,ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            #get the first url
            url = self.music_queue[0][0]['source']

            #remove the first element as you are currently playing it
            self.music_queue.pop(0)

            ctx.voice_client.play(discord.FFmpegPCMAudio(url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))
        else:
            self.is_playing = False

    async def play_music(self,ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True
            #print(self.music_queue)
            url = self.music_queue[0][0]['source']

            if self.vc == "" or  self.vc == None or self.vc!=self.music_queue[0][1]:
                self.vc = self.music_queue[0][1]
                if self.vc!=self.music_queue[0][1]:
                    await ctx.voice_client.disconnect()
                await self.vc.connect()
            #else:
            #    await self.vc.move_to(self.music_queue[0][1])

            print(self.music_queue)

            self.music_queue.pop(0)

            #source=await discord.FFmpegOpusAudio.from_probe(url,**self.FFMPEG_OPTIONS)
            ctx.voice_client.play(discord.FFmpegPCMAudio(url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))

        else:
            self.is_playing = False

    @commands.command(name="play", help="Plays the mentioned song from youtube")
    async def play(self, ctx, *args):
        query = " ".join(args)+' lyrical'


        if ctx.author.voice is None:
            await ctx.send("Connect to a voice channel!")
        else:
            voice_channel = ctx.author.voice.channel
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("Could not download the song.Try another keyword.")
            else:
                await ctx.send("Song added to the queue")
                self.music_queue.append([song, voice_channel])
                print (song)

                if self.is_playing == False:
                    await self.play_music(ctx)

    @commands.command(name="queue", help="Displays the current songs in queue")
    async def q(self, ctx):
        quu = ""
        for i in range(0, len(self.music_queue)):
            quu += self.music_queue[i][0]['title'] + "\n"

        print(quu)
        if quu != "":
            embed = discord.Embed(title="Queue:", color=0, description=quu)
            await ctx.send(embed=embed)
        else:
            await ctx.send("No music in queue")

    @commands.command(name="skip", help="Skips the current song being played")
    async def skip(self, ctx):
        if self.vc != "" and self.vc:
            ctx.voice_client.pause()
            await self.play_music(ctx)

    @commands.command(name="disconnect", help="Disconnects the bot from VC")
    async def dc(self, ctx):
        await ctx.voice_client.disconnect()
        self.vc=None
        self.is_playing = False

class Movies(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(name='genre', help='Suggests a movie of the genre')
    async def gs(self,ctx):
        response=requests.get('https://api.themoviedb.org/3/genre/movie/list?api_key=b65a210962422ff226fd2c3ae0546420&language=en-US')
        data=json.loads(response.text)
        req=ctx.message.content[7:].lower()

        if req=='display':
            gen=''
            for i in data['genres']:
                gen+=i['name']
                gen+='\n'
            embed = discord.Embed(title="Genres:", color=0, description=gen)
            await ctx.send(embed=embed)

        else:
            b=True
            mid=0
            for i in data['genres']:
                if i['name'].lower()==req:
                    mid=i['id']
                    b=False
            if not b:
                page=randint(1,20)
                n=randint(0,19)
                res=requests.get('https://api.themoviedb.org/3/discover/movie?api_key=b65a210962422ff226fd2c3ae0546420&language=en-US&sort_by=popularity.desc&include_adult=true&include_video=false&page={}&with_genres={}&with_watch_monetization_types=flatrate'.format(page,mid))
                list=json.loads(res.text)
                title=list['results'][n]['title']
                des='Overview: '+list['results'][n]['overview']+'\nRelease date: '+list['results'][n]['release_date']+'\nAvg rating: '+str(list['results'][n]['vote_average'])+"\nId: "+str(list['results'][n]['id'])
                embed=discord.Embed(title=title,color=0,description=des)
                await ctx.send(embed=embed)

            else:
                await ctx.send('Invalid genre. To know the valid genres, use \'$genre display\'')

client.add_cog(Wikipedia(client))
client.add_cog(Music(client))
client.add_cog(Movies(client))

client.run('OTQyODczMDMzNjc5NDYyNDQx.Ygq08A.32MAKHy-qDq4OM14eWbUEIy1WHE')
