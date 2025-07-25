# gui/notificacoes.py
from PyQt5.QtWidgets import QMessageBox

def sucesso(parent, texto):
    QMessageBox.information(parent, "✅ Sucesso", texto)

def erro(parent, texto):
    QMessageBox.critical(parent, "❌ Erro", texto)

def aviso(parent, texto):
    QMessageBox.warning(parent, "⚠️ Atenção", texto)
