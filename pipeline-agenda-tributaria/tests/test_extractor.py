import pytest
from scripts.extractor import AgendaExtractor


class ResponseMock:
    def __init__(self, url: str, html: str):
        self.url = url
        self.content = html.encode("utf-8")
        self.status_code = 200

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception("HTTP error")


# Testa a coleta de links de meses sem depender da internet
def test_obter_links_meses_offline(monkeypatch):
    base_url = "https://www.gov.br/receitafederal/pt-br/assuntos/agenda-tributaria/2025"
    html = """
    <html><body>
    <a href="https://www.gov.br/receitafederal/pt-br/assuntos/agenda-tributaria/2025/janeiro">Janeiro</a>
    <a href="https://www.gov.br/receitafederal/pt-br/assuntos/agenda-tributaria/2025/novembro">Novembro</a>
    <a href="https://www.gov.br/receitafederal/pt-br/assuntos/agenda-tributaria/2024/janeiro">Outro Ano</a>
    </body></html>
    """

    def fake_get(url, *_, **__):
        return ResponseMock(url, html)

    monkeypatch.setattr("requests.get", fake_get)

    extractor = AgendaExtractor(ano=2025)
    links = extractor.obter_links_meses()

    assert links == [
        f"{base_url}/janeiro",
        f"{base_url}/novembro",
    ]


# Testa parsing do layout novo de tabela, incluindo datas meta
def test_extrair_tabelas_mockado(monkeypatch):
    evento_url = "https://www.gov.br/receitafederal/pt-br/assuntos/agenda-tributaria/2025/novembro/dia-10-11-2025"
    html_evento = """
    <html><body>
      <span>Publicado em</span><span class="value">01/11/2025</span>
      <span>Atualizado em</span><span class="value">02/11/2025</span>
      <table>
        <thead>
          <tr>
            <th><strong>Código de Receita</strong></th>
            <th><strong>Grupo de Tributo</strong></th>
            <th><strong>Descrição</strong></th>
            <th><strong>Período de apuração</strong></th>
          </tr>
        </thead>
        <tbody>
          <tr><td>cabecalho</td></tr>  <!-- linha do layout que será ignorada -->
          <tr><td>cabecalho2</td></tr> <!-- linha do layout que será ignorada -->
          <tr>
            <td>1234</td>
            <td>Grupo X</td>
            <td>Descricao evento</td>
            <td>11/2025</td>
          </tr>
          <tr>
            <td><a href="https://exemplo.com/darf">DARF</a></td>
            <td>Categoria / Origem</td>
            <td><a href="https://exemplo.com/lei">Lei ABC</a></td>
          </tr>
        </tbody>
      </table>
    </body></html>
    """

    def fake_get(url, *_, **__):
        return ResponseMock(url, html_evento)

    monkeypatch.setattr("requests.get", fake_get)

    extractor = AgendaExtractor(ano=2025)
    resultado = extractor.extrair_tabelas(evento_url)

    assert isinstance(resultado, dict)
    assert resultado["publicado_em"] == "01/11/2025"
    assert resultado["atualizado_em"] == "02/11/2025"

    eventos = resultado["eventos"]
    assert len(eventos) == 1
    evento = eventos[0]
    assert evento["codigo de receita"] == "1234"
    assert evento["grupo de tributo"] == "Grupo X"
    assert evento["descricao"] == "Descricao evento"
    assert evento["documento arrecadacao"] == "DARF"
    assert evento["documento arrecadacao url"] == "https://exemplo.com/darf"


# Testa filtragem de datas: ignora 31/12 e anos diferentes
def test_obter_links_datas_filtra_ano_e_ignora_3112(monkeypatch):
    base_mes = "https://www.gov.br/receitafederal/pt-br/assuntos/agenda-tributaria/2025/novembro"
    html = f"""
    <html><body>
      <a href="{base_mes}/dia-10-11-2025">Dia válido</a>
      <a href="{base_mes}/dia-31-12-2025">Dia especial</a>
      <a href="https://www.gov.br/receitafederal/pt-br/assuntos/agenda-tributaria/2024/janeiro/dia-01-01-2024">Outro ano</a>
      <a href="{base_mes}/dia-12-11-2025?param=1">Dia com query</a>
    </body></html>
    """

    def fake_get(url, *_, **__):
        return ResponseMock(url, html)

    monkeypatch.setattr("requests.get", fake_get)

    extractor = AgendaExtractor(ano=2025)
    links = extractor.obter_links_datas(base_mes)

    assert links == [
        f"{base_mes}/dia-10-11-2025",
        f"{base_mes}/dia-12-11-2025?param=1",
    ]
