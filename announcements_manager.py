import discord

from announcement import Announcement


class AnnouncementsManager:

    def __init__(self):
        self.__announcements = {}

    def add(self, an: Announcement):
        self.__announcements[an.uuid] = an

    def remove(self, uuid: str):
        self.__announcements.pop(uuid)

    def remove(self, an: Announcement):
        self.__announcements.pop(an.uuid)

    async def update(self, seconds_passed, client: discord.Client):
        expired_ids = []
        for id,an in self.__announcements.items():
            await an.pass_time(seconds_passed)
            if an.expired is True:
                expired_ids.append(id)
        for id in expired_ids:
            self.__announcements.pop(id)

    def __str__(self):
        strbuild = ''
        for an in self.__announcements.values():
            strbuild = strbuild + str(an) + '\n'
        return strbuild