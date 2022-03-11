import discord
from discord.ext import commands, tasks
from youtube_dl import YoutubeDL


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

            #remove the first element
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
