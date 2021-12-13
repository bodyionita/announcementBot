import asyncio
import datetime

from dateutil.parser import parse
from discord.ext import tasks

import discord

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
        'M': MINUTE,
        'H': HOUR,
        'd': DAY,
        'w': WEEK,
        'm': MONTH,
        'y': YEAR}

class DiscordClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.announcements_loop.start()
        self.annManager = AnnouncementsManager()
        self.lastEntry = datetime.datetime.now()

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    @tasks.loop(seconds=3) # task runs every 60 seconds
    async def announcements_loop(self):
        time_now = datetime.datetime.now()
        seconds_passed = (time_now - self.lastEntry).total_seconds()

        await self.annManager.update(seconds_passed, self)



    @announcements_loop.before_loop
    async def before_my_task(self):
        await self.wait_until_ready() # wait until the bot logs in


    async def on_message(self, message):
        if message.author == self.user:
            return
        msg = message.content
        channel = message.channel

        ############################################################################
        ############################################################################
        if msg.startswith('$announce'):
            tokens = msg.split()

            ############################################################################
            if tokens[1].startswith('list'):
                # List all announcements.py queued
                tosend = '**__Announcements list__**\n'
                tosend += str(self.annManager)
                await channel.send(tosend)

            ############################################################################
            elif tokens[1].startswith('add'):
                try:
                    freqString = tokens[2]
                    countString = freqString[0:len(freqString) - 1]
                    count = int(countString)
                    granularity = freqString[len(freqString) - 1]

                    untilDate = parse(tokens[3])

                except Exception as e:
                    print(e)
                    await self.error(channel)

                try:
                    sleep = self.calculate_sleep(count, granularity)
                    content = message.reference.resolved.content
                    an = Announcement(content, channel, sleep, untilDate, message.author)
                    self.annManager.add(an)

                except Exception as e:
                    print(e)
                    await self.error(channel)

            ############################################################################
            elif tokens[1].startswith('cancel'):
                await channel.send('Not implemented error')

            ############################################################################
            elif tokens[1].startswith('help'):
                await channel.send('''Announcements help
                Examples:  
                $announce add 1h 15dec2021
                $announce list
                $announce list 4 
                $announce help
                $announce cancel 5''')

    def calculate_sleep(self, count, granularity):
        return count * granularityMaping.get(granularity)

    async def error(self, channel, msg=None):
        await channel.send(f'Command format error. {msg if msg is not None else ""}')