import sqlite3

conn = sqlite3.connect('user_database.db')
c = conn.cursor()
#c.execute("CREATE TABLE users(username text, password text)")
#c.execute("""DROP TABLE pera""")
#c.execute("""DROP TABLE zika""")
#c.execute("""DROP TABLE admin""")
# c.execute("""CREATE TABLE tokens (
#            username text,
#            token text)""")
#            password text)
#           """)
# c.execute("""CREATE TABLE message_history(
#         username text,
#         history blob)""")

#c.execute("INSERT INTO users VALUES('pera', 'pera')")
# c.execute('''ALTER TABLE tokens ADD COLUMN "timestamp" TEXT''')
# c.execute('DELETE FROM tokens')
#c.execute('DELETE FROM message_history')
#c.execute("INSERT INTO message_history VALUES (?,?)",('zika','prva'))
c.execute("SELECT * FROM users")
users = c.fetchall()
print(users)
#c.execute("SELECT * FROM tokens")
#tokens = c.fetchall()
#print(tokens)
#c.execute("SELECT * FROM zika")
#messages = c.fetchall()
#print(messages)
conn.commit()
conn.close()
