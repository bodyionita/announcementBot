import discord
from discord.ext.commands import Bot

from announcement import Announcement


class AnnouncementsManager:

    def __init__(self):
        self.__announcements = {}

    def add(self, an: Announcement):
        self.__announcements[an.data.uuid] = an

    def remove(self, uuid: str):
        self.__announcements.pop(uuid)

    async def update(self, seconds_passed, subscribers):
        expired_ids = []
        for id,an in self.__announcements.items():
            await an.pass_time(seconds_passed, subscribers)
            if an.expired is True:
                expired_ids.append(id)
        for id in expired_ids:
            self.remove(id)

    async def cancel(self, id: str, message):
        try:
            self.remove(id)
        except:
            await message.reply(f'Announcement with that id was not found')
        finally:
            await message.reply(f'Cancelled announcement with id **{id}**')

    def __str__(self):
        strbuild = ''
        for an in self.__announcements.values():
            strbuild = strbuild + str(an) + '\n'
        return strbuild