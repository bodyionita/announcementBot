import datetime
import json
import uuid


class AnnouncementType:
    Channel = 1,
    Private = 2


class AnnouncementData:

    def __init__(self, content, sleep, how_many, annType, uuid, messageId, channelId, guildId, requester, requesterId):
        self.content = content
        self.sleep = sleep
        self.how_many = how_many
        self.annType = annType
        self.uuid = uuid
        self.messageId = messageId
        self.channelId = channelId
        self.guildId = guildId
        self.requester = requester
        self.requesterId = requesterId

    def toJson(self):
        return {
            'content': self.content,
            'sleep': self.sleep,
            'how_many': self.how_many,
            'annType': self.annType,
            'uuid': self.uuid,
            'messageId': self.messageId,
            'channelId': self.channelId,
            'guildId': self.guildId,
            'requester': self.requester,
            'requesterId': self.requesterId
        }


def create_data(content, ctx, sleep, how_many, annType=AnnouncementType.Channel):
    return AnnouncementData(content,
                            sleep,
                            how_many,
                            annType,
                            str(uuid.uuid4())[:8],
                            ctx.message.id,
                            ctx.channel.id,
                            ctx.guild.id,
                            ctx.author.name,
                            ctx.author.id)


async def create_from_data(bot, data):
    channel = bot.get_channel(data.channelId)
    message = await channel.fetch_message(data.messageId)
    context = await bot.get_context(message)
    return Announcement(context, data)


class Announcement:

    def __init__(self, ctx, data):
        self.data = data
        self.ctx = ctx
        self.expired = False
        self.remaining_seconds = data.sleep
        self.remaining_prints = data.how_many

    async def pass_time(self, seconds, subscribers):
        self.remaining_seconds -= seconds

        if self.remaining_prints <= 0:
            self.expired = True

        if self.remaining_seconds <= 0:
            self.remaining_seconds = self.data.sleep
            self.remaining_prints -= 1
            if not self.expired:
                await self.announce(subscribers)

    async def announce(self, subscribers):
        if self.data.annType is AnnouncementType.Channel:
            await self.ctx.message.channel.send(self.data.content)
        else:
            for sub in subscribers:
                try:
                    await sub.send(f'**#hot** news: {self.data.content}')
                except Exception as e:
                    print(e)

    def __str__(self):
        minutes = self.data.sleep / 60
        hours = minutes / 60
        days = hours / 24

        frequency = f'{self.data.sleep} seconds' if minutes < 1 else (
            f'{minutes} minutes' if hours < 1 else (f'{hours} hours' if days < 1 else f'{days} days'))

        return f'"**{self.data.content[0:20]}...**" requested by {self.data.requester}. ' \
               f'Announces on channel **{self.ctx.message.channel}** every **{frequency}**, ' \
               f'{self.remaining_prints} announces left. Id: {self.data.uuid}. '
