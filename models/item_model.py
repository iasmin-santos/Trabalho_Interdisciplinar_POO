import sqlite3

class ItemModel:
    def __init__(self, database):
        self.db = database

    def _converter_para_objeto(self, linhas):
        """Método auxiliar interno para encapsular linhas do banco em objetos com propriedades."""
        lista_modelos = []
        for linha in linhas:
            class ItemEstruturado:
                def __init__(self, id_item, titulo, descricao, tipo_item, foto_path, local, status, data_registro):
                    self.id_item = id_item
                    self.titulo = titulo
                    self.descricao = descricao
                    self.tipo_item = tipo_item
                    self.foto_path = foto_path
                    self.local = local
                    self.status = status
                    self.data_registro = data_registro
            
            # Mapeia exatamente as posições do SELECT das suas queries (8 colunas)
            item = ItemEstruturado(
                id_item=linha[0],
                titulo=linha[1],
                descricao=linha[2],
                tipo_item=linha[3],
                foto_path=linha[4],
                local=linha[5],
                status=linha[6],
                data_registro=linha[7]
            )
            lista_modelos.append(item)
        return lista_modelos

    def obter_todos_itens(self):
        """Retorna todos os itens do banco convertidos em objetos estruturados."""
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
            
            # ALTERAÇÃO: Agora também converte para objetos antes de retornar!
            return self._converter_para_objeto(linhas)
        except Exception as e:
            print(f"Erro ao buscar itens no modelo: {e}")
            return []

    def cadastrar_item(self, dados):
        """Insere um novo registro completo na tabela itens."""
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
        """Busca itens que correspondam ao termo digitado no título ou descrição."""
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