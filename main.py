from decouple import config
from discord_client import DiscordClient

if __name__ == '__main__':
    client = DiscordClient()
    token = config('discordBotToken')
    client.run(token)










