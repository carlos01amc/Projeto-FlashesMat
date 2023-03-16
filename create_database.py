import sqlite3
conn = sqlite3.connect('blog.db')
c = conn.cursor()

c.execute('''CREATE TABLE posts
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              title TEXT,
              content TEXT,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

conn.commit()
conn.close()