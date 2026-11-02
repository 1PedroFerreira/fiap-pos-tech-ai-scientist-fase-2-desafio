# Avaliação da Alfabetização — Real vs Meta (FIAP Pos Tech AI Scientist — Fase 2)

## Sobre o projeto

Pipeline de dados medalhão (**batch + streaming**) construído no Databricks com **dados simulados** inspirados na **Avaliação da Alfabetização do INEP** (dataset disponível via Base dos Dados). O objetivo é comparar a taxa **real** de alfabetização dos alunos avaliados (2º e 3º anos do ensino fundamental) com as **metas** definidas em três níveis: **Brasil**, **UF** e **Município**.

## Leitura das metas (duas leituras)

O Compromisso Nacional tem como aspiração a **universalização da alfabetização até 2030**. As tabelas oficiais publicadas na Base dos Dados, entretanto, trazem uma **trajetória pactuada e mensurável**, com valores anuais de 2024 a 2030 — para a rede pública, a coluna `meta_alfabetizacao_2030` traz o valor **80**.

Neste projeto:

* **Cálculos de distância até a meta** (widgets Real vs Meta, rankings de municípios e a coluna `atingimento_meta` da camada Gold) usam **exclusivamente a trajetória pactuada da fonte** — as metas anuais por Brasil, UF e município;
* A leitura de **universalização até 2030** é um **cenário aspiracional** e **não entra em nenhum cálculo**; se algum dia for exibida em alguma visão, será identificada como "cenário aspiracional".

As duas leituras são legítimas, mas significam coisas diferentes — e não são misturadas em pontos diferentes do projeto.

## Entidades (6)

| Entidade | Conteúdo | Volume |
| --- | --- | --- |
| UF | Dimensão: sigla, nome e região | 27 UFs |
| Município | Dimensão: código IBGE, nome e UF | 263 municípios |
| Meta Alfabetização Brasil | Meta nacional por ano | 4 registros (2022–2025) |
| Meta por UF | Meta estadual por ano | 108 registros (27 UFs × 4 anos) |
| Meta por Município | Meta municipal por ano | 1.052 registros |
| Dados de Alunos | Avaliações por aluno (fato) | ~45 mil alunos (batch, 2022–2024) + ~8 mil alunos (streaming, 2025) |

## Arquitetura

* **Bronze** — ingestão batch (CSVs do volume Unity Catalog) e streaming (Auto Loader na pasta de novos arquivos);
* **Silver** — deduplicação por watermark, *expectations* de qualidade (chaves, faixas de proficiência, nível de escrita) e normalização das dimensões;
* **Gold** — agregações da taxa real de alfabetização e comparação com as metas (Brasil, UF e município), com joins entre todas as entidades.

## Estrutura de pastas

```
├── README.md
├── databricks.yml
├── resources/
│   ├── avaliacao_alfabetizacao.pipeline.yml
│   ├── avaliacao_alfabetizacao.dashboard.yml
│   └── vol_avaliacao_alfabetizacao.volume.yml
├── src/
│   └── transformations/
│       ├── bronze/       # ingestão batch + streaming (Auto Loader)
│       │   ├── bronze_alunos.py
│       │   ├── bronze_uf.py
│       │   ├── bronze_municipio.py
│       │   ├── bronze_meta_alfabetizacao_brasil.py
│       │   ├── bronze_meta_alfabetizacao_uf.py
│       │   └── bronze_meta_alfabetizacao_municipio.py
│       ├── silver/      # deduplicação, expectations e normalização
│       │   ├── silver_alunos.py
│       │   ├── silver_uf.py
│       │   ├── silver_municipio.py
│       │   └── silver_metas.py
│       └── gold/        # agregações real vs meta
│           ├── gold_alunos.py
│           ├── gold_alfabetizacao_brasil.py
│           ├── gold_alfabetizacao_uf.py
│           └── gold_alfabetizacao_municipio.py
└── dashboards/
    └── avaliacao_alfabetizacao_real_vs_meta.lvdash.json
```

## Localização dos dados

Os **dados não são versionados neste repositório** — eles ficam no lakehouse (Unity Catalog) do workspace Databricks:

* **CSVs de entrada:** `/Volumes/workspace/default/vol_avaliacao_alfabetizacao` (subpastas `batch/` e `streaming/`)
* **Tabelas Gold:**
  * `workspace.default.gold_alunos`
  * `workspace.default.gold_alfabetizacao_brasil`
  * `workspace.default.gold_alfabetizacao_uf`
  * `workspace.default.gold_alfabetizacao_municipio`

## Como reproduzir

1. **Carregar os CSVs** das 6 entidades no volume `workspace.default.vol_avaliacao_alfabetizacao` (pastas `batch/uf`, `batch/municipio`, `batch/meta_alfabetizacao_brasil`, `batch/meta_alfabetizacao_uf`, `batch/meta_alfabetizacao_municipio`, `batch/alunos_historico` e `streaming/alunos`);
2. **Criar o Lakeflow Spark Declarative Pipeline** apontando para os arquivos de `src/transformations/`, com destino (catálogo) `workspace.default`, e executar um update (recomenda-se dry run antes);
3. **Importar o dashboard** `dashboards/avaliacao_alfabetizacao_real_vs_meta.lvdash.json` (via UI do Databricks, opção *Importar do arquivo*, ou Databricks CLI) e publicar.

## Implantação em outro workspace (Azure Databricks) via bundle

O repo inclui um **Declarative Automation Bundle** (`databricks.yml` + `resources/`) que cria o volume, o pipeline medalhão e o dashboard em um único deploy — funciona em qualquer workspace Databricks, incluindo Azure:

1. No workspace Azure, clone este repositório (Repos → Adicionar repo);
2. Autentique o Databricks CLI: `databricks auth login --host https://<seu-workspace>.azuredatabricks.net`;
3. No diretório do repo, valide e faça o deploy: `databricks bundle validate -t azure --var warehouse_id=<id-do-seu-warehouse>` e `databricks bundle deploy -t azure --var warehouse_id=<id-do-seu-warehouse>`;
4. O deploy cria: o volume `vol_avaliacao_alfabetizacao` (MANAGED), o pipeline SDP serverless com os 14 scripts de `src/transformations/` e o dashboard (com as fontes dos datasets re-escritas para `${catalog}.${schema}`);
5. Copie os CSVs das 6 entidades para `/Volumes/<catalog>/<schema>/vol_avaliacao_alfabetizacao/` (subpastas `batch/` e `streaming/`);
6. Execute um update do pipeline (UI do pipeline ou CLI) e publique o dashboard.

Variáveis do bundle: `catalog` (padrão `workspace`), `schema` (padrão `default`), `warehouse_id` (obrigatório).

> **Atenção:** os scripts da camada Bronze referenciam o caminho fixo `/Volumes/workspace/default/vol_avaliacao_alfabetizacao/...`. Com os valores padrão (`catalog=workspace`, `schema=default`), basta criar o catálogo `workspace` e o schema `default` no Azure (`CREATE CATALOG workspace;` `CREATE SCHEMA workspace.default;`) e nada mais precisa mudar. Se usar outro catálogo/schema, ajuste também esses caminhos em `src/transformations/bronze/`.

## Dashboard

O dashboard **“Avaliação da Alfabetização — Real vs Meta”** compara Real vs Meta em três níveis:

* **Brasil** — barras Real vs Meta por ano;
* **UF** — barras horizontais Real vs Meta por UF e pizza de situação da meta (atingida / abaixo);
* **Município** — rankings dos municípios com maiores e menores diferenças Real − Meta;
* **Detalhe por aluno** — tabela com proficiências e situação de alfabetização.

Filtros: Ano, Região e UF (globais); Município, Rede, Série e Situação do Aluno (por página).

> **Nota técnica:** os datasets do dashboard estão embutidos no próprio arquivo `.lvdash.json` como *local metric views* (medidas e dimensões declaradas sobre as tabelas Gold, incluindo medidas ponderadas como `SUM(x * qtd_alunos) / SUM(qtd_alunos)`), sem consultas SQL externas. Ao importar o dashboard, as tabelas Gold precisam existir no workspace de destino.

## FinOps e otimização de custos

Práticas de eficiência de custo aplicadas e recomendadas neste projeto:

**Já aplicadas**

* **Computação serverless** — o pipeline (Lakeflow Spark Declarative Pipelines) roda em compute serverless, cobrando por DBU efetivamente consumida, sem custo de cluster ocioso;
* **Materialização dos datasets do dashboard** — as 4 *local metric views* (`alunos`, `alfabetizacao_brasil`, `alfabetizacao_uf`, `alfabetizacao_municipio`) estão com *materialize-on-publish* habilitado: os dados são pré-computados quando o dashboard é publicado, acelerando filtros e widgets e reduzindo tempo de execução no warehouse SQL a cada visualização. Requisitos: publicação com credenciais incorporadas (*run as owner*) e pelo menos um agendamento de atualização ativo — hoje **não há nenhum agendamento**; criar um (ex.: diário) na UI de agendamentos para que a materialização seja atualizada;
* **Deduplicação com watermark** (`silver_alunos`) — a janela de watermark de 30 dias limita o estado mantido pelo streaming, reduzindo memória e compute nos updates;
* **Streaming incremental (Auto Loader)** — apenas os arquivos novos do volume são processados a cada update, sem reingestão completa;
* **Consultas agregadas** — os widgets leem as tabelas Gold já agregadas por ano (Brasil/UF/município); apenas a tabela "Detalhes por Aluno" consulta registros individuais.

**Recomendações**

* **Auto-stop do warehouse SQL** — manter auto-stop curto (5–10 min) e tamanho inicial pequeno, escalando apenas se a latência do dashboard exigir;
* **Pipeline disparado em vez de contínuo** — para dados com tolerância a latência de horas, agendar updates do pipeline (ex.: 1×/dia) em vez de processamento contínuo: o compute só existe durante o update;
* **Atribuição de custos por tags** — aplicar tags de custo (ex.: `projeto:avaliacao_alfabetizacao`) a warehouses e pipelines e monitorar o consumo em `system.billing.usage`;
* **Retenção de arquivos brutos** — revisar o ciclo de vida dos CSVs no volume (`batch/` e `streaming/`); após validação, arquivos históricos podem ser arquivados ou removidos para reduzir armazenamento.
