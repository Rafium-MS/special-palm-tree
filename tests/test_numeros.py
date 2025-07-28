import pytest
pytest.skip("exemplo manual", allow_module_level=True)
import os
import tempfile

import database.db_manager as db
db_file = tempfile.NamedTemporaryFile(delete=False)
db_file.close()
db.DB_NAME = db_file.name
db.init_db(db.DB_NAME)

from database.db_manager import get_connection
from modules.ruas import adicionar_rua
from modules.numeros import adicionar_numero, listar_numeros, remover_numero
from modules.territorios import adicionar_territorio

# Cria território e rua
adicionar_territorio('T2')
conn = get_connection()
territorio_id = conn.cursor().execute("SELECT id FROM territorios WHERE nome='T2'").fetchone()[0]
adicionar_rua(territorio_id, 'Rua B')
rua_id = conn.cursor().execute("SELECT id FROM ruas WHERE territorio_id=?", (territorio_id,)).fetchone()[0]
conn.close()

adicionar_numero(rua_id, '10', '2024-01-01')
print(listar_numeros(rua_id))
numero_id = listar_numeros(rua_id)[0][0]
remover_numero(numero_id)
os.remove(db_file.name)