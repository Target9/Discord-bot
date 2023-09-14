import sqlite3

connection = sqlite3.connect("economy_bot.db")
cursor = connection.cursor()

# Table for user data: ID, doubloons, spam, factories, diamond_spam
cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (id INTEGER PRIMARY KEY, doubloons INTEGER, spam INTEGER, factories INTEGER, diamond_spam INTEGER)''')

connection.commit()
connection.close()
