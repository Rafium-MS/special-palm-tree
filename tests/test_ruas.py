from database.db_manager import init_db
init_db()
from database.db_manager import get_connection
from modules.ruas import adicionar_rua, listar_ruas, remover_rua
from modules.territorios import adicionar_territorio

# Insere território e rua
adicionar_territorio('T1')
conn = get_connection()
territorio_id = conn.cursor().execute("SELECT id FROM territorios WHERE nome='T1'").fetchone()[0]
conn.close()

adicionar_rua(territorio_id, 'Rua A')
print(listar_ruas(territorio_id))
rua_id = listar_ruas(territorio_id)[0][0]
remover_rua(rua_id)