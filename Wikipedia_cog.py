import discord
from discord.ext import commands, tasks
from random import choice,randint
import wikipedia

current_language = "en"

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
