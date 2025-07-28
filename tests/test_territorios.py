import os
import tempfile
import unittest
import database.db_manager as db
from database.db_manager import init_db as _init_db, get_connection as _get_connection

def init_db():
    _init_db(db.DB_NAME)

def get_connection():
    return _get_connection(db.DB_NAME)
from modules.territorios import (
    adicionar_territorio,
    obter_territorio_completo,
    atualizar_territorio,
    remover_completo
)
from modules.ruas import adicionar_rua
from modules.numeros import adicionar_numero

class TestTerritorioCompleto(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.NamedTemporaryFile(delete=False)
        self.temp.close()
        db.DB_NAME = self.temp.name
        db.init_db(db.DB_NAME)
        conn = db.get_connection(db.DB_NAME)
        cur = conn.cursor()
        cur.execute('DELETE FROM numeros')
        cur.execute('DELETE FROM ruas')
        cur.execute('DELETE FROM territorios')
        conn.commit()
        conn.close()

        adicionar_territorio('Territorio Teste')
        conn = db.get_connection(db.DB_NAME)
        self.territorio_id = conn.cursor().execute(
            "SELECT id FROM territorios WHERE nome=?",
            ('Territorio Teste',)
        ).fetchone()[0]
        conn.close()

        adicionar_rua(self.territorio_id, 'Rua X')
        conn = db.get_connection(db.DB_NAME)
        self.rua_id = conn.cursor().execute(
            "SELECT id FROM ruas WHERE territorio_id=?",
            (self.territorio_id,)
        ).fetchone()[0]
        conn.close()

        adicionar_numero(self.rua_id, '1')
        adicionar_numero(self.rua_id, '2')
    def tearDown(self):
        if os.path.exists(self.temp.name):
            os.remove(self.temp.name)

    def test_hierarquia_completa(self):
        dados = obter_territorio_completo(self.territorio_id)
        self.assertIsNotNone(dados)
        self.assertEqual(dados['id'], self.territorio_id)
        self.assertEqual(len(dados['ruas']), 1)
        rua = dados['ruas'][0]
        self.assertEqual(rua['nome'], 'Rua X')
        numeros = sorted(n['numero'] for n in rua['numeros'])
        self.assertListEqual(numeros, ['1', '2'])

class TestAtualizarTerritorio(unittest.TestCase):
    def setUp(self):
        init_db()
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM territorios')
        conn.commit()
        conn.close()

        adicionar_territorio('T1', url='u1', status='novo', observacoes='obs')
        conn = get_connection()
        self.tid = conn.cursor().execute(
            "SELECT id FROM territorios WHERE nome=?",
            ('T1',)
        ).fetchone()[0]
        conn.close()

    def test_apenas_campos_permitidos(self):
        atualizar_territorio(self.tid, nome='Novo', foo='bar')
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT nome, url, status, observacoes FROM territorios WHERE id=?",
            (self.tid,)
        )
        row = cur.fetchone()
        conn.close()
        self.assertEqual(row, ('Novo', 'u1', 'novo', 'obs'))

    def test_sem_campos_validos(self):
        atualizar_territorio(self.tid, invalido='x')
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT nome FROM territorios WHERE id=?", (self.tid,))
        nome = cur.fetchone()[0]
        conn.close()
        self.assertEqual(nome, 'T1')
class TestRemoverCompleto(unittest.TestCase):
    def setUp(self):
        init_db()
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM numeros')
        cur.execute('DELETE FROM ruas')
        cur.execute('DELETE FROM territorios')
        conn.commit()
        conn.close()

        adicionar_territorio('T-Del')
        conn = get_connection()
        self.territorio_id = conn.cursor().execute(
            "SELECT id FROM territorios WHERE nome=?",
            ('T-Del',),
        ).fetchone()[0]
        conn.close()

        adicionar_rua(self.territorio_id, 'Rua Z')
        conn = get_connection()
        self.rua_id = conn.cursor().execute(
            "SELECT id FROM ruas WHERE territorio_id=?",
            (self.territorio_id,),
        ).fetchone()[0]
        conn.close()

        adicionar_numero(self.rua_id, '1')

    def test_remover_completo(self):
        remover_completo(self.territorio_id)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM territorios WHERE id=?', (self.territorio_id,))
        t_count = cur.fetchone()[0]
        cur.execute('SELECT COUNT(*) FROM ruas WHERE territorio_id=?', (self.territorio_id,))
        r_count = cur.fetchone()[0]
        cur.execute('SELECT COUNT(*) FROM numeros WHERE rua_id=?', (self.rua_id,))
        n_count = cur.fetchone()[0]
        conn.close()
        self.assertEqual(t_count, 0)
        self.assertEqual(r_count, 0)
        self.assertEqual(n_count, 0)

if __name__ == '__main__':
    unittest.main()