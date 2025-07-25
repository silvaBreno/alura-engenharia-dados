# imagine que o livro Os Lusíadas parou de ser vendido, precisamos deletar ele da base de dados
SET FOREIGN_KEY_CHECKS = 0;

DELETE FROM LIVROS WHERE ID_LIVRO = 8;

# imagine que avisaram que o preço dos livros estariam com 10% de desconto
UPDATE LIVROS SET PRECO = 0.9*PRECO;