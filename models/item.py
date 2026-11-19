import sqlite3
from abc import ABC, abstractmethod


class Item(ABC):
    """Classe Abstrata que representa a entidade genérica Item do diagrama."""
    def __init__(self, titulo, descricao, local, foto_path, status, id_usuario=None, id_item=None, data_registro=None):
        self.id_item = id_item
        self.titulo = titulo
        self.descricao = descricao
        self.local = local
        self.foto_path = foto_path
        self.status = status
        self.id_usuario = id_usuario
        self.data_registro = data_registro

    @abstractmethod
    def validar(self):
        """Método abstrato obrigatório imposto pelo polimorfismo do diagrama."""
        pass

    def to_dict(self):
        """Mapeia os atributos do objeto para um dicionário compatível com o banco."""
        return {
            'titulo': self.titulo,
            'descricao': self.descricao,
            'local': self.local,
            'foto_path': self.foto_path,
            'status': self.status,
            'id_usuario': self.id_usuario,
            'tipo_item': self.__class__.__name__.replace('Item', '')  # Gera 'Perdido' ou 'Achado'
        }


class ItemPerdido(Item):
    """Especialização que estende Item para representar objetos perdidos."""
    def validar(self):
        """Aplica as regras de validação exclusivas para itens perdidos."""
        if not self.titulo:
            raise ValueError("O título do item perdido não pode ser vazio.")
        if not self.local:
            raise ValueError("O local aproximado da perda precisa ser informado.")


class ItemAchado(Item):
    """Especialização que estende Item para representar objetos achados."""
    def validar(self):
        """Aplica as regras de validação exclusivas para itens achados."""
        if not self.titulo:
            raise ValueError("A categoria/especificação do item achado é obrigatória.")
        if not self.local:
            raise ValueError("O local onde o item foi encontrado precisa ser descrito.")


class ItemModel:
    def __init__(self, database):
        self.db = database

    def _converter_para_objeto(self, linhas):
        """Converte as linhas brutas do banco de dados em objetos reais de POO (Polimorfismo)."""
        lista_modelos = []
        for linha in linhas:
            tipo_item = linha[3]  
            
            # Instancia o objeto correto baseado no tipo salvo no banco de dados
            if tipo_item == "Perdido":
                item = ItemPerdido(
                    id_item=linha[0],
                    titulo=linha[1],
                    descricao=linha[2],
                    foto_path=linha[4],
                    local=linha[5],
                    status=linha[6],
                    data_registro=linha[7]
                )
            else:
                item = ItemAchado(
                    id_item=linha[0],
                    titulo=linha[1],
                    descricao=linha[2],
                    foto_path=linha[4],
                    local=linha[5],
                    status=linha[6],
                    data_registro=linha[7]
                )
            lista_modelos.append(item)
        return lista_modelos

    def obter_todos_itens(self):
        """Retorna todos os itens do banco convertidos em objetos do domínio."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT id_item, titulo, descricao, tipo_item, foto_path, local, status, data_registro
                FROM itens 
                ORDER BY id_item DESC
            """
            cursor.execute(query)
            linhas = cursor.fetchall()
            conn.close()
            
            return self._converter_para_objeto(linhas)
        except Exception as e:
            print(f"Erro ao buscar itens no modelo: {e}")
            return []

    def cadastrar_item(self, dados):
        """Insere um novo registro completo na tabela itens usando o dicionário mapeado."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = """
                INSERT INTO itens (titulo, descricao, local, tipo_item, status, foto_path, id_usuario)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (
                dados['titulo'],
                dados['descricao'],
                dados['local'],
                dados['tipo_item'],
                dados['status'],
                dados['foto_path'],
                dados.get('id_usuario')
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao cadastrar item no banco: {e}")
            return False

    def buscar_itens_por_filtro(self, termo):
        """Busca itens filtrados pelo termo digitado no título ou descrição."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            query = """
                SELECT id_item, titulo, descricao, tipo_item, foto_path, local, status, data_registro
                FROM itens 
                WHERE titulo LIKE ? OR descricao LIKE ?
                ORDER BY id_item DESC
            """
            parametro = f"%{termo}%"
            cursor.execute(query, (parametro, parametro))
            linhas = cursor.fetchall()
            conn.close()
            return self._converter_para_objeto(linhas)
        except Exception as e:
            print(f"Erro ao filtrar itens: {e}")
            return []