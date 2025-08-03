import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sqlite3
from database import create_connection
from utils import verify_password, hash_password
import re

# Variáveis globais

current_user = None
current_user_profile = None

class LoginWindow(tk.Toplevel):
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.master = master
        self.on_login_success = on_login_success
        self.title("Login do Usuário")
        self.geometry("300x200")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        #Rótulo de texto
        tk.Label(self, text="Usuário:").pack(pady=5)
        #Campo de nome do usuário
        self.username_entry = tk.Entry(self)
        self.username_entry.pack(pady=5)

        #Rótulo do texta da senha
        tk.Label(self, text="Senha:").pack(pady=5)

        #campo para entrada de texto da senha com caracteres ocultos
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=5)

        #Botão de Entrar
        tk.Button(self, text="Entrar", command=self.attempt_login).pack(pady=10)

        #Centralizar a tela de login no centro do monitor
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() // 2) - (self.winfo_width() // 2)
        y = master.winfo_y() + (master.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def on_closing(self):
        #Fechar a Janela princial também ao chegar a Janela de login
        self.master.destroy()

    def attempt_login(self)
        #tentar fazer o login do usuário
        global current_user, current_user_profile
        username = self.username_entry.get()
        password = self.password_entry.get()

        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                #fazer a busca do usuário pelo nome do usuário
                cursor.execute("SELECT id_usuario, nome_usuario, senha, perfil FROM usuarios WHERE nome_usuario = ?", (username,))
                user_data = cursor.fetchone()

                if user_data:
                    user_id,stored_username, hashed_password, profile = user_data
                    #verificação se a senha está correta
                    if verify_password(password, hashed_password):
                        current_user = stored_username
                        current_user_profile = profile
                        messagebox.showinfo("Sucesso", f"Bem-Vindo, {current_user} ({current_user_profile})!")
                        self.destroy()
                        self.on_login_success
                        return
                    else:
                        messagebox.showerror("Erro de Login", "Usuário não encontrado.")
            except sqlite3.Error as e:
                messagebox.showerror("Erro de banco de dados", f"Erro:{e}")
            finally:
                conn.close()
        else:
            messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados")

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Controle de Estoque - UniFECAF")
        self.geometry("800x600")
        self.withdraw()

        self.login_window = LoginWindow(self, self.show_main_window)
    
    def show_main_window(self):
        #Mostrar a tela princial após boas-vindas
        self.deiconify()
        self.create_widgets()
    
    def create_widgets(self):
        #Criar o widgets na Janela principal para menus e frames
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Sair", command=self.on_closing)
        self.menu_bar.add_cascade(label="Arquivo", menu=file_menu)

        manage_menu = tk.Menu(self.menu_bar, tearoff=0)
        manage_menu.add_command(label="Visualizar Estoque", command=self.show_stock_view)
