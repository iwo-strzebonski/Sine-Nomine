from sys import stdout
import os

import discord
import yaml

from discord.ext import commands
from cryptography.fernet import Fernet

TOKEN = str(os.environ.get('TOKEN'))
KEY = str(os.environ.get('FERNET'))
PATH = os.getcwd()

USERS = {}

with open(r'{}/config.yml'.format(PATH), 'r') as file:
    CONFIG = yaml.load(file, Loader=yaml.FullLoader)

f = Fernet(KEY)

def get_prefix(_client, message):
    if message.guild is not None:
        return CONFIG['guilds'][message.guild.id]['prefix']
    return '>'

def make_user_list():
    for guild in bot.guilds:
        USERS[guild.id] = guild.members

def add_guild_data(guild):
    CONFIG['guilds'][guild.id] = { 'announcements': None, 'prefix': '>' }


intents = discord.Intents(messages=True, guilds=True, reactions=True)
intents.members = True

bot = commands.Bot(command_prefix=get_prefix, intents=intents)
client = discord.Client(intents=intents, chunk_guilds_at_startup=True)


@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name='Supreme Chancellor'
        )
    )

    print('I am online')
    print(TOKEN)
    print(KEY)
    print(CONFIG)

    for guild in bot.guilds:
        if guild.id not in CONFIG['guilds']:
            add_guild_data(guild)

    with open(r'{}/config.yml'.format(PATH), 'w') as file:
        yaml.dump(CONFIG, file)

    make_user_list()

    for key, value in USERS.items():
        print('=< ' + str(key) + ' >=')
        for member in value:
            print(member)

    stdout.flush()

@bot.event
async def on_guild_join(guild):
    add_guild_data(guild)

    with open(r'{}/config.yml'.format(PATH), 'w') as file:
        yaml.dump(CONFIG, file)

    make_user_list()

@client.event
async def on_guild_remove(guild):
    del CONFIG['guilds'][guild.id]

    with open(r'{}/config.yml'.format(PATH), 'w') as file:
        yaml.dump(CONFIG, file)

    make_user_list()

class MemberEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.name != bot.user.name and str(reaction) == '\N{THUMBS UP SIGN}':
            msg = reaction.message.content

            if 'Ogłoszenie' in msg:
                author = msg[msg.find('|') + 2:msg.find('\n') - 2]
                author = (
                        f.decrypt(author.encode()).decode()
                        if 'Anonimowe Ogłoszenie' in msg
                        else author.replace('<@', '').replace('>', '')
                )
                author = int(author)

                for i in USERS[reaction.message.guild.id]:
                    if i.id == author:
                        await i.send(
                            f'Użytkownik {user.name + "#" + user.discriminator} ||({user.id})|| ' +
                            'jest Tobą zainteresowany!'
                        )
                        break

                stdout.flush()

    @commands.Cog.listener()
    async def on_member_update(self, _before, _after):
        make_user_list()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        make_user_list()
        
        await member.guild.system_channel.send(
            f'Witaj {member.mention} na Serwerze **{member.guild.name}**!{os.linesep}Jednak zanim zaczniesz korzystać z tego serwera, proszę, przeczytaj Regulamin!{os.linesep}Miłego korzystania!'
        )

    @commands.Cog.listener()
    async def on_member_remove(self, _member):
        make_user_list()

class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def return_message(self, ctx, msg=''):
        await ctx.send('Twoja wiadomość to: ' +  msg)

    @commands.command()
    async def msg_emoji(self, ctx):
        emoji = '\N{THUMBS UP SIGN}'
        msg = await ctx.send('Message')

        await msg.add_reaction(emoji)

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def whoami(self, ctx):
        await ctx.send(f'Nazywasz się {ctx.message.author.mention}')

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f':ping_pong: Pong with { str(round(bot.latency, 2)) }')

    @commands.command()
    async def show_config(self, _ctx, message=''):
        if message == KEY:
            print(CONFIG)

        stdout.flush()

class Administration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def users(self, ctx):
        if not isinstance(ctx.channel, discord.channel.DMChannel):
            if ctx.author.guild_permissions.administrator:
                await ctx.send(
                    '\n'.join([(i.name + '#' + i.discriminator) for i in USERS[ctx.guild.id]])
                )
            else:
                await ctx.channel.purge(limit=1)
                await ctx.author.send(
                    'Nie masz wystarczających uprawnień aby wykonać to polecenie!'
                )
        else:
            await ctx.author.send('To polecenie może zostać wydane wyłącznie na serwerze!')

    @commands.command(aliases=['purge'])
    async def clear(self, ctx, amount=4):
        if not isinstance(ctx.channel, discord.channel.DMChannel):
            if ctx.author.guild_permissions.administrator:
                await ctx.channel.purge(limit=amount)
            else:
                await ctx.channel.purge(limit=1)
                await ctx.author.send(
                    'Nie masz wystarczających uprawnień aby wykonać to polecenie!'
                )
        else:
            await ctx.author.send('To polecenie może zostać wydane wyłącznie na serwerze!')

    @commands.command(aliases=['set_announcements', 'sac', 'announcement_channel'])
    async def set_announcement_channel(self, ctx):
        if not isinstance(ctx.channel, discord.channel.DMChannel):
            if ctx.author.guild_permissions.administrator:
                CONFIG['guilds'][ctx.guild.id]['announcements'] = ctx.channel.id

                with open(r'{}/config.yml'.format(PATH), 'w') as file:
                    yaml.dump(CONFIG, file)

                await ctx.send('Ustawiono kanał dla ogłoszeń.')
            else:
                await ctx.channel.purge(limit=1)
                await ctx.author.send(
                    'Nie masz wystarczających uprawnień aby wykonać to polecenie!'
                )
        else:
            await ctx.author.send('To polecenie może zostać wydane wyłącznie na serwerze!')

    @commands.command(pass_context=True, aliases=['prefix'])
    async def change_prefix(self, ctx, prefix):
        if not isinstance(ctx.channel, discord.channel.DMChannel):
            if ctx.author.guild_permissions.administrator:
                CONFIG['guilds'][ctx.guild.id]['prefix'] = prefix

                with open(r'{}/config.yml'.format(PATH), 'w') as file:
                    yaml.dump(CONFIG, file)

                await ctx.send(f'Ustawiono nowy prefix: {prefix}')
            else:
                await ctx.channel.purge(limit=1)
                await ctx.author.send(
                    'Nie masz wystarczających uprawnień aby wykonać to polecenie!'
                )
        else:
            await ctx.author.send('To polecenie może zostać wydane wyłącznie na serwerze!')

class Announcements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def announce_anon(self, ctx):
        '''Po poleceniu podaj nazwę serwera'''
        if isinstance(ctx.channel, discord.channel.DMChannel):
            if ' ' not in ctx.message.content:
                await ctx.author.send('Proszę podać nazwę serwera po spacji po poleceniu!')
                return
            await ctx.author.send(
                'Napisz swoje **ANONIMOWE** ogłoszenie, a gdy skończysz, napisz polecenie **>end**, aby je wysłać!'
            )
        else:
            await ctx.channel.purge(limit=1)
            await ctx.author.send('Ta komenda może być użyta jedynie w prywatnej wiadomości')

    @commands.command()
    async def announce(self, ctx):
        '''Po poleceniu podaj nazwę serwera'''
        if isinstance(ctx.channel, discord.channel.DMChannel):
            if ' ' not in ctx.message.content:
                await ctx.author.send('Proszę podać nazwę serwera po spacji po poleceniu!')
                return
            await ctx.author.send(
                'Napisz swoje ogłoszenie, a gdy skończysz, napisz polecenie **>end**, aby je wysłać!'
            )
        else:
            await ctx.channel.purge(limit=1)
            await ctx.author.send('Ta komenda może być użyta jedynie w prywatnej wiadomości!')

    @commands.command()
    async def end(self, ctx):
        if isinstance(ctx.channel, discord.channel.DMChannel):
            emoji = '\N{THUMBS UP SIGN}'

            limit = 18
            messages = []
            guild_name = None
            channel = None

            for i in await ctx.channel.history(limit=limit).flatten():
                if not i.author.bot:
                    if not i.content.startswith('>'):
                        messages.append(i.content)
                    elif i.content.startswith('>announce'):
                        messages.append(i.content)
                        try:
                            guild_name = i.content[i.content.index(' ') + 1:]
                        except ValueError:
                            await ctx.author.send('Proszę podać nazwę serwera po spacji po poleceniu!')
                            return
                        break

            author = [
                i.author.id
                for i in await ctx.channel.history(limit=limit).flatten()
                if not i.author.bot
            ][0]

            for guild in bot.guilds:
                if guild.name == guild_name:
                    channel = bot.get_channel(CONFIG['guilds'][guild.id]['announcements'])

                    if channel is None:
                        await ctx.author.send('Ten serwer nie ma ustawionego kanału ogłoszeń. Proszę o skontaktowanie się z Administracją.')
                        return
                    break

            if channel is None:
                await ctx.author.send('Podano niepoprawną nazwę serwera!')
                return

            if any('>announce_anon' in string for string in messages):
                msg = (
                    f'**__Anonimowe Ogłoszenie od__**: ||{f.encrypt(str(author).encode()).decode()}||' +
                    '\n' + '\n'.join(messages[:-1])
                )

                mesg = await channel.send(msg)
                await mesg.add_reaction(emoji)

            elif any('>announce' in string for string in messages):
                msg = (
                    f'**__Ogłoszenie od__**: ||<@{str(author)}>||' +
                    '\n' + '\n'.join(messages[:-1])
                )

                mesg = await channel.send(msg)
                await mesg.add_reaction(emoji)

        else:
            await ctx.channel.purge(limit=1)
            await ctx.author.send('Ta komenda może być użyta jedynie w prywatnej wiadomości!')


bot.add_cog(MemberEvents(bot))
bot.add_cog(Test(bot))
bot.add_cog(Administration(bot))
bot.add_cog(Utility(bot))
bot.add_cog(Announcements(bot))


bot.run(TOKEN)
