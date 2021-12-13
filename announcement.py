import uuid


class Announcement:

    def __init__(self, content, channel, sleep, until, requester):
        self.thread = None
        self.uuid = str(uuid.uuid4())[:8]
        self.content = content
        self.channel = channel
        self.sleep = sleep
        self.until = until
        self.requester = requester
        self.running = False

    def __str__(self):
        minutes = self.sleep / 60
        hours = minutes / 60
        days = hours / 24

        frequency = f'{self.sleep} seconds' if minutes < 1 else (f'{minutes} minutes' if hours < 1  else (f'{hours} hours' if days < 1 else f'{days} days' ))

        return f'\'**{self.content[0:20]}...**\' requested by {self.requester}. ' \
               f'Announces on channel **{self.channel}** every **{frequency}**, until {self.until.strftime("%d/%m/%Y, %H:%M:%S")}. Id: {self.uuid}. '

    # def stop(self):
    #     self.running = False
    #     self.thread.stop()
    #
    # async def start(self):
    #     self.thread = threading.Thread(target=asyncio.run, args=(await self.announce(),))
    #     self.thread.start()
    #
    # async def announce(self):
    #     self.running = True
    #     passed = None
    #
    #     if self.until is None:
    #         passed = datetime.datetime.now() + datetime.timedelta(days=1000)
    #
    #     while datetime.datetime.now() < self.until and self.running is True:
    #         await self.channel.send(self.content)
    #         time.sleep(self.sleep)

