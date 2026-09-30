# Projeto-base do aluno: Databricks + Lakehouse

Este projeto reproduz a estrutura de referência para um pipeline de dados no Databricks usando arquitetura em camadas, Unity Catalog, Delta Lake e metadados YAML.

## Objetivo

O aluno deve aprender a construir um pipeline completo de dados comerciais com as camadas:

- Landing
- Raw
- Trusted
- Refined
- Curated

## Estrutura do projeto

```text
projeto_aluno_databricks/
├── README.md
├── requirements.txt
├── data/
│   └── landing/
│       └── comercial/
│           ├── clientes/
│           │   └── clientes.csv
│           ├── produtos/
│           │   └── produtos.csv
│           ├── pedidos/
│           │   └── pedidos.csv
│           └── itens_pedido/
│               └── itens_pedido.csv
├── metadata/
│   ├── full_spec.yml
│   ├── templates/
│   │   ├── template_raw.yml
│   │   ├── template_trusted.yml
│   │   ├── template_refined.yml
│   │   └── template_curated.yml
│   └── modelos/
│       ├── raw_data/
│       │   ├── comercial/
│       │   │   ├── clientes.yml
│       │   │   ├── produtos.yml
│       │   │   └── pedidos.yml
│       ├── trusted_data/
│       │   ├── comercial/
│       │   │   ├── clientes.yml
│       │   │   ├── produtos.yml
│       │   │   └── pedidos.yml
│       ├── refined_data/
│       │   └── comercial/
│       │       └── kpi_vendas_diarias.yml
│       └── curated_data/
│           └── comercial/
│               ├── fato_vendas.yml
│               ├── dim_cliente.yml
│               └── dim_produto.yml
├── notebooks/
│   ├── core/
│   │   └── process_from_yml.py
│   ├── custom/
│   │   ├── raw_data/
│   │   │   └── comercial/
│   │   │       ├── clientes_ingestao.py
│   │   │       ├── produtos_ingestao.py
│   │   │       └── pedidos_ingestao.py
│   │   ├── trusted_data/
│   │   │   └── comercial/
│   │   │       ├── clientes.py
│   │   │       ├── produtos.py
│   │   │       └── pedidos.py
│   │   ├── refined_data/
│   │   │   └── comercial/
│   │   │       └── kpi_vendas_diarias.py
│   │   └── curated_data/
│   │       └── comercial/
│   │           ├── fato_vendas.py
│   │           ├── dim_cliente.py
│   │           └── dim_produto.py
│   └── utils/
│       ├── catalog/
│       │   ├── create_table.py
│       │   ├── alter_table.py
│       │   └── repair_table.py
│       └── helpers/
│           ├── validate_yml.py
│           └── full_apply.py
├── workflows/
│   ├── pipeline_comercial.yml
│   └── templates/
│       └── template_job.yml
├── sql/
│   └── consultas_analiticas.sql
└── data/
    └── landing/
        └── comercial/
            └── pedidos/
```

As definicoes dos Jobs Databricks ficam em `workflows/`. O arquivo `templates/template_job.yml` e um modelo para copiar ao criar outro Job; ele nao e publicado automaticamente pelo Bundle.

## Ambientes sugeridos

- dev
- hml
- prd

Exemplos de catalogos:

```text
raw_data_dev.comercial.pedidos
trusted_data_dev.comercial.pedidos
refined_data_dev.comercial.kpi_vendas_diarias
curated_data_dev.comercial.fato_vendas
```

## Fluxo do pipeline

```text
Landing (arquivos)
  ↓
Raw (dados brutos)
  ↓
Trusted (limpeza, tipagem e qualidade)
  ↓
Refined (agregações e indicadores)
  ↓
Curated (dados prontos para BI)
```

## Instruções de uso

1. Ajuste o ambiente e os nomes de catálogo no YAML.
2. Crie os volumes e caminhos no Databricks.
3. Valide o YAML antes da criação da tabela.
4. Execute os notebooks de ingestão por camada.
5. Aplique as regras de qualidade e os merges.
6. Consulte os resultados em curated.

## Entidades do projeto

- clientes
- produtos
- pedidos
- itens_pedido

## Resultado esperado

A tabela final deve ser:

```text
curated_data_dev.comercial.fato_vendas
```

Com campos como:

- id_pedido
- id_cliente
- id_produto
- dt_pedido
- vl_bruto
- vl_desconto
- vl_liquido
- status_pedido
- ds_regiao
- data_entrega
- indicador_atraso
