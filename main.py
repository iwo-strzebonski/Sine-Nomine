import discord
import os

from sys import exit, stdout
from discord.ext import commands

PREFIX = '>'

token = str(os.environ.get('TOKEN'))

client = commands.Bot(command_prefix=PREFIX)

@client.event
async def on_ready() :
    await client.change_presence(
        status=discord.Status.active,
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name=PREFIX+'help'
        )
    )
    print('I am online')


@client.command()
async def ping(ctx) :
    await ctx.send(f'🏓 Pong with {str(round(client.latency, 2))}')


@client.command(name='whoami')
async def whoami(ctx) :
    await ctx.send(f'You are {ctx.message.author.name}, {ctx.message.author}')


@client.command()
async def clear(ctx, amount=3) :
    await ctx.channel.purge(limit=amount)


@client.command()
async def kill_bot(ctx):
    await ctx.send('F in chat for meself :(')
    exit()


client.run(token)

print(token)
stdout.flush()
