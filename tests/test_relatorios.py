import pytest
pytest.skip("exemplo manual", allow_module_level=True)
import os
import tempfile
import importlib.util
import pytest

import database.db_manager as db
if importlib.util.find_spec("reportlab") is None:
    pytest.skip("reportlab not installed", allow_module_level=True)
from modules.relatorios import gerar_relatorio_mensal, exportar_relatorio_excel, relatorio_por_territorio

db_file = tempfile.NamedTemporaryFile(delete=False)
db_file.close()
db.DB_NAME = db_file.name
db.init_db(db.DB_NAME)

# Relatório mensal (visualização em terminal)
df = gerar_relatorio_mensal(mes=8, ano=2025)
print(df)

# Exportar para Excel
exportar_relatorio_excel(mes=8, ano=2025)

# Histórico por território específico
df2 = relatorio_por_territorio(territorio_id=3)
print(df2)
os.remove(db_file.name)
