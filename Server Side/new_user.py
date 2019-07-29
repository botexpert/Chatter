import sqlite3

conn = sqlite3.connect('user_database.db')
c = conn.cursor()
# c.execute("""CREATE TABLE tokens (
#            username text,
#            token text)""")
#            password text)
#           """)
# c.execute(" INTO users VALUES('zika', 'zika')")
# c.execute('''ALTER TABLE tokens ADD COLUMN "timestamp" TEXT''')
c.execute('DELETE FROM tokens')
c.execute("SELECT * FROM users")
users = c.fetchall()
print(users)
c.execute("SELECT * FROM tokens")
tokens = c.fetchall()
print(tokens)
conn.commit()
conn.close()
