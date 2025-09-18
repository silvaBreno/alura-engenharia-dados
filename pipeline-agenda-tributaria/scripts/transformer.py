import unicodedata
from bs4 import BeautifulSoup
from .logger_config import LoggerConfig

logger = LoggerConfig.configurar_logger()

class AgendaTransformer:
    def __init__(self, ano, dados_agenda):
        self.ano = ano
        self.dados_agenda = dados_agenda

    def transformar(self):
        logger.info("=" * 80)
        logger.info(f"🔄 Iniciando transformação dos dados da Agenda Tributária para o ano {self.ano}")
        logger.info("=" * 80)

        for mes, info_mes in self.dados_agenda.items():
            logger.info(f"📅 Transformando dados do mês: {mes}")
            for dia, info_dia in info_mes["dias"].items():
                logger.info(f"  📆 Dia: {dia} - {len(info_dia['eventos'])} eventos encontrados")
                eventos = info_dia["eventos"]
                eventos_limpos = self.limpar_registros(eventos)
                self.dados_agenda[mes]["dias"][dia]["eventos"] = eventos_limpos
                logger.info(f"  ✅ {len(eventos_limpos)} eventos limpos para o dia {dia}")
        
        logger.info(f"✅ Transformação concluída para o ano {self.ano}")
        return self.dados_agenda

    def limpar_registros(self, registros):
        registros_limpos = []
        for item in registros:
            try:
                item_normalizado = {
                    self._normalizar_texto(k): v for k, v in item.items()
                }
                tipo = self.classificar_tipo(item_normalizado)

                if tipo in ["darf", "gps", "documento"]:
                    periodo = item_normalizado.get("periodo do fato gerador")
                elif tipo in ["declaracao_pf", "declaracao_pj"]:
                    periodo = item_normalizado.get("periodo de apuracao")
                else:
                    periodo = item_normalizado.get("periodo do fato gerador") or item_normalizado.get("periodo de apuracao")

                descricao_html = ""
                for chave in item_normalizado:
                    if "descricao" in chave or "declaracoes" in chave:
                        descricao_html = item_normalizado[chave]
                        break
                descricao = BeautifulSoup(descricao_html or "", "html.parser").text.strip()

                registro = {
                    "tipo": tipo,
                    "codigo_darf": str(item_normalizado.get("codigo darf")) if item_normalizado.get("codigo darf") is not None else None,
                    "codigo_gps": str(item_normalizado.get("codigo gps")) if item_normalizado.get("codigo gps") is not None else None,
                    "documento": str(item_normalizado.get("documento")) if item_normalizado.get("documento") is not None else None,
                    "descricao": descricao,
                    "periodo_fato_gerador": str(periodo) if periodo is not None else None
                }
                registros_limpos.append(registro)
            except Exception:
                logger.exception("❌ Erro ao limpar registro")
                continue
        return registros_limpos

    def classificar_tipo(self, item):
        chaves = [self._normalizar_texto(k) for k in item.keys()]
        if any("codigo darf" in k for k in chaves):
            return "darf"
        elif any("codigo gps" in k for k in chaves):
            return "gps"
        elif any("pessoas juridicas" in k and ("declaracoes" in k or "documentos" in k or "demonstrativos" in k) for k in chaves):
            return "declaracao_pj"
        elif any("pessoas fisicas" in k and ("declaracoes" in k or "documentos" in k or "demonstrativos" in k) for k in chaves):
            return "declaracao_pf"
        elif any("imovel rural" in k and ("declaracoes" in k or "documentos" in k or "demonstrativos" in k) for k in chaves):
            return "declaracao_imovel_rural"
        elif any("declaracoes" in k or "demonstrativos" in k for k in chaves):
            return "declaracao"
        elif any("documento" in k for k in chaves):
            return "documento"
        return "outros"

    def _normalizar_texto(self, texto):
        texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
        return texto.lower().strip()
