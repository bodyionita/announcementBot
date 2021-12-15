import discord
from discord.ext.commands import Bot

from announcement import Announcement


class AnnouncementsManager:

    def __init__(self, annCollection):
        self.__announcements = {}
        self.annCollection = annCollection

    async def add(self, an: Announcement, push=True):
        if push:
            await self.push_db_announcement(an.data)
        self.__announcements[an.data.uuid] = an

    async def remove(self, uuid: str):
        await self.remove_db_announcement(uuid)
        self.__announcements.pop(uuid)

    async def push_db_announcement(self, ann):
        try:
            result = await self.annCollection.insert_one(ann.toJson())
        except Exception as e:
            print(e)

    async def remove_db_announcement(self, uuid):
        try:
            result = await self.annCollection.delete_many({'uuid': uuid})
        except Exception as e:
            print(e)

    async def update(self, seconds_passed, subscribers):
        expired_ids = []
        for id,an in self.__announcements.items():
            await an.pass_time(seconds_passed, subscribers)
            if an.expired is True:
                expired_ids.append(id)
        for id in expired_ids:
            await self.remove(id)

    async def cancel(self, id: str, message):
        try:
            await self.remove(id)
        except Exception as e:
            print(e)
            await message.reply(f'Announcement with that id was not found')
        finally:
            await message.reply(f'Cancelled announcement with id **{id}**')

    def __str__(self):
        strbuild = ''
        for an in self.__announcements.values():
            strbuild = strbuild + str(an) + '\n'
        return strbuild