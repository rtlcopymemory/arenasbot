#!python
import discord
import secret
import sqlite3
import threading
import datetime as dt

conn = sqlite3.connect('example.db', detect_types=sqlite3.PARSE_DECLTYPES)

conn.execute("CREATE TABLE IF NOT EXISTS arenas (id INTEGER PRIMARY KEY AUTOINCREMENT, author TEXT, time DATETIME DEFAULT CURRENT_TIMESTAMP)")

prefix = 'w.'

def checkDatabaseForDelete():
    timeUp = dt.datetime.now() - dt.timedelta(hours=1, minutes=0)
    curr = conn.cursor()
    curr.execute("SELECT * FROM arenas WHERE time < ?", timeUp)
    results = curr.fetchall()
    print(results)
    threading.Timer(20.0, checkDatabaseForDelete).start()

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        checkDatabaseForDelete()

    async def on_message(self, message):
        if (message.content.lower().startswith(prefix + 'startarena')):
          print("Lo sbatti che ho")
          curr = conn.cursor()
          curr.execute(u'''
          INSERT INTO arenas (author)
          VALUES ('{}')
          '''.format(message.author))
          print("Ok, inserted {} into database".format(message.author))

client = MyClient()
client.run(secret.token)