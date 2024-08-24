# Metamorfo
Seu Utilitário Python Multiforme

## Visão Geral
Metamorfo é um pacote Python de versatilidade, projetado para fornecer um conjunto de ferramentas e utilitários de uso geral, com foco especial em conexões com diversos bancos de dados.

Seja você um desenvolvedor back-end, data scientist ou entusiasta de Python, metamorfo pode simplificar suas tarefas e aumentar sua produtividade.

## Características Principais

* **Conexões com múltiplos bancos de dados:** Conecte-se facilmente à diversas bases de dados.
    - PostgreSQL
    - MongoDB
    - Redis
    - TrinoDB
* **Funções utilitárias:** Uma coleção de funções para tarefas comuns, como por exemplo:
    - Geração dinamica para listas em consultas
    - Geração de hash`s para pacote de dados, em base64, sha-256 e md5
    - Muito mais.
* **Design modular:** O pacote é organizado em módulos bem definidos, facilitando a manutenção e a expansão.
* **Documentação clara:** Documentação detalhada para cada função e classe, com exemplos práticos.

## Instalação
> Foi pensado em instalações opcionais dos módulos, instalando somente dependencias que serão realmente utilizadas.

Para instalar metamorfo, utilize o pip:

```bash
## Para instalar conectores
pip install metamorfo metamorfo[databases]
```

---
```python
from metamorfo.database import TrinoDB
from metamorfo.utility import list_in_query

# Conectando ao TrinoDB
db = TrinoDB(
    host='seu_host'
    , database='sua_base'
    , username='seu_usuario'
    , password='sua_senha'
    , source='sua_sorce'
)

# Executando uma consulta
resultado = db.execute_query(
    "SELECT current_timestamp, :valor as column_1"
    , params={'valor': 1}
)

# Função utilitária
# Gerar lista de parametros e valores em uma consulta com IN
data_formatada = metamorfo.formatar_data('2023-11-22', formato='%d/%m/%Y')
qry = 'SELECT * FROM sua_tabela WHERE seu_campo in (:lista_campo) and outro_campo = :outro_campo_valor'
prm = {
    'outro_campo_valor': 123
}
qry, prm = list_in_query(
    lista=[1,2,3,4,5,6]
    , nome_parametro="lista_campo"
    , query=qry
    , parametros=prm
)
resultado = db.execute_query(
    qry
    , params=prm
)
```

Também é possível de conectar usando variáveis de ambiente, porém dessa forma é possível se conectar a somente um banco de cada instância por vez.
### Utilizar as seguintes variáveis
#### Para TrinoDB
- METAMORFO_TRINO_USER
- METAMORFO_TRINO_PASSWORD
- METAMORFO_TRINO_HOST
- METAMORFO_TRINO_PORT
- METAMORFO_TRINO_SOURCE
#### Para Redis
- METAMORFO_REDIS_USER
- METAMORFO_REDIS_PASSWORD
- METAMORFO_REDIS_HOST
- METAMORFO_REDIS_PORT
#### Para MongoDB
- METAMORFO_MONGO_USER
- METAMORFO_MONGO_PASSWORD
- METAMORFO_MONGO_HOST
- METAMORFO_MONGO_PORT
#### Para PostgreSQL
- METAMORFO_POSTGRES_USER
- METAMORFO_POSTGRES_PASSWORD
- METAMORFO_POSTGRES_HOST
- METAMORFO_POSTGRES_PORT
- METAMORFO_POSTGRES_DB

---
## Contribuindo
Contribuições são bem-vindas! Para contribuir com metamorfo, siga estes passos:
1. Fork este repositório.
2. Crie um novo branch para sua feature.
3. Faça suas alterações e commit.
4. Envie um pull request.

### Licença
Este projeto está licenciado sob a licença MIT.

## Autores
[Guilherme Costa](mailto:guiijc96@gmail.com?subject=[Python]Metamorfo) - criador e mantenedor principal


## Funcionalidades Futuras
- Classe de conexão unificada: Implementação de uma classe base abstrata para conexões de banco de dados, utilizando o padrão de projeto Interface, para facilitar a adição de novos bancos de dados e a criação de adapters.
- Suporte a outros bancos de dados: Expansão para incluir suporte a outros sistemas de gerenciamento de bancos de dados como SQL Server, Oracle, MySQL, SQLite, DuckDB, MemGraph entre outros.