# Guia de aula: GitHub Actions executando um Job Databricks

Este roteiro ensina a ligar um workflow do GitHub Actions a um Job que ja existe no Databricks. O aluno vai configurar os dados de acesso, disparar o workflow, acompanhar a execucao e diagnosticar falhas.

> O GitHub Actions nao cria nem configura o Job Databricks. Ele pede ao Databricks que execute um Job ja criado.

## Objetivos

Ao final, o aluno deve conseguir:

- diferenciar um workflow do GitHub Actions de um Job do Databricks;
- criar e testar um Job Databricks;
- guardar host e token nos locais apropriados do GitHub;
- iniciar o Job manualmente ou por push;
- encontrar nos logs se a falha ocorreu no GitHub ou no Databricks.

## 1. Como as pecas se comunicam

```text
push para main ou disparo manual
        -> GitHub Actions inicia um runner Linux
        -> runner instala a Databricks CLI
        -> CLI autentica usando host e token
        -> CLI pede ao Databricks para executar o Job pelo ID
        -> aluno consulta o resultado no Databricks e nos logs do GitHub
```

Sao duas execucoes diferentes: o runner do GitHub roda a CLI; o Job executa as tasks no compute do Databricks. Neste exemplo, o GitHub nao envia os arquivos do projeto ao workspace nem cria as tasks. O Job precisa estar configurado para encontrar o codigo e os dados que utiliza.

## 2. Pre-requisitos

- O repositorio do projeto esta no GitHub e Actions esta habilitado.
- O aluno tem acesso a um workspace Databricks Free.
- Existe um Job Databricks configurado e testado com **Run now**.
- O Job usa recursos disponiveis no workspace. No Free, o compute e serverless e ha limites de uso e concorrencia.
- O workspace permite criar e usar um Personal Access Token (PAT). Se a opcao nao estiver disponivel, consulte o professor ou a administracao do workspace; nao tente contornar as politicas de acesso.

## 3. Criar e testar o Job no Databricks

1. Entre no workspace Databricks.
2. Abra **Jobs & Pipelines** e escolha **Create job**.
3. De um nome claro, por exemplo `pipeline-comercial-dev`.
4. Adicione as tasks de processamento e suas dependencias. Para este projeto, planeje a ordem das camadas: Raw, Trusted, Refined e Curated.
5. Configure o compute serverless disponivel no workspace Free e confirme que as tasks tem permissao para ler os arquivos e gravar nas tabelas.
6. Salve o Job.
7. Anote o Job ID mostrado nos detalhes do Job. Cada aluno deve usar o ID do proprio Job.
8. Clique em **Run now** e confirme que a execucao termina com sucesso antes de integrar o GitHub.

Se o Job falhar aqui, resolva primeiro no Databricks. O GitHub Actions nao consegue corrigir tasks, tabelas, caminhos, permissoes ou dados incorretos.

## 4. Criar um PAT no workspace

O PAT e uma credencial. Nunca o coloque no codigo, neste guia, em um commit ou em uma mensagem.

1. No workspace, abra o menu do usuario e entre em **Settings**.
2. Abra **Developer** e, ao lado de **Access tokens**, escolha **Manage**.
3. Gere um token com nome que identifique seu uso, por exemplo `github-actions-aula`.
4. Copie o valor uma unica vez para adiciona-lo ao GitHub no proximo passo. Mantenha-o privado.

Se a tela nao permitir gerar token, o workspace pode ter PATs desabilitados ou sua conta pode nao ter permissao. Se uma execucao revelar que o Databricks rejeita o token, gere um PAT valido para este workspace e atualize o secret no GitHub. Nao compartilhe o valor do token para depurar.

## 5. Configurar as variaveis e o secret no GitHub

No repositorio do GitHub:

1. Abra **Settings → Secrets and variables → Actions**.
2. Na secao **Variables**, crie `DATABRICKS_HOST` com o host do workspace. Use somente a origem, por exemplo `https://dbc-exemplo.cloud.databricks.com`; nao inclua `?o=...`, caminhos, virgula ou o nome do Job.
3. Na secao **Secrets**, crie `DATABRICKS_TOKEN` e cole o PAT gerado no workspace.
4. Salve as configuracoes.

O Job ID nao e um segredo. No arquivo usado nesta aula ele fica configurado diretamente no workflow. Substitua o valor de exemplo pelo ID do Job que o aluno anotou. O host e o token nunca devem ser colocados diretamente no YAML.

## 6. Entender o arquivo do Actions

O workflow desta aula fica em `.github/workflows/executar_databricks.yml`:

```yaml
name: Executar Job Databricks

on:
  workflow_dispatch:
  push:
    branches: [main]
    paths:
      - ".github/workflows/**"
      - "projeto_aluno_databricks/notebooks/**"
      - "projeto_aluno_databricks/metadata/**"

permissions:
  contents: read

jobs:
  executar-job:
    runs-on: ubuntu-latest
    steps:
      - name: Instalar Databricks CLI
        uses: databricks/setup-cli@main

      - name: Executar Job
        env:
          DATABRICKS_HOST: ${{ vars.DATABRICKS_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
          JOB_ID: 312724880725806
        run: databricks jobs run-now "$JOB_ID"
```

Troque `312724880725806` pelo ID do Job do aluno. Os demais elementos:

- `workflow_dispatch` habilita o botao de execucao manual.
- `push` inicia o fluxo quando um push chega a `main` e pelo menos um caminho listado muda.
- `permissions: contents: read` da ao runner apenas a leitura necessaria do repositorio.
- `runs-on` escolhe a maquina temporaria que executa os comandos.
- `uses` instala a Databricks CLI.
- `vars.DATABRICKS_HOST` le a variavel do repositorio.
- `secrets.DATABRICKS_TOKEN` le o PAT sem exibi-lo nos logs.
- `databricks jobs run-now` solicita a execucao do Job pelo ID.

O arquivo nao tem evento `pull_request`: abrir um pull request nao executa esse Job. Um push para `main`, como o merge de um pull request, executa se os caminhos modificados corresponderem aos filtros.

## 7. Enviar o workflow para o GitHub

Na raiz do repositorio, confira as alteracoes:

```bash
git status
git diff
```

Adicione e faca commit do arquivo:

```bash
git add .github/workflows/executar_databricks.yml
git commit -m "Adiciona execucao do Job Databricks"
```

Envie a alteracao para o GitHub. Se estiver trabalhando em uma branch de aula, envie a branch e faca merge para `main`; o gatilho de push ocorre no merge:

```bash
git push -u origin NOME_DA_BRANCH
```

O gatilho automatico exige `main` e um caminho incluido em `paths`. Uma alteracao apenas no README, por exemplo, nao inicia este workflow.

## 8. Fazer o primeiro teste manual

1. No GitHub, abra a aba **Actions**.
2. Escolha **Executar Job Databricks**.
3. Clique em **Run workflow** e selecione a branch `main`.
4. Abra a nova execucao e depois o job `executar-job`.
5. Expanda **Executar Job** para ver o resultado da chamada.
6. No workspace Databricks, abra **Jobs & Pipelines** e confirme o resultado das tasks.

Comece pelo disparo manual. Depois de validar, teste o push automatico alterando um arquivo incluido em `paths` e enviando-o para `main`. Cada execucao pode consumir compute e quota do workspace Free.

## 9. Diagnosticar erros

- **Nenhuma execucao aparece:** confirme que o YAML foi enviado para `.github/workflows/`, que a branch e `main` e que os arquivos alterados correspondem aos caminhos em `paths`. Para testar sem push, use `workflow_dispatch`.
- **`cannot configure default credentials`:** confira se existe o secret `DATABRICKS_TOKEN` e se o job le `secrets.DATABRICKS_TOKEN`. Um secret criado apenas em um GitHub Environment precisa que o job declare esse environment.
- **`Credential was not sent or was of an unsupported type`:** o runner recebeu um valor, mas o Databricks o rejeitou. Gere um PAT valido no workspace correto, atualize o secret e confira que ele nao contem `Bearer `, aspas ou espacos adicionados.
- **Erro 401/403:** confira se o token esta ativo e se a identidade que o criou pode executar aquele Job.
- **Job nao encontrado ou acesso negado:** confirme que o Job ID pertence ao workspace indicado por `DATABRICKS_HOST` e que o usuario do token tem permissao para executar o Job.
- **O step do GitHub passa, mas a task do Databricks falha:** abra a execucao do Job no Databricks e investigue os logs da task, compute, dependencias, permissoes e caminhos de dados.

Nunca imprima o valor do token nos logs nem o envie ao professor. Se houver suspeita de exposicao, revogue-o no Databricks e crie outro.

## 10. Atividade para o aluno

1. Execute o Job manualmente pelo GitHub Actions.
2. Altere um arquivo de notebook ou metadata e envie para `main`.
3. Compare o log da execucao manual com o log disparado pelo push.
4. Em uma branch descartavel, teste um Job ID invalido e observe o erro; depois restaure o ID correto.
5. Explique quais configuracoes sao publicas (`DATABRICKS_HOST`, Job ID) e qual e secreta (`DATABRICKS_TOKEN`).

## Referencias

- [Lakeflow Jobs](https://docs.databricks.com/aws/en/jobs/)
- [Criar PATs do workspace](https://docs.databricks.com/aws/en/dev-tools/auth/pat)
- [GitHub Actions no Databricks](https://docs.databricks.com/aws/en/dev-tools/ci-cd/github)
- [Limitacoes do Databricks Free Edition](https://docs.databricks.com/aws/en/getting-started/free-edition-limitations)