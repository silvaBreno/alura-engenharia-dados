# Projeto: Pipeline de Dados de Vendas

Este projeto demonstra a construção de um pipeline de dados ETL (Extração, Transformação e Carga) em Python. O objetivo é consolidar e padronizar dados de vendas de duas fontes distintas (Empresa A e Empresa B), que estão em formatos diferentes (JSON e CSV), e unificá-los em um único arquivo CSV processado.

## 🚀 Objetivo

O principal objetivo é criar um processo automatizado para:
1.  **Extrair** dados de um arquivo JSON e um arquivo CSV.
2.  **Transformar** os dados para que tenham um esquema de colunas consistente.
3.  **Tratar** dados ausentes.
4.  **Unificar** os dois conjuntos de dados.
5.  **Carregar** o resultado em um novo arquivo CSV, pronto para análise.

## 📂 Estrutura do Projeto

O repositório está organizado da seguinte forma:


-   **`data_raw/`**: Contém os arquivos de dados brutos das empresas A (JSON) e B (CSV).
-   **`data_processed/`**: Armazena o arquivo de saída do pipeline (`dados_combinados.csv`).
-   **`notebooks/`**: Inclui o Jupyter Notebook (`exploracao.ipynb`) usado para a exploração inicial e desenvolvimento da lógica do pipeline.
-   **`scripts/`**: Contém os scripts Python para a execução do pipeline.
-   **`guia_config.md`**: Um guia detalhado para configurar o ambiente de desenvolvimento.

## ⚙️ O Processo ETL

O pipeline foi desenvolvido seguindo as três etapas clássicas do ETL:

### 1. Extração (Extract)

Os dados são lidos de duas fontes com formatos e estruturas distintas:

-   **Empresa A**: Um arquivo `JSON` (`dados_empresaA.json`) contendo uma lista de objetos, onde cada objeto representa um produto.
-   **Empresa B**: Um arquivo `CSV` (`dados_empresaB.csv`) com os dados de vendas, possuindo nomes de colunas diferentes da Empresa A.

As bibliotecas nativas do Python, `json` e `csv` (especificamente `csv.DictReader`), foram utilizadas para carregar os dados em memória como uma lista de dicionários, facilitando a manipulação.

### 2. Transformação (Transform)

Esta é a etapa mais complexa, onde os dados são limpos e padronizados:

-   **Padronização de Colunas**: Os nomes das colunas do arquivo da Empresa B foram mapeados e renomeados para corresponder ao padrão da Empresa A. Isso garante que ambos os conjuntos de dados compartilhem o mesmo esquema.

    *Mapeamento de Colunas:*
    ```python
    key_mapping = {
        'Nome do Item': 'Nome do Produto',
        'Classificação do Produto': 'Categoria do Produto',
        'Valor em Reais (R$)': 'Preço do Produto (R$)',
        'Quantidade em Estoque': 'Quantidade em Estoque',
        'Nome da Loja': 'Filial',
        'Data da Venda': 'Data da Venda'
    }
    ```

-   **Tratamento de Dados Ausentes**: Foi identificado que os dados da Empresa A não possuíam a coluna `Data da Venda`. Para manter a consistência, essa coluna foi adicionada a todos os registros da Empresa A com o valor padrão `"Indisponível"`. A função `dict.get(chave, valor_padrao)` foi essencial para essa tarefa.

-   **Unificação dos Dados**: Após a padronização, os dois conjuntos de dados foram combinados em uma única lista.

### 3. Carga (Load)

O conjunto de dados final, unificado e limpo, é salvo no diretório `data_processed/` como um novo arquivo CSV chamado `dados_combinados.csv`. Este arquivo está pronto para ser consumido por ferramentas de análise ou business intelligence.

## 💡 Evolução do Código

O desenvolvimento do projeto seguiu uma evolução natural:

1.  **Exploração em Notebook**: A lógica inicial foi desenvolvida no Jupyter Notebook `exploracao.ipynb`. Isso permitiu uma análise interativa dos dados e a identificação dos desafios de transformação.

2.  **Script Procedural**: A lógica foi inicialmente portada para um script Python (`fusao_mercado.py`) de forma procedural, com funções separadas para cada etapa do ETL.

3.  **Refatoração para Programação Orientada a Objetos (POO)**: Para melhorar a organização, o reuso e a manutenibilidade do código, a lógica foi refatorada de um script procedural (`fusao_mercado.py`) para uma abordagem orientada a objetos.
    -   **Abstração e Encapsulamento**: Foi criada a classe `Dados` no arquivo `processamento_dados.py`. Essa classe **abstrai** a complexidade da manipulação dos dados (sejam eles JSON ou CSV) e **encapsula** tanto os dados brutos (`self.dados`) quanto as operações que podem ser realizadas sobre eles (ler, renomear colunas, juntar, salvar).
    -   **Coesão e Reusabilidade**: Métodos como `rename_columns` e `salvando_dados` agora pertencem à classe `Dados`, tornando o código mais coeso e fácil de entender. Qualquer programador que utilize a classe não precisa saber *como* os dados são lidos ou salvos, apenas que pode chamar `Dados.leitura_dados()` e `dados_fusao.salvando_dados()`.
    -   **Orquestração Simplificada**: O script final, `fusao_mercado_fev.py`, tornou-se um "orquestrador" do pipeline. Ele utiliza as instâncias da classe `Dados` para executar as etapas de E-T-L de forma limpa, legível e com um alto nível de abstração, focando no "o quê" em vez do "como".

## 🛠️ Como Executar o Projeto

Para executar o pipeline de dados, siga os passos abaixo. Para um guia mais detalhado sobre a configuração do ambiente, consulte o arquivo `guia_config.md`.

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/pipeline_dados.git
    cd pipeline_dados
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    # Para Linux/macOS
    python3 -m venv .venv
    source .venv/bin/activate

    # Para Windows
    python -m venv .venv
    .\.venv\Scripts\activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute o pipeline:**
    ```bash
    python scripts/fusao_mercado_fev.py
    ```

Após a execução, o arquivo `data_processed/dados_combinados.csv` será criado com os dados unificados.

## 📚 Principais Aprendizados

-   Manipulação de diferentes formatos de arquivo (JSON e CSV) em Python.
-   Técnicas de padronização de esquemas de dados (renomeação de colunas).
-   Estratégias para lidar com dados ausentes ou inconsistentes.
-   Estruturação de um pipeline de ETL simples.
-   **Refatoração para Programação Orientada a Objetos (POO)**: Aplicação de **abstração** e **encapsulamento** para criar uma classe (`Dados`) coesa e reutilizável, separando as responsabilidades e simplificando o script principal do pipeline. Isso resultou em um código mais limpo e de fácil manutenção em comparação com a abordagem procedural inicial.
-   A importância do uso de ambientes virtuais para o gerenciamento de dependências.
