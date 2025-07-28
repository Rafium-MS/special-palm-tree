import pytest
pytest.skip("exemplo manual", allow_module_level=True)
import os
import tempfile

import database.db_manager as db
from modules.sugestoes import gerar_sugestoes_automaticas, listar_sugestoes

db_file = tempfile.NamedTemporaryFile(delete=False)
db_file.close()
db.DB_NAME = db_file.name
db.init_db(db.DB_NAME)
# Gerar automaticamente
novas = gerar_sugestoes_automaticas(dias_limite=90)
print("Sugestões geradas:")
for s in novas:
    print(s)

# Listar todas
for linha in listar_sugestoes():
    print(linha)
os.remove(db_file.name)
