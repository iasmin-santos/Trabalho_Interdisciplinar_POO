import sqlite3

class Database:
    def __init__(self, db_name="achados_e_perdidos.db"):
        self.db_name = db_name
        self.criar_tabelas()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def criar_tabelas(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Tabela Usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios(
                id_usuarios INTEGER PRIMARY KEY AUTOINCREMENT, 
                nome TEXT NOT NULL, 
                email TEXT NOT NULL, 
                senha TEXT NOT NULL, 
                nascimento TEXT, 
                tipo_usuario TEXT NOT NULL CHECK(tipo_usuario IN('aluno', 'funcionario')), 
                ra TEXT, curso TEXT, 
                periodo TEXT NOT NULL CHECK(periodo IN('Integral', 'Noturno')), 
                semestre INTEGER, cargo TEXT)
        ''')

        # Tabela Categorias
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categorias(
                id_categorias INTEGER PRIMARY KEY AUTOINCREMENT, 
                nome TEXT NOT NULL, 
                descricao TEXT)
        ''')

        # Tabela Itens
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS itens(
                id_item INTEGER PRIMARY KEY AUTOINCREMENT, 
                titulo TEXT NOT NULL, 
                descricao TEXT, 
                data_registro TEXT DEFAULT (datetime('now', 'localtime')), 
                local TEXT NOT NULL, 
                tipo_item TEXT NOT NULL CHECK(tipo_item IN ('Perdido', 'Achado')), 
                status TEXT NOT NULL DEFAULT 'Ativo' CHECK(status IN ('Ativo', 'Reivindicado', 'Entregue', 'Arquivado')), 
                id_categoria INTEGER, 
                id_usuario INTEGER, 
                FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria) ON DELETE SET NULL, 
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE)
        ''')

        # Tabela Solicitacoes
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS solicitacoes(
                id_solicitacao INTEGER PRIMARY KEY AUTOINCREMENT, 
                data_solicitacao TEXT DEFAULT (datetime('now', 'localtime')), 
                status TEXT NOT NULL DEFAULT 'Pendente' CHECK(status IN ('Pendente', 'Aprovada', 'Rejeitada')), 
                id_item INTEGER NOT NULL, 
                id_usuario INTEGER NOT NULL, 
                justificativa TEXT NOT NULL, 
                FOREIGN KEY (id_item) REFERENCES itens(id_item) ON DELETE CASCADE, 
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE)
        ''')

        # Tabela Entregas
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS entregas(
                id_entrega INTEGER PRIMARY KEY AUTOINCREMENT, 
                id_solicitacao INTEGER NOT NULL, 
                data_entrega TEXT DEFAULT (datetime('now', 'localtime')), 
                comprovante TEXT, 
                id_usuario_que_entregou INTEGER NOT NULL, 
                FOREIGN KEY (id_solicitacao) REFERENCES solicitacoes(id_solicitacao) ON DELETE CASCADE, 
                FOREIGN KEY (id_usuario_que_entregou) REFERENCES usuarios(id_usuario))
        ''')

        conn.commit()
        conn.close()