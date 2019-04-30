def initDB(sqlite3, dbName):
  conn = sqlite3.connect(dbName)
  cursor = conn.cursor()
  cursor.execute("CREATE TABLE IF NOT EXISTS arenas (id INTEGER PRIMARY KEY AUTOINCREMENT, channelID INTEGER, categoryID INTEGER, author TEXT, authorID INTEGER, time INTEGER)")
  cursor.execute("CREATE TABLE IF NOT EXISTS servers (id INTEGER PRIMARY KEY AUTOINCREMENT, serverID INTEGER, categoryID INTEGER)")
  cursor.close()
  conn.commit()
  conn.close()
