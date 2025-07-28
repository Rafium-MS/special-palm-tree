import pytest
pytest.skip("exemplo manual", allow_module_level=True)
import os
import tempfile

import database.db_manager as db
from modules.designacoes import criar_designacao, listar_designacoes, atualizar_designacao, remover_designacao

db_file = tempfile.NamedTemporaryFile(delete=False)
db_file.close()
db.DB_NAME = db_file.name
db.init_db(db.DB_NAME)

# Criar
criar_designacao(territorio_id=2, saida_id=5, data_inicio="2025-08-01", data_fim="2025-08-30")

# Listar
for d in listar_designacoes():
    print(d)

# Atualizar
atualizar_designacao(1, status="concluída")

# Remover
remover_designacao(1)
os.remove(db_file.name)
