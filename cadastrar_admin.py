import sqlite3
import os

db_path = "achados_e_perdidos.db"

if not os.path.exists(db_path):
    for f in os.listdir("."):
        if f.endswith(".db"):
            db_path = f
            break

print(f"Usando banco de dados em: {db_path}")

conexao = sqlite3.connect(db_path)
cursor = conexao.cursor()

try:
    # Passando 'Integral' no campo periodo para satisfazer a CHECK constraint
    cursor.execute("""
        INSERT INTO usuarios (nome, email, senha, tipo_usuario, cargo, periodo)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ("Bibliotecária Admin", "biblioteca@ifmg.edu.br", "12345", "funcionario", "Bibliotecária", "Integral"))
    
    conexao.commit()
    print("[SUCESSO]: Administrador inserido diretamente na base de dados!")
except Exception as e:
    print(f"[ERRO]: Falha ao inserir no banco: {e}")
finally:
    conexao.close()  