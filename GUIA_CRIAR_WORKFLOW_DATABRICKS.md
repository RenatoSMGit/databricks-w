# Aula pratica: criar um Job Databricks pelo GitHub Actions

Este roteiro demonstra como criar e manter um Job Databricks como configuracao versionada. O Databricks Asset Bundle (Declarative Automation Bundle) descreve o Job; o GitHub Actions valida e faz o deploy.

O fluxo HML valida a definicao, cria/atualiza o Job comercial, mostra os detalhes do recurso, executa a DAG e publica um resumo visual no GitHub Actions.

## Objetivos

- Entender a diferenca entre GitHub Actions e Lakeflow Jobs.
- Definir um Job Databricks em YAML.
- Usar GitHub Actions para validar e publicar essa definicao.
- Configurar credenciais sem grava-las no repositorio.
- Conferir o Job criado no workspace.

## 1. Entender o fluxo

```text
push para hml ou execucao manual
    -> GitHub baixa o repositorio e instala a Databricks CLI
    -> bundle validate confere a definicao
    -> bundle deploy cria ou atualiza o Job no workspace
    -> CLI mostra o Job publicado
    -> Databricks executa as tasks pela DAG
    -> GitHub publica o resultado de cada fase
```

GitHub Actions e o orquestrador de CI/CD. Lakeflow Job e o recurso Databricks com as tasks e suas dependencias. Um Bundle descreve esse recurso em arquivos versionados para que o deploy possa ser repetido sem criar um Job novo a cada execucao.

Este repositorio tem workflows separados para a validacao inicial, para o Job Ola Mundo e para a esteira comercial da branch `hml`. O workflow HML abaixo executa apenas o recurso `pipeline_comercial` do Bundle.

## 2. Pre-requisitos

- Repositorio GitHub com Actions habilitado e permissao para alterar Settings.
- Workspace Databricks Free acessivel pelo aluno.
- Permissao para criar e editar Jobs e para usar os arquivos do workspace.
- Um PAT valido do workspace. Nunca compartilhe ou comite esse token.
- Um workspace Free com quota disponivel. A definicao usa serverless e limita cada Job a uma execucao simultanea.

## 3. Conhecer os arquivos

O Bundle tem a configuracao principal na raiz e guarda os Jobs dentro do projeto do aluno:

```text
databricks.yml
projeto_aluno_databricks/workflows/pipeline_comercial.yml
projeto_aluno_databricks/workflows/templates/template_job.yml
```

`databricks.yml` nomeia o Bundle, inclui os arquivos YAML de primeiro nivel em `projeto_aluno_databricks/workflows/` e determina o alvo `dev`. `pipeline_comercial.yml` define o Job, suas tasks, o compute serverless e a ordem de dependencias. O arquivo dentro de `workflows/templates/` e um modelo generico e nao e implantado.

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

Abra `projeto_aluno_databricks/workflows/pipeline_comercial.yml` e localize:

- `resources.jobs.pipeline_comercial`: a chave que identifica o recurso no Bundle.
- `name`: o nome que aparece em Jobs & Pipelines.
- `tasks`: as unidades de trabalho; cada `task_key` e unica.
- `spark_python_task.python_file`: o script Python executado pela task.
- `depends_on`: define a ordem de execucao.
- `environment_key` e `environments`: selecionam o ambiente serverless. Python e PySpark fazem parte do ambiente base; nao instale PySpark como dependencia do ambiente serverless.
- `max_concurrent_runs: 1`: evita duas execucoes do mesmo Job ao mesmo tempo.

Os caminhos dos scripts sao relativos ao arquivo `projeto_aluno_databricks/workflows/pipeline_comercial.yml`. O Bundle sincroniza os arquivos Python de `projeto_aluno_databricks/notebooks/custom/` para o workspace no deploy.

Para criar outro Job, copie `projeto_aluno_databricks/workflows/templates/template_job.yml` para um novo arquivo diretamente em `projeto_aluno_databricks/workflows/`, troque a chave do recurso, o nome, as tasks e seus caminhos. O `include` do Bundle carrega esses YAMLs de primeiro nivel e ignora a pasta `templates/`.

## 6. Revisar a GitHub Action

Abra `.github/workflows/esteira_comercial_hml.yml`:

- `workflow_dispatch` permite iniciar o deploy manualmente.
- `push` inicia o deploy quando mudam o Bundle, as definicoes em `projeto_aluno_databricks/workflows/`, os scripts Python incluidos ou o proprio workflow, desde que o push chegue a `hml`.
- `actions/checkout` baixa os arquivos locais necessarios pelo Bundle.
- `databricks bundle validate -t dev` valida a configuracao antes da publicacao.
- `databricks bundle deploy -t dev` cria ou atualiza os Jobs definidos em `projeto_aluno_databricks/workflows/` no workspace.
- `databricks bundle summary -t dev` confirma o recurso publicado e exibe o link para o Job.
- `databricks bundle run pipeline_comercial -t dev` espera a conclusao do Job; falha se uma task falhar.
- A etapa final escreve o resultado de cada fase no resumo da execucao do GitHub.

Na pagina do run do GitHub, as fases aparecem como cinco quadrados conectados no grafo: validar, publicar, confirmar o Job, executar e resumir. Clique em cada quadrado para ver os logs. O resumo final continua visivel mesmo quando uma fase anterior falha, indicando `success`, `failure` ou `skipped`.

## 7. Publicar pelo GitHub

Depois de revisar os arquivos, confira as mudancas:

```bash
git status
git diff
```

Adicione e envie os arquivos novos:

```bash
git add databricks.yml projeto_aluno_databricks/workflows .github/workflows/esteira_comercial_hml.yml GUIA_CRIAR_WORKFLOW_DATABRICKS.md projeto_aluno_databricks/notebooks/custom
git commit -m "Define Job Databricks como Bundle"
git push -u origin NOME_DA_BRANCH
```

Abra um pull request com destino a `hml` e faca o merge. A action **Esteira comercial (branch hml)** sera disparada pelo push nessa branch. Para testar manualmente, abra essa action em **Actions → Run workflow** e selecione `hml`.

## 8. Conferir o resultado

1. No GitHub, abra a execucao da Action.
2. Confira as etapas numeradas e expanda cada uma para ver seus logs.
3. Abra o resumo visual no final do run e confira o resultado de cada fase.
4. Use o link impresso por `bundle summary` para abrir o Job no Databricks.
5. Na aba de execucoes do Job, abra a DAG e confira o resultado de cada task.

Se usar outra identidade para deploy, o Bundle pode criar outro estado/Job de desenvolvimento. Para esta aula, use o mesmo usuario e o mesmo alvo `dev` em deploys sucessivos.

## 9. Diagnosticar falhas

- **A Action nao aparece:** confira se os arquivos estao na branch `hml`, nos caminhos em `paths`, e dentro de `.github/workflows/`.
- **Credenciais ausentes:** confira `DATABRICKS_HOST` em Variables e `DATABRICKS_TOKEN` em Secrets, usando exatamente esses nomes.
- **Token rejeitado:** gere um PAT para o workspace correto e atualize o secret; nao imprima o valor para depurar.
- **Sem permissao para criar/editar Job:** a identidade do PAT precisa ter as permissoes de workspace necessarias.
- **`bundle validate` falha:** leia o primeiro erro de schema e confira indentacao, caminho do script, nomes de `task_key` e dependencias.
- **Deploy passou, mas a execucao da esteira falha:** isso e um erro de uma task, nao do deploy. Abra o Job pelo link do `bundle summary` e veja o log da primeira task com falha.

Antes de executar, confirme que as tabelas e volumes usados pelo projeto existem e que os dados de entrada estao corretos. As tabelas Trusted, Refined e a fato Curated sao reconstruidas com `overwrite` em cada execucao; isso evita o uso de `mode('merge')`, que nao e suportado por `DataFrameWriter.mode`.

## 10. Exercicio

1. Copie `projeto_aluno_databricks/workflows/templates/template_job.yml` para `projeto_aluno_databricks/workflows/` e personalize o Job.
2. Envie a alteracao para uma branch e abra um pull request.
3. Faca merge para `hml` e observe as etapas numeradas e o resumo visual no GitHub Actions.
4. No Databricks, abra o Job pelo link do resumo e confira o estado das tasks na DAG.
5. Identifique as fases de validacao, deploy e execucao e explique o resultado de cada uma.

## Referencias

- [Declarative Automation Bundles](https://docs.databricks.com/aws/en/dev-tools/bundles/)
- [Tasks Python em Bundles](https://docs.databricks.com/aws/en/dev-tools/bundles/job-task-types#python-script-task)
- [Ambientes serverless para Jobs](https://docs.databricks.com/aws/en/compute/serverless/dependencies)
- [GitHub Actions no Databricks](https://docs.databricks.com/aws/en/dev-tools/ci-cd/github)