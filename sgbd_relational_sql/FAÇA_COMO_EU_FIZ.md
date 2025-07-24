## **Faça como eu fiz: criando as outras tabelas**

Para criar uma tabela usamos o comando `CREATE TABLE` e logo em seguida o nome da tabela que será criada. Após o nome da tabela abrimos e fechamos parênteses, e todos os campos e seus tipos serão definidos dentro desses parênteses. Para finalizar também será declarado o campo que é chave primária usando o comando `PRIMARY KEY`.

O modelo relacional do Clube do Livro define quatro diferentes tipos de tabelas: Livros, Estoque, Vendas e Vendedores. Construa comigo cada uma delas!

1. Tabela `Livros`:

```sql
CREATE TABLE LIVROS (
    ID_LIVRO INT NOT NULL,
    NOME_LIVRO VARCHAR(100) NOT NULL,
    AUTORIA VARCHAR(100) NOT NULL,
    EDITORA VARCHAR(100) NOT NULL,
    CATEGORIA VARCHAR(100) NOT NULL,
    PREÇO DECIMAL(5,2) NOT NULL,
 PRIMARY KEY (ID_LIVRO)
);
```

2. Tabela Estoque:

```sql
CREATE TABLE ESTOQUE (
    ID_LIVRO INT NOT NULL,
    QTD_ESTOQUE INT NOT NULL,
 PRIMARY KEY (ID_LIVRO)
);
```

3. Tabela Vendas:

```sql
CREATE TABLE VENDAS (
    ID_PEDIDO INT NOT NULL,
    ID_VENDEDOR INT NOT NULL,
    ID_LIVRO INT NOT NULL,
    QTD_VENDIDA INT NOT NULL,
    DATA_VENDA DATE NOT NULL,
 PRIMARY KEY (ID_VENDEDOR,ID_PEDIDO)
);
```

4. Tabela Vendedores:

```sql
CREATE TABLE VENDEDORES (
    ID_VENDEDOR INT NOT NULL,
    NOME_VENDEDOR VARCHAR(255) NOT NULL,
 PRIMARY KEY (ID_VENDEDOR)
);
```

## **Faça como eu fiz: definindo as relações entre tabelas**

Para estabelecer a relação entre duas tabelas já criadas é preciso alterar uma tabela definindo o campo que será a chave estrangeira e finalizando fazendo referência ao campo de outra tabela. No modelo relacional abaixo, percebemos três diferentes ligações. Vamos criar cada uma delas?

![Modelo Relacional](assets/aula2.png)

1. Relação entre as tabelas `Vendas` e `Livros`

O comando abaixo irá alterar a tabela `Vendas` (tabela filha), adicionando a restrição de chave estrangeira apelidada de `CE_VENDAS_LIVROS` que referencia a tabela `Livros` (tabela pai), vinculando as colunas `ID_LIVRO` de ambas as tabelas.

```sql
ALTER TABLE VENDAS ADD CONSTRAINT CE_VENDAS_LIVROS
FOREIGN KEY (ID_LIVRO)
REFERENCES LIVROS (ID_LIVRO)
ON DELETE NO ACTION
ON UPDATE NO ACTION;
```

2. Relação entre as tabelas `Livros` e `Estoque`

```sql
ALTER TABLE ESTOQUE ADD CONSTRAINT CE_ESTOQUE_LIVROS
FOREIGN KEY (ID_LIVRO)
REFERENCES LIVROS (ID_LIVRO)
ON DELETE NO ACTION
ON UPDATE NO ACTION;
```

Lembrando que essa relação já foi a adicionada no vídeo anterior, integridades referenciais, caso já tenha feito pode pular para o próximo passo para evitar duplicidade.

3. Relação entre as tabelas `Vendedores` e `Vendas`

```sql
ALTER TABLE VENDAS ADD CONSTRAINT CE_VENDAS_VENDEDORES
FOREIGN KEY (ID_VENDEDOR)
REFERENCES VENDEDORES (ID_VENDEDOR)
ON DELETE NO ACTION
ON UPDATE NO ACTION;
```

Após escrever todas as restrições, basta selecionar o código e executá-lo. No MySQL Workbench, é usando o atalho CTRL + ENTER ou apertando no botão de raio no menu superior.

A restrição de **chave estrangeira** garante a integridade referencial. Aqui no “faça como eu fiz”, foram estabelecidas todas as ligações entre tabelas do modelo relacional do Clube do Livro.

Lembre-se que declaramos o padrão `NO ACTION` para os comandos `ON DELETE` e `ON UPDATE`, a qual, de modo simplificado, significa que será gerado um erro ao alterar uma nova observação na tabela filha que não exista na tabela pai. Essa é uma das maneiras de personalizar a referência entre as tabelas.
