import unittest
from database.db_manager import init_db, get_connection
from modules.territorios import adicionar_territorio, obter_territorio_completo
from modules.ruas import adicionar_rua
from modules.numeros import adicionar_numero

class TestTerritorioCompleto(unittest.TestCase):
    def setUp(self):
        init_db()
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM numeros')
        cur.execute('DELETE FROM ruas')
        cur.execute('DELETE FROM territorios')
        conn.commit()
        conn.close()

        adicionar_territorio('Territorio Teste')
        conn = get_connection()
        self.territorio_id = conn.cursor().execute(
            "SELECT id FROM territorios WHERE nome=?",
            ('Territorio Teste',)
        ).fetchone()[0]
        conn.close()

        adicionar_rua(self.territorio_id, 'Rua X')
        conn = get_connection()
        self.rua_id = conn.cursor().execute(
            "SELECT id FROM ruas WHERE territorio_id=?",
            (self.territorio_id,)
        ).fetchone()[0]
        conn.close()

        adicionar_numero(self.rua_id, '1')
        adicionar_numero(self.rua_id, '2')

    def test_hierarquia_completa(self):
        dados = obter_territorio_completo(self.territorio_id)
        self.assertIsNotNone(dados)
        self.assertEqual(dados['id'], self.territorio_id)
        self.assertEqual(len(dados['ruas']), 1)
        rua = dados['ruas'][0]
        self.assertEqual(rua['nome'], 'Rua X')
        numeros = sorted(n['numero'] for n in rua['numeros'])
        self.assertListEqual(numeros, ['1', '2'])

if __name__ == '__main__':
    unittest.main()