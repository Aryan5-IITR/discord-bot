import discord
from discord.ext import commands, tasks
import requests
from random import choice,randint
import json


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
                res2=requests.get('https://api.themoviedb.org/3/movie/{}/watch/providers?api_key=b65a210962422ff226fd2c3ae0546420'.format(list['results'][n]['id']))
                link=json.loads(res2.text)
                title=list['results'][n]['title']
                des='Overview: '+list['results'][n]['overview']+'\nRelease date: '+list['results'][n]['release_date']+'\nAvg rating: '+str(list['results'][n]['vote_average'])+"\nId: "+str(list['results'][n]['id'])
                watchlink=link['results']['US']['link']
                watchlink=watchlink[0:len(watchlink)-2]
                watchlink+='IN'
                des+='\nOfficial streaming info(INDIA): '+watchlink
                us='https://hdwatch.tv/search/'+'-'.join(list['results'][n]['title'].split(' '))
                des+='\nUnofficial streaming: '+us

                embed=discord.Embed(title=title,color=0,description=des)
                await ctx.send(embed=embed)

            else:
                await ctx.send('Invalid genre. To know the valid genres, use \'$genre display\'')

    @commands.command(name='movie',help='Gets info by taking movie id')
    async def movie(self,ctx):
        req=int(ctx.message.content[7:])
        res=requests.get('https://api.themoviedb.org/3/movie/{}?api_key=b65a210962422ff226fd2c3ae0546420&language=en-US'.format(req))
        output=json.loads(res.text)
        res2=requests.get('https://api.themoviedb.org/3/movie/{}/watch/providers?api_key=b65a210962422ff226fd2c3ae0546420'.format(req))
        link=json.loads(res2.text)
        title=output['title']
        des='Overview: '+output['overview']+"\nGenre: "
        for gen in output['genres']:
            des+=gen['name']+' '
        des+='\nRelease date: '+output['release_date']+'\nAvg rating: '+str(output['vote_average'])
        watchlink=link['results']['US']['link']
        watchlink=watchlink[0:len(watchlink)-2]
        watchlink+='IN'
        des+='\nOfficial streaming info(INDIA): '+watchlink
        us='https://hdwatch.tv/search/'+'-'.join(title.split(' '))
        des+='\nUnofficial streaming: '+us
        embed=discord.Embed(title=title,color=0,description=des)
        await ctx.send(embed=embed)

    @commands.command(name='latest',help='Fetches latest, upcoming movies')
    async def latest(self,ctx):
        res=requests.get('https://api.themoviedb.org/3/movie/upcoming?api_key=b65a210962422ff226fd2c3ae0546420&language=en-US&page=1')
        list=json.loads(res.text)
        n=10
        des=''
        while n>0:
            des+=str(10-n+1)+'. '+list['results'][10-n]['title']+'\nRelease date: '+list['results'][10-n]['release_date']+'\nAvg rating: '+str(list['results'][10-n]['vote_average'])+'\n'
            n-=1
        embed=discord.Embed(title='Latest/Upcoming movies',color=0,description=des)
        await ctx.send(embed=embed)
