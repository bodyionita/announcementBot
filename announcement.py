import datetime
import uuid


class AnnouncementType:
    Channel = 1,
    Private = 2


class Announcement:

    def __init__(self, content, ctx, sleep, how_many, requester, annType = AnnouncementType.Channel):
        self.annType = annType
        self.uuid = str(uuid.uuid4())[:8]
        self.content = content
        self.ctx = ctx
        self.sleep = sleep
        self.how_many = how_many
        self.requester = requester
        self.expired = False
        self.remaining_seconds = sleep
        self.remaining_prints = how_many

    async def pass_time(self, seconds, subscribers):
        self.remaining_seconds -= seconds

        if self.remaining_prints <= 0:
            self.expired = True

        if self.remaining_seconds <= 0:
            self.remaining_seconds = self.sleep
            self.remaining_prints -= 1
            if not self.expired:
                await self.announce(subscribers)

    async def announce(self, subscribers):
        if self.annType is AnnouncementType.Channel:
            await self.ctx.message.channel.send(self.content)
        else:
            for sub in subscribers:
                await sub.send(f'New **#hot**: {self.content}')

    def __str__(self):
        minutes = self.sleep / 60
        hours = minutes / 60
        days = hours / 24

        frequency = f'{self.sleep} seconds' if minutes < 1 else (
            f'{minutes} minutes' if hours < 1 else (f'{hours} hours' if days < 1 else f'{days} days'))

        return f'"**{self.content[0:20]}...**" requested by {self.requester}. ' \
               f'Announces on channel **{self.ctx.message.channel}** every **{frequency}**, ' \
               f'{self.remaining_prints} announces left. Id: {self.uuid}. '
