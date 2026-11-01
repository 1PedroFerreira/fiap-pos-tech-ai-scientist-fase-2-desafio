# Avaliação da Alfabetização — Real vs Meta (FIAP Pos Tech AI Scientist — Fase 2)

## Sobre o projeto

Pipeline de dados medalhão (**batch + streaming**) construído no Databricks com **dados simulados** inspirados na **Avaliação da Alfabetização do INEP** (dataset disponível via Base dos Dados). O objetivo é comparar a taxa **real** de alfabetização dos alunos avaliados (2º e 3º anos do ensino fundamental) com as **metas** definidas em três níveis: **Brasil**, **UF** e **Município**.

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

## Dashboard

O dashboard **“Avaliação da Alfabetização — Real vs Meta”** compara Real vs Meta em três níveis:

* **Brasil** — barras Real vs Meta por ano;
* **UF** — barras horizontais Real vs Meta por UF e pizza de situação da meta (atingida / abaixo);
* **Município** — rankings dos municípios com maiores e menores diferenças Real − Meta;
* **Detalhe por aluno** — tabela com proficiências e situação de alfabetização.

Filtros: Ano, Região e UF (globais); Município, Rede, Série e Situação do Aluno (por página).
