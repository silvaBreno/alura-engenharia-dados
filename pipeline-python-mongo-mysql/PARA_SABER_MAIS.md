## **Para saber mais: deletando um banco de dados**

Durante o desenvolvimento de projetos, às vezes precisamos fazer uma faxina, eliminando bancos de dados que não são mais necessários. Seja para liberar espaço ou manter a organização, o **pymongo** – a biblioteca Python para trabalhar com MongoDB – torna isso simples com o comando `drop_database`.

O drop_database é uma operação que **deve ser usada com cautela**. Quando executado, ele irá eliminar completamente o banco de dados especificado, junto com todas as suas coleções e documentos. Aqui está um exemplo de como utilizá-lo:

```python
client.drop_database("nome_do_banco_de_dados")
```  
Neste caso, "nome_do_banco_de_dados" deve ser substituído pelo nome do banco de dados que desejamos excluir. Este comando informa ao pymongo para eliminar o banco de dados correspondente no servidor MongoDB conectado. Uma vez realizado, não há como reverter a operação. O banco de dados e todo o seu conteúdo serão permanentemente removidos.

## **Para saber mais: link da API**

Como já sabemos, os registros referentes aos produtos vendidos pela empresa de e-commerce estão armazenados em uma API. A URL que nos permite acessar esses dados é: https://labdados.com/produtos

Os dados contidos nesse link estão formatados em JSON, que é um formato amplamente utilizado para intercâmbio de dados entre cliente-servidor na web. A boa notícia é que esse formato é plenamente compatível com o MongoDB, o que facilitará nosso processo de inserção dos dados em nossa base.

Lembre de guardar essa URL, pois ela será a porta de entrada para a aquisição dos dados que necessitamos. No próximo passo, vamos realizar a extração desses dados.

## **Para saber mais: método find()**

Lembra do método `find_one()` que vimos anteriormente? Ele é usado para recuperar um único documento de uma coleção que corresponda a um determinado critério. Agora, vamos falar sobre o método `find()` que é bastante similar, porém usado para recuperar múltiplos documentos de uma coleção.

O método `find()` do pymongo é usado para buscar documentos em uma coleção no MongoDB. Ele é equivalente a uma operação de SELECT em um banco de dados SQL. Este método é bastante flexível e poderoso, pois permite especificar critérios de pesquisa, controlar o número de documentos retornados e ordenar os resultados.

O método `find()` pode receber os seguintes parâmetros:

1. **query (opcional):** um filtro que especifica as condições que os documentos devem atender para serem retornados. É basicamente um dicionário Python que especifica os campos e valores que você está procurando. Por exemplo, `{"Produto": "Corda de pular"}` procuraria por todos os documentos onde o campo "Produto" é igual a "Corda de pular". Se o parâmetro query for omitido, o método `find()` retornará todos os documentos na coleção.

2. **projection (opcional):** filtro para especificar quais campos devem ser incluídos nos documentos retornados. É útil quando você tem interesse apenas em alguns campos específicos e não em todo o documento.

O retorno do método `find()` é um objeto Cursor que você pode iterar para acessar os documentos retornados. É importante lembrar que os dados realmente não são recuperados do banco de dados até que a gente comece a iterar o cursor. Isso é conhecido como "lazy loading" e pode ser muito eficiente quando se lida com grandes quantidades de dados.

Aqui está um exemplo de como poderíamos usar o método `find()`:

```python
cursor = collection.find({"Produto": "Corda de pular"}, {"_id": 0, "Produto": 1, "Data da Compra": 1, "Vendedor": 1})

for doc in cursor:
    print(doc)
```  

Nele estamos buscando todos os documentos onde o campo "Produto" é igual a "Corda de pular". Além disso, estamos solicitando que apenas os campos "Produto", "Data da Compra" e "Vendedor" sejam retornados em cada documento (estamos excluindo o campo "_id", que é incluído por padrão).

Portanto, este script imprimirá todas as vendas do produto "Corda de pular", mostrando apenas o nome do produto, a data da compra e o vendedor para cada venda.

## **Para saber mais: Regex**

Em algumas situações, precisamos buscar dados que não sabemos exatamente como são, mas temos uma ideia do formato. Nesse caso, podemos utilizar expressões regulares, ou **Regex**, que são uma sequência de caracteres que definem um padrão de busca.

No nosso caso, utilizamos um comando para buscar todos os produtos cuja data de compra ocorreu a partir de 2021. O código foi o seguinte:

```python
query = {"Data da Compra": {"$regex": "/202[1-9]"}}

lista_produtos = []
for doc in collection.find(query):
    lista_produtos.append(doc)
```  

A expressão "/202[1-9]" é uma regex que define o padrão de busca. Vamos entender melhor:

- `/202:` corresponde exatamente aos caracteres "/202". Ou seja, estamos buscando strings que possuam em sua composição o padrão /202.
- `[1-9]:` corresponde a qualquer caractere único entre 1 e 9. Como estamos buscando por anos a partir de 2021, queremos que o quarto dígito seja pelo menos 1.
Assim, o comando busca por todas as datas de compra que tenham os caracteres "/202" seguidos de qualquer dígito de 1 a 9, o que inclui todos os anos de 2021 a 2029.

As expressões regulares são ferramentas poderosas e podem ser bastante complexas, permitindo definir padrões de busca muito específicos. Se quiser aprender mais sobre elas, recomendo o Alura+: [Manipulação de strings com Pandas.](https://unibb.alura.com.br/extra/alura-mais/manipulacao-de-strings-com-pandas-c2003)

## **Para saber mais: operadores de consulta**

O pymongo, assim como o MongoDB, suporta uma variedade de operadores de consulta para lidar com diferentes situações. Aqui estão alguns dos mais comumente usados:

- $gt: captura documentos no qual o valor de um campo é superior ao especificado.
- $gte: utilizado quando o valor de um campo precisa ser maior ou igual ao valor especificado.
- $lt: encontra documentos em que o valor de um campo é menor que o especificado.
- $lte: utilizado para valores de campos menores ou iguais ao valor especificado.
- $ne: filtra documentos nos quais o valor de um campo é diferente do valor especificado.
- $in: útil quando o valor de um campo está dentro de um conjunto especificado de valores.
- $nin: encontra documentos em que o valor de um campo não está em um conjunto especificado de valores.
- $regex: permite a utilização de uma expressão regular para correspondências mais complexas.

Vamos ver alguns exemplos de como podemos usar estes operadores:

- **$gt:** encontra documentos onde o "Preço" é superior a 500.
```python
query = {"Preço": {"$gt": 500}}
``` 
- **$gte:** localiza documentos onde a "Avaliação da compra" seja maior ou igual a 4. 
```python
query = {"Avaliação da compra": {"$gte": 4}}
``` 
- **$lt:** busca documentos onde a "Quantidade de parcelas" é menor que 3.
```python
query = {"Quantidade de parcelas": {"$lt": 3}}
``` 
- **$lte:** seleciona documentos em que o "Frete" seja menor ou igual a 50.
```python
query = {"Frete": {"$lte": 50}}
``` 
- **$ne:** localiza documentos em que o "Tipo de pagamento" não seja "cartao_credito".
```python
query = {"Tipo de pagamento": {"$ne": "cartao_credito"}}
``` 
- **$in:** filtra documentos nos quais a "Categoria do Produto" seja "esporte e lazer" ou "eletrônicos".
```python
query = {"Categoria do Produto": {"$in": ["esporte e lazer", "eletronicos"]}}
``` 
- **$nin:** busca documentos nos quais a "Categoria do Produto" não seja nem "esporte e lazer" nem "eletrônicos".
```python
query = {"Categoria do Produto": {"$nin": ["esporte e lazer", "eletronicos"]}}
``` 
- **$regex:** encontra todos os vendedores cujos nomes começam com "Ma".
```python
query = {"Vendedor": {"$regex": "^Ma"}}
``` 
Todos esses exemplos utilizam o método collection.find(query). Este método retornará um cursor que permite percorrer os documentos que atendem aos critérios da consulta. Para imprimir os documentos, podemos usar um loop `for`.

```python
for doc in collection.find(query):
    print(doc)
``` 

Esses são apenas alguns exemplos do que é possível fazer com os operadores disponíveis. Para uma lista completa, você pode consultar a [documentação oficial do mongodb.](https://www.mongodb.com/docs/manual/reference/operator/query/)

## **Para saber mais: conhecendo o mysql.connector**

O `mysql.connector` é uma biblioteca Python que permite a conexão com um banco de dados MySQL a partir de um script Python. Isso é feito através do MySQL Connector/Python, um driver de banco de dados que permite que as aplicações Python se comuniquem com os servidores MySQL.

Essa biblioteca apresenta diversas funcionalidades essenciais na manipulação de bancos de dados. Entre as principais, podemos destacar:

1. **`connect():`** é o método que estabelece a conexão entre a aplicação Python e o servidor de banco de dados. Ele é essencial para iniciar qualquer operação no banco de dados. O método connect() requer parâmetros como host, usuário, senha e nome do banco de dados para estabelecer a conexão.

2. **`cursor():`** uma vez estabelecida a conexão, a função cursor() é utilizada para criar um objeto cursor. Esse objeto é uma interface que permite a execução de comandos SQL e a manipulação dos registros do banco de dados. O cursor permite navegar, buscar, inserir e excluir registros na base de dados.

3. **`execute():`** método que efetivamente executa os comandos SQL. Ele é aplicado através do objeto cursor e recebe como parâmetro a string do comando SQL a ser executado.

Utilizando o `mysql.connector`, é possível executar todas as operações padrão de um banco de dados, como: inserir, selecionar, atualizar e excluir dados em um banco de dados MySQL. Além disso, você pode usar esse módulo para realizar operações mais avançadas, como transações, procedimentos armazenados e muito mais. Assim, o `mysql.connector` torna-se uma ferramenta poderosa e flexível para a manipulação de bancos de dados MySQL a partir de aplicações Python.

Caso queira saber mais sobre essa biblioteca, consulte a documentação: [MySQL Connector/Python Developer Guide.](https://dev.mysql.com/doc/connector-python/en/)

## **Para saber mais: MySQL no terminal**

Da mesma forma que conseguimos criar e manipular bancos de dados utilizando o Python com o MySQL, também podemos realizar essas operações diretamente via terminal. Isso é possível graças ao MySQL Server que possui sua própria interface de linha de comando, permitindo a execução direta de comandos SQL.

Vamos ver um exemplo de como fazer isso:

1. Primeiramente, abra o terminal do MySQL com o seguinte comando:

```bash
sudo mysql
``` 
2. Com o terminal do MySQL aberto, vamos criar um banco de dados de exemplo chamado "mydb". Para isso, use o comando:
```sql
CREATE DATABASE mydb;
``` 
3. Após a criação, podemos conferir se o banco de dados foi criado corretamente listando todos os bancos de dados existentes:
```sql
SHOW DATABASES;
``` 
Nessa lista que será exibida, você deve ver o "mydb" que acabamos de criar.

4. Quando não precisarmos mais do banco de dados, podemos removê-lo com o comando DROP DATABASE. Lembre-se: isso irá apagar permanentemente o banco de dados e todos os dados armazenados nele.
```sql
DROP DATABASE mydb;
``` 
Para nossos propósitos no desenvolvimento de um pipeline de dados, optamos por utilizar Python para as operações de banco de dados, pois isso nos oferece maior flexibilidade e integração com o restante do nosso fluxo de trabalho automatizado.

## **Para saber mais: entendendo o %s**

No contexto das consultas SQL que executamos através do MySQL Connector em Python, o `%s` é um espaço reservado, ou seja, um substituto para um valor que queremos inserir na nossa base de dados.

Em nosso projeto, usamos `%s` em uma consulta SQL para inserir dados na tabela "tb_livros" do nosso banco de dados. Para fazer isso, a consulta SQL ficou da seguinte forma:

```python
sql = "INSERT INTO dbprodutos.tb_livros VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
``` 
Neste caso, cada `%s`  é um espaço reservado para os valores que queremos inserir na tabela. Estes valores são fornecidos por ` lista_dados` , que é uma lista de tuplas, em que cada tupla contém os valores para uma linha da tabela.

Quando executamos a consulta SQL com o método ` executemany()` , cada `%s`  na consulta é substituído por um valor da tupla correspondente em ` lista_dados`. O módulo MySQL Connector cuida de fazer esta substituição por nós.

Desta forma, podemos preparar uma consulta SQL uma única vez, e então usar essa consulta para inserir muitos dados diferentes, simplesmente fornecendo diferentes valores para substituir os `%s` . Isso nos permite inserir muitos dados de forma eficiente e sem ter que escrever uma consulta SQL diferente para cada conjunto de valores.

Para maiores informações, consulte a [documentação oficial do MySQL Connector.](https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-execute.html)

## **Para saber mais: arquivo .env**

Quando estamos desenvolvendo um projeto, muitas vezes temos que lidar com informações sensíveis, como chaves de acesso, senhas, nomes de usuários(as) e outras configurações que não gostaríamos de expor publicamente, especialmente se o projeto for hospedado em um repositório público no GitHub.

Nesses casos, podemos usar um arquivo `.env` para armazenar essas informações. O `.env` é um arquivo de texto simples que armazena variáveis de ambiente para um projeto específico. Ele é muito útil para esconder informações sensíveis, como senhas, chaves secretas ou qualquer outro tipo de dado que você não deseja expor em seu código fonte. Nele definimos variáveis de ambiente no seguinte formato:

```bash
NOME_DA_VARIAVEL=valor_da_variavel
``` 
Por exemplo, no nosso caso, poderíamos ter um arquivo .env assim:

```bash
MONGODB_URI="mongodb+srv://millenagena:12345@cluster-pipeline.bsouxli.mongodb.net/?retryWrites=true&w=majority"
DB_HOST="localhost"
DB_USERNAME="millenagena"
DB_PASSWORD="12345"
``` 

Uma vez criado o arquivo .env, precisamos instalar a biblioteca python-dotenv que nos permite carregar essas variáveis de ambiente em nosso script Python. A instalação pode ser feita utilizando o gerenciador de pacotes pip:

```python
source venv/bin/activate
``` 

```python
pip install python-dotenv
``` 

Depois disso, no nosso script, podemos carregar e usar essas variáveis da seguinte forma:

```python
import os
from dotenv import load_dotenv
import mysql.connector

# Carrega as variáveis do arquivo .env no ambiente de trabalho
load_dotenv()

# A função os.getenv é usada para obter o valor das variáveis de ambiente
host = os.getenv("DB_HOST")
user = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")

cnx = mysql.connector.connect(
    host=host,
    user=user,
    password=password
)

print(cnx)
``` 

E também podemos aplicar esse processo para a variável uri no código de conexão do Python com o MongoDB. Assim, o conteúdo sensível é substituído por uri=os.getenv("MONGODB_URI") e a URI real é mantida segura no arquivo .env. Dessa maneira, os dados sensíveis não estão expostos no código, mas ainda podem ser facilmente acessados através das variáveis de ambiente.

```
Lembre-se: não inclua o arquivo .env em seu controle de versão (como GitHub), pois isso pode expor todas as suas informações sensíveis. Geralmente, adiciona-se o .env ao arquivo .gitignore para evitar que ele seja enviado para um repositório público.
``` 

Agora você sabe como utilizar o arquivo .env para proteger informações sensíveis em seus projetos Python! Para maiores informações, consulte a [documentação oficial do python-dotenv.](https://pypi.org/project/python-dotenv/)

## **Para saber mais: salvando seu projeto no GitHub**
Salvar e compartilhar seu projeto no GitHub é uma prática muito valiosa, seja para construção de um portfólio pessoal, trabalho em equipe ou mesmo para que outras pessoas da comunidade possam aprender com o seu trabalho. O GitHub é uma das plataformas mais utilizadas no mundo para hospedagem de código fonte com controle de versão usando o Git.

Guardar as versões do seu projeto no GitHub traz uma série de vantagens:

1. **Controle de Versão:** o GitHub proporciona um histórico completo do seu projeto. Isso permite rastrear progresso, bem como entender porque determinadas decisões foram tomadas ao longo do caminho. Além disso, você pode experimentar novas ideias em branches separados, sem o risco de desestabilizar a versão principal do seu projeto.

2. **Portfólio:** se você está se candidatando para empregos ou estágios, o GitHub pode funcionar como um portfólio de seus projetos e demonstrar suas habilidades técnicas.

3. **Colaboração:** se você estiver trabalhando em equipe, o GitHub permite que múltiplas pessoas desenvolvedoras contribuam no mesmo projeto sem interferir no trabalho umas das outras.

4. **Contribuição para a comunidade:** ao publicar seu trabalho no GitHub, você está contribuindo para a comunidade de desenvolvedores. Outros podem aprender com seu projeto ou até mesmo colaborar com melhorias e correções.

5. **Backup:** ao guardar seu projeto no GitHub, você cria uma cópia na nuvem. Isso significa que se algo acontecer com seu computador, seu trabalho estará a salvo.

No entanto, ao publicar seu projeto no GitHub, **é importante ter cuidado para não expor dados sensíveis, como chaves de API, senhas ou informações pessoais.** Como mencionado na atividade ["Para saber mais: Arquivo .env"](https://unibb.alura.com.br/course/pipeline-dados-integrando-python-mongodb-mysql/task/138703), a utilização de arquivos .env para guardar esses dados sensíveis é uma prática segura e recomendada, especialmente ao compartilhar seu projeto publicamente.

Caso queira aprender diferentes maneiras de subir seu projeto no [GitHub: diferentes maneiras de compartilhar seu projeto.](https://unibb.alura.com.br/extra/alura-mais/github-diferentes-maneiras-de-compartilhar-seu-projeto-c2002)