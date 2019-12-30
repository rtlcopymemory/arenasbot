def init_db(sqlite3, db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS arenas (id INTEGER PRIMARY KEY AUTOINCREMENT, channelID INTEGER, "
        "authorID INTEGER, time INTEGER)")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS servers (id INTEGER PRIMARY KEY AUTOINCREMENT, serverID INTEGER,"
        "categoryID INTEGER)")
    cursor.close()
    conn.commit()
    conn.close()
