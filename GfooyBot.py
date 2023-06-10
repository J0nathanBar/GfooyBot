import asyncio
import discord
from discord.ext import commands
import re
from BotConf import TOKEN
import mongobongo
import DawnFrager
import socket
from datetime import datetime, timedelta
import aiocron

mongo = mongobongo.BongoMongo()
intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
triggers = []


def start_bot():
    bot.run(TOKEN)


def subs(string, sub):
    pattern = '^' + re.escape(sub) + '*$'
    return bool(re.match(pattern, string))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.reply("Command not found.")

    else:
        await ctx.reply(f'Error: {error}')


async def send_scheduled_messages():
    print('seccces')
    current_time = datetime.now()
    users_collection = mongo.db['users']
    users = users_collection.find(
        {'messages': {'$elemMatch': {'send_time': {'$lt': current_time.isoformat()}, 'sent': False}}})
    print(users.count())
    for user in users:
        print(user['uid'])
    #     for message in user['messages']:
    #         send_time = datetime.fromisoformat(message['send_time'])
    #         if send_time <= current_time:
    #             target_user = bot.get_user(user['id'])
    #             target_channel = bot.get_channel(int(message['channel_id']))
    #             await target_user.send(message['text'], target_channel)
    #             message['sent'] = True
    #     users_collection.replace_one({'id': user['id']}, user)


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    print(f'we are currently in the fixed reason update')
    # aiocron.crontab('* * * * *', func=send_scheduled_messages, start=True)
    await update_triggers_cache()

    try:
        synced = await bot.tree.sync()
        print(f'synced {len(synced)} commands')
    except Exception as e:
        print(f'Error syncing command: {e}')


async def update_triggers_cache():
    while True:
        # Update triggers cache with fresh data from the database
        triggers.clear()
        triggers.extend(mongo.get_triggers())
        print("Triggers cache updated")
        # Wait for 1 hour before updating again
        await asyncio.sleep(3600)


@bot.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.name == 'general' or channel.name == 'general-chat':
            await display_about(channel)
            break


async def admin_command(ctx):
    uid = ctx.author.id
    if mongo.is_admin(uid):
        return True
    else:
        await permission_denied(ctx)
        return False


@bot.command(help='generic info about the bot')
async def about(ctx):
    await display_about(ctx.channel)


async def display_about(channel):
    bot_name = "Gfooy bot"
    bot_description = "Was designed to imitate the gfooy experience use !help or try pinging me to do stuff"
    bot_version = "1.0"
    embed = discord.Embed(title=bot_name, description=bot_description, color=discord.Color.blue())
    embed.add_field(name="Version", value=bot_version)
    await channel.send(embed=embed)


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


@bot.command(help='adds more custom made replies to the database, takes a discord id and a reply as arguments')
async def add_reply(ctx, dest_uid: str, reply: str):
    if await admin_command(ctx):
        if mongo.add_reply(uid=dest_uid, reply=reply):
            await ctx.send('added reply successfully!')
        else:
            await ctx.send('there was an error processing your request!')


@bot.command(help='adds more custom made replies to the database,takes a discord id and a nickname as arguments')
async def add_nickname(ctx, dest_uid: str, nickname: str):
    if await admin_command(ctx):
        if mongo.add_nickname(uid=dest_uid, nickname=nickname):
            await ctx.send('added nickname successfully!')
        else:
            await ctx.send('there was an error processing your request!')


@bot.command(help='adds another user to the database')
async def add_user(ctx):
    try:
        if await admin_command(ctx):
            await ctx.send('name: ')
            name = (await user_input(ctx)).content
            await ctx.send('user id: ')
            new_uid = (await user_input(ctx)).content
            await ctx.send('affiliated group:')
            group = (await user_input(ctx)).content
            nicknames = await new_user_nicknames(ctx)
            replies = await new_user_replies(ctx)
            reasons = await new_user_reasons(ctx)
            user = DawnFrager.User(_id=new_uid, replies=replies, nicknames=nicknames, group=group, name=name,reasons=reasons)
            while True:
                await display_user(ctx, user)
                res = (await user_input(ctx)).content.upper()
                if res == 'YES':
                    await ctx.send(mongo.add_user(user))
                    break
                elif res == 'NO':
                    await ctx.reply('operation stopped by user!')
                    break

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
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return
    mentioned_users = message.mentions
    for user in mentioned_users:
        await was_mentioned(message, user)
    upper = message.content.upper()
    if bot.user.mentioned_in(message):
        await on_mentioned(message)
    if subs(upper, 'E'):
        await message.channel.send(upper + 'E')
    if 'WOMEN' in upper and 'RIGHT' in upper and not is_substring_between(upper, 'WOMEN', 'RIGHT', 'NO'):
        await message.channel.send(
            'it seems you have mentioned women\'s rights without a no in the middle. it seems like a mistake',
            reference=message)
    for trigger in triggers:
        if trigger in upper:
            reply = mongo.get_trigger_reply(trigger)
            await message.channel.send(reply, reference=message)
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
    embed.add_field(name='reasons', value=user.get_reasons())
    await ctx.send(embed=embed)


@bot.command(help='displays user profiles, use by !show_user [discord id]')
async def show_user(ctx, uid):
    if await admin_command(ctx):
        user = mongo.get_user(uid)
        if user:
            await user_display(ctx, user)
        else:
            await ctx.reply('user doesnt exist')


@bot.command(help='shows all users')
async def show_users(ctx):
    if await admin_command(ctx):
        users = mongo.get_users()
        print(users)
        for user in users:
            await user_display(ctx, user)


async def user_display(ctx, user):
    embed = discord.Embed(title=user['name'],
                          description='A user in the database',
                          color=discord.Color.blue())
    embed.add_field(name='id', value=user['uid'])
    embed.add_field(name='group', value=user['group'])
    embed.add_field(name='nicknames', value=user['nicknames'])
    embed.add_field(name='replies', value=user['replies'])
    embed.add_field(name='reason', value=user['reasons'])
    await ctx.send(embed=embed)


async def permission_denied(ctx):
    nickname = mongo.get_nickname(mongo.get_user(ctx.author.id))
    await ctx.reply(f'{nickname} wtf are you trying to do??? permission denied bitch')


async def new_user_reasons(ctx):
    reasons = ['']
    while True:
        await ctx.send('enter reasons, input stop to stop, use "" if necessary')
        reason = await user_input(ctx)
        if 'STOP' in reason.content.upper():
            break
        reasons.append(reason.content)
    return reasons


@bot.tree.command(name='hello')
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message('hello there!')


@bot.command()
async def echo(ctx: commands.Context):
    print(ctx.message.content)
    await ctx.send(f'{ctx.message.content} eee')


@bot.command(hidden=True, help='gets the ip')
async def get_ip(ctx):
    ip_name = socket.gethostname()
    ip_addr = socket.gethostbyaddr(ip_name)
    await ctx.send(f'host name: {ip_name} address{ip_addr}')


@bot.command(name='add_wisdom', help='add a wisdom to the pull of wisdoms. use by !add_wisdom [wisdom]')
async def add_wisdom(ctx, wisdom):
    if await admin_command(ctx):
        if mongo.add_wisdom(wisdom):
            await ctx.send('Wisdom added successfully!')
        else:
            ctx.reply('something went wrong')


async def was_mentioned(message, user):
    if user.status == discord.Status.offline:
        mong_usr = mongo.get_user(user.id)
        reason = mongo.get_reason(mong_usr)
        if reason == '':
            print(f'no reason found')
            return
        nickname = mongo.get_nickname(mong_usr)
        await message.channel.send(f'{nickname} is {reason} and thus is unavailable',
                                   reference=message)


@bot.command(help='adds triggers to the system\nuse by !add_trigger [trigger] [reply]')
async def add_trigger(ctx, trigger: str, reply: str):
    if await admin_command(ctx):
        if mongo.add_trigger(trigger=trigger, reply=reply):
            await ctx.send('added trigger successfully!')
        else:
            await ctx.send('there was an error processing your request!')


@bot.command()
async def schedule_message(ctx, user_id, message_text, channel_id, date, time):
    send_time_input = f"{date} {time}"
    try:
        send_time = datetime.fromisoformat(send_time_input)
    except ValueError:
        await ctx.send("Invalid format. Please use the format YYYY-MM-DD HH:MM for date and time.")
        return

    if mongo.add_message(user_id, message_text, channel_id, send_time):
        await ctx.send(f"Message scheduled for user {user_id} at {send_time}.")
    else:
        await ctx.send('something went wrong')


@bot.command(help='adds a reason for being offline\n use by !add_reason [uid] [reason]')
async def add_reason(ctx, uid, reason):
    if await admin_command(ctx):
        if mongo.add_reason(uid=uid, reason=reason):
            await ctx.send('added reason successfully!')
        else:
            await ctx.send('there was an error processing your request!')
