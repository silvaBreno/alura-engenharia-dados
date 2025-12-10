## Pipeline de Dados da Agenda Tributária

Projeto para extrair a Agenda Tributária da Receita Federal, normalizar os eventos e gravar um JSON validado por schema. Há uma etapa opcional de carga em Oracle já pronta.

### Como o código está organizado
```
scripts/
  main.py                -> orquestra ETL
  extractor.py           -> navega meses/dias e lê tabelas (layout antigo e novo)
  transformer.py         -> normaliza campos, classifica tipo e ordena meses/dias
  loader.py              -> valida contra o schema e grava JSON (gravação atômica)
  oracle_loader.py       -> achata o JSON e insere via pandas.to_sql (Oracle)
  spark_oracle_loader.py -> achata o JSON e insere via Spark JDBC (Oracle)
  logger_config.py       -> logger com rotação diária
data/
  raw/                 -> opcional para dumps brutos
  transformed/         -> JSONs finais
schemas/
  agenda_schema.json   -> contrato do JSON final
tests/                 -> pytest com mocks offline
logs/                  -> gerados pelo logger
```

### Componentes em poucas linhas
- `AgendaExtractor`: encontra links de meses/dias (filtra ano e ignora 31/12), lê tabelas em dois layouts e coleta publicado/atualizado.
- `AgendaTransformer`: limpa texto/HTML, classifica tipo (darf/gps/declaracao/documento/outros), descarta registros vazios e reorganiza meses/dias em ordem com datas ISO.
- `AgendaLoader`: valida com `schemas/agenda_schema.json`, acrescenta `schema_version`, registra métricas de contagem e grava em `data/transformed/agenda_tributaria_<ano>_<timestamp>.json`.
- `OracleLoader` (pandas, opcional): em `oracle_loader.py`, achata o JSON, valida colunas/obrigatórios e insere em Oracle via `pandas.to_sql` (usa chunks).
- `SparkOracleLoader` (opcional): em `spark_oracle_loader.py`, faz o mesmo flatten/validação e insere via Spark JDBC com paralelismo.
- Logging: `logger_config.py` cria `logs/agenda_tributaria_scrapper.log` com rotação diária e retenção de 30 arquivos.

### Formato esperado do JSON
```json
{
  "fonte": "https://www.gov.br/receitafederal/pt-br/assuntos/agenda-tributaria/2025",
  "extraido_em": "2025-01-10",
  "ano": 2025,
  "schema_version": "1.0",
  "meses": [
    {
      "mes": 1,
      "nome": "janeiro",
      "url": ".../janeiro",
      "dias": [
        {
          "data": "2025-01-10",
      "url": ".../dia-10-01-2025",
      "publicado_em": "10/01/2025",
      "atualizado_em": "10/01/2025",
      "eventos": [
        {
          "nr_idfr_cmpo": null,
          "tipo": "darf",
          "codigo_receita": "1234",
          "descricao": "Pagamento de tributo",
          "periodo_fato_gerador": "12/2024",
          "grupo_tributo": "IRRF",
              "documento_arrecadacao": "DARF",
              "documento_arrecadacao_url": "...",
              "categoria_declaracao": "Cat",
              "origem_escrituracao": "Origem",
              "fundamentacao_legal": "Lei 123",
              "fundamentacao_legal_url": "..."
            }
          ]
        }
      ]
    }
  ]
}
```

### Como rodar
Requisitos: Python 3.8+ e pacotes de `requirements.txt`.
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
Execute a pipeline (configure ano/meses em `scripts/main.py`):
```bash
python -m scripts.main
```
Saídas: JSON validado em `data/transformed/agenda_tributaria_<ano>_<timestamp>.json` e log em `logs/agenda_tributaria_scrapper.log`.

### Testes
Pytest com mocks, sem depender de internet:
```bash
pytest
```
Cobertura: extractor (links e layout novo), transformer (layouts antigo/novo, ordenação, filtros), loader (gravação + schema), validação de schema e rotação de log.

### Carga em Oracle (opcional)
#### Via pandas (to_sql)
```python
from scripts.oracle_loader import OracleLoader

loader = OracleLoader(
    user="USR", password="PWD", host="HOST", port="1521",
    service_name="SERVICE", table_name="TABELA_COMPROMISSO", chunk_size=5000
)
loader.inserir_json("data/transformed/agenda_tributaria_2025_20251209_104910_com_id.json")
```
O loader pandas (`oracle_loader.py`) achata o JSON, valida obrigatórios (incluindo `NR_IDFR_CMPO` não nulo/numérico) e escreve em lotes via `pandas.to_sql`.

#### Via Spark (JDBC)
```python
from scripts.spark_oracle_loader import SparkOracleLoader

loader = SparkOracleLoader(
    user="USR", password="PWD", host="HOST", port="1521",
    service_name="SERVICE", table_name="TABELA_COMPROMISSO",
    jar_path="/caminho/ojdbc8.jar", batchsize=5000, num_partitions=4
)
loader.inserir_json("data/transformed/agenda_tributaria_2025_20251209_104910_com_id.json")
```
O loader Spark faz o flatten/validação equivalentes e grava via JDBC com paralelismo.
