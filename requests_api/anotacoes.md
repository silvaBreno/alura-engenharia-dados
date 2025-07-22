## Para saber mais: o que são headers?

### Próxima Atividade

Quando precisamos fazer um pedido ou resposta HTTP, utilizamos **headers** para enviar informações junto com as requisições. Geralmente, headers contêm itens importantes sobre o pedido ou a resposta de uma requisição, como:

- Data
- Hora
- Utilização do navegador
- Informações de autenticação, como o **Token**

Esse recurso é muito útil para ajudar o servidor a entender melhor o que está sendo pedido e como será respondido de forma adequada.

Por exemplo, se alguém estiver tentando acessar uma página protegida por senha, o servidor pode verificar o header **“Authorization”** para garantir que essa pessoa tem permissão para acessar o conteúdo da página.

O **“Authorization”** é um exemplo de header usado com frequência para autenticação. Esse header geralmente é usado para enviar um **token** (um código único que identifica se a pessoa usuária é legítima) para o servidor.

**Em resumo**, headers são informações importantes que ajudam a fazer a comunicação entre o cliente e o servidor funcionar como esperado.

## Para saber mais: outros tipos de autenticação

### Próxima Atividade

A autenticação em APIs é um processo que permite a verificação da identidade da pessoa usuária que está acessando os dados. Existem diferentes tipos de autenticação, cada um com suas características e formas de implementação. Os principais tipos de autenticação são:

### 1. Autenticação por chave de API (API Key)

Esse tipo de autenticação é o mais simples e comum. Nele, a API fornece uma chave de acesso exclusiva para cada pessoa usuária, que é usada como um "código de identificação".  
A chave é enviada junto com a requisição para a API e é verificada pelo servidor para permitir ou negar o acesso aos dados.

### 2. Autenticação por token

Nesse tipo de autenticação, a API fornece um token de acesso para a pessoa usuária após a autenticação bem-sucedida, geralmente usando um login e senha.  
O token é um código que permite que a pessoa usuária acesse os recursos da API sem precisar enviar novamente suas credenciais.  
Ele pode ter um tempo de validade, e a pessoa usuária pode precisar solicitar um novo token após o vencimento.

### 3. Autenticação por OAuth

O OAuth é um protocolo de autorização que permite que uma pessoa usuária conceda acesso a seus recursos em uma API, sem compartilhar suas credenciais de login com a aplicação de terceiros.  
Nesse tipo de autenticação:

- A pessoa usuária é redirecionada para a página de login da API para inserir suas credenciais.
- Depois, é solicitada à pessoa usuária a autorização para que a aplicação de terceiros acesse seus recursos.
- A autorização é concedida por meio de um **token OAuth**, que permite que a aplicação acesse apenas os recursos autorizados pela pessoa usuária.

### Exemplos de APIs que utilizam esses tipos de autenticação:

- **API da NASA**: usa uma chave de API para autenticação e controle de acesso.
- **API do GitHub**: usa token de acesso para autenticação e controle de acesso aos recursos.
- **API do Spotify**: usa OAuth para autenticação e autorização de acesso aos recursos.

## Para saber mais: tratamento de erros

### Próxima Atividade

Durante a extração dos dados de uma API, é importante considerar a possibilidade de tratar erros e exceções que podem ocorrer durante a execução do código.  
Caso os erros não sejam tratados de forma adequada, podemos ter comportamentos inesperados.

Nesse contexto, o uso de uma estrutura utilizando `try` e `except` pode ser fundamental para lidar com esses possíveis erros e exceções.  
Podemos exemplificar com a situação abaixo:

```python
numero = "trinta"

try:
    numero_inteiro = int(numero)
    print("O número inteiro é:", numero_inteiro)
except ValueError:
    print("Erro: a string não pode ser convertida para inteiro.")
```

Como foi dito, o `try-except` é uma estrutura em Python que permite lidar com exceções e erros durante a execução do seu código.  
No código de exemplo, tentamos converter a string `"trinta"` para inteiro com a função `int()`, mas como essa conversão não é possível, uma exceção do tipo `ValueError` é indicada.  
Então, o bloco `except` é acionado, e a mensagem que deixamos será a saída do nosso código.

O uso de técnicas para tratamento de erros e exceções oferece algumas vantagens, como:

### 1. Lidar com erros de forma prática

Quando ocorre um erro no código e não há tratamento para ele, o programa simplesmente para de executar.  
Usando `try/except`, você pode lidar com esses erros e garantir que seu programa continue funcionando, informando o que deu errado e executando o restante do código.

### 2. Facilitar a depuração do código

Quando ocorre um erro, o bloco `except` permite capturar informações importantes sobre o erro, como o tipo de exceção e a mensagem de erro.  
Isso facilita muito a depuração do seu código.

### 3. Manter o controle do fluxo do programa

Com o uso do bloco `try/except`, é possível garantir que o fluxo do programa continue, mesmo que ocorram erros.  
Isso é útil em situações em que várias tarefas precisam ser executadas, mesmo que uma ou mais delas não possam ser concluídas.
