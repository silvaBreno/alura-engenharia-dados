from pathlib import Path
import pytest
from scripts.loader import AgendaLoader

def test_salvar_json(tmp_path):
    dados_mock = {
        "janeiro": {
            "url": "https://exemplo.com/janeiro",
            "dias": {
                "dia-01": {
                    "url": "https://exemplo.com/dia-01",
                    "eventos": []
                }
            }
        }
    }
    caminho = tmp_path / "agenda_test.json"
    schema_path = Path(__file__).parent.parent / "schemas" / "agenda_schema.json"

    loader = AgendaLoader(ano=2025, dados_agenda=dados_mock, base_url="https://exemplo.com")
    loader.salvar_json(caminho_arquivo=str(caminho), caminho_schema=schema_path)

    assert caminho.exists()