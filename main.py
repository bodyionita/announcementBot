import datetime

from dateutil.parser import parse
from decouple import config
from discord.ext import tasks
from discord.ext.commands import Bot

from announcement import Announcement
from announcements_manager import AnnouncementsManager

SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
WEEK = 7 * DAY
MONTH = 29 * DAY
YEAR = 12 * MONTH

granularityMaping = {
    'S': SECOND,
    'minute': MINUTE,
    'minutes': MINUTE,
    'Minute': MINUTE,
    'Minutes': MINUTE,
    'M': MINUTE,
    'hour': HOUR,
    'hours': HOUR,
    'Hour': HOUR,
    'Hours': HOUR,
    'H': HOUR,
    'day': DAY,
    'days': DAY,
    'd': DAY,
    'week': WEEK,
    'weeks': WEEK,
    'w': WEEK,
    'month': MONTH,
    'months': MONTH,
    'm': MONTH}

bot = Bot(command_prefix='$', description='A bot that makes announcements at certain intervals')
annManager = AnnouncementsManager()
lastEntry = datetime.datetime.now()


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@tasks.loop(seconds=3)  # task runs every 60 seconds
async def announcements_loop():
    time_now = datetime.datetime.now()
    seconds_passed = (time_now - lastEntry).total_seconds()

    await annManager.update(seconds_passed)


@bot.group(description='Main command')
async def announce(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send(f'No such sub-command exists: **{ctx.subcommand_passed}**')


@announce.command(description='List the current announcements queue')
async def list(ctx):
    tosend = '**__Announcements list__**\n'
    tosend += str(annManager)
    await ctx.reply(tosend)


@announce.command(description='Cancel an announcement')
async def cancel(ctx, id: str):
    await annManager.cancel(id, ctx.message)


@announce.command(description='Create a new announcement')
async def add(ctx, how_many: int, granularity: str, date_time: str):
    try:
        untilDate = parse(date_time)

    except Exception as e:
        print(e)
        await error(ctx, f'Could not understand the date "{date_time}"')

    try:
        content = ctx.message.reference.resolved.content
    except:
        await error(ctx, f'Did not find the replied message to announce. '
                         f'Make sure you "Reply" the message containing the announcement ')

    try:
        sleep = calculate_sleep(how_many, granularity)
    except:
        await error(ctx, f'The granularity did not match any known ones.')

    try:
        an = Announcement(content, ctx, sleep, untilDate, ctx.message.author)
        annManager.add(an)
    except Exception as e:
        print(e)
        await error(ctx)


def calculate_sleep(count, granularity):
    return count * granularityMaping.get(granularity)


async def error(ctx, msg=None):
    await ctx.reply(f'Command error. {msg if msg is not None else ""}')


if __name__ == '__main__':
    token = config('discordBotToken')
    announcements_loop.start()
    bot.run(token)
