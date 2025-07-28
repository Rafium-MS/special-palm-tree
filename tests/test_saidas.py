import pytest
pytest.skip("exemplo manual", allow_module_level=True)
import os
import tempfile

import database.db_manager as db
from modules.saidas import criar_saida, listar_saidas, atualizar_saida, remover_saida

db_file = tempfile.NamedTemporaryFile(delete=False)
db_file.close()
db.DB_NAME = db_file.name
db.init_db(db.DB_NAME)

# Criar uma saída
criar_saida("2025-08-01", "Grupo 1", "João da Silva", dirigente_fixo=True)

# Listar saídas
for saida in listar_saidas():
    print(saida)

# Atualizar
atualizar_saida(1, dirigente="Maria Oliveira")

# Remover
remover_saida(1)
os.remove(db_file.name)
