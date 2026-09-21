def create_table_from_yml(yaml_path: str, env: str = 'dev'):
    print(f'Criando tabela a partir do YAML: {yaml_path} | ambiente: {env}')


def alter_table_from_yml(yaml_path: str, env: str = 'dev'):
    print(f'Alterando tabela a partir do YAML: {yaml_path} | ambiente: {env}')


def repair_table(table_name: str):
    print(f'Reparando tabela: {table_name}')
