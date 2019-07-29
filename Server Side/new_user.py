import sqlite3

conn = sqlite3.connect('user_database.db')
c = conn.cursor()
# c.execute("""CREATE TABLE users (
#            username text,
#            password text)
#           """)
#c.execute("INSERT INTO users VALUES('branko', 'car')")
#c.execute('DELETE FROM users')

c.execute("SELECT * FROM users")

users = c.fetchall()
print(users)
conn.commit()
conn.close()
