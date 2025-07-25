SELECT * FROM LIVROS;

SELECT ID_LIVRO FROM LIVROS;

SELECT ID_LIVRO AS "Código do Livro" FROM LIVROS;


# Filtrando registros que são da categoria Biografia
SELECT * FROM LIVROS WHERE CATEGORIA = "BIOGRAFIA";

# Primeira demanda: Uma tabela com os romances que custam menos de R$ 48
SELECT * FROM LIVROS WHERE (CATEGORIA = 'Romance' AND PRECO < 48)

# Segunda demanda: Uma tabela com poesias que não são nem de Luís Vaz de Camões, e nem de Gabriel Pedrosa.
SELECT * FROM LIVROS WHERE CATEGORIA = 'Poesia' AND NOT (AUTORIA = 'Luís Vaz de Camões' OR AUTORIA = 'Gabriel Pedrosa');

# Ou essa segunda opção
SELECT * FROM LIVROS WHERE CATEGORIA = 'Poesia' AND AUTORIA NOT IN ('Luís Vaz de Camões', 'Gabriel Pedrosa');

# Realizando agora, uma seleção distinta
SELECT DISTINCT ID_LIVRO FROM VENDAS WHERE id_vendedor = 1 ORDER BY ID_LIVRO ASC;

# imagine que o livro Os Lusíadas parou de ser vendido, precisamos deletar ele da base de dados
SET FOREIGN_KEY_CHECKS = 0;

DELETE FROM LIVROS WHERE ID_LIVRO = 8;

# imagine que avisaram que o preço dos livros estariam com 10% de desconto
UPDATE LIVROS SET PRECO = 0.9*PRECO;

# Unindo informações de tabelas diferentes
SELECT 
	v.id_vendedor, 
	vd.nome_vendedor,
	SUM(v.qnd_vendida) AS total_vendido
FROM VENDAS v
JOIN vendedores vd 
ON v.id_vendedor = vd.id_vendedor
GROUP BY v.id_vendedor;

SELECT 
	v.id_vendedor, 
	vd.nome_vendedor,
	COUNT(v.qnd_vendida) AS total_vendido
FROM VENDAS v
JOIN vendedores vd 
ON v.id_vendedor = vd.id_vendedor
GROUP BY v.id_vendedor;

SELECT 
	v.id_vendedor, 
	vd.nome_vendedor,
	v.qnd_vendida
FROM VENDAS v
JOIN vendedores vd 
ON v.id_vendedor = vd.id_vendedor;

## Será que todos os livros da nossa base de dados foram vendidos?
SELECT li.NOME_LIVRO, v.qnd_vendida 
FROM livros li
LEFT JOIN vendas v
ON li.ID_LIVRO = v.id_livro
WHERE v.qnd_vendida IS NULL;

SELECT li.ID_LIVRO,li.NOME_LIVRO, v.id_livro,v.qnd_vendida 
FROM livros li
RIGHT JOIN vendas v
ON li.ID_LIVRO = v.id_livro;

#######    Código Extra  ###############
#Filtrando com datas
SELECT * FROM VENDAS WHERE data_venda >= '2020-07-03';
SELECT * FROM VENDAS WHERE YEAR(data_venda) >= 2021;

SELECT @@sql_mode;

/* 
FUNCAO SUM()
SUM(v.qnd_vendida)

O que faz -> Soma os valores da coluna qnd_vendida
Exemplo prático -> Se um vendedor vendeu 3, depois 5, depois 2 livros → total = 10
*/

/* 
FUNCAO COUNT()
COUNT(v.qnd_vendida)

O que faz -> Conta quantas linhas têm valor não nulo em qnd_vendida
Exemplo prático -> Se houver 3 registros de venda (independente da quantidade) → total = 3
*/

