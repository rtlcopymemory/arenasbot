#!python
import discord
import secret
import sqlite3
import threading
import datetime as dt

conn = sqlite3.connect('example.db')

cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS arenas (id INTEGER PRIMARY KEY AUTOINCREMENT, author TEXT, time NUMBER)")

cursor.execute('''
INSERT INTO arenas (author, time) VALUES ('test', 1234)
''')

prefix = 'w.'

def checkDatabaseForDelete():
  conn2 = sqlite3.connect('example.db')
  timeUp = dt.datetime.now() - dt.timedelta(hours=0, minutes=1)
  curr = conn2.cursor()
  curr.execute("SELECT * FROM arenas") # WHERE time < ?", (timeUp.strftime('%Y%m%d%H%M%S'), )
  results = curr.fetchone()
  curr.close()
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
      curr.execute('''
      INSERT INTO arenas (author, time)
      VALUES (?, ?)
      ''', (str(message.author), int(dt.datetime.now().strftime('%Y%m%d%H%M%S'))))
      curr.close()
      print("Ok, inserted {} into database".format(message.author))

client = MyClient()
client.run(secret.token)