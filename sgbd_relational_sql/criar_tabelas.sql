create table LIVROS (
	ID_LIVRO INT not null,
	NOME_LIVRO VARCHAR(100) not null,
	AUTORIA VARCHAR(100) not null,
	EDITORA VARCHAR(100) not null,
	CATEGORIA VARCHAR(100) not null,
	PRECO DECIMAL(5,2) not null,
	
	primary key (ID_LIVRO)
);

CREATE TABLE ESTOQUE (
	id_livro INT NOT NULL PRIMARY KEY,
	qtd_estoque INT NOT NULL
);

CREATE TABLE VENDAS (
	id_pedido INT NOT NULL,
	id_vendedor INT NOT NULL,
	id_livro INT NOT NULL,
	qnd_vendida INT NOT NULL,
	data_venda DATE NOT NULL,
	PRIMARY KEY (id_pedido, id_vendedor)
);

CREATE TABLE VENDEDORES (
	id_vendedor INT NOT NULL PRIMARY KEY,
	nome_vendedor VARCHAR(255) NOT NULL
);

-- Agora precisamos criar o relacionamento entre as tabelas, mas nesse caso como já criamos as tabelas precisamos realizar as alterações necessárias:

ALTER TABLE ESTOQUE ADD CONSTRAINT CE_ESTOQUE_LIVROS
FOREIGN KEY (id_livro)
REFERENCES livros (id_livro)
ON DELETE NO ACTION
ON UPDATE NO ACTION;

ALTER TABLE VENDAS ADD CONSTRAINT CE_VENDAS
FOREIGN KEY (id_livro)
REFERENCES livros (id_livro);

ALTER TABLE VENDAS ADD CONSTRAINT CE_VENDAS
FOREIGN KEY (id_vendedor)
REFERENCES vendedores(id_vendedor);


