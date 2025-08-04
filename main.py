import tkinter as tk
from database import create_tables, add_initial_admin
from gui import MainApplication

def main():
    # Inicializa o banco de dados
    create_tables()
    add_initial_admin()

    # Cria a janela principal da aplicação e a executa
    app = MainApplication()
    app.mainloop()

if __name__ == '__main__':
    main()