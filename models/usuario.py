import sqlite3
import bcrypt 
from abc import ABC, abstractmethod

class Usuario(ABC):
    """Classe Abstrata que representa a entidade genérica Usuário do diagrama."""
    def __init__(self, nome, email, senha, data_nascimento, id_usuario=None):
        self.id_usuario = id_usuario
        self.nome = nome
        self.email = email
        self.senha = senha
        self.data_nascimento = data_nascimento

    @abstractmethod
    def validar(self):
        """Método abstrato obrigatório para validação das regras de negócio (Polimorfismo)."""
        pass

    def to_dict(self):
        """Mapeia os atributos base do usuário para persistência estruturada."""
        return {
            'nome': self.nome,
            'email': self.email,
            'senha': self.senha,
            'nascimento': self.data_nascimento,
            'tipo_usuario': self.__class__.__name__.lower() 
        }


class Aluno(Usuario):
    """Especialização de Usuário que encapsula os atributos e regras do Aluno."""
    def __init__(self, nome, email, senha, data_nascimento, ra, curso, periodo, semestre, id_usuario=None):
        super().__init__(nome, email, senha, data_nascimento, id_usuario)
        self.ra = ra
        self.curso = curso
        self.periodo = periodo
        self.semestre = semestre

    def validar(self):
        """Valida regras obrigatórias de negócio para o cadastro de alunos."""
        if not self.ra or len(self.ra) < 4:
            raise ValueError("O Registro Acadêmico (RA) é obrigatório e deve ser válido.")
        if not self.curso:
            raise ValueError("O curso do aluno precisa ser informado.")

    def to_dict(self):
        """Estende o mapeamento base injetando os atributos específicos de Aluno."""
        dados = super().to_dict()
        dados.update({
            'ra': self.ra,
            'curso': self.curso,
            'periodo': self.periodo,
            'semestre': self.semestre,
            'cargo': None
        })
        return dados


class Funcionario(Usuario):
    """Especialização de Usuário que encapsula os atributos e regras do Funcionário."""
    def __init__(self, nome, email, senha, data_nascimento, cargo, id_usuario=None):
        super().__init__(nome, email, senha, data_nascimento, id_usuario)
        self.cargo = cargo

    def validar(self):
        """Valida regras obrigatórias de negócio para o cadastro de funcionários."""
        if not self.cargo:
            raise ValueError("O cargo do funcionário é um campo obrigatório.")

    def to_dict(self):
        """Estende o mapeamento base injetando os atributos específicos de Funcionário."""
        dados = super().to_dict()
        dados.update({
            'ra': None,
            'curso': None,
            'periodo': None,
            'semestre': None,
            'cargo': self.cargo
        })
        return dados


class UsuarioModel:
    def __init__(self, database):
        self.db = database  

    def cadastrar_usuario(self, dados):
        """Criptografa a credencial de segurança e insere o registro completo na tabela."""
        senha_clean = dados.get('senha')
        if not senha_clean:
            return False 

        senha_bytes = senha_clean.encode('utf-8')
        # Salt e o hash da senha usando Bcrypt
        senha_hash_bytes = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())
        # Converte o hash para string antes de armazenar no banco
        senha_criptografada = senha_hash_bytes.decode('utf-8')

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
            conn = self.db.get_connection() 
            cursor = conn.cursor()
            cursor.execute(query, valores)
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao salvar usuário no banco: {e}")
            return False

    def verificar_login(self, email, senha_teste):
        """Busca o usuário pelo e-mail e valida a assinatura da senha digital via Bcrypt."""
        if not email or not senha_teste:
            return False 

        query = "SELECT senha FROM usuarios WHERE email =?"

        try: 
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (email,))
            resultado = cursor.fetchone()
            conn.close()

            # Se o e-mail não for localizado no banco, recusa o acesso
            if resultado is None:
                return False

            # Recupera a senha criptografada persistida no banco
            senha_hash_banco = resultado[0]

            # Transforma as cadeias de texto em bytes para a checagem segura do Bcrypt
            senha_teste_bytes = senha_teste.encode('utf-8')
            senha_hash_bytes = senha_hash_banco.encode('utf-8')

            # Valida criptograficamente o segredo enviado
            return bcrypt.checkpw(senha_teste_bytes, senha_hash_bytes)
        
        except sqlite3.Error as e: 
            print(f"Erro crítico durante rotina de login: {e}")
            return False