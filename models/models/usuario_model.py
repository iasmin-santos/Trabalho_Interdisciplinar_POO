import sqlite3
import bcrypt 

class UsuarioModel:
    def __init__(self, database):
        self.db = database  # Recebe a instância da classe Database

    def cadastrar_usuario(self, dados):
        #Hash com bcrypt
        senha_clean =dados.get('senha')
        if not senha_clean:
            return False 

        senha_bytes= senha_clean.encode('utf-8')
        #salt e o hash da senha
        senha_hash_bytes = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())
        #converte a hash pra string 
        senha_criptografada=senha_hash_bytes.decode('utf-8')

        query = '''
            INSERT INTO usuarios (nome, email, senha, nascimento, tipo_usuario, ra, curso, periodo, semestre, cargo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''

        valores = (
            dados.get('nome'), dados.get('email'), senha_criptografada, 
            dados.get('nascimento'), dados.get('tipo_usuario'), dados.get('ra'),
            dados.get('curso'), dados.get('periodo'), dados.get('semestre'), dados.get('cargo')
        )
        try:
            conn = self.db.get_connection() # Usa a conexão do seu banco principal
            cursor = conn.cursor()
            cursor.execute(query, valores)
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Erro: {e}")
            return False

    def verificar_login(self, email, senha_teste):
        """Busca o usuario pelo e-mail e valida a senha com o Bcrypt"""
        if not email or not senha_teste:
            return False 

        query= "SELECT senha FROM usuarios WHERE email =?"

        try: 
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (email,))
            resultado = cursor.fetchone()
            conn.close()

            #Se o email não for encontrado no database, retorna False
            if resultado is None:
                return False

            #Recupera senha criptografada do database
            senha_hash_banco = resultado[0]

            #converte a senha do db pra bytes
            senha_teste_bytes = senha_teste.encode('utf-8')
            senha_hash_bytes =  senha_hash_banco.encode('utf-8')

            #Valida a senha com bcrypt
            return bcrypt.checkpw(senha_teste_bytes, senha_hash_bytes)
        
        except sqlite3.Error as e: 
            print(f"Erro no login: {e}")
            return False 
        
