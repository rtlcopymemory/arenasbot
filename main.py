#!python
import discord
import secret
import sqlite3

conn = sqlite3.connect('example.db')

conn.execute("CREATE TABLE IF NOT EXISTS arenas (id INTEGER PRIMARY KEY AUTOINCREMENT, author TEXT, time DATETIME DEFAULT CURRENT_TIMESTAMP)")

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