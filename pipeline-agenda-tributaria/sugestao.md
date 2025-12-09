## Proposta de modelagem e carga diaria

**Objetivo**  
Manter os compromissos atualizados em execucoes diarias, sem duplicar registros e preservando historico quando a Receita alterar alguma informacao.

**Modelagem**

- `NR_IDFR_CMPO`: `NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY` (Oracle gera; o loader nao envia).
- Chave de negocio para identificar o compromisso sem depender de descricao: `AA_REF_CMPO, MM_REF_CMPO, DD_REF_CMPO, TX_URL_DOC_ARC (ou dia_url), CD_RC_CMPO, TX_DOC_ARC_CMPO, TX_CTGR_DCL_CMPO, TX_OGM_LCTO_CMPO, TX_PER_APRC_CMPO`. Se algum vier “--”, mantemos na combinacao.
- `HASH_CONTEUDO`: hash (ex. SHA-256) dos campos sujeitos a mudar (descricao, base legal, URLs etc.).
- Controle de vigencia: `FLAG_ATIVO` (1/0), `TS_ATIVACAO`, `TS_INATIVACAO`. O backend expõe aos clientes apenas registros com `FLAG_ATIVO=1` (ou a linha mais recente por chave), mantendo os inativos apenas para historico/auditoria.

**Tabelas**  
Final (COMPROMISSO): PK identity, colunas de negocio, `HASH_CONTEUDO`, `FLAG_ATIVO`, `TS_ATIVACAO`, `TS_INATIVACAO`.  
Staging (TMP_COMPROMISSO): mesma estrutura, sem PK identity nem constraints.

**Processo diario**

1. Carregar o JSON do dia na staging, populando chave de negocio, hash, `FLAG_ATIVO=1`, `TS_ATIVACAO=SYSTIMESTAMP`.
2. MERGE na tabela final pela chave de negocio:
   - Encontrou e hash igual: nao faz nada.
   - Encontrou e hash diferente: marca o registro atual como inativo (`FLAG_ATIVO=0`, `TS_INATIVACAO=SYSTIMESTAMP`) e insere nova linha com hash novo (`FLAG_ATIVO=1`, `TS_ATIVACAO=SYSTIMESTAMP`, PK identity novo).
   - Nao encontrou: insere com `FLAG_ATIVO=1` e hash calculado.
3. Resultado: sempre uma linha ativa por compromisso; historico preservado para auditoria.
