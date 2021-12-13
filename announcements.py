from announcement import Announcement


class Announcements:

    def __init__(self):
        self.__announcements = {}

    def add(self, an: Announcement):
        self.__announcements[an.uuid] = an

    def remove(self, uuid: str):
        self.__announcements.pop(uuid)

    def remove(self, an: Announcement):
        self.__announcements.pop(an.uuid)

    def __str__(self):
        strbuild = ''
        for an in self.__announcements.values():
            strbuild = strbuild + str(an) + '\n\n'
        return strbuild