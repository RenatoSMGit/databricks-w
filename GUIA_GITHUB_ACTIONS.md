# Aula pratica: GitHub Actions do inicio ao fim

Este guia usa o workflow deste repositorio, localizado em `.github/workflows/validate.yml`, para ensinar como automatizar verificacoes a cada mudanca no GitHub.

## Objetivos da aula

Ao final, o aluno deve conseguir:

- explicar o que e GitHub Actions e quando usar integracao continua (CI);
- identificar os eventos, jobs, steps e runner de um workflow;
- enviar uma alteracao, abrir um pull request e acompanhar a execucao;
- encontrar a causa de uma falha nos logs e corrigi-la;
- distinguir validacao automatica de execucao de um pipeline Databricks.

## 1. Preparacao

O aluno precisa de:

- uma conta GitHub com acesso a este repositorio;
- Git instalado;
- o repositorio clonado na maquina;
- permissao para enviar uma branch e abrir um pull request.

Abra um terminal na pasta do repositorio e confirme que o Git reconhece o projeto:

```bash
git status
```

Se ainda nao clonou o repositorio, copie a URL pela opcao **Code** no GitHub e execute:

```bash
git clone URL_DO_REPOSITORIO
cd NOME_DO_REPOSITORIO
```

## 2. O que e GitHub Actions?

GitHub Actions e o servico do GitHub que executa tarefas automatizadas em resposta a eventos do repositorio. Essas tarefas podem validar codigo, rodar testes, criar artefatos ou publicar uma aplicacao.

Neste projeto, o workflow faz **integracao continua (CI)**: verifica algumas propriedades do codigo para detectar erros cedo. Ele nao publica nada e nao executa os dados no Databricks.

O arquivo que define o workflow precisa estar dentro de `.github/workflows/`. Aqui, o arquivo e:

```text
.github/workflows/validate.yml
```

Cada arquivo YAML nesse diretorio pode definir um workflow. YAML usa indentacao para representar a hierarquia; mantenha os espacos consistentes e nao use tabulacoes.

## 3. Entendendo o workflow deste projeto

Abra `.github/workflows/validate.yml`. A estrutura principal e:

```yaml
name: Validar projeto Databricks

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Baixar codigo
        uses: actions/checkout@v4

      - name: Configurar Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Instalar validador YAML
        run: python -m pip install pyyaml

      - name: Validar sintaxe Python
        run: python -m compileall -q projeto_aluno_databricks/notebooks

      - name: Validar arquivos YAML
        run: |
          python - <<'PY'
          from pathlib import Path
          import yaml

          metadata_dir = Path("projeto_aluno_databricks/metadata")
          files = sorted(metadata_dir.rglob("*.yml"))
          files += sorted(metadata_dir.rglob("*.yaml"))
          if not files:
              raise SystemExit("Nenhum arquivo YAML encontrado em metadata/")

          for file in files:
              with file.open(encoding="utf-8") as stream:
                  yaml.safe_load(stream)
              print(f"OK: {file}")
          PY
```

### Partes importantes

- `name`: nome que aparece na interface do GitHub.
- `on`: eventos que iniciam o workflow. `push` roda quando ha envio para `main`; `pull_request` roda em pull requests cujo destino e `main`; `workflow_dispatch` permite iniciar manualmente.
- `permissions`: concede apenas leitura do conteudo do repositorio, que e o necessario para estas verificacoes.
- `jobs`: conjunto de trabalhos. Aqui existe um job chamado `validate`.
- `runs-on`: maquina virtual usada para executar o job. `ubuntu-latest` indica uma versao atual do Ubuntu mantida pelo GitHub.
- `steps`: comandos executados em ordem dentro do job.
- `uses`: usa uma action pronta. `actions/checkout` baixa o conteudo do repositorio para a maquina virtual; `actions/setup-python` instala/configura Python.
- `with`: fornece parametros para uma action, neste caso a versao do Python.
- `run`: executa um comando de terminal. Se um comando terminar com erro, o step e o job falham e os passos seguintes daquele job nao rodam.

O bloco `run: |` contem varias linhas de shell. O script Python procura arquivos `.yml` e `.yaml` em `projeto_aluno_databricks/metadata` e tenta carrega-los. Se um arquivo tiver sintaxe YAML invalida, a validacao falha.

## 4. Quando ele roda?

Este workflow tem tres formas de execucao:

1. **Push para `main`:** uma alteracao enviada diretamente para a branch `main` inicia a validacao.
2. **Pull request para `main`:** abrir ou atualizar um pull request com destino a `main` inicia a validacao antes da integracao.
3. **Execucao manual:** na pagina do repositorio no GitHub, abra **Actions**, escolha **Validar projeto Databricks** e use **Run workflow**. A opcao manual aparece porque existe `workflow_dispatch`.

O filtro de branch importa: um push para outra branch nao inicia o workflow por este gatilho. Um pull request destinado a outra branch tambem nao corresponde a configuracao atual.

## 5. Fazer uma alteracao e acompanhar a CI

Crie uma branch para a atividade:

```bash
git switch -c aula/minha-primeira-validacao
```

Faca uma pequena alteracao em um arquivo de projeto, salve e confira o que mudou:

```bash
git status
git diff
```

Adicione e envie a alteracao:

```bash
git add CAMINHO_DO_ARQUIVO
git commit -m "Adiciona alteracao da aula"
git push -u origin aula/minha-primeira-validacao
```

No GitHub, abra um pull request da branch `aula/minha-primeira-validacao` para `main`. A verificacao deve aparecer na pagina do pull request, normalmente na secao de status ou em **Checks**.

Para acompanhar os detalhes:

1. Abra a aba **Actions** do repositorio.
2. Selecione a execucao mais recente de **Validar projeto Databricks**.
3. Abra o job `validate`.
4. Expanda cada step para ler os comandos e a saida.

Um check verde indica que todas as etapas terminaram com sucesso. Um check vermelho indica que alguma etapa retornou erro; abra os logs e encontre o primeiro erro relevante, nao apenas a ultima linha.

## 6. Experimento: provocar e corrigir uma falha

Este exercicio ensina a ler o resultado da CI. Faca-o em uma branch de teste, nunca na `main`.

1. Abra um dos arquivos `.yml` em `projeto_aluno_databricks/metadata/`.
2. Em uma linha temporaria, introduza um erro de sintaxe, como remover a aspa final de um valor entre aspas.
3. Salve, faca commit, envie a branch e atualize o pull request.
4. Abra **Actions** e observe a falha no step **Validar arquivos YAML**. Os logs indicam o arquivo e o problema de parsing.
5. Restaure a sintaxe YAML, faca outro commit e envie novamente.
6. Confirme que uma nova execucao fica verde.

Como segundo teste, introduza temporariamente um erro de sintaxe Python em um arquivo `.py` dentro de `projeto_aluno_databricks/notebooks/`. A etapa **Validar sintaxe Python** deve falhar. Corrija o arquivo e confirme que o check volta a passar.

Depois do exercicio, confirme que nao ficou nenhuma alteracao de teste sem querer:

```bash
git status
```

## 7. O que esta validacao cobre (e o que nao cobre)

O workflow atual:

- compila sintaticamente os arquivos Python em `projeto_aluno_databricks/notebooks`;
- carrega os arquivos YAML encontrados em `projeto_aluno_databricks/metadata`;
- acusa erro se nao encontrar nenhum arquivo YAML nessa pasta.

Ele **nao** executa os notebooks, testa regras de negocio, conecta ao Databricks, valida credenciais, cria tabelas ou verifica se os caminhos e catalogos existem no ambiente. `compileall` verifica sintaxe Python, nao comportamento. `yaml.safe_load` verifica se o documento pode ser interpretado como YAML, nao se ele segue todas as regras de negocio do projeto.

Para executar o pipeline Databricks seriam necessarios outros passos e configuracao, como ambiente de execucao, acesso ao workspace e credenciais protegidas. Essas credenciais nunca devem ser gravadas diretamente no arquivo do workflow nem enviadas ao Git.

## 8. Problemas comuns

- **O workflow nao apareceu:** confira se o arquivo esta em `.github/workflows/`, se foi enviado ao GitHub e se o evento/branch corresponde aos filtros em `on`.
- **Erro de YAML no workflow:** verifique indentacao, dois-pontos, aspas e espacos. O YAML do workflow e diferente dos YAML de metadados que o proprio workflow valida.
- **Arquivo ou pasta nao encontrado:** confira os caminhos relativos a raiz do repositorio. Os comandos atuais esperam a pasta `projeto_aluno_databricks/` na raiz.
- **Falha ao instalar PyYAML:** abra o log do step **Instalar validador YAML** e confira se o runner conseguiu acessar o indice de pacotes.
- **Falha em um pull request:** leia o primeiro erro nos logs e corrija-o na mesma branch. Um novo push atualiza o pull request e inicia outra validacao.
- **A execucao manual nao aparece:** confirme que o workflow ja foi enviado para o GitHub e abra a aba **Actions** do repositorio.

## 9. Desafio para a turma

Proponha uma nova verificacao para o workflow e responda antes de implementar:

1. Que problema ela detecta?
2. Em qual step deve ser executada?
3. Que comando ou ferramenta seria necessaria?
4. Como demonstrar, com um exemplo, que a verificacao funciona?

Sugestoes: adicionar testes automatizados, validar um arquivo obrigatorio ou verificar uma regra especifica dos metadados. Mantenha a verificacao pequena, provoque uma falha controlada na branch e confirme que o log ajuda a localizar o problema.

## Resumo para o aluno

```text
evento do GitHub
    -> runner inicia
    -> checkout baixa o repositorio
    -> Python e dependencias sao configurados
    -> steps executam as validacoes
    -> GitHub mostra sucesso ou os logs da falha
```

O ciclo de trabalho e: **alterar -> enviar para uma branch -> abrir/atualizar pull request -> ler o check -> corrigir -> confirmar sucesso**.