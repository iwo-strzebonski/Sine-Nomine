import discord
import os

from sys import stdout
from discord.ext import commands

PREFIX = '>'

token = str(os.environ.get('TOKEN'))

client = commands.Bot(command_prefix=PREFIX)

@client.event
async def on_ready() :
    await client.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name=PREFIX+'help'
        )
    )
    print('I am online')
    print(token)
    stdout.flush()


@client.command()
async def ping(ctx):
    await ctx.send(f'🏓 Pong with {str(round(client.latency, 2))}')


@client.command(name='whoami')
async def whoami(ctx):
    await ctx.send(f'You are {ctx.message.author.mention}')


@client.command()
async def clear(ctx, amount=4):
    await ctx.channel.purge(limit=amount)


client.run(token)
