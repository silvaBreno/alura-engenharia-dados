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
    assert registros_limpos[0]["tipo"] == "darf"
    assert registros_limpos[0]["descricao"] == "Pagamento de tributo"
