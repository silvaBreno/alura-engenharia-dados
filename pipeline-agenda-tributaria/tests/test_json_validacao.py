import json
import pytest
from pathlib import Path
from jsonschema import validate, ValidationError

# Caminhos para os arquivos
schema_path = Path(__file__).parent.parent / "schemas" / "agenda_schema.json"
json_path = Path(__file__).parent.parent / "data" / "transformed" / "teste17_agenda_tributaria_2025.json"
print(f"Schema path: {schema_path}")
print(f"JSON path: {json_path}")

def load_json_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def test_json_structure_is_valid():    
    schema = load_json_file(schema_path)
    assert json_path.exists(), f"Arquivo JSON não encontrado em: {json_path}"
    data = load_json_file(json_path)

    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        pytest.fail(f"JSON inválido: {e.message}")

