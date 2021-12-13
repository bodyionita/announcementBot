import asyncio
import datetime
import time
import uuid
from threading import Thread

import discord
from dateutil.parser import parse

from announcement import Announcement

client = discord.Client()
token = 'OTE5NTQyNjEyNDI2Mzc5Mjg0.YbXUyw.aZpl5Po1Ax97BwDXGMzhFhxMnQU'

announcements = {}

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


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content
    channel = message.channel

    ############################################################################
    ############################################################################
    if msg.startswith('$announce'):
        tokens = msg.split()

        ############################################################################
        if tokens[1].startswith('list'):
            # List all announcements queued
            tosend = 'Announcements list\n'
            for an in announcements.values():
                tosend = tosend + str(an) + '\n\n'
            await channel.send(tosend)

        ############################################################################
        elif tokens[1].startswith('add'):
            try:
                freqString = tokens[2]
                countString = freqString[0:len(freqString)-1]
                count = int(countString)
                granularity = freqString[len(freqString)-1]

                untilDate = parse(tokens[3])

            except Exception as e:
                print(e)
                await error(channel)

            try:
                sleep = calculate_sleep(count, granularity)
                content = message.reference.resolved.content
                an = Announcement(content, channel, sleep, untilDate, message.author)
                announcements[an.uuid] = an

            except Exception as e:
                print(e)
                await error(channel)

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




def calculate_sleep(count, granularity):
    return count * granularityMaping.get(granularity)

async def error(channel, msg = None):
    await channel.send(f'Command format error. {msg if msg is not None else ""}')



client.run(token)

