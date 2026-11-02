# Avaliação da Alfabetização — Real versus Meta

## Sobre o Projeto

Projeto da fase 2 da Pós-Tech em AI Scientist da FIAP, que consiste em um pipeline de dados com arquitetura medalhão (**batch + streaming**) construído no Databricks com **dados da Avaliação da Alfabetização do INEP** (dataset disponível via Base dos Dados). O objetivo é comparar a taxa **real** de alfabetização dos alunos avaliados (2º e 3º anos do ensino fundamental) com as **metas** definidas em três níveis: **Brasil**, **UF** e **Município**.

## Links Úteis
[Dashboard](https://dbc-6fa0cfa6-b5cf.cloud.databricks.com/dashboardsv3/01f1d583fd4211b0979fd806160b7e76/published?o=7474655927371602)
<br>
[Vídeo Executivo](https://youtube.com)

## Leitura das Metas

O Compromisso Nacional tem como aspiração a **universalização da alfabetização até 2030**. As tabelas oficiais publicadas na Base dos Dados, entretanto, trazem uma **trajetória pactuada e mensurável**, com valores anuais de 2024 a 2030 — para a rede pública, a coluna `meta_alfabetizacao_2030` traz o valor **80**.

Neste projeto:

* **Cálculos de distância até a meta** (widgets Real vs Meta, rankings de municípios e a coluna `atingimento_meta` da camada Gold) usam **exclusivamente a trajetória pactuada da fonte** — as metas anuais por Brasil, UF e município;
* A leitura de **universalização até 2030** é um **cenário aspiracional** e **não entra em nenhum cálculo**; se algum dia for exibida em alguma visão, será identificada como "cenário aspiracional".

As duas leituras são legítimas, mas significam coisas diferentes — e não são misturadas em pontos diferentes do projeto.

## Entidades

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

## Localização dos Dados

Os **dados não são versionados neste repositório** — eles ficam no lakehouse (Unity Catalog) do workspace Databricks:

* **CSVs de entrada:** `/Volumes/workspace/default/vol_avaliacao_alfabetizacao` (subpastas `batch/` e `streaming/`)
* **Tabelas Gold:**
  * `workspace.default.gold_alunos`
  * `workspace.default.gold_alfabetizacao_brasil`
  * `workspace.default.gold_alfabetizacao_uf`
  * `workspace.default.gold_alfabetizacao_municipio`

## Como Reproduzir

1. **Acessar** o link do dashboard no início do Readme.

## Dashboard

O dashboard **“Avaliação da Alfabetização — Real versus Meta”** compara Real vs Meta em três níveis:

* **Brasil** — barras Real vs Meta por ano;
* **UF** — barras horizontais Real vs Meta por UF e pizza de situação da meta (atingida / abaixo);
* **Município** — rankings dos municípios com maiores e menores diferenças Real − Meta;
* **Detalhe por aluno** — tabela com proficiências e situação de alfabetização.

Filtros: Ano, Região e UF (globais); Município, Rede, Série e Situação do Aluno (por página).

## FinOps e Otimização de Custos

| Operação | Consumo Estimado | Custo Estimado |
| --- | --- | --- |
| Update completo do pipeline (dry run + full) | ~1–3 min de compute serverless | ~US$ 0,10–0,60 |
| Update incremental diário (Auto Loader) | < 1 min | ~US$ 0,05–0,20 |
| Primeira carga do dashboard (16 widgets) | segundos de warehouse SQL serverless | ~US$ 0,01–0,05 |
| Mudança de filtro (dados materializados) | quase nulo | ~US$ 0,00–0,01 |

Cenário mensal típico (um update por dia + uso moderado do dashboard): ordem de US$ 5–20/mês. 

## Tecnologias Utilizadas

| Tecnologia | Uso no projeto |
| --- | --- |
| Databricks | Plataforma principal de desenvolvimento e execução |
| Unity Catalog | Governança de dados e gerenciamento das tabelas |
| Lakeflow Declarative Pipelines | Orquestração e processamento da pipeline medalhão |
| Auto Loader | Ingestão incremental dos dados streaming |
| Delta Lake | Armazenamento transacional das tabelas Bronze, Silver e Gold |
| SQL Warehouse | Consulta e visualização dos dados analíticos |
| Databricks Dashboards | Construção do dashboard Real versus Meta |
| Apache Spark | Processamento distribuído dos dados |

Foi adotada uma arquitetura nativa do ecossistema Databricks para reduzir complexidade operacional, simplificar governança e aproveitar funcionalidades gerenciadas de ingestão, processamento e visualização. 
