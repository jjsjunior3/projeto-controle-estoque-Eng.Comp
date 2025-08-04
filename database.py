import sqlite3
import os
from utils import hash_password, verify_password

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
DATABASE_FILE = os.path.join(DATA_DIR, 'estoque.db')

def create_connection():
    conn = None
    try:
        os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)
        conn = sqlite3.connect(DATABASE_FILE)
        return conn
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return conn

def create_tables():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Tabela de usuários - CORRIGIDA
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_usuario TEXT NOT NULL UNIQUE,
                    senha TEXT NOT NULL,
                    perfil TEXT NOT NULL
                );
            """)
            
            # Tabela de produtos - CORRIGIDA! (IF, id_produto, descricao, INTEGER)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS produtos (
                    id_produto INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_produto TEXT UNIQUE NOT NULL,
                    descricao TEXT,
                    quantidade INTEGER NOT NULL DEFAULT 0,
                    quantidade_minima INTEGER NOT NULL DEFAULT 0
                );
            ''')
            conn.commit()
            print("Tabelas criadas ou já existentes.")
        
        except sqlite3.Error as e:
            print(f"Erro ao criar tabela: {e}")
        
        finally:
            if conn:
                conn.close()

def add_initial_admin():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # CORRIGIDO: de 'usurarios' para 'usuarios' e 'Adminstrador' para 'Administrador'
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE perfil = 'Administrador'")
            admin_count = cursor.fetchone()[0]
            if admin_count == 0:
                # 'from utils import hash_password' movido para dentro da função para evitar circular import se necessário
                from utils import hash_password 
                admin_password = hash_password("admin123")
                cursor.execute("INSERT INTO usuarios (nome_usuario, senha, perfil) VALUES (?, ?, ?)",
                               ("admin", admin_password, "Administrador"))
                conn.commit()
                print("Usuário Administrador inicial 'admin' criado.")
            else:
                print("Usuário Administrador já existe.")
                
        except sqlite3.Error as e:
            print(f"Erro ao adicionar admin inicial: {e}")
        finally:
            if conn:
                conn.close()

if __name__ == '__main__':
    # Adicionei os prints de debug aqui novamente para você confirmar o caminho
    print(f"DEBUG: O diretório de dados é: {DATA_DIR}")
    print(f"DEBUG: O arquivo do banco de dados será: {DATABASE_FILE}")
    create_tables()
    add_initial_admin()