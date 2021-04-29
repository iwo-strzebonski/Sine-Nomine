from sys import stdout
import os

import discord
import yaml

from discord.ext import commands
from cryptography.fernet import Fernet

PREFIX = '>'

TOKEN = str(os.environ.get('TOKEN'))
KEY = str(os.environ.get('FERNET'))
PATH = os.getcwd()

f = Fernet(KEY)

with open(r'{}/config.yml'.format(PATH)) as file:
    CONFIG = yaml.load(file, Loader=yaml.FullLoader)

bot = commands.Bot(command_prefix=PREFIX)
client = discord.Client()

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name=PREFIX+'help'
        )
    )

    print('I am online')
    print(TOKEN)
    print(KEY)
    print(CONFIG)

    stdout.flush()

@bot.event
async def on_reaction_add(reaction, user):
    if user.name != bot.user.name and str(reaction) == '\N{THUMBS UP SIGN}':
        msg = reaction.message.content
        
        if 'Anonimowe Ogłoszenie' in msg:
            author = msg[msg.find('|')+2:msg.find('\n')-2]
            author = f.decrypt(author.encode()).decode()
            author = int(author)
            print(author)
            stdout.flush()

        elif 'Ogłoszenie' in msg:
            author = msg[msg.find(':')+2:msg.find('\n')]
            author = author.replace('<@', '').replace('>', '')
            author = int(author)
            print(author)
            stdout.flush()


@bot.command()
async def ping(ctx):
    await ctx.send(f'🏓 Pong with {str(round(bot.latency, 2))}')

@bot.command()
async def whoami(ctx):
    await ctx.send(f'You are {ctx.message.author.mention}')

@bot.command(aliases=['purge'])
async def clear(ctx, amount=4):
    if not isinstance(ctx.channel, discord.channel.DMChannel):
        if ctx.author.guild_permissions.administrator:
            await ctx.channel.purge(limit=amount)
        else:
            await ctx.channel.purge(limit=1)
            await ctx.author.send('Nie masz wystarczających uprawnień, aby wykonać to polecenie!')
    else:
        await ctx.author.send('To polecenie może zostać wydane wyłącznie na serwerze!')

@bot.command()
async def msg_emoji(ctx):
    emoji = '\N{THUMBS UP SIGN}'
    msg = await ctx.send('Message')

    await msg.add_reaction(emoji)

@bot.command()
async def announce_anon(ctx):
    if isinstance(ctx.channel, discord.channel.DMChannel):
        await ctx.author.send(
            f'Napisz swoje **ANONIMOWE** ogłoszenie, a gdy skończysz, napisz komendę ' +
            f'**{PREFIX}end**, aby je wysłać!'
        )
    else:
        await ctx.author.send('Ta komenda może być użyta jedynie w prywatnej wiadomości')
        await ctx.channel.purge(limit=1)

@bot.command()
async def announce(ctx):
    if isinstance(ctx.channel, discord.channel.DMChannel):
        await ctx.author.send(
            'Napisz swoje ogłoszenie, a gdy skończysz, napisz komendę ' +
            f'**{PREFIX}end**, aby je wysłać!'
        )
    else:
        await ctx.author.send('Ta komenda może być użyta jedynie w prywatnej wiadomości!')
        await ctx.channel.purge(limit=1)

@bot.command()
async def end(ctx):
    if isinstance(ctx.channel, discord.channel.DMChannel):
        emoji = '\N{THUMBS UP SIGN}'

        limit = 18
        index = -1

        messages = []

        for i in await ctx.channel.history(limit=limit).flatten():
            if not i.author.bot:
                if i.content.startswith(PREFIX + 'announce'):
                    messages.append(i.content)
                    break
                elif not i.content.startswith(PREFIX):
                    messages.append(i.content)

        author = [
            i.author.id
            for i in await ctx.channel.history(limit=limit).flatten()
            if not i.author.bot
        ][0]

        channel = bot.get_channel(CONFIG['announcements'])

        if PREFIX + 'announce_anon' in messages:
            msg = (
                # pylint: disable=f-string-without-interpolation
                f'**__Anonimowe Ogłoszenie od__**:' +
                f'||{f.encrypt(str(author).encode()).decode()}||' +
                '\n' + '\n'.join(messages[:-1])
            )

            mesg = await channel.send(msg)
            await mesg.add_reaction(emoji)

        elif PREFIX + 'announce' in messages:
            msg = (
                f'**__Ogłoszenie od__**: <@{str(author)}>' +
                '\n' + '\n'.join(messages[:-1])
            )

            mesg = await channel.send(msg)
            await mesg.add_reaction(emoji)

    else:
        await ctx.author.send('This command can only be used in DM!')
        await ctx.channel.purge(limit=1)


bot.run(TOKEN)
