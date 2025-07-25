import os
import unittest

from database.db_manager import DB_NAME, init_db, get_connection
from modules.territorios import adicionar_territorio, agrupar_por_proximidade
from modules.ruas import adicionar_rua
from modules.numeros import adicionar_numero


class TestAgruparProximidade(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.path.exists(DB_NAME):
            os.remove(DB_NAME)
        init_db()
        adicionar_territorio('T-Group')
        conn = get_connection()
        cls.territorio_id = conn.cursor().execute(
            "SELECT id FROM territorios WHERE nome='T-Group'"
        ).fetchone()[0]
        adicionar_rua(cls.territorio_id, 'Rua P')
        cls.rua_id = conn.cursor().execute(
            "SELECT id FROM ruas WHERE territorio_id=?",
            (cls.territorio_id,),
        ).fetchone()[0]
        conn.close()
        for n in range(1, 26):
            adicionar_numero(cls.rua_id, str(n))

    def test_passo_dez(self):
        grupos = agrupar_por_proximidade(self.rua_id, passo=10)
        esperado = [
            ('1-10', list(range(1, 11))),
            ('11-20', list(range(11, 21))),
            ('21-30', list(range(21, 26))),
        ]
        self.assertEqual(grupos, esperado)

    def test_passo_quinze(self):
        grupos = agrupar_por_proximidade(self.rua_id, passo=15)
        esperado = [
            ('1-15', list(range(1, 16))),
            ('16-30', list(range(16, 26))),
        ]
        self.assertEqual(grupos, esperado)


if __name__ == '__main__':
    unittest.main()