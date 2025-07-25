import logging
import os
from datetime import datetime
from database.db_manager import get_connection

# Configuração do arquivo de log
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# 🔹 Log em arquivo
def log_info(msg):
    logging.info(msg)

def log_erro(msg):
    logging.error(msg)

def log_aviso(msg):
    logging.warning(msg)

# 🔸 Log no banco de dados também (tabela log_acoes)
def log_db(acao):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO log_acoes (acao) VALUES (?)", (acao,))
    conn.commit()
    conn.close()

# Combinar log em arquivo + banco
def log(msg, tipo="info"):
    if tipo == "erro":
        log_erro(msg)
    elif tipo == "aviso":
        log_aviso(msg)
    else:
        log_info(msg)
    log_db(msg)
