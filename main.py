import os
import datetime
from datetime import timedelta

from dateutil.parser import parse
from decouple import config
from discord.ext import tasks
from discord.ext.commands import Bot

from keep_alive import keep_alive
from announcement import Announcement
from announcements_manager import AnnouncementsManager


bot = Bot(command_prefix='$', description='A bot that makes announcements at certain intervals')
annManager = AnnouncementsManager()
lastEntry = datetime.datetime.now()

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.group(description='Main command')
async def announce(ctx):
    if ctx.invoked_subcommand is None:
        await try_private(ctx, f'No such sub-command exists: **{ctx.subcommand_passed}**')


@announce.command(description='Respond with help page of Announce commands')
async def help(ctx):
    await try_private(ctx, f'''
__Announcement **Bot** Help page__

Use **$announce** followed by the sub-command

**Attention**: any sequence of characters part of commands should be in-between **"  "** if it contains spaces 

Subcommands:

**$announce add <how_many> <granularity> <date_time>** - adds new announcement
    where: 
       **<how_many>** - a number representing how many times the announcement should be printed
       **<interval_in_minutes>** - a number representing how often in minutes it should do so
    examples:   
        $announce add 40 15 - announce 40 times every 15 minutes
        $announce add 20 3  - announce 20 times every 3 minutes

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
    await try_private(ctx,tosend)


@announce.command(description='Cancel an announcement')
async def cancel(ctx, id: str):
    allowed = any(x.name == '@everyone' for x in ctx.message.author.roles)
    if not allowed:
        await try_private(ctx,'You do not have the required role')
    else:
        await annManager.cancel(id, ctx.message)

@announce.command(description='Create a new announcement')
async def add(ctx, how_many: int, minutes_interval: float, *, content: str=None):
    allowed = any(x.name == '@everyone' for x in ctx.message.author.roles)
    if not allowed:
        await try_private(ctx, 'You do not have the required role')
    else:
        final_content = content
        try:
            final_content = ctx.message.reference.resolved.content
        except:
            pass
            # await error(ctx, f'Did not find the replied message to announce. '
            #                  f'Make sure you "Reply" the message containing the announcement ')
            # return  
        if minutes_interval < 0.5:
            await error(ctx, 'Frequency too low. It should be at least 30 seconds apart.')
            #return

        total_minutes = minutes_interval * how_many
        until = datetime.datetime.now()+timedelta(minutes=total_minutes)
        try:
            an = Announcement(final_content, ctx, minutes_interval*60, how_many, ctx.message.author, until)
            annManager.add(an)
        except Exception as e:
            print(e)
            await error(ctx)
            return

        await try_private(ctx, f'New announcement added to my watchlist. Id {an.uuid}')


async def try_private(ctx, content):
  try:
    await ctx.message.author.send(content)
  except:
    await ctx.reply('I tried to message you privately but I couldn\'t so now I am printing here. Message:' + content)


async def error(ctx, msg=None):
    await try_private(ctx, f'Command error. {msg if msg is not None else ""}')


@tasks.loop(seconds=5)  # task runs every 10 seconds
async def announcements_loop():
    global lastEntry
    time_now = datetime.datetime.now()
    seconds_passed = (time_now - lastEntry).total_seconds()

    await annManager.update(seconds_passed)
    lastEntry = time_now

if __name__ == '__main__':
    token = os.environ['discordBotToken']
    #token = config('discordBotToken')
    announcements_loop.start()
    keep_alive() # empty flask webserver to ping this Replit from an UptimeRobot Monitor and keep it alive
    bot.run(token)
