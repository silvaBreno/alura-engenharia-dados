import json
from pathlib import Path

from jsonschema import validate

from scripts.loader import AgendaLoader


# Testa salvar JSON com evento completo e validar contra o schema
def test_salvar_json(tmp_path):
    dados_mock = [
        {
            "mes": 1,
            "nome": "janeiro",
            "url": "https://exemplo.com/janeiro",
            "dias": [
                {
                    "data": "2025-01-01",
                    "url": "https://exemplo.com/dia-01",
                    "publicado_em": "01/01/2025 10h00",
                    "atualizado_em": "02/01/2025 09h00",
                    "eventos": [
                        {
                            "tipo": "darf",
                            "codigo_receita": "1234",
                            "descricao": "Pagamento de tributo",
                            "periodo_fato_gerador": "12/2024",
                            "grupo_tributo": None,
                            "documento_arrecadacao": "DARF",
                            "documento_arrecadacao_url": "https://exemplo.com/darf",
                            "categoria_declaracao": "Cat",
                            "origem_escrituracao": "Orig",
                            "fundamentacao_legal": "Lei 123",
                            "fundamentacao_legal_url": "https://exemplo.com/lei",
                        }
                    ],
                }
            ],
        }
    ]

    caminho = tmp_path / "agenda_test.json"
    schema_path = Path(__file__).parent.parent / "schemas" / "agenda_schema.json"

    loader = AgendaLoader(
        ano=2025, dados_agenda=dados_mock, base_url="https://exemplo.com", schema_version="test"
    )
    destino = loader.salvar_json(caminho_arquivo=str(caminho), caminho_schema=schema_path)

    assert destino.exists()

    conteudo = json.loads(destino.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validate(instance=conteudo, schema=schema)
