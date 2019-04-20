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
serverName = "Sargasso - Wolf SSBU"
arenaChatsCatName = 'arena chats'

# Function called every 20 seconds to check if any arena has to be deleted. It gets first called on Discord's on_ready function
# def checkDatabaseForDelete():
#   conn2 = sqlite3.connect('example.db')
#   timeUp = dt.datetime.now() - dt.timedelta(hours=1, minutes=0) # timeout arenas
#   curr = conn2.cursor()
#   curr.execute("SELECT * FROM arenas WHERE time < ?", (timeUp.strftime('%Y%m%d%H%M%S'), ))
#   results = curr.fetchall() # returns an array of tuples with the arenas to delete
#   # TODO: Delete the arenas channels and their database entry
#   curr.close()
#   conn2.close()
#   print(results)
#   threading.Timer(20.0, checkDatabaseForDelete).start()

class MyClient(discord.Client):
  # Method called every 20 seconds to check if any arena has to be deleted. It gets first called on Discord's on_ready function
  async def checkDatabaseForDelete(self):
    conn2 = sqlite3.connect('example.db')
    timeUp = dt.datetime.now() - dt.timedelta(hours=0, minutes=1) # timeout arenas
    curr = conn2.cursor()
    curr.execute("SELECT * FROM arenas WHERE time < ?", (timeUp.strftime('%Y%m%d%H%M%S'), ))
    results = curr.fetchall() # returns an array of tuples with the arenas to delete
    curr.close()
    conn2.close()
    print(results)
    threading.Timer(20.0, self.checkDatabaseForDelete).start() # TODO: Solve function to await in Timer
    if results != []: # Do it only if its needed
      for entry in self.guilds:
        if serverName in entry.name:
          # Found server to delete the channel from: entry.categories
          for channel in entry.channels:
            for toDelete in results:
              if toDelete[1].lower().replace(' ', '-') in channel.name:
                await channel.delete()

  ####################################### on_ready #################################################
  async def on_ready(self):
    print('Logged on as {0}!'.format(self.user))
    await self.checkDatabaseForDelete()

  ###################################### on_message ################################################
  async def on_message(self, message):
    if (message.content.lower().startswith(prefix + 'startarena')):
      authorName = message.author.name
      # SQL STUFF
      conn = sqlite3.connect('example.db') # open database
      curr = conn.cursor() # create cursor
      curr.execute("SELECT * FROM arenas WHERE author = ?", (str(authorName),)) # Check if user already has an arena
      if curr.fetchone() == None:
        curr.execute('''
          INSERT INTO arenas (author, time)
          VALUES (?, ?)
        ''', (str(authorName), int(dt.datetime.now().strftime('%Y%m%d%H%M%S')))) # Insert into table with automatic ID, author nick and timestamp as '20190420130059'
        print("Ok, inserted {} into database".format(authorName))
        # Get the 'arena chats' category
        for entry in message.guild.categories:
          if entry.name == arenaChatsCatName:
            # create channel
            channelName = str(authorName) + '_arena'
            createdChannel = await entry.create_text_channel(channelName) # Creates the channel in the specified category
      else:
        await message.channel.send("You already have an arena\nArena channels run out after 1 hour")
      curr.close()
      conn.commit() # ALWAYS remember to commit before closing the connection
      conn.close()
      # END SQL STUFF
  
  ####################################### on_error #################################################
  async def on_error(event, *args, **kwargs):
    message = args[0]
    print("on_error: ", args)
    print("kwargs: ", kwargs)
    await args[1].channel.send("Insufficent Permissions")

client = MyClient()
client.run(secret.token)