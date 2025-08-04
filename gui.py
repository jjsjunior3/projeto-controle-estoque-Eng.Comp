import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import os  # Necessário para os.path.abspath, se usado para debug do caminho do DB
from database import create_connection, DATABASE_FILE # Para conexão com o DB e seu caminho
from models import Produto, Usuario # Se você usa as classes Product e User no GUI
from utils import hash_password, verify_password # Para funções de hash e verificação de senha (login)

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

    def attempt_login(self):
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
                        self.on_login_success()
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
        if current_user_profile == "Administrador":
            manage_menu.add_command(label="Cadastrar Produto", command=self.show_add_product)
            manage_menu.add_command(label="Cadastrar Usuário", command=self.show_add_user)
        self.menu_bar.add_cascade(label="Gerenciamento", menu=manage_menu)

        self.main_frame = tk.Frame()
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.show_stock_view()

    def show_stock_view(self):
        #Limpar o frame princial e mostrar a tela com a visualização de estoques
        self.clear_main_frame()
        StockView(self.main_frame)
    
    def show_add_product(self):
        #Limpar o frame principal e mostrar a tela de cadastro dos produtos
        self.clear_main_frame()
        AddProductView(self.main_frame, self.show_stock_view)
    
    def show_add_user(self):
        #Limpar o frame principal e mostrar a tela de cadastro dos usuários (somenmt para o Admin)
        if current_user_profile == "Administrador":
            self.clear_main_frame()
            AddUserView(self.main_frame)
        else:
            messagebox.showwarning("Permissão Negada", "Somente Administradores podem cadastrar novos usuários.")
    
    def clear_main_frame(self):
        #Apagada todos os widgets no frame principal para trocar de tela
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def on_closing(self):
        #Pergunta ao usuário se realmente deseja sair da aplicação
        if messagebox.askokcancel("Sair", "Deseja realmente sair?"):
            self.destroy()
    
class StockView(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        tk.Label(self, text="Produtos em Estoque", font=("Arial", 16, "bold")).pack(pady=10)

        self.list_frame = tk.Frame(self)
        self.list_frame.pack(fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(self.list_frame)
        self.scrollbar.pack(side="right", fill="y")

        #Criar um widget TreeView para exibir os produtos em formato de tabela
        self.product_listbox = ttk.Treeview(self.list_frame, columns=("ID", "Nome", "Quantidade", "Mínima"), show="headings", yscrollcommand=self.scrollbar.set)
        self.product_listbox.pack(side="left", fill="both", expand=True)
        self.scrollbar.config(command=self.product_listbox.yview)

        #Definir o cabeçalho das colunos do TreeView
        self.product_listbox.heading("ID", text="ID")
        self.product_listbox.heading("Nome", text="Nome do Produto")
        self.product_listbox.heading("Quantidade", text="Quantidade")
        self.product_listbox.heading("Mínima", text="Qtd. Mínima")

        #Ajeste da largura das colunas
        self.product_listbox.column("ID", width=50, anchor="center")
        self.product_listbox.column("Nome", width=250)
        self.product_listbox.column("Quantidade", width=100, anchor="center")
        self.product_listbox.column("Mínima", width=100, anchor="center")

        self.product_listbox.bind("<<TreeviewSelect>>", self.on_product_select)

        self.edit_button = tk.Button(self, text="Editar Quantidade", command=self.edit_product_quantity, state="disabled")
        self.edit_button.pack(pady=5)

        self.delete_button = tk.Button(self, text="Excluir Produto", command=self.delete_product)
        if current_user_profile == "Administrador":
            self.delete_button.pack(pady=5)
        else:
            self.delete_button.pack_forget()
        
        self.load_product()
    
    def load_product(self):
        #Carregar os produtos no Banco de Dados e mostrar no TreeView
        for item in self.product_listbox.get_children():
            self.product_listbox.delete(item)
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                #fazer uma busca ordenada pelo nome
                cursor.execute("SELECT id_produto, nome_produto, quantidade, quantidade_minima FROM produtos ORDER BY nome_produto")
                products = cursor.fetchall()

                for prod in products:
                    prod_id, name, qty, min_qty = prod
                    #Inserir cada produto no TreeView
                    item_id = self.product_listbox.insert("", tk.END, values=(prod_id, name, qty, min_qty))
                    if qty < min_qty:
                        #colocar um tag vermelha em produtos que estão baixos no estoque
                        self.product_listbox.item(item_id, tags=('baixo_estoque',))
                
                #Configuração da tag para ter cor salmão
                self.product_listbox.tag_configure('baixo_estoque', background='salmon')
            except sqlite3.Error as e:
                messagebox.showerror("Erro de Banco de Dados", f"Erro ao carregar produto: {e}")
            finally:
                conn.close()

    def on_product_select(self, event):
        #Habilitar e desabilitar o botão de edição baseado na seleção do TreeView
        if self.product_listbox.selection():
            self.edit_button.config(state="normal")
        else:
            self.edit_button.config(state="disabled")
    
    def get_select_product_id(self):
        #Obter o produto selecionado no TreeView
        selection = self.product_listbox.selection()
        if selection:
            #Pega os valores da linha selecionada e o id é o primeiro
            values = self.product_listbox.item(selection[0], 'values')
            return int(values[0])
        return None
    
    def edit_product_quantity(self):
        #abrir a janela para editar a quantidade de um produto selecionado
        product_id = self.get_select_product_id()
        if product_id:
            conn = create_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    #Buscar o nome e a quantidade do produto selecionado
                    cursor.execute("SELECT nome_produto, quantidade FROM produtos WHERE id_produto = ?", (product_id,))
                    product_data = cursor.fetchone()
                    if product_data:
                        nome_produto, quantidade_atual = product_data
                        #Pergunta ao usuário se é ENTRADA ou SAIDA
                        action = messagebox.askquestion("Edição de Estoque",
                                                        f"Editar {nome_produto}. É uma Entrada ou SAÍDA?",
                                                        icon='question', type='yesnocancel',
                                                        detail="Clique 'Sim' para Entrar, 'Não' para Saída.")
                        if action == 'cancel':
                            return
                        
                        try:
                            #solicita a quantidade a ser adicionada ou removida
                            qty_change = simpledialog.askinteger("Quantidade",
                                                                 f"Informe a quantidade para {'entrada'if action == 'yes' else 'saída'}:",
                                                                 minvalue=1)
                            if qty_change is None:
                                return
                        except ValueError:
                            messagebox.showerror("Erro de Entrada", "Por favor, digite um número válido.")
                            return
                        
                        nova_quantidade = quantidade_atual
                        if action == 'yes': #Entrada
                            nova_quantidade += qty_change
                        elif action == 'no': #Saída
                            if quantidade_atual >= qty_change:
                                nova_quantidade -= qty_change
                            else:
                                messagebox.showwarning("Aviso", "Quantidade em estoque insuficiente para esta saída.")
                                return
                        
                        #atualizar a quantidade de produtos no banco de dados
                        cursor.execute("UPDATE produtos SET quantidade = ? WHERE id_produto = ?", (nova_quantidade, product_id))
                        conn.commit()
                        messagebox.showinfo("Sucesso", f"Estoque de {nome_produto} atualizado para {nova_quantidade}.")
                        self.load_product()
                    else:
                        messagebox.showwarning("Aviso", "Produto não encontrato.")
                except sqlite3.Error as e:
                    messagebox.showerror("Erro de Banco de Dados", f"ERro ao atualizar protudo: {e}")
                finally:
                    conn.close()
            else:
                messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados.")
        else:
            messagebox.showwarning("Aviso", "Selecione um produto para editar.")
    
    def delete_product(self):
        #Excluir produto do banco de dados, apenas Admin
        if current_user_profile != "Administrador":
            messagebox.showwarning("Permissão Negada", "Somente administradores podem excluir produtos.")
            return
        
        product_id = self.get_select_product_id()
        if product_id:
            if messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir este produto?"):
               conn = create_connection()
               if conn:
                   try:
                       cursor = conn.cursor()
                       cursor.execute("DELETE FROM produtos WHERE id_produto = ?", (product_id,))
                       conn.commit()
                       messagebox.showinfo("Sucesso", "Produto excluído com sucesso.")
                       self.load_product()
                   except sqlite3.Error as e:
                       messagebox.showerror("Erro de Banco de Dados", f"Erro ao excluir produto: {e}")
                   finally:
                       conn.close()
               else:
                   messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados.")
        else:
            messagebox.showwarning("Aviso", "Selecione um produto para exluir.")

class AddProductView(tk.Frame):
    def __init__(self, master, on_save_callback):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.on_save_callback = on_save_callback

        tk.Label(self, text="Cadastrar Novo Produto", font=("Arial", 16, "bold")).pack(pady=10)

        tk.Label(self, text="Nome do Produto").pack(pady=5)
        self.name_entry = tk.Entry(self, width=40)
        self.name_entry.pack(pady=5)

        tk.Label(self, text="Descrição (Opcional):").pack(pady=5)
        self.desc_entry = tk.Entry(self, width=40)
        self.desc_entry.pack(pady=5)

        tk.Label(self, text="Quantidade Inicial:").pack(pady=5)
        self.qty_entry = tk.Entry(self, width=40)
        self.qty_entry.pack(pady=5)

        tk.Label(self, text="Quantidade Mínima para Alerta:").pack(pady=5)
        self.min_qty_entry = tk.Entry(self, width=40)
        self.min_qty_entry.pack(pady=5)

        tk.Button(self, text="Salvar Produto", command=self.save_product).pack(pady=10)
        tk.Button(self, text="Voltar", command=self.on_save_callback).pack(pady=5)
        
    def save_product(self):
        #Salvar um novo produto no banco de dados
        name = self.name_entry.get().strip()
        description = self.desc_entry.get().strip()
        qty_str = self.qty_entry.get().strip()
        min_qty_str = self.min_qty_entry.get().strip()

        if not name:
            messagebox.showerror("Erro de Validaçã", "O Nome do produto é obrigatório.")
            return
        
        try:
            quantity = int(qty_str)
            min_quantity = int(min_qty_str)
            if quantity < 0 or min_quantity < 0:
                messagebox.showerror("Erro de Validação", "Quantidade ou Quantidade Mínima deve ser positiva ou zero.")
                return
        except ValueError:
            messagebox.showerror("Erro de Validação", "Quantidade e Quantidade Mínima devem ser número válidos.")
            return
        
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                #Inserir o novo produto no banco de dados
                cursor.execute("INSERT INTO produtos (nome_produto, descricao, quantidade, quantidade_minima) VALUES (?, ?, ?, ?)",
                               (name, description, quantity, min_quantity))
                conn.commit()
                messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")
                self.on_save_callback()
            except sqlite3.IntegrityError:
                messagebox.showerror("Erro", "Já existe esse produto com este nome.")
            except sqlite3.Error as e:
                messagebox.showerror("Erro de Banco de Dados", f"Erro ao cadastrar produto: {e}")
            finally:
                conn.close()
        else:
            messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados.")

class AddUserView(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        #Verificação de permissão do usuário, se não for Admin exibi aviso e volta
        if current_user_profile != "Administrador":
            messagebox.showwarning("Permissão Negada", "Somente adminstradores podem cadastrar novos usuários.")
            self.master.winfo_toplevel().show_stock_view()
            return
        
        tk.Label(self, text="Cadastrar Novo Usuário", font=("Arial", 16, "bold")).pack(pady=10)

        tk.Label(self, text="Nome do Usuário:").pack(pady=5)
        self.username_entry = tk.Entry(self, width=40)
        self.username_entry.pack(pady=5)

        tk.Label(self, text="Senha:").pack(pady=5)
        self.password_entry = tk.Entry(self, width=40, show="*")
        self.password_entry.pack(pady=5)

        tk.Label(self, text="Confirmar Senha:").pack(pady=5)
        self.confirm_password_entry = tk.Entry(self, width=40, show="*")
        self.confirm_password_entry.pack(pady=5)

        tk.Label(self, text="Perfil:").pack(pady=5)
        self.profile_var = tk.StringVar(self)
        self.profile_var.set("Comun")
        self.profile_menu = tk.OptionMenu(self, self.profile_var, "Administrador", "Comun")
        self.profile_menu.pack(pady=5)

        tk.Button(self, text="Salvar Usuário", command=self.save_user).pack(pady=10)
        tk.Button(self, text="Voltar", command=self.master.winfo_toplevel().show_stock_view).pack(pady=5)
    
    def save_user(self):
        #Salva um novo usuário no banco de dados (apenas para Admin)
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()
        profile = self.profile_var.get()

        if not username or not password or not confirm_password:
            messagebox.showerror("Erro de Validação", "Todos os campos são obrigatórios.")
            return

        if password != confirm_password:
            messagebox.showerror("Erro de Validação", "As senhas não coincidem.")
            return

        hashed_password = hash_password(password)

        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                # Insere o novo usuário no banco de dados.
                cursor.execute("INSERT INTO usuarios (nome_usuario, senha, perfil) VALUES (?, ?, ?)",
                               (username, hashed_password, profile))
                conn.commit()
                messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
                self.master.winfo_toplevel().show_stock_view()
            except sqlite3.IntegrityError:
                messagebox.showerror("Erro", "Já existe um usuário com este nome.")
            except sqlite3.Error as e:
                messagebox.showerror("Erro de Banco de Dados", f"Erro ao cadastrar usuário: {e}")
            finally:
                conn.close()
        else:
            messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados.")