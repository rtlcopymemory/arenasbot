#!python
import discord
import secret
import sqlite3
import threading
import datetime as dt

conn = sqlite3.connect('example.db')

cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS arenas (id INTEGER PRIMARY KEY AUTOINCREMENT, author TEXT, time INTEGER)")
cursor.close()
conn.commit()
conn.close()

prefix = 'w.'

def checkDatabaseForDelete():
  conn2 = sqlite3.connect('example.db')
  timeUp = dt.datetime.now() - dt.timedelta(hours=0, minutes=1)
  curr = conn2.cursor()
  curr.execute("SELECT * FROM arenas WHERE time < ?", (timeUp.strftime('%Y%m%d%H%M%S'), ))
  results = curr.fetchall()
  curr.close()
  conn2.close()
  print(results)
  threading.Timer(20.0, checkDatabaseForDelete).start()

class MyClient(discord.Client):
  async def on_ready(self):
    print('Logged on as {0}!'.format(self.user))
    checkDatabaseForDelete()

  async def on_message(self, message):
    if (message.content.lower().startswith(prefix + 'startarena')):
      print("Lo sbatti che ho")
      # SQL STUFF
      conn = sqlite3.connect('example.db') # open database
      curr = conn.cursor() # create cursor
      curr.execute('''
        INSERT INTO arenas (author, time)
        VALUES (?, ?)
      ''', (str(message.author), int(dt.datetime.now().strftime('%Y%m%d%H%M%S')))) # Insert into table with automatic ID, author nick and timestamp as '20190420130059'
      curr.close()
      conn.commit() # ALWAYS remember to commit before closing the connection
      conn.close()
      # END SQL STUFF
      print("Ok, inserted {} into database".format(message.author))

client = MyClient()
client.run(secret.token)