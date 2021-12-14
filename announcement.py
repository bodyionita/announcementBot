import datetime
import uuid


class Announcement:

    def __init__(self, content, ctx, sleep, requester, until=datetime.datetime(2023, 1, 1)):
        self.uuid = str(uuid.uuid4())[:8]
        self.content = content
        self.ctx = ctx
        self.sleep = sleep
        self.until = until
        self.requester = requester
        self.expired = False
        self.remaining_seconds = sleep

    async def pass_time(self, seconds):
        self.remaining_seconds -= seconds

        if datetime.datetime.now() >= self.until:
            self.expired = True
        if self.remaining_seconds <= 0:
            self.remaining_seconds = self.sleep
            if not self.expired:
                await self.ctx.message.channel.send(self.content)

    def __str__(self):
        minutes = self.sleep / 60
        hours = minutes / 60
        days = hours / 24

        frequency = f'{self.sleep} seconds' if minutes < 1 else (
            f'{minutes} minutes' if hours < 1 else (f'{hours} hours' if days < 1 else f'{days} days'))

        return f'"**{self.content[0:20]}...**" requested by {self.requester}. ' \
               f'Announces on channel **{self.ctx.message.channel}** every **{frequency}**, ' \
               f'until {self.until.strftime("%d/%m/%Y, %H:%M:%S")}. Id: {self.uuid}. '
