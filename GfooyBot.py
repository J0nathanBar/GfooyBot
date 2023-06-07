import asyncio
import discord
from discord.ext import commands
import re
from BotConf import TOKEN
import mongobongo
import DawnFrager
from discord import app_commands
import socket

mongo = mongobongo.BongoMongo()
intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


def start_bot():
    bot.run(TOKEN)


def subs(string, sub):
    pattern = '^' + re.escape(sub) + '*$'
    return bool(re.match(pattern, string))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found.")
    else:
        # Handle other types of errors
        print(f'Error: {error}')


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'synced {len(synced)} commands')
    except Exception as e:
        print(f'Error syncing command: {e}')


@bot.command(help='generic info about the bot')
async def about(ctx):
    bot_name = "Gfooy bot"
    bot_description = "Was designed to imitate the gfooy experience"
    bot_version = "1.0"
    embed = discord.Embed(title=bot_name, description=bot_description, color=discord.Color.blue())
    embed.add_field(name="Version", value=bot_version)
    await ctx.send(embed=embed)


@bot.command(help='test your iq')
async def iq_test(ctx):
    await ctx.send('How much is 72²?')
    try:
        answer = await user_input(ctx)
        if not answer.content.isdigit():
            raise ValueError('hahaha you stupid!!! the answer is a number! you have -1 iq.')
        if int(answer.content) == 72 ** 2:
            await ctx.send('you have ' + str(74 ** 2) + ' iq! you are a genius only second to Roee Eshel himself!')
        else:
            await ctx.send('wrong!!!!! you so stupid!!!! 7 iq')
    except asyncio.TimeoutError:
        await ctx.reply('Timeout: You took too long to respond.')
    except ValueError as e:
        await ctx.send(str(e))


@bot.command(help='brings to the worlds Gfooy\'s wisodm through his pre-programmed words')
async def words_of_wisdom(ctx):
    await ctx.send(mongo.get_wisdom())


@bot.command(help='adds more custom made replies to the database')
async def add_reply(ctx, dest_uid: str, reply: str):
    uid = ctx.author.id
    admin = mongo.is_admin(uid)
    if admin:
        if mongo.add_reply(uid=dest_uid, reply=reply):
            await ctx.send('added reply successfully!')
        else:
            await ctx.send('there was an error processing your request!')
    else:
        await permission_denied(ctx)


@bot.command(help='adds more custom made replies to the database')
async def add_nickname(ctx, dest_uid: str, nickname: str):
    uid = ctx.author.id
    admin = mongo.is_admin(uid)
    if admin:
        if mongo.add_nickname(uid=dest_uid, nickname=nickname):
            await ctx.send('added nickname successfully!')
        else:
            await ctx.send('there was an error processing your request!')
    else:
        await permission_denied(ctx)


@bot.command(help='adds another user to the database')
async def add_user(ctx):
    try:
        uid = ctx.author.id
        if mongo.is_admin(uid):
            await ctx.send('name: ')
            name = (await user_input(ctx)).content
            await ctx.send('user id: ')
            new_uid = (await user_input(ctx)).content
            await ctx.send('affiliated group:')
            group = (await user_input(ctx)).content
            nicknames = await new_user_nicknames(ctx)
            replies = await new_user_replies(ctx)
            user = DawnFrager.User(_id=new_uid, replies=replies, nicknames=nicknames, group=group, name=name)
            while True:
                await display_user(ctx, user)
                res = (await user_input(ctx)).content.upper()
                if res == 'YES':
                    await ctx.send(mongo.add_user(user))
                    break
                elif res == 'NO':
                    await ctx.reply('operation stopped by user!')
                    break
        else:
            await permission_denied(ctx)
    except asyncio.TimeoutError:
        await ctx.reply('Timeout: You took too long to respond.')


async def new_user_nicknames(ctx):
    nicknames = ['']
    while True:
        await ctx.send('enter nicknames, input stop to stop, use "" if necessary')
        nickname = await user_input(ctx)
        if 'STOP' == nickname.content.upper():
            break
        nicknames.append(nickname.content)
    return nicknames


async def new_user_replies(ctx):
    replies = ['']
    while True:
        await ctx.send('enter replies, input stop to stop, use "" if necessary')
        reply = await user_input(ctx)
        if 'STOP' in reply.content.upper():
            break
        replies.append(reply.content)
    return replies


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    uppered = message.content.upper()
    if bot.user.mentioned_in(message):
        await on_mentioned(message)
    elif subs(uppered, 'E'):
        await message.channel.send(uppered + 'E')
    elif 'EGG' in uppered:
        await message.channel.send('I like eggy weggy')
    if 'WOMEN' in uppered and 'RIGHT' in uppered and not is_substring_between(uppered, 'WOMEN', 'RIGHT', 'NO'):
        await message.channel.send(
            'it seems you have mentioned women\'s rights without a no in the middle. it seems like a mistake',
            reference=message)
    if 'HELLO THERE' in uppered:
        await message.channel.send('General Kenobi', reference=message)
    await bot.process_commands(message)


async def user_input(ctx):
    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel

    try:
        answer = await bot.wait_for('message', check=check, timeout=30)
    except asyncio.TimeoutError as e:
        raise e
    return answer


async def on_mentioned(message):
    uid = message.author.id
    await message.channel.send(mongo.mentioned(uid), reference=message)


def is_substring_between(string, start_substring, end_substring, substring):
    start_index = string.find(start_substring)
    end_index = string.find(end_substring)
    if start_index != -1 and end_index != -1 and start_index < end_index:
        substring_index = string.find(substring, start_index + len(start_substring), end_index)
        if substring_index != -1:
            return True
    return False


async def display_user(ctx, user):
    embed = discord.Embed(title=user.get_name(),
                          description='A user in the database press YES to continue and NO to stop',
                          color=discord.Color.blue())
    embed.add_field(name='id', value=user.get_id())
    embed.add_field(name='group', value=user.get_group())
    embed.add_field(name='nicknames', value=user.get_nicknames())
    embed.add_field(name='replies', value=user.get_replies())
    await ctx.send(embed=embed)


@bot.command(help='displays user profiles')
async def show_user(ctx, uid):
    if mongo.is_admin(ctx.author.id):
        user = mongo.get_user(uid)
        if user:
            await user_display(ctx, user)
        else:
            await ctx.reply('user doesnt exist')

    else:
        await permission_denied(ctx)


@bot.command(help='show all users')
async def show_users(ctx):
    if mongo.is_admin(ctx.author.id):
        users = mongo.get_users()
        print(users)
        for user in users:
            await user_display(ctx, user)
    else:
        await permission_denied(ctx)


async def user_display(ctx, user):
    embed = discord.Embed(title=user['name'],
                          description='A user in the database',
                          color=discord.Color.blue())
    embed.add_field(name='id', value=user['uid'])
    embed.add_field(name='group', value=user['group'])
    embed.add_field(name='nicknames', value=user['nicknames'])
    embed.add_field(name='replies', value=user['replies'])
    await ctx.send(embed=embed)


async def permission_denied(ctx):
    nickname = mongo.get_nickname(mongo.get_user(ctx.author.id))
    await ctx.reply(f'{nickname} wtf are you trying to do??? permission denied bitch')


@bot.tree.command(name='hello')
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message('hello there!')


@bot.command(hidden=True)
async def get_ip(ctx):
    ip_name = socket.gethostname()
    ip_addr = socket.gethostbyaddr(ip_name)
    await ctx.send(f'host name: {ip_name} address{ip_addr}')


@bot.command(name='add_wisdom', help='add a wisdom to the pull of wisdoms. use by !add_wisdom [wisdom]')
async def add_wisdom(ctx, wisdom):
    if await admin_command(ctx):
        mongo.add_wisdom(wisdom)


async def admin_command(ctx):
    uid = ctx.author.id
    admin = mongo.is_admin(uid)
    if admin:
        return True
    else:
        await permission_denied(ctx)
        return False
