# ACHADOS E PERDIDOS IFMG
## 🎯Sobre o projeto 
O Achados e Perdidos IFMG é um sistema desenvolvido para auxiliar no registro e na localização de objetos perdidos dentro do campus Ibirité. O objetivo é facilitar a comunicação entre quem encontrou um item e seu possível proprietário.
## 🛠️Tecnologias utilizadas
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-41CD52?logo=pyside&logoColor=white)
![Qt Designer](https://img.shields.io/badge/Qt%20Designer-41CD52?logo=qt&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)
## ✨Funcionalidades
- Cadastro de usuários.
- Cadastro de objetos encontrados.
- Consulta de itens cadastrados.
- Registro da devolução de itens.
## 📌 Arquitetura do Projeto e Diagrama de Classes
O projeto foi estruturado seguindo o padrão arquitetural Model-View-Controller (MVC). A camada de View carrega interfaces dinamicamente via `QUiLoader` a partir de arquivos `.ui`, além de renderizar componentes reutilizáveis como o `item_card.py`. A persistência utiliza uma base de dados relacional SQLite (`achados_e_perdidos.db`), centralizada em uma classe `Database` e estendida por um `BaseModel`. O domínio do sistema aplica conceitos avançados de POO, utilizando classes abstratas (`Item` e `Usuario`) que se ramificam polimorficamente em especializações para o ecossistema acadêmico do IFMG (como `Aluno`, `Funcionario`, `ItemPerdido` e `ItemAchado`).
Projeto desenvolvido para a disciplina Trabalho de Extensão: Orientação a objetos do Curso de Ciência da Computação do IFMG-Campus Ibirité.
