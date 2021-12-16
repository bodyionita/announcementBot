import json
import os
import datetime
from datetime import timedelta

import discord
from dateutil.parser import parse
from decouple import config
from discord.ext import tasks
from discord.ext.commands import Bot

import motor.motor_asyncio

from keep_alive import keep_alive
from announcement import Announcement, AnnouncementType, AnnouncementData, create_from_data, create_data
from announcements_manager import AnnouncementsManager

DEFAULT_FREQUENCY = 0.1  # In minutes
DEFAULT_REPETITIONS = 5  # number of repetitions
ALLOWED_ROLES = ['@everyone']

subscribers = {}

token = config('discordBotToken')
mongourl = config('mongodb')
# token = os.environ['discordBotToken']
# mongourl = os.environ['mongodb']


client = motor.motor_asyncio.AsyncIOMotorClient(mongourl)
db = client['stakeborgdao-bot']

configsCollection = db['configs']
announcementsCollection = db['announcements']
subscribersCollection = db['subscribers']

activity = discord.Activity(type=discord.ActivityType.listening, name="$announce help | $help announce")
bot = Bot(command_prefix='$', activity=activity, status=discord.Status.online, description='A bot that makes announcements at certain intervals')
annManager = AnnouncementsManager(announcementsCollection)
lastEntry = datetime.datetime.now()


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    await get_configs()
    await get_db_announcements()
    await get_db_subscribers()


@bot.group(description='Main command')
async def announce(ctx):
    if ctx.invoked_subcommand is None:
        await try_private(ctx, f'No such sub-command exists: **{ctx.subcommand_passed}**')


@announce.command(description='Respond with help page of Announce commands')
async def help(ctx):
    await try_private(ctx, f'''
__Announcement Bot Help page__
*The announcements content can be passed either at the end of the command or by replying the command to the message that you wish to be announced*

`#hot` at the end of a message (or as a reply to another message) creates a default announcement that is broadcasted to all subscribers

`$announce list` - lists current announcements

`$announce subscribe` - susbcribe to the #hot announcements to receive private message when a moderator tags a message with #hot
`$announce unsubscribe` - unsusbcribe from the #hot announcements

`$announce add <how_many> <interval_in_minutes>  <content>` - adds new announcement
    where: 
       **<how_many>** - a number representing how many times the announcement should be printed
       **<interval_in_minutes>** - a number representing how often in minutes it should do so
       **<content>** - if it's not a reply you can pass content as part of the command at the end of it
    examples:   
        `$announce add 40 15` - announce 40 times every 15 minutes the message that you replied to
        `$announce add 20 3`  - announce 20 times every 3 minutes  the message that you replied to
        `$announce add 1 3 whatever is important...`  - announce 1 time every 3 minutes the message "whatever is important..." 

`$announce cancel <id>` - cancels an announcement
    where: 
        **<id>** - a sequence of characters representing the announcement to cancel
    examples: 
        `$announce cancel 36d3f852`
        `$announce cancel 23c9ce39`

    ''')


@announce.command(description='List the current announcements queue')
async def list(ctx):
    tosend = '**__Announcements list__**\n'
    tosend += str(annManager)
    await try_private(ctx, tosend)


@announce.command(description='Cancel an announcement')
async def cancel(ctx, id: str):
    if not authorized(ctx):
        await try_private(ctx, 'You do not have the required role')
    else:
        await annManager.cancel(id, ctx.message)


@announce.command(description='Subscribe to the #hot announcements')
async def subscribe(ctx):
    if ctx.author.id not in subscribers.keys():
        subscribers[ctx.author.id] = ctx.author
        await push_db_subscriber(ctx.author)
        await try_private(ctx, 'You have been subscribed to #hot announcements')


@announce.command(description='Unsubscribe from the #hot announcements')
async def unsubscribe(ctx):
    if ctx.author.id in subscribers.keys():
        subscribers.pop(ctx.author.id)
        await remove_db_subscriber(ctx.author)
        await try_private(ctx, 'You have been unsubscribed from #hot announcements')


@bot.listen('on_message')
async def on_message(message):
    if message.author == bot.user:
        return
    ctx = await bot.get_context(message)
    if not authorized(ctx):
        return  # do not look at non authorized user's messages

    msg = message.content
    if msg.endswith('#hot'):
        msg = msg.replace('#hot', '')
        if message.reference is not None:
            msg = message.reference.resolved.content
        if len(msg) > 0:
            await process_add(ctx, DEFAULT_REPETITIONS, DEFAULT_FREQUENCY, msg, AnnouncementType.Private)


@announce.command(description='Create a new announcement')
async def add(ctx, how_many: int, minutes_interval: float, *, content: str = None):
    if not authorized(ctx):
        await try_private(ctx, 'You do not have the required role')
    else:
        await process_add(ctx, how_many, minutes_interval, content)


async def process_add(ctx, how_many: int, minutes_interval: float, content: str,
                      annType: AnnouncementType = AnnouncementType.Channel):
    final_content = content
    try:
        final_content = ctx.message.reference.resolved.content
    except Exception as e:
        print(e)

    if minutes_interval < 0.5:
        # await error(ctx, 'Frequency too low. It should be at least 30 seconds apart.')
        # return
        pass #todo

    try:
        annData = create_data(final_content, ctx, minutes_interval * 60, how_many, annType)
        an = await create_from_data(bot, annData)
        await annManager.add(an)

    except Exception as e:
        print(e)
        await error(ctx)
        return

    await try_private(ctx, f'New announcement added to my watchlist. Id {an.data.uuid}')


def authorized(ctx):
    try:
        return any(x.name in ALLOWED_ROLES for x in ctx.author.roles)
    except:
        return False  # not allowing private itneraction on secure commands


async def try_private(ctx, content):
    try:
        await ctx.author.send(content)
    except:
        await ctx.reply(
            '*I tried to message you privately but I couldn\'t so now I am printing here.*\n' + content)


async def error(ctx, msg=None):
    await try_private(ctx, f'Command error. {msg if msg is not None else ""}')


async def get_configs():
    pass


async def get_db_announcements():
    results = announcementsCollection.find()
    for result in await results.to_list(length=1000):
        anData = AnnouncementData(result['content'],
                                  result['sleep'],
                                  result['how_many'],
                                  result['annType'],
                                  result['uuid'],
                                  result['messageId'],
                                  result['channelId'],
                                  result['guildId'],
                                  result['requester'],
                                  result['requesterId'])
        ann = await create_from_data(bot, anData)
        await annManager.add(ann, False)


async def get_db_subscribers():
    results = subscribersCollection.find()
    for result in await results.to_list(length=5000):
        userId = result['userId']
        guildId = result['guildId']
        try:
            guild = bot.get_guild(guildId)
            subscribers[userId] = await guild.fetch_member(userId)
        except Exception as e:
            print(e)

async def push_db_subscriber(author):
    try:
        result = await subscribersCollection.insert_one({'userId': author.id, 'name': author.name, 'displayName': author.display_name, 'guild': author.guild.name, 'guildId': author.guild.id })
    except Exception as e:
        print(e)


async def remove_db_subscriber(author):
    try:
        result = await subscribersCollection.delete_many({'userId': author.id})
    except Exception as e:
        print(e)


@tasks.loop(seconds=5)  # task runs every 10 seconds
async def announcements_loop():
    global lastEntry
    time_now = datetime.datetime.now()
    seconds_passed = (time_now - lastEntry).total_seconds()

    await annManager.update(seconds_passed, subscribers)
    lastEntry = time_now


@tasks.loop(seconds=300)  # task runs every 10 seconds
async def config_get_loop():
    global DEFAULT_FREQUENCY
    global DEFAULT_REPETITIONS
    global ALLOWED_ROLES
    results = await configsCollection.find_one({'name': 'default'}, max_time_ms=100)
    DEFAULT_FREQUENCY = results['default_frequency']
    DEFAULT_REPETITIONS = results['default_count']
    ALLOWED_ROLES = results['allowed_roles']

if __name__ == '__main__':
    config_get_loop.start()
    announcements_loop.start()
    # keep_alive()  # empty flask webserver to ping this Replit from an UptimeRobot Monitor and keep it alive
    bot.run(token)
