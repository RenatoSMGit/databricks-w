from pyspark.sql import SparkSession

spark = SparkSession.getActiveSession()


def process_from_yml(yaml_path: str, env: str = 'dev'):
    """Exemplo de orchestrator para pipeline YAML."""
    print(f'Processando YAML: {yaml_path} | ambiente: {env}')
    print('Leitura do metadata e execução do pipeline aqui.')
    return True


if __name__ == '__main__':
    process_from_yml('/Workspace/Users/<usuario>/projeto_aluno_databricks/metadata/modelos/trusted_data/comercial/pedidos.yml', env='dev')
