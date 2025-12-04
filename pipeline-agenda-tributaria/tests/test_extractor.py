import pytest
from scripts.extractor import AgendaExtractor

def test_obter_links_meses():
    extractor = AgendaExtractor(ano=2025)
    links = extractor.obter_links_meses()
    assert isinstance(links, list)
    assert all(link.startswith(extractor.base_url) for link in links)

def test_extrair_tabelas_com_url_valida():
    extractor = AgendaExtractor(ano=2025)
    # URL de teste real pode ser substituída por uma mockada
    url = "https://www.gov.br/receitafederal/pt-br/assuntos/agenda-tributaria/2025/janeiro/dia-10-01-2025"
    tabelas = extractor.extrair_tabelas(url)
    assert isinstance(tabelas, dict)
    assert "eventos" in tabelas
    assert "publicado_em" in tabelas
    assert "atualizado_em" in tabelas
