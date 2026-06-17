class ItemModel:
    def __init__(self, database):
        self.db = database

    def obter_ultimos_itens(self, limite=5):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT titulo, local, data_registro, tipo_item 
            FROM itens 
            WHERE status = 'Ativo' 
            ORDER BY data_registro DESC 
            LIMIT ?
        '''
        cursor.execute(query, (limite,))
        itens = cursor.fetchall()
        conn.close()
        
        return itens