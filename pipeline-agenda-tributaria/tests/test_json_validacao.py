import json
from pathlib import Path

import pytest
from jsonschema import ValidationError, validate

schema_path = Path(__file__).parent.parent / "schemas" / "agenda_schema.json"


# Testa validação do payload mínimo contra o schema oficial
def test_json_structure_is_valid(tmp_path):
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    payload = {
        "fonte": "https://exemplo.com",
        "extraido_em": "2025-01-01",
        "ano": 2025,
        "meses": [
            {
                "mes": 1,
                "nome": "janeiro",
                "url": "https://exemplo.com/janeiro",
                "dias": [
                    {
                        "data": "2025-01-10",
                        "url": "https://exemplo.com/dia-10",
                        "publicado_em": "01/01/2025",
                        "atualizado_em": "02/01/2025",
                        "eventos": [
                            {
                                "tipo": "darf",
                                "codigo_receita": "1234",
                                "descricao": "Pagamento de tributo",
                                "periodo_fato_gerador": "01/2025",
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
        ],
    }

    destino = tmp_path / "agenda.json"
    destino.write_text(json.dumps(payload), encoding="utf-8")

    try:
        validate(instance=payload, schema=schema)
    except ValidationError as e:
        pytest.fail(f"JSON inválido: {e.message}")
