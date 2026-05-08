import mysql.connector
from mysql.connector import Error, pooling

# Parâmetros de conexão — editados apenas aqui, usados em todo o sistema
_DB_PARAMS = {
    'host':               'localhost',
    'user':               'root',
    'password':           '',
    'database':           'imc_python',
    'charset':            'utf8mb4',
    'sql_mode':           ('STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,'
                           'ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION'),
    'time_zone':          '-03:00',   # Horário de Brasília
    'use_pure':           True,       # Python puro — compatível com todos os ambientes
    'connection_timeout': 10,         # desiste após 10s sem resposta
    'autocommit':         False,      # exige commit() explícito
}

# Pool criado uma única vez quando o módulo é carregado pela primeira vez.
# conn.close() devolve a conexão ao pool — não fecha fisicamente.
_pool = pooling.MySQLConnectionPool(
    pool_name='imc_pool',
    pool_size=5,           # conexões abertas permanentemente
    pool_reset_session=True,
    **_DB_PARAMS
)


def get_connection():
    """Retorna uma conexão do pool. Levanta Exception em caso de falha."""
    try:
        return _pool.get_connection()
    except Error as e:
        raise Exception(f'Não foi possível obter conexão do pool: {e}')


def execute_query(sql, params=None, fetch=False):
    conn = get_connection()
    cursor = None # Inicialize como None para o finally não quebrar se o cursor falhar
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())

        if fetch:
            return cursor.fetchall()
        else:
            conn.commit() # O SEGREDO ESTÁ AQUI
            return cursor.rowcount
    except Error as e:
        if conn:
            conn.rollback()
        raise Exception(f'Erro ao executar query: {e}')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def execute_one(sql, params=None):
    """
    Executa um SELECT e retorna apenas a primeira linha (ou None).
    Útil para buscar um registro por ID.
    """
    resultados = execute_query(sql, params, fetch=True)
    return resultados[0] if resultados else None

def verificar_criar_tabela():
    sql_teste = "SHOW TABLES LIKE 'calculos'"
    resultado = execute_query(sql_teste, fetch=True)

    if not resultado:
        print("Tabela de calculos não encontrada! Criando a tabela...")
        sql = '''
            CREATE TABLE IF NOT EXISTS calculos(
            id_calculo BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            peso DECIMAL(6,2) NOT NULL,
            altura DECIMAL(5,2) NOT NULL,

            criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            alterado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            deletado_em DATETIME NULL
        );
        '''
        resultado = execute_query(sql,fetch=True)
        print("Tabela criada com sucesso!!!")
    else:
        print('Tabela calculos já existe! Bora jogar...')
