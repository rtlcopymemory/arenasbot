#!python
import discord
import secret
import sqlite3
import datetime as dt
import asyncio
import re

conn = sqlite3.connect('example.db')

cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS arenas (id INTEGER PRIMARY KEY AUTOINCREMENT, channelID INTEGER, author TEXT, authorID INTEGER, time INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS servers (id INTEGER PRIMARY KEY AUTOINCREMENT, serverID INTEGER, categoryID INTEGER)")
cursor.close()
conn.commit()
conn.close()

prefix = 'w.'
serverName = "Sargasso - Wolf SSBU"
arenaChatsCatName = 'arena chats'

class MyClient(discord.Client):
  # Method called every 20 seconds to check if any arena has to be deleted. It gets first called on Discord's on_ready function
  # async def checkDatabaseForDelete(self):
  #   while True:
  #     conn2 = sqlite3.connect('example.db')
  #     timeUp = dt.datetime.now() - dt.timedelta(hours=1, minutes=0) # timeout arenas
  #     curr = conn2.cursor()
  #     curr.execute("SELECT * FROM arenas WHERE time < ?", (timeUp.strftime('%Y%m%d%H%M%S'), ))
  #     results = curr.fetchall() # returns an array of tuples with the arenas to delete
  #     print(results)
  #     if results != []: # Do it only if its needed
  #       for entry in self.guilds:
  #         if serverName in entry.name:
  #           # Found server to delete the channel from: entry.categories
  #           for channel in entry.channels:
  #             for toDelete in results:
  #               if toDelete[1].lower().replace(' ', '-') in channel.name:
  #                 await channel.delete()
  #                 curr2 = conn2.cursor()
  #                 curr2.execute("DELETE FROM arenas WHERE author = ?", (toDelete[1].lower(), ) )
  #                 curr2.close()
  #     curr.close()
  #     conn2.commit()
  #     conn2.close()
  #     await asyncio.sleep(20)

  ####################################### on_ready #################################################
  async def on_ready(self):
    print('Logged on as {0}!'.format(self.user))
    # await self.checkDatabaseForDelete()

  ###################################### on_message ################################################
  async def on_message(self, message):
    if message.author.bot:
      return
    # OnMessage
    messArgv = message.content.split(' ')
    author = message.author
    authorID = message.author.id
    if message.content.lower().startswith(prefix + 'startarena'):
      # Create arena
      conn = sqlite3.connect('example.db')
      cur = conn.cursor()
      cur.execute("SELECT * FROM arenas WHERE authorID = ?", (authorID,))
      check = cur.fetchone()
      if check != None:
        message.channel.send("You already have an arena open")
      else:
        # create it
        await message.guild
        cur.execute("""
          INSERT INTO arenas (channelID, author, authorID, time)
          VALUES (?, ?, ?, ?)
        """, ())
      cur.close()
      conn.commit()
      conn.close()
    elif message.content.lower().startswith(prefix + 'closearena'): # closearena command
      # Delete arena
      print("lul")
    elif message.content.lower().startswith(prefix + 'setcategory'): # setcategory command
      if re.fullmatch(r"^\d{18}$", messArgv[1]):
        # check if the category exists
        found = False
        for cat in message.guild.categories:
          if cat.id == messArgv[1]:
            found = True
        if not found:
          await message.channel.send("Category not found, are you sure it was a category ID?")
          return
        # Set arenas category
        conn = sqlite3.connect('example.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO servers (serverID, categoryID) VALUES (?, ?)", (message.guild.id, messArgv[1]))
        cur.close()
        conn.commit()
        conn.close()
      else:
        await message.channel.send("Invalid ID, please give the bot a category ID")
    elif message.content.lower().startswith(prefix + 'help'):
      # Help message
      print("lul")
  ####################################### on_error #################################################
  async def on_error(self, event, *args, **kwargs):
    # OnError
    print("lul Error: ", event)

client = MyClient()
client.run(secret.token)