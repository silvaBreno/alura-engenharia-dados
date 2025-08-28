import json
import pytest
from jsonschema import validate, ValidationError

# Caminhos para os arquivos
schema_path = "../schemas/agenda_schema.json"
json_path = "../data/transformed/teste15_agenda_tributaria_2025.json"

def load_json_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def test_json_structure_is_valid():
    schema = load_json_file(schema_path)
    data = load_json_file(json_path)

    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        pytest.fail(f"JSON inválido: {e.message}")
