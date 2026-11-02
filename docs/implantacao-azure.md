# Implantação no Azure Databricks — Guia passo a passo

Guia detalhado para implantar o pipeline medalhão (**Avaliação da Alfabetização — Real vs Meta**) e o dashboard em um workspace do **Azure Databricks**, usando o Declarative Automation Bundle incluído neste repo.

Tempo estimado: ~40–60 minutos (mais o tempo de criação do workspace).

---

## 0. Pré-requisitos

* Assinatura do Azure com permissão para criar recursos (ou um workspace Azure Databricks já existente);
* Plano **Premium** do Azure Databricks — **necessário para Unity Catalog** (o Standard não suporta);
* Unity Catalog ativo no workspace (contas recentes já vêm com metastore habilitado; caso contrário, associe um metastore de conta);
* **Databricks CLI ≥ 0.281.0** (o dashboard do bundle usa `dataset_catalog`/`dataset_schema`, suportados a partir dessa versão);
* Git instalado localmente;
* Os **CSVs das 6 entidades** — eles ficam no volume do workspace de origem e **não estão no GitHub** (veja a seção 4).

---

## 1. Criar o workspace (se ainda não existir)

1. No [Portal do Azure](https://portal.azure.com), clique em **Criar um recurso** e busque **Azure Databricks**;
2. Preencha assinatura, grupo de recursos e região; em **Tipo de preço**, escolha **Premium**;
3. Clique em **Revisar + criar** → **Criar** e aguarde a implantação;
4. Clique em **Iniciar workspace** (Launch Workspace) para abrir a interface do Databricks;
5. Na barra lateral, abra **Catálogo** — se abrir sem erros, o Unity Catalog está ativo.

> Se o Catálogo reclamar de metastore, peça ao administrador da conta para criar/associar um metastore do Unity Catalog ao workspace (documentação: *Set up a Unity Catalog metastore*).

---

## 2. Clonar o repo e autenticar a CLI

1. Clone o repositório localmente:

   ```bash
   git clone https://github.com/1PedroFerreira/fiap-pos-tech-ai-scientist-fase-2-desafio-.git
   cd fiap-pos-tech-ai-scientist-fase-2-desafio-
   ```

2. Instale a Databricks CLI:

   ```bash
   # Windows
   winget install Databricks.DatabricksCLI

   # macOS
   brew install databricks
   ```

3. Confirme a versão (precisa ser ≥ 0.281.0):

   ```bash
   databricks --version
   ```

4. Autentique no workspace Azure (abrirá o navegador para login com a conta da Microsoft/Entra ID):

   ```bash
   databricks auth login --host https://<seu-workspace>.azuredatabricks.net
   ```

5. Teste a autenticação:

   ```bash
   databricks current-user me
   ```

---

## 3. Preparar catálogo e warehouse

1. Crie o catálogo **workspace** (os nomes padrão do bundle — assim os scripts Bronze não precisam de ajuste, pois referenciam `/Volumes/workspace/default/...`):

   ```bash
   databricks catalogs create workspace
   ```

   > O schema `default` é criado automaticamente junto com o catálogo.

2. Liste os SQL warehouses e copie o **ID** de um (serverless):

   ```bash
   databricks warehouses list
   ```

   Se não houver nenhum: na UI do Azure, **SQL Warehouses → Criar warehouse** (Serverless Starter serve) e copie o ID.

---

## 4. Copiar os CSVs do workspace de origem para a sua máquina

No workspace de origem, abra **Catálogo → workspace → default → vol_avaliacao_alfabetizacao** e baixe localmente as pastas (usando o botão de download do Catalog Explorer):

* `batch/uf`
* `batch/municipio`
* `batch/meta_alfabetizacao_brasil`
* `batch/meta_alfabetizacao_uf`
* `batch/meta_alfabetizacao_municipio`
* `batch/alunos_historico`
* `streaming/alunos`

Você vai reenviar essa mesma estrutura para o Azure na seção 6.

---

## 5. Validar e fazer o deploy do bundle

No diretório raiz do repo (onde está o `databricks.yml`):

```bash
databricks bundle validate -t azure --var warehouse_id=<id-do-warehouse>

databricks bundle deploy -t azure --var warehouse_id=<id-do-warehouse>
```

O deploy cria no Azure:

* o **volume** MANAGED `vol_avaliacao_alfabetizacao` (em `workspace.default`);
* o **pipeline SDP serverless** "Avaliação da Alfabetização — Pipeline Medalhão", com os 14 scripts de `src/transformations/`;
* o **dashboard** "Avaliação da Alfabetização — Real vs Meta", com as fontes dos datasets re-escritas para `workspace.default`.

Variáveis disponíveis (override com `--var`): `catalog` (padrão `workspace`), `schema` (padrão `default`), `warehouse_id` (obrigatório).

---

## 6. Enviar os CSVs para o volume no Azure

No Azure, abra **Catálogo → workspace → default → vol_avaliacao_alfabetizacao** e, com **Upload**, recrie as mesmas subpastas da seção 4 (`batch/uf`, `batch/municipio`, `batch/meta_alfabetizacao_brasil`, `batch/meta_alfabetizacao_uf`, `batch/meta_alfabetizacao_municipio`, `batch/alunos_historico` e `streaming/alunos`) e envie os arquivos.

> Se preferir CLI: `databricks fs cp <arquivo.csv> /Volumes/workspace/default/vol_avaliacao_alfabetizacao/<subpasta>/`

---

## 7. Executar o pipeline

1. No menu **Data Pipelines / Lakeflow** do Azure, abra o pipeline **Avaliação da Alfabetização — Pipeline Medalhão**;
2. Rode primeiro a **validação (dry run)** para checar erros de sintaxe/ligações sem gravar dados;
3. Depois clique em **Iniciar (Start)** para o update completo;
4. Acompanhe as tabelas surgindo em **Catálogo → workspace → default**: `bronze_*` (6), `silver_*` (4) e `gold_*` (4).

> O pipeline é **disparado** (não contínuo). Para agendar updates diários, crie um job com tarefa de pipeline — ver a seção *FinOps* do README.

---

## 8. Publicar o dashboard

1. Em **Dashboards**, abra **Avaliação da Alfabetização — Real vs Meta** e confira os dados (os filtros Ano/Região/UF e os KPIs devem carregar);
2. Clique em **Publicar**. Se quiser materialização (consultas mais rápidas e mais baratas), marque *executar como proprietário* (credenciais incorporadas) e crie um **agendamento de atualização** (ex.: diário) na UI de agendamentos — sem agendamento, os datasets materializados não são renovados.

---

## 9. Checklist de verificação final

* [ ] Volume com as 6 entidades nas subpastas corretas (`batch/…` e `streaming/alunos`)
* [ ] Dry run do pipeline sem erros
* [ ] Update completo concluído (expectations sem descartar massa de registros)
* [ ] `SELECT COUNT(*) FROM workspace.default.gold_alunos` retorna linhas
* [ ] Dashboard abre com Real vs Meta (Brasil, UF e municípios)

---

## Solução de problemas

| Sintoma | Causa provável e correção |
| --- | --- |
| Erro no deploy citando `dataset_catalog`/`dataset_schema` | CLI < 0.281.0 — atualize a Databricks CLI |
| Pipeline falha com caminho/volume não encontrado | Estrutura de pastas do volume errada (seção 6) ou uso de `catalog`/`schema` diferentes do padrão — os scripts Bronze referenciam `/Volumes/workspace/default/vol_avaliacao_alfabetizacao/...`; ajuste em `src/transformations/bronze/` |
| Permissão negada ao criar catálogo | Sua conta precisa do privilégio `CREATE CATALOG` no metastore (fale com o admin da conta) |
| Unity Catalog indisponível | Workspace deve ser plano **Premium** com metastore associado (seção 1) |
| CLI expira/token vencido | Refaça `databricks auth login --host …` |
| Deploy funciona, mas dashboard sem dados | Falta o update do pipeline (seção 7) — os datasets leem as tabelas Gold |
