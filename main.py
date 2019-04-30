#!python
import discord
import secret
import sqlite3
import datetime as dt
import asyncio
import re
import modules

databaseName = 'database.db'

modules.initDB(sqlite3, databaseName)

prefix = 'w.'

class MyClient(discord.Client):
  # Method called every 20 seconds to check if any arena has to be deleted. It gets first called on Discord's on_ready function
  async def checkDatabaseForDelete(self):
    while True:
      conn2 = sqlite3.connect(databaseName)
      timeUp = dt.datetime.now() - dt.timedelta(hours=0, minutes=1) # timeout arenas
      curr = conn2.cursor()
      curr.execute("SELECT channelID, categoryID FROM arenas WHERE time < ?", (timeUp.strftime('%Y%m%d%H%M%S'), ))
      results = curr.fetchall() # returns an array of tuples with the arenas to delete
      print(results)
      if results != []: # Do it only if its needed
        # Delete database entry and channel
        for toDelete in results:
          # toDelete = (channelID, CategoryID)
          curr.execute("SELECT serverID FROM servers WHERE categoryID = ?", (toDelete[1], ))
          serverID = curr.fetchone()[0]
          for server in self.guilds:
            if server.id == serverID:
              for cat in server.categories:
                if cat.id == toDelete[1]:
                  for channel in cat.channels:
                    if channel.id == toDelete[0]:
                      await channel.delete()
                      curr.execute("DELETE FROM arenas WHERE channelID = ?", (toDelete[0], ))
      curr.close()
      conn2.commit()
      conn2.close()
      await asyncio.sleep(10)

  ####################################### on_ready #################################################
  async def on_ready(self):
    print('Logged on as {0}!'.format(self.user))
    await self.checkDatabaseForDelete()

  ###################################### on_message ################################################
  async def on_message(self, message):
    if message.author.bot: # Ignore the message if its a bot who sent it
      return
    # OnMessage
    messArgv = message.content.split(' ')
    author = message.author
    authorID = message.author.id
    if message.content.lower().startswith(prefix + 'startarena'):
      # Create arena
      if len(messArgv) != 3:
        if not (re.fullmatch(r"^[0-9a-zA-Z]{5}$", messArgv[1]) and re.fullmatch(r"^\d{4,10}$", messArgv[2])):
          await message.channel.send("Please provide an arena ID and a Password")
          return
      conn = sqlite3.connect(databaseName)
      cur = conn.cursor()
      cur.execute("SELECT * FROM arenas WHERE authorID = ?", (authorID,))
      check = cur.fetchone()
      if check != None:
        await message.channel.send("You already have an arena open")
      else:
        # create it
        cur.execute("SELECT categoryID FROM servers WHERE serverID = ?", (message.guild.id,))
        categoryID = cur.fetchone()
        if categoryID == None:
          await message.channel.send("Sorry fam, gotta ask an admin to set up the category first")
          return
        categoryID = categoryID[0]
        newChannel = None
        for cat in message.guild.categories:
          if cat.id == categoryID:
            newChannel = await cat.create_text_channel(author.name + "_arena")
            break
        timeoutstart = dt.datetime.now()
        while newChannel == None:
          if (dt.datetime.now() - timeoutstart) < dt.datetime(second=30):
            await message.channel.send("Something went wrong, request took longer than a minute")
            return
          continue
        channelID = newChannel.id
        cur.execute("""
          INSERT INTO arenas (channelID, categoryID, author, authorID, time)
          VALUES (?, ?, ?, ?, ?)
        """, (channelID, categoryID, author.name, authorID, dt.datetime.now().strftime('%Y%m%d%H%M%S')))
        infoMessage = await newChannel.send("ID: {0}\nPass: {1}".format(messArgv[1], messArgv[2]))
        timeoutstart = dt.datetime.now()
        while infoMessage == None:
          if (dt.datetime.now() - timeoutstart) < dt.datetime(second=30):
            await message.channel.send("Something went wrong with the message pinning, request took longer than a minute")
            return
          continue
        await infoMessage.pin()
        await message.channel.send("Ight bro, here's your arena channel. You have 3 hour before it expires\n<#{}>".format(channelID))
      cur.close()
      conn.commit()
      conn.close()
    elif message.content.lower().startswith(prefix + 'closearena'): # closearena command
      # Delete arena
      conn = sqlite3.connect(databaseName)
      cur = conn.cursor()
      cur.execute("SELECT channelID FROM arenas WHERE authorID = ?", (authorID, ))
      res = cur.fetchone()
      if res == None:
        await message.channel.send("Fam, you first gotta open an arena to close it...")
        return
      cur.execute("DELETE FROM arenas WHERE authorID = ?", (authorID, ))
      cur.fetchone()
      cur.execute("SELECT categoryID FROM servers WHERE serverID = ?", (message.guild.id, ))
      categoryID = (cur.fetchone())[0]
      channelID = res[0]
      for channel in message.guild.channels:
        if channel.id == channelID:
          await channel.delete()
          break
      if message.channel.id != channelID:
        await message.channel.send("Ok, arena channel deleted")
      cur.close()
      conn.commit()
      conn.close()
    elif message.content.lower().startswith(prefix + 'setcategory'): # setcategory command
      if not author.permissions_in(message.channel).administrator:
        await message.channel.send("Only admins can set this... sorry")
      if re.fullmatch(r"^\d{18}$", messArgv[1]):
        # check if the category exists
        found = False
        for cat in message.guild.categories:
          if cat.id == int(messArgv[1]):
            found = True
        if not found:
          await message.channel.send("Category not found, are you sure it was a category ID?")
          return
        # Set arenas category
        conn = sqlite3.connect(databaseName)
        cur = conn.cursor()
        cur.execute("INSERT INTO servers (serverID, categoryID) VALUES (?, ?)", (message.guild.id, messArgv[1]))
        cur.close()
        conn.commit()
        conn.close()
        await message.channel.send("Ight, category set")
      else:
        await message.channel.send("Invalid ID, please give the bot a category ID")
    elif message.content.lower().startswith(prefix + 'help'): # help command
      # embed
      embed = discord.Embed()
      embed.color = discord.Color.from_rgb(149, 66, 244)
      embed.set_author(name = "Bot by: Sesilaso", url = "https://github.com/StackWolfed/arenasbot")
      embed.title = "Help"
      embed.add_field(name=(prefix + "startarena <ARENA_ID> <ARENA_PSW>"), value="Creates an arena")
      embed.add_field(name=(prefix + "closearena"), value="Closes an arena")
      embed.add_field(name=(prefix + "setcategory <cATEGORY_ID>"), value="[ADMINS ONLY] Sets the target category to create arena channels")
      embed.add_field(name=(prefix + "help"), value="This")
      await message.channel.send(embed=embed)
  ####################################### on_error #################################################
  async def on_error(self, event, *args, **kwargs):
    # OnError
    print("lul Error: ", event)
    print("lul stuff: ", args)
    print("lul even more stuff: ", kwargs)

client = MyClient()
client.run(secret.token)