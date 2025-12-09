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
