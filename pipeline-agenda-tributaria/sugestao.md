## Proposta para ID, historico e upsert diario

- `NR_IDFR_CMPO` como `NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY`. O Oracle gera o ID; o loader nao envia.
- Chave de negocio para identificar compromissos sem depender de descricao: `AA_REF_CMPO, MM_REF_CMPO, DD_REF_CMPO, TX_URL_DOC_ARC (ou dia_url), CD_RC_CMPO, TX_DOC_ARC_CMPO, TX_CTGR_DCL_CMPO, TX_OGM_LCTO_CMPO, TX_PER_APRC_CMPO`. Se algum vier como “--”, mantemos na combinacao.
- Hash de conteudo (ex.: SHA-256) sobre campos variaveis como descricao, base legal e URLs, gravado em `HASH_CONTEUDO`.
- Controle de vigencia: `FLAG_ATIVO` (1/0) e timestamps `TS_ATIVACAO` / `TS_INATIVACAO`. A visao para cliente filtra `FLAG_ATIVO=1`.

Fluxo diario com MERGE:
1) Carregar o JSON do dia em staging, com chave de negocio, hash, `FL_ATIVO=1`, `TS_ATIVACAO=SYSTIMESTAMP`.
2) MERGE na tabela final pela chave de negocio:
   - Se encontrar e o hash for igual, nao faz nada.
   - Se encontrar e o hash for diferente, marca o registro atual como inativo (`FLAG_ATIVO=0`, `TS_INATIVACAO=SYSTIMESTAMP`) e insere uma nova linha com o novo hash (`FLAG_ATIVO=1`, `TS_ATIVACAO=SYSTIMESTAMP`, PK identity novo).
   - Se nao encontrar, insere com `FLAG_ATIVO=1`, hash calculado e `TS_ATIVACAO=SYSTIMESTAMP`.
3) Resultado: uma linha ativa por chave de negocio e historico preservado para auditoria.

Beneficios: evita duplicidade nas execucoes diarias, captura alteracoes feitas pela Receita mantendo historico, e mantem o ID simples (identity) sem amarrar a chave de negocio.

### Tabelas sugeridas

**Tabela final (COMPROMISSO)**  
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
  -- campos de controle
  HASH_CONTEUDO      VARCHAR2(64),
  FLAG_ATIVO         NUMBER(1,0) DEFAULT 1 NOT NULL,
  TS_ATIVACAO        TIMESTAMP DEFAULT SYSTIMESTAMP,
  TS_INATIVACAO      TIMESTAMP
);
```
Sugerir `UNIQUE` para a chave de negocio (ajustar conforme regra):
```
ALTER TABLE COMPROMISSO ADD CONSTRAINT UQ_COMPROMISSO_CHAVE
UNIQUE (AA_REF_CMPO, MM_REF_CMPO, DD_REF_CMPO, TX_URL_DOC_ARC,
        CD_RC_CMPO, TX_DOC_ARC_CMPO, TX_CTGR_DCL_CMPO, TX_OGM_LCTO_CMPO, TX_PER_APRC_CMPO);
```

**Tabela staging (TMP_COMPROMISSO)**  
Mesma estrutura da final, exceto sem PK identity e sem constraints adicionais:
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

### MERGE sugerido (diario)
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
Observacao: no bloco `MATCHED` acima, a primeira clausula opcionaliza a inativacao; dependendo da regra do time de DB, pode separar em dois MERGEs ou usar logica equivalente (ex.: inativar e inserir novo em passos distintos).
