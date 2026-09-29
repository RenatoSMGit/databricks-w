# Aula pratica: criar um Job Databricks pelo GitHub Actions

Este roteiro demonstra como criar e manter um Job Databricks como configuracao versionada. O Databricks Asset Bundle (Declarative Automation Bundle) descreve o Job; o GitHub Actions valida e faz o deploy.

> Este fluxo cria ou atualiza o Job, mas nao inicia suas tasks. Depois do deploy, o aluno pode revisar o Job e escolher **Run now** no Databricks.

## Objetivos

- Entender a diferenca entre GitHub Actions e Lakeflow Jobs.
- Definir um Job Databricks em YAML.
- Usar GitHub Actions para validar e publicar essa definicao.
- Configurar credenciais sem grava-las no repositorio.
- Conferir o Job criado no workspace.

## 1. Entender o fluxo

```text
push para main ou execucao manual
    -> GitHub baixa o repositorio e instala a Databricks CLI
    -> bundle validate confere a definicao
    -> bundle deploy cria ou atualiza o Job no workspace
    -> aluno revisa e inicia o Job no Databricks
```

GitHub Actions e o orquestrador de CI/CD. Lakeflow Job e o recurso Databricks com as tasks e suas dependencias. Um Bundle descreve esse recurso em arquivos versionados para que o deploy possa ser repetido sem criar um Job novo a cada execucao.

Este repositorio tambem tem `executar_databricks.yml`, que chama um Job existente pelo ID. A action `criar_job_databricks.yml` e separada: ela publica o Job definido no Bundle e nao executa o Job antigo.

## 2. Pre-requisitos

- Repositorio GitHub com Actions habilitado e permissao para alterar Settings.
- Workspace Databricks Free acessivel pelo aluno.
- Permissao para criar e editar Jobs e para usar os arquivos do workspace.
- Um PAT valido do workspace. Nunca compartilhe ou comite esse token.
- Um workspace Free com quota disponivel. A definicao usa serverless e limita cada Job a uma execucao simultanea.

## 3. Conhecer os arquivos

O Bundle tem a configuracao principal na raiz:

```text
databricks.yml
resources/pipeline_comercial.yml
```

`databricks.yml` nomeia o Bundle, inclui a definicao do recurso e determina o alvo `dev`. `resources/pipeline_comercial.yml` define o Job, suas tasks, o compute serverless e a ordem de dependencias.

O Job cobre os scripts existentes:

```text
Raw clientes, produtos e pedidos
    -> Trusted correspondentes
        -> Refined KPI de vendas e Curated fato/dimensoes
```

As tasks Raw independentes podem iniciar em paralelo. Cada task Trusted espera a respectiva Raw. KPI e fato esperam Trusted pedidos; cada dimensao espera a tabela Trusted correspondente. O projeto ainda nao tem um script de ingestao Raw para itens_pedido, por isso essa entidade nao aparece como task.

## 4. Configurar o acesso no GitHub

1. No workspace Databricks, gere um PAT em **Settings → Developer → Access tokens → Manage → Generate new token**, se essa opcao estiver habilitada para a conta.
2. No repositorio GitHub, abra **Settings → Secrets and variables → Actions**.
3. Crie a variavel `DATABRICKS_HOST` com somente a origem do workspace, por exemplo `https://dbc-exemplo.cloud.databricks.com`. Nao inclua `?o=...`.
4. Crie o secret `DATABRICKS_TOKEN` e cole o PAT. Nao adicione `Bearer`, aspas ou espacos extras.

O Bundle/CLI recebem o host pela variavel de ambiente `DATABRICKS_HOST`; a CLI recebe a credencial por `DATABRICKS_TOKEN`. O valor do token nao deve aparecer em logs nem neste guia.

Se o workspace nao permitir gerar ou usar PAT, pare e consulte o administrador/professor. Nao tente contornar as regras de autenticacao do workspace.

## 5. Revisar a definicao do Job

Abra `resources/pipeline_comercial.yml` e localize:

- `resources.jobs.pipeline_comercial`: a chave que identifica o recurso no Bundle.
- `name`: o nome que aparece em Jobs & Pipelines.
- `tasks`: as unidades de trabalho; cada `task_key` e unica.
- `spark_python_task.python_file`: o script Python executado pela task.
- `depends_on`: define a ordem de execucao.
- `environment_key` e `environments`: selecionam o ambiente serverless. Python e PySpark fazem parte do ambiente base; nao instale PySpark como dependencia do ambiente serverless.
- `max_concurrent_runs: 1`: evita duas execucoes do mesmo Job ao mesmo tempo.

Os caminhos dos scripts sao relativos ao arquivo `resources/pipeline_comercial.yml`. O Bundle sincroniza os arquivos Python de `projeto_aluno_databricks/notebooks/custom/` para o workspace no deploy.

## 6. Revisar a GitHub Action

Abra `.github/workflows/criar_job_databricks.yml`:

- `workflow_dispatch` permite iniciar o deploy manualmente.
- `push` inicia o deploy quando mudam o Bundle, os scripts Python incluidos ou o proprio workflow, desde que o push chegue a `main`.
- `actions/checkout` baixa os arquivos locais necessarios pelo Bundle.
- `databricks bundle validate -t dev` valida a configuracao antes da publicacao.
- `databricks bundle deploy -t dev` cria ou atualiza o Job `pipeline_comercial` no workspace.

Depois do deploy, a Action executa `databricks bundle run ola_mundo -t dev`. Um check verde confirma a execucao do Job simples `ola_mundo`; nao significa que as tasks do pipeline comercial processaram dados.

## 7. Publicar pelo GitHub

Depois de revisar os arquivos, confira as mudancas:

```bash
git status
git diff
```

Adicione e envie os arquivos novos:

```bash
git add databricks.yml resources/pipeline_comercial.yml .github/workflows/criar_job_databricks.yml GUIA_CRIAR_WORKFLOW_DATABRICKS.md
git commit -m "Define Job Databricks como Bundle"
git push -u origin NOME_DA_BRANCH
```

Faca merge da branch para `main`. A Action sera disparada pelo push de merge. Para testar sem fazer um novo commit, use **Actions → Criar ou atualizar Job Databricks → Run workflow** e selecione `main`.

## 8. Conferir o resultado

1. No GitHub, abra a execucao da Action.
2. Confirme que **Validar definicao do Job**, **Criar ou atualizar Job no workspace** e **Executar Job Ola Mundo** terminaram sem erro.
3. No workspace Databricks, abra **Jobs & Pipelines** e procure `ola-mundo-dev` ou o nome com prefixo de desenvolvimento.
4. Abra a execucao de Ola Mundo e confira a saida `Ola, mundo!` nos logs da task.
5. O Job comercial tambem e criado/atualizado pelo Bundle, mas nao e executado por esta Action. Revise caminhos, tabelas e permissoes antes de inicia-lo manualmente.

Se usar outra identidade para deploy, o Bundle pode criar outro estado/Job de desenvolvimento. Para esta aula, use o mesmo usuario e o mesmo alvo `dev` em deploys sucessivos.

## 9. Diagnosticar falhas

- **A Action nao aparece:** confira se os arquivos estao na branch `main`, nos caminhos em `paths`, e dentro de `.github/workflows/`.
- **Credenciais ausentes:** confira `DATABRICKS_HOST` em Variables e `DATABRICKS_TOKEN` em Secrets, usando exatamente esses nomes.
- **Token rejeitado:** gere um PAT para o workspace correto e atualize o secret; nao imprima o valor para depurar.
- **Sem permissao para criar/editar Job:** a identidade do PAT precisa ter as permissoes de workspace necessarias.
- **`bundle validate` falha:** leia o primeiro erro de schema e confira indentacao, caminho do script, nomes de `task_key` e dependencias.
- **Deploy passou, mas Run now falha:** isso e um erro das tasks, nao do deploy. Abra os logs da task no Databricks.

Validar e publicar o Bundle nao executa os scripts. Antes da primeira execucao, revise a logica Python e confirme que as tabelas e volumes usados pelo projeto existem. Por exemplo, `pedidos_ingestao.py` usa `F.current_timestamp()` sem importar `functions as F`; ha tambem scripts com `.write.mode('merge')`, modo que deve ser revisto para a API Delta usada pelo projeto.

## 10. Exercicio

1. Altere o nome do Job ou adicione uma descricao em `resources/pipeline_comercial.yml`.
2. Envie a alteracao para uma branch e abra um pull request.
3. Faca merge para `main` e observe a validacao e o deploy.
4. No Databricks, confirme que o mesmo Job foi atualizado em vez de aparecer uma copia para cada deploy.
5. Identifique qual parte executa as tasks e explique por que o deploy, sozinho, nao processa os dados.

## Referencias

- [Declarative Automation Bundles](https://docs.databricks.com/aws/en/dev-tools/bundles/)
- [Tasks Python em Bundles](https://docs.databricks.com/aws/en/dev-tools/bundles/job-task-types#python-script-task)
- [Ambientes serverless para Jobs](https://docs.databricks.com/aws/en/compute/serverless/dependencies)
- [GitHub Actions no Databricks](https://docs.databricks.com/aws/en/dev-tools/ci-cd/github)