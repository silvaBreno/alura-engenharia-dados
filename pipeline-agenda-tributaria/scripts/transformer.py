import unicodedata
import re
from bs4 import BeautifulSoup
from .logger_config import LoggerConfig

logger = LoggerConfig.configurar_logger()

class AgendaTransformer:
    def __init__(self, ano, dados_agenda):
        self.ano = ano
        self.dados_agenda = dados_agenda
        self._ordem_meses = [
            'janeiro', 'fevereiro', 'marco', 'abril', 'maio', 'junho',
            'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'
        ]

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

        self.dados_agenda = self._reorganizar_meses()
        logger.info(f"✅ Transformação concluída para o ano {self.ano}")
        return self.dados_agenda

    # terceiro teste -> considerando html novo de novembro:
    
    def limpar_registros(self, registros):
        registros_limpos = []
        for item in registros:
            try:
                item_normalizado = {self._normalizar_texto(k): v for k, v in item.items()}
                if "codigo de receita" in item_normalizado:
                    logger.info("📐 Layout detectado: NOVO")
                    registros_limpos.append(self._limpar_registro_novo(item_normalizado))
                else:
                    logger.info("📐 Layout detectado: ANTIGO")
                    registros_limpos.append(self._limpar_registro_antigo(item_normalizado))
            except Exception:
                logger.exception("❌ Erro ao limpar registro")
                continue

        # Mantém apenas DARF e GPS para curadoria inicial
        registros_filtrados = [r for r in registros_limpos if r.get("tipo") in {"darf", "gps"}]
        return registros_filtrados

    def _limpar_registro_antigo(self, item):
        tipo = self.classificar_tipo(item)
        periodo = self._limpar_texto(item.get("periodo do fato gerador") or item.get("periodo de apuracao"))
        descricao = self._extrair_descricao(item)

        codigo_darf = self._limpar_texto(item.get("codigo darf"))
        codigo_gps = self._limpar_texto(item.get("codigo gps"))
        documento = self._limpar_texto(item.get("documento"))
        codigo_receita = self._resolver_codigo_receita(None, codigo_darf, codigo_gps)

        return self._formar_registro(
            tipo=tipo,
            codigo_receita=codigo_receita,
            descricao=descricao,
            periodo=periodo,
            grupo_tributo=None,
            documento_arrecadacao=documento,
            categoria_declaracao=None,
            fundamentacao_legal=None,
            origem_escrituracao=None,
            fundamentacao_legal_url=None,
        )

    def _limpar_registro_novo(self, item):
        doc_arrec = self._limpar_texto(item.get("documento arrecadacao"))
        tipo = self._classificar_por_documento(doc_arrec)
        categoria_declaracao = self._limpar_texto(item.get("categoria da declaracao / origem escrituracao"))
        cat, origem = self._split_categoria_declaracao(categoria_declaracao)

        return self._formar_registro(
            tipo=tipo,
            codigo_receita=self._limpar_texto(item.get("codigo de receita")),
            descricao=self._limpar_texto(item.get("descricao")),
            periodo=self._limpar_texto(item.get("periodo de apuracao")),
            grupo_tributo=self._limpar_texto(item.get("grupo de tributo")),
            documento_arrecadacao=doc_arrec,
            categoria_declaracao=cat,
            origem_escrituracao=origem,
            fundamentacao_legal=self._limpar_texto(item.get("fundamentacao legal")),
            fundamentacao_legal_url=self._limpar_texto(item.get("fundamentacao legal url")),
        )


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
        if texto is None:
            return ""
        texto = str(texto)
        texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
        return texto.lower().strip()

    def _classificar_por_documento(self, documento):
        doc_norm = self._normalizar_texto(documento)
        if "darf" in doc_norm:
            return "darf"
        if "gps" in doc_norm:
            return "gps"
        return "outros"

    def _limpar_texto(self, valor):
        if valor is None:
            return None
        return str(valor).strip()

    def _resolver_codigo_receita(self, codigo_receita, codigo_darf, codigo_gps):
        return (
            self._limpar_texto(codigo_receita)
            or self._limpar_texto(codigo_darf)
            or self._limpar_texto(codigo_gps)
        )

    def _extrair_descricao(self, item):
        descricao_html = ""
        for chave in item:
            if "descricao" in chave or "declaracoes" in chave:
                descricao_html = item[chave]
                break
        return self._limpar_texto(BeautifulSoup(descricao_html or "", "html.parser").text)

    def _formar_registro(
        self,
        *,
        tipo,
        codigo_receita,
        descricao,
        periodo,
        grupo_tributo,
        documento_arrecadacao,
        categoria_declaracao,
        origem_escrituracao,
        fundamentacao_legal,
        fundamentacao_legal_url,
    ):
        codigo_receita_resolvido = self._resolver_codigo_receita(codigo_receita, None, None)
        return {
            "tipo": tipo,
            "codigo_receita": codigo_receita_resolvido,
            "descricao": descricao or "",
            "periodo_fato_gerador": periodo,
            "grupo_tributo": grupo_tributo,
            "documento_arrecadacao": documento_arrecadacao,
            "categoria_declaracao": categoria_declaracao or "--",
            "origem_escrituracao": origem_escrituracao or "--",
            "fundamentacao_legal": fundamentacao_legal,
            "fundamentacao_legal_url": fundamentacao_legal_url,
        }

    def _split_categoria_declaracao(self, texto):
        if not texto:
            return None, None
        partes = [p.strip() for p in texto.split("/", 1)]
        if len(partes) == 1:
            return partes[0] or None, None
        return partes[0] or None, partes[1] or None

    def _reorganizar_meses(self):
        meses_lista = []
        for idx, mes_nome in enumerate(self._ordem_meses, start=1):
            if mes_nome not in self.dados_agenda:
                continue
            info_mes = self.dados_agenda[mes_nome]
            dias_lista = []
            for dia_nome, info_dia in info_mes.get("dias", {}).items():
                data_iso = self._converter_data(dia_nome)
                dias_lista.append({
                    "data": data_iso or dia_nome,
                    "url": info_dia.get("url"),
                    "publicado_em": info_dia.get("publicado_em", ""),
                    "atualizado_em": info_dia.get("atualizado_em", ""),
                    "eventos": info_dia.get("eventos", [])
                })
            dias_lista.sort(key=lambda d: d["data"])
            meses_lista.append({
                "mes": idx,
                "nome": mes_nome,
                "url": info_mes.get("url"),
                "dias": dias_lista
            })
        return meses_lista

    def _converter_data(self, nome_dia):
        match = re.search(r"(\d{1,2})-(\d{1,2})-(\d{4})", nome_dia)
        if match:
            dd, mm, yyyy = match.groups()
            return f"{yyyy}-{int(mm):02d}-{int(dd):02d}"
        return None


# def limpar_registros(self, registros):
    #     registros_limpos = []
    #     for item in registros:
    #         try:
    #             item_normalizado = {
    #                 self._normalizar_texto(k): v for k, v in item.items()
    #             }
    #             tipo = self.classificar_tipo(item_normalizado)

    #             if tipo in ["darf", "gps", "documento"]:
    #                 periodo = item_normalizado.get("periodo do fato gerador")
    #             elif tipo in ["declaracao_pf", "declaracao_pj"]:
    #                 periodo = item_normalizado.get("periodo de apuracao")
    #             else:
    #                 periodo = item_normalizado.get("periodo do fato gerador") or item_normalizado.get("periodo de apuracao")

    #             descricao_html = ""
    #             for chave in item_normalizado:
    #                 if "descricao" in chave or "declaracoes" in chave:
    #                     descricao_html = item_normalizado[chave]
    #                     break
    #             descricao = BeautifulSoup(descricao_html or "", "html.parser").text.strip()

    #             registro = {
    #                 "tipo": tipo,
    #                 "codigo_darf": str(item_normalizado.get("codigo darf")) if item_normalizado.get("codigo darf") is not None else None,
    #                 "codigo_gps": str(item_normalizado.get("codigo gps")) if item_normalizado.get("codigo gps") is not None else None,
    #                 "documento": str(item_normalizado.get("documento")) if item_normalizado.get("documento") is not None else None,
    #                 "descricao": descricao,
    #                 "periodo_fato_gerador": str(periodo) if periodo is not None else None
    #             }
    #             registros_limpos.append(registro)
    #         except Exception:
    #             logger.exception("❌ Erro ao limpar registro")
    #             continue
    #     return registros_limpos

    #   teste 2 -- estrutura unificada:
    # def limpar_registros(self, registros):
    #     registros_limpos = []
    #     for item in registros:
    #         try:
    #             item_normalizado = {
    #                 self._normalizar_texto(k): self._normalizar_texto(v) for k, v in item.items()
    #             }

    #             # Detecta tipo pelo documento arrecadação ou chaves antigas
    #             doc_arrec = item_normalizado.get("documento arrecadacao") or item_normalizado.get("documento", "")
    #             tipo = "darf" if "darf" in doc_arrec.lower() else "gps" if "gps" in doc_arrec.lower() else "outros"

    #             # Preenche campos unificados
    #             registro = {
    #                 "tipo": tipo,
    #                 "codigo_receita": item_normalizado.get("codigo de receita") or item_normalizado.get("codigo darf") or item_normalizado.get("codigo gps"),
    #                 "grupo_tributo": item_normalizado.get("grupo de tributo"),
    #                 "descricao": item_normalizado.get("descricao") or self._extrair_descricao(item_normalizado),
    #                 "periodo_fato_gerador": item_normalizado.get("periodo de apuracao") or item_normalizado.get("periodo do fato gerador"),
    #                 "documento_arrecadacao": doc_arrec,
    #                 "categoria_declaracao": item_normalizado.get("categoria da declaracao / origem escrituracao"),
    #                 "fundamentacao_legal": item_normalizado.get("fundamentacao legal")
    #             }

    #             registros_limpos.append(registro)
    #         except Exception:
    #             logger.exception("❌ Erro ao limpar registro")
    #             continue
    #     return registros_limpos

    # def _extrair_descricao(self, item_normalizado):
    #     # Fallback para descrição antiga (HTML)
    #     for chave in item_normalizado:
    #         if "descricao" in chave or "declaracoes" in chave:
    #             return BeautifulSoup(item_normalizado[chave] or "", "html.parser").text.strip()
    #     return ""

    #   segundo teste
    # def limpar_registros(self, registros):
    #     registros_limpos = []
    #     for item in registros:
    #         try:
    #             item_normalizado = {
    #                 self._normalizar_texto(k): self._normalizar_texto(v) for k, v in item.items()
    #             }

    #             if "codigo de receita" in item_normalizado:
    #                 registro = self._limpar_registro_novo(item_normalizado)
    #             else:
    #                 registro = self._limpar_registro_antigo(item_normalizado)

    #             registros_limpos.append(registro)
    #         except Exception:
    #             logger.exception("❌ Erro ao limpar registro")
    #             continue
    #     return registros_limpos

    # def _limpar_registro_antigo(self, item):
    #     tipo = self.classificar_tipo(item)
    #     periodo = item.get("periodo do fato gerador") or item.get("periodo de apuracao")
    #     descricao_html = ""
    #     for chave in item:
    #         if "descricao" in chave or "declaracoes" in chave:
    #             descricao_html = item[chave]
    #             break
    #     descricao = BeautifulSoup(descricao_html or "", "html.parser").text.strip()

    #     return {
    #         "tipo": tipo,
    #         "codigo_darf": item.get("codigo darf"),
    #         "codigo_gps": item.get("codigo gps"),
    #         "documento": item.get("documento"),
    #         "descricao": descricao,
    #         "periodo_fato_gerador": periodo
    #     }

    # def _limpar_registro_novo(self, item):
    #     doc_arrec = item.get("documento arrecadacao", "")
    #     tipo = "darf" if "darf" in doc_arrec.lower() else "gps" if "gps" in doc_arrec.lower() else "outros"

    #     return {
    #         "tipo": tipo,
    #         "codigo_receita": item.get("codigo de receita"),
    #         "grupo_tributo": item.get("grupo de tributo"),
    #         "descricao": item.get("descricao"),
    #         "periodo_fato_gerador": item.get("periodo de apuracao"),
    #         "documento_arrecadacao": doc_arrec,
    #         "categoria_declaracao": item.get("categoria da declaracao / origem escrituracao"),
    #         "fundamentacao_legal": item.get("fundamentacao legal")
    #     }
