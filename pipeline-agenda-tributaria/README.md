## 🚀 Pipeline de Dados da Agenda Tributária

Este projeto consiste em um pipeline de dados para extrair, transformar e carregar (ETL) informações da Agenda Tributária da Receita Federal do Brasil. O objetivo é coletar os dados brutos, processá-los e armazená-los em um formato JSON estruturado e de fácil consumo.

## 🎯 Funcionalidades

- **Extração de Dados**: Coleta as informações diretamente do site da Receita Federal.
- **Transformação e Limpeza**: Normaliza os dados brutos, padroniza chaves, trata valores nulos e categoriza os diferentes tipos de eventos (DARF, GPS, Declarações, etc.).
- **Estruturação**: Organiza os dados em um esquema JSON aninhado e enriquecido, facilitando consultas e análises.
- **Armazenamento**: Salva os dados processados em arquivos JSON, separados por ano.

## 📁 Estrutura do Projeto

```
pipeline-agenda-tributaria/
├── data/
│   ├── raw/
│   │   └── agenda_tributaria_2025.json  # Dados brutos extraídos
│   └── transformed/
│       └── agenda_tributaria_2025.json  # Dados processados e estruturados
├── src/                                     # (Sugestão) Código-fonte da pipeline
│   ├── __init__.py
│   ├── main.py                            # Orquestrador da pipeline
│   ├── extractor.py                       # Módulo de extração
│   ├── transformer.py                     # Módulo de transformação
│   └── loader.py                          # Módulo de carregamento
├── .venv/                                   # Ambiente virtual
├── README.md                              # Documentação do projeto
└── requirements.txt                       # Dependências do projeto


pipeline-agenda-tributaria/
├── .venv/                                          # Ambiente virtual
├── scripts
│     ├── init.py                                   # Inicialização do ambiente virtual
│     ├── main.py                                   # Orquestrador da pipeline
│     ├── extractor.py                              # Módulo de extração
│     ├── transformer.py                            # Módulo de transformação
│     └── loader.py                                 # Módulo de carregamento
├── data/
│     ├── raw/
│     │     └── agenda_tributaria_2025.json         # Dados extraídos do site (brutos)
│     └── transformed/
│           └── agenda_tributaria_2025.json         # Dados limpos e estruturados
├── logs/
│     └── agenda_tributaria_scrapper.log            # Registro de logs do processo de extração
├── notebooks/
│     └── exploracao_dados.ipynb                    # Análise exploratória dos dados
├── schemas/
│     └── agenda_schema.json                        # Schema JSON para validação dos dados
├── scripts/
│     └── agenda_scrapper.py                        # Script de extração dos dados
│     └── logger_config.py                          # Configuração do logger
│     └── json_validacao.py                         # Validação do schema do JSON
├── tests/
│     └── test_json_validacao.py                    # Teste de validação do schema do JSON
├── README.md                                       # Documentação do projeto
└── requirements.txt                                # Dependências do projeto

pipeline-agenda-tributaria/
├── scripts/
│   ├── main.py                # Orquestra o pipeline ETL
│   ├── extractor.py           # Extrai dados da página da Receita Federal
│   ├── transformer.py         # Limpa, normaliza e classifica os dados
│   ├── loader.py              # Valida e salva os dados em JSON
│   └── logger_config.py       # Configuração do sistema de logs
│
├── data/
│   ├── raw/                   # (opcional) dados brutos
│   ├── transformed/           # dados processados
│
├── schemas/
│   └── agenda_schema.json     # Schema para validação
│
├── tests/
│   └── test_extractor.py
│   └── test_transformer.py
│   └── test_loader.py
│
├── README.md
└── requirements.txt
```

### 📁 scripts/

**main.py**

Orquestra o pipeline completo:

- Extrai os dados com AgendaExtractor
- Transforma com AgendaTransformer
- Valida e salva com AgendaLoader
- Usa o logger para registrar o processo

**extractor.py**

Contém a classe AgendaExtractor:

- Extrai os links dos meses e dias da agenda tributária
- Lê as tabelas de eventos
- Retorna os dados brutos organizados por mês e dia

**transformer.py**

Contém a classe AgendaTransformer:

- Limpa e normaliza os registros
- Classifica os tipos de eventos (DARF, GPS, declarações, etc.)
- Retorna os dados transformados prontos para validação

**loader.py**

Contém a classe AgendaLoader:

- Valida os dados com JSON Schema
- Salva o JSON final na pasta data/transformed
- Registra sucesso ou erro no logger

**logger_config.py**

Configura o logger com:

- Rotação diária (when="midnight")
- Backup dos últimos 30 arquivos
- Mensagem de verificação para garantir rotação

## 📊 Esquema dos Dados Transformados

O arquivo JSON final (`data/transformed/agenda_tributaria_2025.json`) segue a estrutura abaixo:

```json
{
  "fonte": "URL da fonte dos dados",
  "extraido_em": "Data da extração (YYYY-MM-DD)",
  "ano": 2025,
  "meses": {
    "janeiro": {
      "url": "URL da agenda do mês",
      "dias": {
        "dia-DD-MM-YYYY": {
          "url": "URL da agenda do dia",
          "eventos": [
            [
              {
                "tipo": "darf | gps | documento | declaracao_pj | declaracao_pf",
                "codigo_darf": "Integer | null",
                "codigo_gps": "Integer | null",
                "documento": "String | null",
                "descricao": "String",
                "periodo_fato_gerador": "String | null"
              }
            ]
          ]
        }
      }
    }
  }
}
```

### Descrição dos Campos

- `tipo`: Categoriza o evento. Pode ser:
  - `darf`: Pagamento via Documento de Arrecadação de Receitas Federais.
  - `gps`: Pagamento via Guia da Previdência Social.
  - `documento`: Entrega de documentos (e.g., DAS, Simples Doméstico).
  - `declaracao_pj`: Entrega de declarações por Pessoas Jurídicas.
  - `declaracao_pf`: Entrega de declarações por Pessoas Físicas.
- `codigo_darf` / `codigo_gps`: Código numérico do tributo, quando aplicável.
- `documento`: Nome do documento de arrecadação (e.g., DAS, DAE).
- `descricao`: Descrição do tributo ou obrigação.
- `periodo_fato_gerador`: Período de apuração do evento.

## Configuração de Logger com Rotação Diária

O projeto utiliza um sistema de logging configurado com `TimedRotatingFileHandler` para registrar eventos importantes durante a execução do scraper. A configuração está localizada no arquivo `logger_config.py`.

### 🔧 Detalhes da configuração:

```python
handler = TimedRotatingFileHandler(
    filename=os.path.join(pasta_logs, "agenda_tributaria_scrapper.log"),
    when="midnight",       # Rotaciona o log à meia-noite
    interval=1,            # A cada 1 dia
    backupCount=30,        # Mantém os últimos 30 arquivos de log
    encoding="utf-8"       # Suporte a caracteres especiais
)
```

### 📌 Comportamento esperado:

- Um novo arquivo de log é criado **diariamente à meia-noite.**
- O arquivo atual é renomeado com a data, por exemplo: **agenda_tributaria_scrapper.log.2025-08-28**
- Um novo arquivo vazio com o nome original (agenda_tributaria_scrapper.log) é iniciado.
- Os **30 arquivos mais recentes** são mantidos automaticamente. Os mais antigos são excluídos.

### ✅ Boas práticas aplicadas:

- Evita múltiplos handlers com cache interno (\_logger) para reutilização do logger.
- Cria a pasta de logs automaticamente, se não existir.
- Adiciona uma mensagem de verificação logo após a configuração para garantir que a rotação seja detectada:

```python
logger = LoggerConfig.configurar_logger()
logger.info("Verificando rotação de log...")
```

## ⚙️ Como Executar

Siga os passos abaixo para configurar e executar o projeto.

### 1. Pré-requisitos

- Python 3.8 ou superior

### 2. Instalação

Clone o repositório e instale as dependências.

```bash
# Crie o ambiente virtual
python3 -m venv .venv

# Ative o ambiente virtual (Linux/macOS)
source .venv/bin/activate

# Atualize o pip
pip install --upgrade pip

# Instale as dependências
pip install -r requirements.txt
```

### 3. Executando a Pipeline

Para executar o pipeline completo, utilize o seguinte comando:

```bash
python src/main.py
```

```python
pip install -r requirements.txt
```

## Comentarios relevantes

Por que sugeri a outra estrutura?
A estrutura que sugeri com `main.py`, `extractor.py`, `transformer.py` e `loader.py` é um padrão de projeto muito comum em engenharia de dados. A ideia é aplicar o Princípio da Responsabilidade Única, onde cada arquivo tem uma única e bem definida função:

- `extractor.py`: Seria responsável apenas por extrair os dados brutos. No seu caso, os métodos obter_links_meses, obter_links_datas e parte do extrair_tabelas estariam aqui.
- `transformer.py`: Cuidaria apenas da limpeza e transformação dos dados. Os seus métodos limpar_registros e classificar_tipo se encaixariam perfeitamente aqui.
- `loader.py`: Teria a única função de carregar/salvar os dados transformados. O seu método salvar_json viria para cá.
- `main.py`: Atuaria como um "orquestrador", chamando as funções dos outros módulos na ordem correta (extrair -> transformar -> carregar).

**Vantagens desse padrão:**

Manutenção: Se o site da Receita Federal mudar o layout, você saberia que precisa mexer apenas no extractor.py.
Testes: Fica muito mais fácil testar cada etapa do pipeline de forma isolada.
Reutilização: Você poderia, por exemplo, reutilizar o loader.py para salvar dados de outro projeto em JSON.
Clareza: Fica explícito para qualquer pessoa que olhe o projeto qual é o fluxo de dados.
