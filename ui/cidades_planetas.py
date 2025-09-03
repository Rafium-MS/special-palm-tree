# -*- coding: utf-8 -*-
"""
 – Construtor de Cidades e Planetas (PyQt5)

Objetivo: protótipo de interface para criação de cidades (fantasia medieval) e planetas (sci-fi).

Como executar:
  pip install PyQt5
  python cidades_planetas.py
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict
import json
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSplitter, QListWidget, QListWidgetItem,
    QStackedWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QTextEdit, QComboBox, QPushButton, QSpinBox, QDoubleSpinBox, QGroupBox,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QFileDialog, QMessageBox
)

from core.economia.perfis import EconomiaPerfil, apply_rules

# ----------------------------- Estado -----------------------------
@dataclass
class Localidade:
    nome: str = ""
    tipo: str = "Cidade"  # Cidade, Vila, Capital, Planeta, Estação Espacial
    populacao: int = 1000
    bioma: str = "planície"
    clima: str = "temperado"
    recursos: List[str] = field(default_factory=lambda: ["água", "alimentos"])
    arquitetura: str = ""
    governo: str = ""
    economia: str = ""
    notas: str = ""

    distritos: List[Dict[str, str]] = field(default_factory=list)  # {nome, descricao}
    pontos_interesse: List[Dict[str, str]] = field(default_factory=list)  # {nome, descricao}
    perfil_economico: EconomiaPerfil = field(default_factory=EconomiaPerfil)

# ----------------------------- Páginas -----------------------------
class PageBasico(QWidget):
    def __init__(self, loc: Localidade, on_change):
        super().__init__()
        self.l = loc
        self.on_change = on_change
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Informações Básicas</h2>"))
        form = QFormLayout()
        self.ed_nome = QLineEdit(self.l.nome)
        self.cb_tipo = QComboBox(); self.cb_tipo.addItems(["Vila", "Cidade", "Capital", "Planeta", "Estação Espacial"]); self.cb_tipo.setCurrentText(self.l.tipo)
        self.sp_pop = QSpinBox(); self.sp_pop.setRange(0, 1000000000); self.sp_pop.setValue(self.l.populacao)
        self.cb_bioma = QComboBox(); self.cb_bioma.addItems(["planície", "floresta", "montanha", "deserto", "litoral", "tundra", "selva", "oceânico"]); self.cb_bioma.setCurrentText(self.l.bioma)
        self.cb_clima = QComboBox(); self.cb_clima.addItems(["temperado", "frio", "quente", "árido", "úmido"]); self.cb_clima.setCurrentText(self.l.clima)
        form.addRow("Nome:", self.ed_nome)
        form.addRow("Tipo:", self.cb_tipo)
        form.addRow("População:", self.sp_pop)
        form.addRow("Bioma:", self.cb_bioma)
        form.addRow("Clima:", self.cb_clima)
        layout.addLayout(form)
        btn = QPushButton("Salvar Básico")
        btn.clicked.connect(self.save)
        layout.addWidget(btn)
        layout.addStretch(1)

    def save(self):
        self.l.nome = self.ed_nome.text().strip()
        self.l.tipo = self.cb_tipo.currentText()
        self.l.populacao = self.sp_pop.value()
        self.l.bioma = self.cb_bioma.currentText()
        self.l.clima = self.cb_clima.currentText()
        self.on_change()

class PageSociedade(QWidget):
    def __init__(self, loc: Localidade, on_change):
        super().__init__()
        self.l = loc
        self.on_change = on_change
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Sociedade & Governo</h2>"))
        form = QFormLayout()
        self.ed_arq = QLineEdit(self.l.arquitetura)
        self.ed_gov = QLineEdit(self.l.governo)
        self.ed_eco = QLineEdit(self.l.economia)
        self.tx_notas = QTextEdit(self.l.notas)
        form.addRow("Arquitetura:", self.ed_arq)
        form.addRow("Governo:", self.ed_gov)
        form.addRow("Economia:", self.ed_eco)
        form.addRow("Notas:", self.tx_notas)
        layout.addLayout(form)
        btn = QPushButton("Salvar Sociedade")
        btn.clicked.connect(self.save)
        layout.addWidget(btn)
        layout.addStretch(1)

    def save(self):
        self.l.arquitetura = self.ed_arq.text().strip()
        self.l.governo = self.ed_gov.text().strip()
        self.l.economia = self.ed_eco.text().strip()
        self.l.notas = self.tx_notas.toPlainText().strip()
        self.on_change()

class PageDistritos(QWidget):
    def __init__(self, loc: Localidade, on_change):
        super().__init__()
        self.l = loc
        self.on_change = on_change
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Distritos</h2>"))
        self.tbl = QTableWidget(0, 2)
        self.tbl.setHorizontalHeaderLabels(["Distrito", "Descrição"])
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.setEditTriggers(QAbstractItemView.AllEditTriggers)
        layout.addWidget(self.tbl)
        btn_add = QPushButton("Adicionar Distrito")
        btn_del = QPushButton("Remover Selecionado")
        hl = QHBoxLayout(); hl.addWidget(btn_add); hl.addWidget(btn_del); hl.addStretch(1)
        layout.addLayout(hl)
        btn_save = QPushButton("Salvar Distritos")
        btn_save.clicked.connect(self.save)
        layout.addWidget(btn_save)
        layout.addStretch(1)
        btn_add.clicked.connect(self._add)
        btn_del.clicked.connect(self._del)
        self._load()

    def _load(self):
        self.tbl.setRowCount(0)
        for d in self.l.distritos:
            r = self.tbl.rowCount(); self.tbl.insertRow(r)
            self.tbl.setItem(r, 0, QTableWidgetItem(d.get("nome", "")))
            self.tbl.setItem(r, 1, QTableWidgetItem(d.get("descricao", "")))

    def _add(self):
        r = self.tbl.rowCount(); self.tbl.insertRow(r)
        self.tbl.setItem(r, 0, QTableWidgetItem("Novo Distrito"))
        self.tbl.setItem(r, 1, QTableWidgetItem("Descrição"))

    def _del(self):
        r = self.tbl.currentRow()
        if r >= 0:
            self.tbl.removeRow(r)

    def save(self):
        self.l.distritos = []
        for r in range(self.tbl.rowCount()):
            nome = self.tbl.item(r, 0).text() if self.tbl.item(r, 0) else ""
            desc = self.tbl.item(r, 1).text() if self.tbl.item(r, 1) else ""
            self.l.distritos.append({"nome": nome, "descricao": desc})
        self.on_change()

class PagePOI(QWidget):
    def __init__(self, loc: Localidade, on_change):
        super().__init__()
        self.l = loc
        self.on_change = on_change
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Pontos de Interesse</h2>"))
        self.tbl = QTableWidget(0, 2)
        self.tbl.setHorizontalHeaderLabels(["Nome", "Descrição"])
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.setEditTriggers(QAbstractItemView.AllEditTriggers)
        layout.addWidget(self.tbl)
        btn_add = QPushButton("Adicionar POI")
        btn_del = QPushButton("Remover Selecionado")
        hl = QHBoxLayout(); hl.addWidget(btn_add); hl.addWidget(btn_del); hl.addStretch(1)
        layout.addLayout(hl)
        btn_save = QPushButton("Salvar POIs")
        btn_save.clicked.connect(self.save)
        layout.addWidget(btn_save)
        layout.addStretch(1)
        btn_add.clicked.connect(self._add)
        btn_del.clicked.connect(self._del)
        self._load()

    def _load(self):
        self.tbl.setRowCount(0)
        for d in self.l.pontos_interesse:
            r = self.tbl.rowCount(); self.tbl.insertRow(r)
            self.tbl.setItem(r, 0, QTableWidgetItem(d.get("nome", "")))
            self.tbl.setItem(r, 1, QTableWidgetItem(d.get("descricao", "")))

    def _add(self):
        r = self.tbl.rowCount(); self.tbl.insertRow(r)
        self.tbl.setItem(r, 0, QTableWidgetItem("Novo Ponto"))
        self.tbl.setItem(r, 1, QTableWidgetItem("Descrição"))

    def _del(self):
        r = self.tbl.currentRow()
        if r >= 0:
            self.tbl.removeRow(r)

    def save(self):
        self.l.pontos_interesse = []
        for r in range(self.tbl.rowCount()):
            nome = self.tbl.item(r, 0).text() if self.tbl.item(r, 0) else ""
            desc = self.tbl.item(r, 1).text() if self.tbl.item(r, 1) else ""
            self.l.pontos_interesse.append({"nome": nome, "descricao": desc})
        self.on_change()

class PageResumo(QWidget):
    def __init__(self, loc: Localidade):
        super().__init__()
        self.l = loc
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Resumo</h2>"))
        self.tx = QTextEdit(); self.tx.setReadOnly(True)
        layout.addWidget(self.tx)
        self.refresh()

    def refresh(self):
        data = asdict(self.l)
        data["perfil_economico"] = asdict(self.l.perfil_economico)
        self.tx.setPlainText(json.dumps(data, indent=2, ensure_ascii=False))

# ----------------------------- Janela Principal -----------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Construtor de Cidades e Planetas")
        self.resize(1200, 720)

        self.localidades: List[Localidade] = []
        self.idx_atual = -1

        splitter = QSplitter(self)

        left = QWidget(); vleft = QVBoxLayout(left)
        self.lst = QListWidget()
        hl = QHBoxLayout()
        self.btn_new = QPushButton("Nova")
        self.btn_dup = QPushButton("Duplicar")
        self.btn_del = QPushButton("Excluir")
        hl.addWidget(self.btn_new); hl.addWidget(self.btn_dup); hl.addWidget(self.btn_del)
        vleft.addWidget(QLabel("Localidades"))
        vleft.addWidget(self.lst, 1)
        vleft.addLayout(hl)

        self.stack = QStackedWidget()
        self.lbl_empty = QLabel("<i>Crie ou selecione uma localidade…</i>")
        self.lbl_empty.setAlignment(Qt.AlignCenter)
        self.stack.addWidget(self.lbl_empty)

        splitter.addWidget(left)
        splitter.addWidget(self.stack)
        splitter.setStretchFactor(1, 1)
        self.setCentralWidget(splitter)

        self.btn_new.clicked.connect(self._nova)
        self.btn_dup.clicked.connect(self._duplicar)
        self.btn_del.clicked.connect(self._excluir)
        self.lst.currentRowChanged.connect(self._trocar)

        # menu
        self._build_menu()

    def _nova(self):
        l = Localidade(nome=f"Localidade {len(self.localidades)+1}")
        self.localidades.append(l)
        self._refresh_lista()
        self.lst.setCurrentRow(len(self.localidades)-1)

    def _duplicar(self):
        i = self.lst.currentRow()
        if i < 0: return
        base = self.localidades[i]
        copia = json.loads(json.dumps(asdict(base)))
        novo = Localidade(**copia)
        novo.nome = base.nome + " (cópia)"
        self.localidades.append(novo)
        self._refresh_lista()
        self.lst.setCurrentRow(len(self.localidades)-1)

    def _excluir(self):
        i = self.lst.currentRow()
        if i < 0: return
        del self.localidades[i]
        self._refresh_lista()
        self.stack.setCurrentIndex(0)

    def _refresh_lista(self):
        self.lst.clear()
        for l in self.localidades:
            self.lst.addItem(l.nome)

    def _trocar(self, idx):
        if idx < 0 or idx >= len(self.localidades):
            self.stack.setCurrentIndex(0)
            return
        self.idx_atual = idx
        l = self.localidades[idx]
        self._montar_paginas(l)

    def _montar_paginas(self, l: Localidade):
        while self.stack.count() > 1:
            w = self.stack.widget(1)
            self.stack.removeWidget(w)
            w.deleteLater()
        self.page_basico = PageBasico(l, self._on_change)
        self.page_soc = PageSociedade(l, self._on_change)
        self.page_dis = PageDistritos(l, self._on_change)
        self.page_poi = PagePOI(l, self._on_change)
        l.perfil_economico = apply_rules(l)
        self.page_res = PageResumo(l)
        for w in [self.page_basico, self.page_soc, self.page_dis, self.page_poi, self.page_res]:
            wrap = QWidget(); v = QVBoxLayout(wrap); v.setContentsMargins(16,16,16,16); v.addWidget(w)
            self.stack.addWidget(wrap)
        self.stack.setCurrentIndex(1)

    def _on_change(self):
        if self.idx_atual >= 0:
            l = self.localidades[self.idx_atual]
            l.perfil_economico = apply_rules(l)
            self.page_res.refresh()

    def _build_menu(self):
        m = self.menuBar().addMenu("Arquivo")
        act_exp = m.addAction("Exportar localidade (JSON)")
        act_exp.triggered.connect(self._exportar)
        act_imp = m.addAction("Importar localidade (JSON)")
        act_imp.triggered.connect(self._importar)
        m.addSeparator()
        act_all = m.addAction("Exportar todas (JSON)")
        act_all.triggered.connect(self._exportar_todas)

    def _exportar(self):
        i = self.idx_atual
        if i < 0:
            return
        l = self.localidades[i]
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Localidade", f"{l.nome}.json", "JSON (*.json)")
        if not path:
            return
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(asdict(l), f, ensure_ascii=False, indent=2)

    def _importar(self):
        path, _ = QFileDialog.getOpenFileName(self, "Importar Localidade", "", "JSON (*.json)")
        if not path:
            return
        try:
            data = json.loads(open(path, 'r', encoding='utf-8').read())
            l = Localidade(**data)
            self.localidades.append(l)
            self._refresh_lista()
        except Exception as err:
            QMessageBox.critical(self, "Erro", f"Falha ao importar: {err}")

    def _exportar_todas(self):
        if not self.localidades:
            QMessageBox.information(self, "Aviso", "Nenhuma localidade para exportar.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Conjunto", "localidades.json", "JSON (*.json)")
        if not path:
            return
        data = [asdict(l) for l in self.localidades]
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

# ----------------------------- Execução -----------------------------
def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
