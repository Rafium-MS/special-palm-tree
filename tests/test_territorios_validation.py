import unittest
from database.db_manager import init_db, get_connection
from modules.territorios import (
    adicionar_territorio,
    atualizar_territorio,
    MAX_NOME_LENGTH,
    MAX_OBSERVACOES_LENGTH,
)


class TestTerritorioValidation(unittest.TestCase):
    def setUp(self):
        init_db()
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM territorios')
        conn.commit()
        conn.close()

    def test_nome_vazio(self):
        with self.assertRaises(ValueError):
            adicionar_territorio('')

    def test_status_invalido(self):
        with self.assertRaises(ValueError):
            adicionar_territorio('Teste', status='invalido')

    def test_nome_muito_longo(self):
        nome = 'x' * (MAX_NOME_LENGTH + 1)
        with self.assertRaises(ValueError):
            adicionar_territorio(nome)

    def test_observacoes_muito_longa(self):
        obs = 'x' * (MAX_OBSERVACOES_LENGTH + 1)
        with self.assertRaises(ValueError):
            adicionar_territorio('Teste', observacoes=obs)

    def test_atualizar_com_status_invalido(self):
        adicionar_territorio('Valido')
        conn = get_connection()
        territorio_id = conn.cursor().execute(
            "SELECT id FROM territorios WHERE nome=?",
            ('Valido',)
        ).fetchone()[0]
        conn.close()
        with self.assertRaises(ValueError):
            atualizar_territorio(territorio_id, status='errado')


if __name__ == '__main__':
    unittest.main()