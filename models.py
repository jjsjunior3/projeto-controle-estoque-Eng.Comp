class Usuario:
    def __init__(self, id_usuario, nome_usuario, senha, perfil):
        self.id_usuario = id_usuario
        self.nome_usuario = nome_usuario
        self.senha = senha
        self.perfil = perfil
    

    def __repr__(self):
        return f"Usuario(ID: {self.id_usuario}, Nome: {self.nome_usuario}, Perfil: {self.perfil})"

class Produto:
    def __init__(self, id_produto, nome_produto, descricao, quantidade, quantidade_minima):
        self.id_produto = id_produto
        self.nome_produto = nome_produto
        self.descricao = descricao
        self.quantidade = quantidade
        self.quantidade_minima = quantidade_minima

    def __repr__(self):
        return (f"Produto(ID: {self.id_produto}, Nome: {self.nome_produto}," f"Quantidade: {self.quantidade}, Mínima: {self.quantidade_minima})") 