import sqlite3
import os

DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'data', 'estoque.db')

def create_connection():
    conn = None
    try:
        os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)
        conn = sqlite3.connect(DATABASE_FILE)
        return conn
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao banco de datos: {e}")
        return conn

def create_tables():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id_usuario INTERGER PRIMARY KEY AUTOINCREMENT,
                           nome_usuario TEXT UNIQUE NOT NULL,
                           senha TEXT NOT NULL,
                           perfil TEXT NOT NULL       
                );
            ''')
            cursor.execute('''
                CREATE TABLE IR NOT EXISTS produtos (
                    id_protudo INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_produto TEXT UNIQUE NOT NULL,
                    decricao TEXT,
                    quantidade INTEGER NOT NULL DEFAULT 0,       
                    quantidade_minima INTERGER NOT NULL DEFAULT 0
                 );
            ''')
            conn.commit()
            print("Tabelas criadas ou já existentes.")
        
        except sqlite3.Error as e:
            print(f"Erro ao criar tabela: {e}")
        
        finally:
            conn.close()

def add_initial_admin():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM usurarios WHERE perfil = 'Adminstrador'")
            admin_count = cursor.fetchone()[0]
            if admin_count == 0:
                from utils import hash_password
                admin_password = hash_password("admin123")
                cursor.execute("INSERT INTO usuarios (nome_usuario, senha, perfil) VALUES (?, ?, ?)",
                               ("admin", admin_password, "Administrador"))
                conn.commit()
                print("Usuário Administrador inicial 'admin' criado")
            else:
                print("Usuário Administrador já existe.")
                
        except sqlite3.Error as e:
            print(f"Erro ao adicionar admin inicial: {e}")
        finally:
            conn.close()

if __name__=='__main__':
    create_tables()
    add_initial_admin()