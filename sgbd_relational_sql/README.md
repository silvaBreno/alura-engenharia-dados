# Projeto de Estudo: Modelagem de Banco de Dados Relacional com SQL

Este repositório contém os scripts e anotações do projeto de estudo sobre modelagem de banco de dados relacional e SQL, desenvolvido durante o curso da [Alura](https://www.alura.com.br/). O objetivo principal foi aplicar conceitos teóricos de bancos de dados, desde a criação do schema até a execução de consultas complexas.

## 🎯 Objetivo

O projeto simula a gestão de uma livraria, chamada "Clube do Livro", e aborda os seguintes tópicos:

- Criação de um schema de banco de dados.
- Definição de tabelas, colunas e tipos de dados.
- Estabelecimento de chaves primárias e estrangeiras para garantir a integridade referencial.
- Inserção, atualização e exclusão de dados (`INSERT`, `UPDATE`, `DELETE`).
- Realização de consultas (`SELECT`) com filtros (`WHERE`), ordenação (`ORDER BY`) e junções (`JOIN`).
- Uso de funções de agregação (`SUM`, `COUNT`, `GROUP BY`) para gerar métricas.

## 🛠️ Tecnologias Utilizadas

- **SGBD:** MySQL
- **Servidor:** Uniform Server Zero
- **Cliente SQL:** DBeaver

## 📂 Estrutura do Repositório

O projeto está organizado nos seguintes arquivos:

```
sgbd_relational_sql/
├── criar_schema.sql        # Script para a criação do schema do banco de dados.
├── criar_tabelas.sql       # Script para criar as tabelas e definir os relacionamentos (chaves estrangeiras).
├── inserindo_dados.sql     # Script para popular as tabelas com dados iniciais.
├── consultando_dados.sql   # Exemplos de consultas SQL, de simples a complexas, utilizando JOINs e agregações.
├── alterando_dados.sql     # Exemplos de comandos UPDATE e DELETE para modificar os dados.
├── FAÇA_COMO_EU_FIZ.md     # Anotações no estilo "passo a passo" do curso.
└── PARA_SABER_MAIS.md      # Anotações com conceitos teóricos aprofundados sobre SQL.
```

## 🗄️ Modelo do Banco de Dados

O banco de dados `clube_do_livro` é composto por quatro tabelas principais:

1.  **`livros`**: Armazena informações sobre os livros, como título, autor, editora, categoria e preço.
2.  **`vendedores`**: Contém os dados dos vendedores da loja.
3.  **`vendas`**: Registra todas as vendas realizadas, relacionando um vendedor, um livro e a quantidade vendida.
4.  **`estoque`**: Controla a quantidade de cada livro disponível no estoque.

### Diagrama de Relacionamento

```mermaiderDiagram
    LIVROS {
        INT id_livro PK
        VARCHAR nome_livro
        VARCHAR autoria
        VARCHAR editora
        VARCHAR categoria
        DECIMAL preco
    }
    VENDAS {
        INT id_pedido PK
        INT id_vendedor PK, FK
        INT id_livro FK
        INT qnd_vendida
        DATE data_venda
    }
    VENDEDORES {
        INT id_vendedor PK
        VARCHAR nome_vendedor
    }
    ESTOQUE {
        INT id_livro PK, FK
        INT qtd_estoque
    }

    LIVROS ||--o{ VENDAS : "contém"
    LIVROS ||--|| ESTOQUE : "possui"
    VENDEDORES ||--o{ VENDAS : "realiza"
```

## 🚀 Como Executar

Para recriar o banco de dados e executar as consultas, siga os passos abaixo na ordem sugerida, utilizando um cliente SQL como o DBeaver conectado a uma instância MySQL.

1.  **Criar o Schema:**
    Execute o conteúdo do arquivo `criar_schema.sql`.
    ```sql
    CREATE SCHEMA clube_do_livro;
    ```

2.  **Criar as Tabelas e Relacionamentos:**
    Execute o conteúdo do arquivo `criar_tabelas.sql` para criar a estrutura das tabelas e suas chaves.

3.  **Inserir os Dados:**
    Execute o conteúdo do arquivo `inserindo_dados.sql` para popular o banco de dados.

4.  **Consultar e Manipular:**
    Utilize os scripts `consultando_dados.sql` e `alterando_dados.sql` para explorar os dados e testar diferentes comandos SQL.

---
*Este projeto é um reflexo do meu aprendizado e dedicação no estudo de tecnologias de dados. Sinta-se à vontade para explorar o código e as anotações.*

