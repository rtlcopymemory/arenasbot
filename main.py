#!python
import discord
import secret

prefix = 'w.'

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        if (message.content.lower().startswith(prefix + 'startarena')):
          print("Lo sbatti che ho")
          # TODO: take author nickname, create channel with 'username + "_arena"', get time of creation, check for deletion needed

client = MyClient()
client.run(secret.token)