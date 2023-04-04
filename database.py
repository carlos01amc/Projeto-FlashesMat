import sqlite3
import hashlib

conn = sqlite3.connect('database.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS posts
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              title TEXT,
              content TEXT,
              thumbnail_url TEXT,
              file_url TEXT,
              author TEXT,
              snapshots_1 TEXT,
              snapshots_2 TEXT,
              snapshots_3 TEXT,
              links TEXT,
              download TEXT,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

# Crie a tabela de usuários com as colunas 'nome', 'email', 'senha' e 'tipo'
c.execute('''CREATE TABLE IF NOT EXISTS usuarios 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
              nome TEXT, 
              email TEXT, 
              senha TEXT, 
              tipo TEXT DEFAULT "regular")''')

c.execute('''ALTER TABLE usuarios ADD COLUMN reset_password_token TEXT''')

# Crie a tabela de formulario
c.execute('''CREATE TABLE IF NOT EXISTS forms
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              title TEXT,
              content TEXT,
              thumbnail_url TEXT,
              file_url TEXT,
              author TEXT,
              snapshots_1 TEXT,
              snapshots_2 TEXT,
              snapshots_3 TEXT,
              links TEXT,
              download TEXT,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

# Adiciona um usuário admin à tabela de usuários
hash_senha = hashlib.sha256('admin'.encode('utf-8')).hexdigest()
c.execute('INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)', ('Admin', 'admin@example.com', hash_senha, 'admin'))

conn.commit()
conn.close()

