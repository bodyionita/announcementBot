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
        await ctx.reply(f'No such sub-command exists: **{ctx.subcommand_passed}**')


@announce.command(description='Respond with help page of Announce commands')
async def help(ctx):
    await ctx.reply(f'''
__Announcement **Bot** Help page__

Use **$announce** followed by the sub-command

**Attention**: any sequence of characters part of commands should be in-between **"  "** if it contains spaces 

Subcommands:

**$announce add <how_many> <granularity> <date_time>** - adds new announcement
    where: 
       **<how_many>** - a number representing a multiplier for the granularity
       **<granularity>** - a sequence of character(s) from the possible ones 
       *[{' ,'.join(granularityMaping.keys())}]*
       **<date_time>** - a sequence of characters that define a date (non-us format, so no MM/DD/YYYY format)
    examples:   
        $announce add 5 minutes 25Dec2021   
        $announce add 20 M "25Dec2021 08:59"  
        $announce add 1 day 25Dec2022 08:59.435"  

**$announce list** - lists current announcements
    
**$announce cancel <id>** - cancels an announcement
    where: 
        **<id>** - a sequence of characters representing the announcement to cancel
    examples: 
        $announce cancel 36d3f852
        $announce cancel 23c9ce39  
    
    ''')

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
        return

    try:
        content = ctx.message.reference.resolved.content
    except:
        await error(ctx, f'Did not find the replied message to announce. '
                         f'Make sure you "Reply" the message containing the announcement ')
        return

    try:
        sleep = calculate_sleep(how_many, granularity)
    except:
        await error(ctx, f'The granularity did not match any known ones.')
        return

    try:
        an = Announcement(content, ctx, sleep, untilDate, ctx.message.author)
        annManager.add(an)
    except Exception as e:
        print(e)
        await error(ctx)
        return


def calculate_sleep(count, granularity):
    return count * granularityMaping.get(granularity)


async def error(ctx, msg=None):
    await ctx.reply(f'Command error. {msg if msg is not None else ""}')


if __name__ == '__main__':
    token = config('discordBotToken')
    announcements_loop.start()
    bot.run(token)
