Ótima pergunta, Breno. Vamos direto ao ponto, olhando para **o DDL da tabela** e para **o que seu JSON já traz hoje**. A ideia é verificar **campo a campo** se você tem insumos suficientes para **popular os NOT NULL** e os demais, e onde precisar, definir **regras de derivação** ou **valores padrão**.

---

## ✅ O que a tabela exige (e o que seu JSON já tem)

**Tabela**: `ORAGNCOW0005.CMPO_TRBA_PJ_SRF`  
**NOT NULL** (pelo seu DDL e constraints) — todas as colunas são obrigatórias **exceto** `TS_ATL_CMPO`:

1.  **NR_IDFR_CMPO** _(PK)_ → **Gerar no Python** (determinística, hash)

    - **Tem no JSON?** Não vem pronto; **você gera** com base em: **data** (`YYYY-MM-DD`), **tipo** (ex.: `darf`, `gps`, `declaracao_pj`, `declaracao_pf`), **periodo_fato_gerador** e uma **assinatura** da `descricao` (e **`codigo_receita`** quando existir).
    - ✅ **Viável** com seu JSON atual (mesmo quando `codigo_receita` for `null`).

2.  **AA_REF_CMPO / MM_REF_CMPO / DD_REF_CMPO**

    - **Tem no JSON?** Sim—extraímos de `dias.data` (`YYYY-MM-DD`).
    - ✅ **Ok**.

3.  **CD_RC_CMPO** _(NUMBER(6,0))_

    - **Tem no JSON?** Em muitos eventos, sim (`codigo_receita`); em declarações, pode ser `null`.
    - ❗ **É NOT NULL na tabela** → você **precisa de regra** para casos sem código:
      - **Solução**: para eventos **sem código de receita** (declarações, documentos), **definir um código substituto funcional** (ex.: `0`) **não é possível** porque quebraria o NOT NULL.
      - **Recomendação prática**: **ajustar o DDL** e tornar `CD_RC_CMPO` **NULLABLE** **OU** criar **campo alternativo de chave funcional** e **não exigir código de receita** para esses tipos.
      - Alternativa: **mapear** alguns tipos de declaração para **códigos internos padronizados** (catálogo próprio) — mas isso seria **um código de negócio**, não de receita da RFB. Se aceitável, mantenha o campo com esse catálogo.

4.  **TX_URL_FON_CMPO** _(VARCHAR2(150))_

    - **Tem no JSON?** Sim (`fonte`: URL da agenda do ano).
    - ✅ **Ok**.

5.  **TX_GR_TRBT_CMPO** _(VARCHAR2(25))_

    - **Tem no JSON?** Em parte (`grupo_tributo` pode estar `null`).
    - ✅ **Derivável**: a partir da `descricao` (ex.: “IRRF”, “IOF”, “IPI”, “IRPJ”, “CSLL”, “COFINS”, “PIS/PASEP”), ou pelo bloco do qual o evento foi extraído. Defina **heurística**: primeira sigla antes do “ - ” na `descricao`.

6.  **TX_DOC_ARC_CMPO** _(VARCHAR2(10))_

    - **Tem no JSON?** Às vezes (`documento_arrecadacao`), senão derivável pelo `tipo`:
      - `darf` → “DARF”
      - `gps` → “GPS”
      - `documento` com “Simples Nacional” → “DAS”
      - `documento` com “MEI” → “DAS-MEI”
    - ✅ **Ok** com regra.

7.  **TX_URL_DOC_ARC** _(VARCHAR2(150))_

    - **Tem no JSON?** Sim (`dias.url`), a URL específica do dia.
    - ✅ **Ok**.

8.  **TX_DCR_CMPO** _(VARCHAR2(300))_

    - **Tem no JSON?** Sim (`descricao`).
    - ✅ **Ok** (truncar se exceder 300).

9.  **TX_CTGR_DCL_CMPO** _(VARCHAR2(100))_

    - **Tem no JSON?** Às vezes (`categoria_declaracao`), pode estar `null`.
    - ✅ **Derivável**: para `declaracao_pj`/`declaracao_pf`, extrair o nome da obrigação da `descricao` (ex.: “DCTF Mensal”, “EFD-Contribuições”, “EFD-Reinf”, “Dirf”, “Dimob”, “DME”, “DOI”, “PGDAS-D”, “e-Financeira”, “Dirbi”). Para `darf`/`gps`, pode ser “ARRECADAÇÃO”.

10. **TX_OGM_LCTO_CMPO** _(VARCHAR2(100))_

    - **Tem no JSON?** Não diretamente.
    - ❗ **É NOT NULL** → defina **valor padrão de negócio** (ex.: “AGENDA RFB”), ou outra origem que faça sentido (ex.: “SITE-RFB”).
    - ✅ Com **default** e revisão de significado, dá para seguir.

11. **TX_PER_APRC_CMPO** _(VARCHAR2(64))_

    - **Tem no JSON?** Sim (`periodo_fato_gerador`).
    - ✅ **Ok** (truncar 64).

12. **TX_BASE_LGAL_CMPO** _(VARCHAR2(80))_

    - **Tem no JSON?** Às vezes aparece textual na `descricao`; mas em vários casos está `null`.
    - ❗ **É NOT NULL** → você **precisa** de regra:
      - **Opção A**: extrair referências legais quando existirem (ex.: “art. 9º da Lei nº 9.249/95”) e, quando **não existir**, preencher um **placeholder padrão** (ex.: “N/A”), **mas isso não é ideal** semanticamente.
      - **Opção B (recomendada)**: **ajustar o DDL** para permitir **NULL** aqui. Muitos compromissos da agenda **não** exibem base legal explícita — exigir sempre **não reflete o dado real**.
    - ⚠️ Sem ajuste de DDL, você terá que preencher com um **texto genérico** (ex.: “Agenda Tributária RFB”) para cumprir NOT NULL.

13. **TX_URL_BASE_LGAL** _(VARCHAR2(150))_

    - **Tem no JSON?** Geralmente **não** (só teria se você capturar links da base legal, o site nem sempre fornece).
    - ❗ **É NOT NULL** → **mesma situação** da base legal textual:
      - **Opção A**: quando não houver link, usar a **URL do dia** como referência (não é “base legal”, mas cumpre o obrigatório).
      - **Opção B (recomendada)**: ajustar o DDL para **NULLABLE**, porque nem sempre existe URL de base legal.

14. **TS_PBC_CMPO** _(TIMESTAMP)_

    - **Tem no JSON?** Sim (`publicado_em` do dia, padronizar para ISO).
    - ✅ **Ok**.

15. **TS_ATL_CMPO** _(TIMESTAMP)_ — **única NÃO obrigatória**
    - **Tem no JSON?** Sim (`atualizado_em` — pode ser `null`).
    - ✅ **Ok**.

---

## 🎯 Conclusão objetiva

- Você já tem **quase tudo** para carregar com segurança **se** adotar **regras de derivação** e/ou **ajuste de DDL** para os campos que **não existem** ou **nem sempre existem** no dado real:
  - **OK com derivação**: `NR_IDFR_CMPO`, `AA/MM/DD`, `TX_GR_TRBT_CMPO`, `TX_DOC_ARC_CMPO`, `TX_CTGR_DCL_CMPO`, `TX_OGM_LCTO_CMPO`, `TX_PER_APRC_CMPO`, `TX_URL_FON_CMPO`, `TX_URL_DOC_ARC`, `TX_DCR_CMPO`, `TS_PBC_CMPO`, `TS_ATL_CMPO`.
  - **Pontos críticos (NOT NULL no DDL, mas faltam no JSON em muitos casos)**:
    - `CD_RC_CMPO`: **nem todo evento tem** (declarações/documentos).  
      → **Sugestão**: tornar **NULLABLE** no DDL **ou** criar catálogo interno (código de negócio).
    - `TX_BASE_LGAL_CMPO` e `TX_URL_BASE_LGAL`: **nem sempre há base legal/URL**.  
      → **Sugestão**: tornar **NULLABLE** no DDL; se não puder, usar **placeholders seguros** (ex.: “N/A” e a própria `url_dia`), ciente do **trade-off** semântico.

> Em termos de **qualidade e integridade**, a opção **ideal** é **ajustar o DDL** desses três campos para refletirem a realidade da fonte (RFB), evitando preenchimentos artificiais em colunas obrigatórias.

---

## ✅ Estratégia recomendada de transformação (resumo)

1.  **PK determinística**:

    ```python
    NR_IDFR_CMPO = hash( data + tipo + periodo_fato_gerador + assinatura(descricao) + (codigo_receita or '') + cauda(url_dia) ) % 10**11
    ```

2.  **Grupo de tributo**:

    - Extrair sigla do início da `descricao` (ex.: “IRRF”, “IOF”, …).

3.  **Documento de arrecadação**:

    - Mapear pelo `tipo`: `darf`→“DARF”, `gps`→“GPS”, etc.

4.  **Categoria de declaração**:

    - Para `declaracao_*`, extrair o nome canônico (ex.: “DCTF Mensal”).

5.  **Origem escrituração**:

    - Padrão: “AGENDA RFB”.

6.  **Base legal / URL base legal**:

    - Extrair quando houver; **caso contrário**:
      - Se **DDL ajustar para NULL**: deixar `None`.
      - Se **não ajustar**: preencher com “N/A” e `url_dia` (trade-off).

7.  **Código de receita**:

    - Quando `null` em eventos **que não são arrecadação**, **idealmente** permitir `NULL` no DDL.  
      Se não der, usar catálogo interno (defina com sua área de negócio).

8.  **Truncamentos**:

    - Enforce limites: 150/25/10/150/300/100/100/64/80/150.

9.  **Validações**:
    - `MM` ∈ \[1..12], `DD` ∈ \[1..31], **NOT NULL** (exceto `TS_ATL_CMPO`).

---

## 📌 Próximos passos práticos

- **Decidir** com sua área de negócio/DBA:

  1.  Tornar **NULLABLE**: `CD_RC_CMPO`, `TX_BASE_LGAL_CMPO`, `TX_URL_BASE_LGAL`;  
      **ou**
  2.  Adotar **placeholders/catálogos** para cumprir NOT NULL.

- Eu posso te gerar:
  - Um **script `ALTER TABLE`** com essas mudanças de nulabilidade.
  - O **script Python de transformação** pronto (parse JSON → DF Oracle) com todas as **regras de derivação**, **validações**, **truncamentos** e **PK determinística**.
  - O **MERGE** staging → produção, idempotente.

Quer que eu siga com a **opção de ajustar o DDL** (NULLABLE) ou **preferem manter NOT NULL com regras de preenchimento**? Com sua escolha, eu já te entrego os arquivos (SQL e `.py`) prontos para rodar no seu pipeline.
