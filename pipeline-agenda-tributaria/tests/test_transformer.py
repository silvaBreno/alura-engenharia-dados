# Testa limpeza de um registro no layout antigo (DARF/GPS)
from scripts.transformer import AgendaTransformer


# Testa limpeza de um registro no layout antigo (DARF básico)
def test_limpar_registros_layout_antigo():
    dados_exemplo = [
        {
            "Código DARF": "1234",
            "Descrição": "<p>Pagamento de tributo</p>",
            "Período do Fato Gerador": "01/2025",
        }
    ]
    transformer = AgendaTransformer(ano=2025, dados_agenda={})
    registros_limpos = transformer.limpar_registros(dados_exemplo)
    registro = registros_limpos[0]

    assert registro["tipo"] == "darf"
    assert registro["descricao"] == "Pagamento de tributo"
    assert registro["codigo_receita"] == "1234"
    assert registro["grupo_tributo"] is None
    assert "codigo_darf" not in registro
    assert "codigo_gps" not in registro
    assert "documento" not in registro


# Testa limpeza de um registro no layout novo com documento, categorias e URLs
def test_limpar_registros_layout_novo():
    dados_exemplo = [
        {
            "codigo de receita": "5678",
            "grupo de tributo": "Grupo X",
            "descricao": "Descricao evento",
            "periodo de apuracao": "02/2025",
            "documento arrecadacao": "DARF",
            "documento arrecadacao url": "https://exemplo.com/darf",
            "categoria da declaracao / origem escrituracao": "Cat / Origem",
            "fundamentacao legal": "Lei XYZ",
            "fundamentacao legal url": "https://exemplo.com/lei",
        }
    ]
    transformer = AgendaTransformer(ano=2025, dados_agenda={})
    registros_limpos = transformer.limpar_registros(dados_exemplo)
    registro = registros_limpos[0]

    assert registro["tipo"] == "darf"
    assert registro["codigo_receita"] == "5678"
    assert registro["grupo_tributo"] == "Grupo X"
    assert registro["documento_arrecadacao_url"] == "https://exemplo.com/darf"
    assert registro["categoria_declaracao"] == "Cat"
    assert registro["origem_escrituracao"] == "Origem"


# Testa reorganização de meses/dias na ordem correta e datas em formato ISO
def test_reorganizar_meses_ordena_e_formata_data():
    dados = {
        "fevereiro": {
            "url": "https://exemplo.com/fevereiro",
            "dias": {
                "dia-02-02-2025": {"url": "u2", "publicado_em": "", "atualizado_em": "", "eventos": []},
                "dia-01-02-2025": {"url": "u1", "publicado_em": "", "atualizado_em": "", "eventos": []},
            },
        },
        "janeiro": {
            "url": "https://exemplo.com/janeiro",
            "dias": {
                "dia-10-01-2025": {"url": "u3", "publicado_em": "", "atualizado_em": "", "eventos": []},
            },
        },
    }
    transformer = AgendaTransformer(ano=2025, dados_agenda=dados)
    reorganizado = transformer._reorganizar_meses()

    assert reorganizado[0]["nome"] == "janeiro"
    assert reorganizado[1]["nome"] == "fevereiro"

    dias_fev = reorganizado[1]["dias"]
    assert dias_fev[0]["data"] == "2025-02-01"
    assert dias_fev[1]["data"] == "2025-02-02"


# Testa remoção de registros "outros" sem informação útil
def test_registro_vazio_outros_e_removido():
    transformer = AgendaTransformer(ano=2025, dados_agenda={})
    registros = [
        {
            "tipo": "outros",
            "codigo_receita": "",
            "descricao": "",
            "periodo_fato_gerador": "",
            "grupo_tributo": "",
            "documento_arrecadacao": "",
            "documento_arrecadacao_url": "",
            "categoria_declaracao": "",
            "origem_escrituracao": "",
            "fundamentacao_legal": "",
            "fundamentacao_legal_url": "",
        }
    ]
    filtrados = transformer.limpar_registros(registros)
    assert filtrados == []
