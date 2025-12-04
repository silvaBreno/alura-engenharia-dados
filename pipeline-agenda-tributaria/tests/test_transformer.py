import pytest
from scripts.transformer import AgendaTransformer

def test_limpar_registros():
    dados_exemplo = [{
        "Código DARF": "1234",
        "Descrição": "<p>Pagamento de tributo</p>",
        "Período do Fato Gerador": "01/2025"
    }]
    transformer = AgendaTransformer(ano=2025, dados_agenda={})
    registros_limpos = transformer.limpar_registros(dados_exemplo)
    assert isinstance(registros_limpos, list)
    registro = registros_limpos[0]
    assert registro["tipo"] == "darf"
    assert registro["descricao"] == "Pagamento de tributo"
    assert registro["codigo_receita"] == "1234"
    assert registro["grupo_tributo"] is None
    assert "codigo_darf" not in registro
    assert "codigo_gps" not in registro
    assert "documento" not in registro
