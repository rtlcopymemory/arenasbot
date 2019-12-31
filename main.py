#!python
import discord
import secret
import sqlite3
import datetime as dt
import asyncio
import re
import modules

database_name: str = 'database.db'
time_format_string: str = '%Y%m%d%H%M%S'
prefix: str = 'w.'
timeout_hours: int = 3

modules.init_db(sqlite3, database_name)


class MyClient(discord.Client):
    def __init__(self, **options):
        super().__init__(**options)
        self.conn = sqlite3.connect(database_name)

    # Method looping every 10 seconds to check if any arena has to be deleted. It gets first called on Discord's
    # on_ready function
    async def check_database_for_delete(self):
        while True:
            time_out = dt.datetime.now() - dt.timedelta(hours=timeout_hours, minutes=0)  # timeout arenas
            curr = self.conn.cursor()
            curr.execute("SELECT channelID FROM arenas WHERE time < ?", (time_out.strftime(time_format_string),))
            channel_ids = curr.fetchall()  # [ChannelID, ...]
            if len(channel_ids) > 0:
                # Delete database entry and channel
                for toDelete in channel_ids:
                    channel_to_delete: discord.TextChannel = self.get_channel(int(toDelete))
                    await channel_to_delete.delete()
                    curr.execute("DELETE FROM arenas WHERE channelID = ?", (int(toDelete),))
            curr.close()
            self.conn.commit()
            await asyncio.sleep(10)

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        await self.change_presence(status=discord.Status.online,
                                   activity=discord.Game("{}help for help".format(prefix)))
        await self.check_database_for_delete()

    async def start_arena(self, message):
        message_argv = message.content.split(' ')
        author: discord.User = message.author

        if len(message_argv) < 3:
            await message.channel.send("Please provide an arena ID and a Password (Not enough arguments)")
            return

        if not re.fullmatch(r"^[0-9a-zA-Z]{5}$", message_argv[1]) or not re.fullmatch(r"^\d{1,8}$", message_argv[2]):
            await message.channel.send("Please provide an arena ID and a Password")
            return

        cur = self.conn.cursor()

        cur.execute("SELECT * FROM arenas WHERE authorID = ?", (author.id,))

        if cur.fetchone() is not None:
            await message.channel.send("You already have an arena open")
            cur.close()
            return

        # create it
        cur.execute("SELECT categoryID FROM servers WHERE serverID = ?", (message.guild.id,))
        categoryID: int = cur.fetchone()[0]

        if categoryID is None:
            await message.channel.send(
                'Sorry fam, gotta ask an admin to set up the category first\nUse {}setcategory CATEGORY_ID'.format(
                    prefix))
            cur.close()
            return

        category = self.get_channel(categoryID)
        if category is None:
            await message.channel.send("Someone thought it was funny to delete my category...")
            cur.close()
            return

        newChannel = await category.create_text_channel(author.name + "_arena")

        cur.execute("""INSERT INTO arenas (channelID, authorID, time) VALUES (?, ?, ?)""", (
            newChannel.id, author.id, dt.datetime.now().strftime(time_format_string)))

        infoMessage = await newChannel.send("ID: {0}\nPass: {1}".format(message_argv[1], message_argv[2]))
        await infoMessage.pin()
        await message.channel.send(
            "Ight bro, here's your arena channel. You have {} hours before it expires\n<#{}>".format(timeout_hours,
                                                                                                     newChannel.id))

        self.conn.commit()
        cur.close()

    async def close_arena(self, message):
        author: discord.User = message.author

        cur = self.conn.cursor()
        cur.execute("SELECT channelID FROM arenas WHERE authorID = ?", (author.id,))
        res = cur.fetchone()
        if res is None:
            await message.channel.send("Fam, you first gotta open an arena to close it...")
            return

        cur.execute("DELETE FROM arenas WHERE authorID = ?", (author.id,))
        channelID = res[0]
        await self.get_channel(channelID).delete()

        if message.channel.id != channelID:
            await message.channel.send("Ok, arena channel deleted")

        self.conn.commit()
        cur.close()

    async def set_category(self, message):
        author: discord.User = message.author
        message_argv: list = message.content.split(' ')

        if not author.permissions_in(message.channel).administrator:
            await message.channel.send("Only admins can set this... sorry")
            return

        if len(message_argv) < 2:
            await message.channel.send("Wrong usage, missing CATEGORY_ID parameter")
            return

        if not re.fullmatch(r"^\d{18}$", message_argv[1]):
            await message.channel.send("Invalid ID, please give the bot a category ID")
            return

        category: discord.CategoryChannel = self.get_channel(int(message_argv[1]))
        if category is None:
            await message.channel.send("Category not found, are you sure it was a category ID?")
            return

        cur = self.conn.cursor()

        cur.execute("DELETE FROM servers WHERE serverID = ?", (message.guild.id,))
        self.conn.commit()

        cur.execute("INSERT INTO servers (serverID, categoryID) VALUES (?, ?)", (message.guild.id, message_argv[1]))
        self.conn.commit()

        await message.channel.send("Ight, category set")
        cur.close()

    async def help(self, message):
        embed: discord.Embed = discord.Embed(color=discord.Color.from_rgb(149, 66, 244))
        embed.set_author(name="Bot by: Sesilaso", url="https://github.com/StackWolfed/arenasbot")
        embed.title = "Help"
        embed.add_field(name=(prefix + "startarena <ARENA_ID> <ARENA_PSW>"), value="Creates an arena")
        embed.add_field(name=(prefix + "close"), value="Closes an arena")
        embed.add_field(name=(prefix + "setcategory <CATEGORY_ID>"),
                        value="[ADMINS ONLY] Sets the target category to create arena channels")
        embed.add_field(name=(prefix + "help"), value="This help message")
        await message.channel.send(embed=embed)

    async def on_message(self, message):
        # Ignore the message if its a bot who sent it
        if message.author.bot:
            return

        if message.content.lower().startswith(prefix + 'startarena'):
            await self.start_arena(message)

        elif message.content.lower().startswith(prefix + 'close'):
            await self.close_arena(message)

        elif message.content.lower().startswith(prefix + 'setcategory'):
            await self.set_category(message)

        elif message.content.lower().startswith(prefix + 'help'):
            await self.help(message)

    async def on_error(self, event, *args, **kwargs):
        if isinstance(args[0], discord.Message):
            await args[0].channel.send("An error occurred in function {}: {}".format(event, args))


client = MyClient()
client.run(secret.token)
