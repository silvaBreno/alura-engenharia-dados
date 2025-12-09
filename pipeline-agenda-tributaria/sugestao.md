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
1) Carregar o JSON do dia na staging, populando chave de negocio, hash, `FLAG_ATIVO=1`, `TS_ATIVACAO=SYSTIMESTAMP`.  
2) MERGE na tabela final pela chave de negocio:  
   - Encontrou e hash igual: nao faz nada.  
   - Encontrou e hash diferente: marca o registro atual como inativo (`FLAG_ATIVO=0`, `TS_INATIVACAO=SYSTIMESTAMP`) e insere nova linha com hash novo (`FLAG_ATIVO=1`, `TS_ATIVACAO=SYSTIMESTAMP`, PK identity novo).  
   - Nao encontrou: insere com `FLAG_ATIVO=1` e hash calculado.  
3) Resultado: sempre uma linha ativa por compromisso; historico preservado para auditoria.

**DDL sugerida (ajustar tamanhos conforme necessidade)**  
Final:  
```
CREATE TABLE COMPROMISSO (
  NR_IDFR_CMPO       NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  AA_REF_CMPO        NUMBER(4,0)      NOT NULL,
  MM_REF_CMPO        NUMBER(2,0)      NOT NULL,
  DD_REF_CMPO        NUMBER(2,0)      NOT NULL,
  TS_ATL_CMPO        TIMESTAMP,
  CD_RC_CMPO         VARCHAR2(150),
  TX_URL_FON_CMPO    VARCHAR2(150),
  TX_GR_TRBT_CMPO    VARCHAR2(25),
  TX_DOC_ARC_CMPO    VARCHAR2(10),
  TX_URL_DOC_ARC     VARCHAR2(150),
  TX_DCR_CMPO        VARCHAR2(300),
  TX_CTGR_DCL_CMPO   VARCHAR2(100),
  TX_OGM_LCTO_CMPO   VARCHAR2(100),
  TX_PER_APRC_CMPO   VARCHAR2(64),
  TX_BASE_LGAL_CMPO  VARCHAR2(80),
  TX_URL_BASE_LGAL   VARCHAR2(150),
  TS_PBC_CMPO        TIMESTAMP,
  HASH_CONTEUDO      VARCHAR2(64),
  FLAG_ATIVO         NUMBER(1,0) DEFAULT 1 NOT NULL,
  TS_ATIVACAO        TIMESTAMP DEFAULT SYSTIMESTAMP,
  TS_INATIVACAO      TIMESTAMP
);
ALTER TABLE COMPROMISSO ADD CONSTRAINT UQ_COMPROMISSO_CHAVE
UNIQUE (AA_REF_CMPO, MM_REF_CMPO, DD_REF_CMPO, TX_URL_DOC_ARC,
        CD_RC_CMPO, TX_DOC_ARC_CMPO, TX_CTGR_DCL_CMPO, TX_OGM_LCTO_CMPO, TX_PER_APRC_CMPO);
```
Staging: mesma estrutura, sem PK identity/constraints.

DDL staging (ajustar tamanhos se precisar):
```
CREATE TABLE TMP_COMPROMISSO (
  AA_REF_CMPO        NUMBER(4,0),
  MM_REF_CMPO        NUMBER(2,0),
  DD_REF_CMPO        NUMBER(2,0),
  TS_ATL_CMPO        TIMESTAMP,
  CD_RC_CMPO         VARCHAR2(150),
  TX_URL_FON_CMPO    VARCHAR2(150),
  TX_GR_TRBT_CMPO    VARCHAR2(25),
  TX_DOC_ARC_CMPO    VARCHAR2(10),
  TX_URL_DOC_ARC     VARCHAR2(150),
  TX_DCR_CMPO        VARCHAR2(300),
  TX_CTGR_DCL_CMPO   VARCHAR2(100),
  TX_OGM_LCTO_CMPO   VARCHAR2(100),
  TX_PER_APRC_CMPO   VARCHAR2(64),
  TX_BASE_LGAL_CMPO  VARCHAR2(80),
  TX_URL_BASE_LGAL   VARCHAR2(150),
  TS_PBC_CMPO        TIMESTAMP,
  HASH_CONTEUDO      VARCHAR2(64),
  FLAG_ATIVO         NUMBER(1,0),
  TS_ATIVACAO        TIMESTAMP,
  TS_INATIVACAO      TIMESTAMP
);
```

**MERGE sugerido (diario)**  
```
MERGE INTO COMPROMISSO tgt
USING TMP_COMPROMISSO src
   ON (tgt.AA_REF_CMPO = src.AA_REF_CMPO
       AND tgt.MM_REF_CMPO = src.MM_REF_CMPO
       AND tgt.DD_REF_CMPO = src.DD_REF_CMPO
       AND tgt.TX_URL_DOC_ARC = src.TX_URL_DOC_ARC
       AND tgt.CD_RC_CMPO = src.CD_RC_CMPO
       AND tgt.TX_DOC_ARC_CMPO = src.TX_DOC_ARC_CMPO
       AND tgt.TX_CTGR_DCL_CMPO = src.TX_CTGR_DCL_CMPO
       AND tgt.TX_OGM_LCTO_CMPO = src.TX_OGM_LCTO_CMPO
       AND tgt.TX_PER_APRC_CMPO = src.TX_PER_APRC_CMPO)
 WHEN MATCHED THEN
   UPDATE SET
     tgt.FLAG_ATIVO    = CASE WHEN tgt.HASH_CONTEUDO = src.HASH_CONTEUDO THEN tgt.FLAG_ATIVO ELSE 0 END,
     tgt.TS_INATIVACAO = CASE WHEN tgt.HASH_CONTEUDO = src.HASH_CONTEUDO THEN tgt.TS_INATIVACAO ELSE SYSTIMESTAMP END
   WHERE tgt.HASH_CONTEUDO <> src.HASH_CONTEUDO
 WHEN MATCHED THEN
   UPDATE SET
     tgt.TS_ATL_CMPO       = src.TS_ATL_CMPO,
     tgt.TX_GR_TRBT_CMPO   = src.TX_GR_TRBT_CMPO,
     tgt.TX_DOC_ARC_CMPO   = src.TX_DOC_ARC_CMPO,
     tgt.TX_URL_DOC_ARC    = src.TX_URL_DOC_ARC,
     tgt.TX_DCR_CMPO       = src.TX_DCR_CMPO,
     tgt.TX_CTGR_DCL_CMPO  = src.TX_CTGR_DCL_CMPO,
     tgt.TX_OGM_LCTO_CMPO  = src.TX_OGM_LCTO_CMPO,
     tgt.TX_PER_APRC_CMPO  = src.TX_PER_APRC_CMPO,
     tgt.TX_BASE_LGAL_CMPO = src.TX_BASE_LGAL_CMPO,
     tgt.TX_URL_BASE_LGAL  = src.TX_URL_BASE_LGAL,
     tgt.TS_PBC_CMPO       = src.TS_PBC_CMPO,
     tgt.HASH_CONTEUDO     = src.HASH_CONTEUDO,
     tgt.FLAG_ATIVO        = 1,
     tgt.TS_ATIVACAO       = CASE WHEN tgt.HASH_CONTEUDO = src.HASH_CONTEUDO THEN tgt.TS_ATIVACAO ELSE SYSTIMESTAMP END
   WHERE tgt.HASH_CONTEUDO <> src.HASH_CONTEUDO
 WHEN NOT MATCHED THEN
   INSERT (AA_REF_CMPO, MM_REF_CMPO, DD_REF_CMPO, TS_ATL_CMPO, CD_RC_CMPO,
           TX_URL_FON_CMPO, TX_GR_TRBT_CMPO, TX_DOC_ARC_CMPO, TX_URL_DOC_ARC,
           TX_DCR_CMPO, TX_CTGR_DCL_CMPO, TX_OGM_LCTO_CMPO, TX_PER_APRC_CMPO,
           TX_BASE_LGAL_CMPO, TX_URL_BASE_LGAL, TS_PBC_CMPO,
           HASH_CONTEUDO, FLAG_ATIVO, TS_ATIVACAO)
   VALUES (src.AA_REF_CMPO, src.MM_REF_CMPO, src.DD_REF_CMPO, src.TS_ATL_CMPO, src.CD_RC_CMPO,
           src.TX_URL_FON_CMPO, src.TX_GR_TRBT_CMPO, src.TX_DOC_ARC_CMPO, src.TX_URL_DOC_ARC,
           src.TX_DCR_CMPO, src.TX_CTGR_DCL_CMPO, src.TX_OGM_LCTO_CMPO, src.TX_PER_APRC_CMPO,
           src.TX_BASE_LGAL_CMPO, src.TX_URL_BASE_LGAL, src.TS_PBC_CMPO,
           src.HASH_CONTEUDO, 1, SYSTIMESTAMP);
```
Obs.: se preferir, a inativacao e a insercao em caso de hash diferente podem ser feitas em dois passos separados para deixar o MERGE mais simples.
