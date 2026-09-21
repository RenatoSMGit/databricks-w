def full_apply(yaml_path: str, env: str = 'dev'):
    print(f'Executando full_apply para {yaml_path} no ambiente {env}')
    print('1. validar YAML')
    print('2. criar/alterar tabela')
    print('3. executar notebook de origem')
    print('4. persistir dados')
