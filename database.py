import sqlite3
import hashlib

conn = sqlite3.connect('database.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS posts
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              title TEXT,
              content TEXT,
              file_url TEXT,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

# Crie a tabela de usuários com as colunas 'nome', 'email', 'senha' e 'tipo'
c.execute('CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, email TEXT, senha TEXT, tipo TEXT DEFAULT "regular")')

# Adiciona um usuário admin à tabela de usuários
hash_senha = hashlib.sha256('admin'.encode('utf-8')).hexdigest()
c.execute('INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)', ('Admin', 'admin@example.com', hash_senha, 'admin'))

conn.commit()
conn.close()
