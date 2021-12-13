import time

from dateutil.parser import parse
from decouple import config
from discord_client import DiscordClient
from announcement import Announcement
from announcements import Announcements

client = DiscordClient()
token = config('discordBotToken')
client.run(token)








