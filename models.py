import sqlite3

def connect():
    return sqlite3.connect('database.db')

def init_db():
    with connect() as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY,
                nome TEXT,
                senha TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS movimentacoes (
                id INTEGER PRIMARY KEY,
                tipo TEXT,
                material TEXT,
                quantidade INTEGER,
                valor REAL,
                data TEXT,
                quem_colocou TEXT,
                quem_retirou TEXT,
                equipe TEXT
            )
        ''')
        c.execute("INSERT OR IGNORE INTO usuarios (id, nome, senha) VALUES (1, 'admin', 'admin')")
        conn.commit()

def get_user(nome, senha):
    with connect() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM usuarios WHERE nome = ? AND senha = ?', (nome, senha))
        return c.fetchone()

def add_entry(data):
    with connect() as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO movimentacoes 
            (tipo, material, quantidade, valor, data, quem_colocou, quem_retirou, equipe)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('entrada', data['material'], data['quantidade'], data['valor'], data['data'],
              data['quem_colocou'], '', data['equipe']))
        conn.commit()

def add_exit(data):
    with connect() as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO movimentacoes 
            (tipo, material, quantidade, valor, data, quem_colocou, quem_retirou, equipe)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('saida', data['material'], data['quantidade'], data['valor'], data['data'],
              '', data['quem_retirou'], data['equipe']))
        conn.commit()

def get_stock():
    with connect() as conn:
        c = conn.cursor()
        c.execute('''
            SELECT material,
                SUM(CASE WHEN tipo = 'entrada' THEN quantidade ELSE -quantidade END) AS saldo
            FROM movimentacoes
            GROUP BY material
        ''')
        return c.fetchall()

def get_history():
    with connect() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM movimentacoes ORDER BY data DESC')
        return c.fetchall()

def create_user(nome, senha):
    with connect() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM usuarios WHERE nome = ?', (nome,))
        if c.fetchone():
            return False  # usuário já existe
        c.execute('INSERT INTO usuarios (nome, senha) VALUES (?, ?)', (nome, senha))
        conn.commit()
        return True
