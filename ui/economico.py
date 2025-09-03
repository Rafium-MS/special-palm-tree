# -*- coding: utf-8 -*-
"""
Wireframe – Construtor Econômico (PyQt5)

Objetivo: protótipo navegável para estruturar economias de cidades/reinos/planetas
(fantasia e sci‑fi). Inclui templates, eventos econômicos e exportação em JSON.

Como executar:
  pip install PyQt5
  python economico_wireframe.py
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict
import json
import sys
import re

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSplitter, QListWidget, QListWidgetItem,
    QStackedWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QTextEdit, QComboBox, QPushButton, QSpinBox, QDoubleSpinBox, QGroupBox,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QFileDialog, QMessageBox,
    QCheckBox, QInputDialog
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# ----------------------------- Estado -----------------------------
@dataclass
class Economia:
    nome: str = ""
    escopo: str = "Cidade"  # Cidade, Reino, Império, Estação, Planeta
    moeda: str = "moedas de prata"  # ou créditos/energia
    # parâmetros macro
    populacao: int = 10000
    renda_per_capita: float = 1.0  # renda base (índice)
    taxa_imposto: float = 10.0     # % média
    tarifa_comercial: float = 5.0  # % média
    inflacao: float = 2.0          # % anual

    # listas
    recursos: List[Dict[str, str]] = field(default_factory=list)   # {recurso, abundancia, notas}
    producao: List[Dict[str, str]] = field(default_factory=list)   # {bem, quantidade, unidade}
    rotas: List[Dict[str, str]] = field(default_factory=list)      # {origem, destino, bem, volume}
    setores: List[Dict[str, str]] = field(default_factory=list)    # {setor, participacao%}

    # indicadores derivados (placeholders simples)
    eventos: List[str] = field(default_factory=list)

# ----------------------------- Templates -----------------------------
TEMPLATES_ECON: Dict[str, Dict] = {
    "Cidade Portuária (Fantasia)": {
        "escopo": "Cidade",
        "moeda": "moedas de prata",
        "populacao": 12000,
        "renda_per_capita": 1.2,
        "taxa_imposto": 8.0,
        "tarifa_comercial": 3.0,
        "inflacao": 2.0,
        "recursos": [
            {"recurso": "peixe", "abundancia": "alta", "notas": "sazonal"},
            {"recurso": "madeira", "abundancia": "média", "notas": "carpintaria naval"}
        ],
        "producao": [
            {"bem": "sal", "quantidade": "40", "unidade": "ton/ano"},
            {"bem": "embarcações", "quantidade": "15", "unidade": "un/ano"}
        ],
        "rotas": [
            {"origem": "Cidade Portuária", "destino": "Capital", "bem": "peixe salgado", "volume": "20 ton/mês"}
        ],
        "setores": [
            {"setor": "Comércio", "participacao%": "45"},
            {"setor": "Pesca", "participacao%": "25"},
            {"setor": "Artesanato", "participacao%": "20"}
        ],
    },
    "Colônia de Mineração (Sci‑Fi)": {
        "escopo": "Estação",
        "moeda": "créditos",
        "populacao": 20000,
        "renda_per_capita": 1.5,
        "taxa_imposto": 12.0,
        "tarifa_comercial": 2.0,
        "inflacao": 3.5,
        "recursos": [
            {"recurso": "hélio-3", "abundancia": "alta", "notas": "combustível de fusão"},
            {"recurso": "gelo", "abundancia": "média", "notas": "água e propelente"}
        ],
        "producao": [
            {"bem": "isótopos", "quantidade": "500", "unidade": "kg/mês"}
        ],
        "rotas": [
            {"origem": "Colônia", "destino": "Mercado Orbital", "bem": "hélio-3", "volume": "450 kg/mês"}
        ],
        "setores": [
            {"setor": "Mineração", "participacao%": "60"},
            {"setor": "Serviços", "participacao%": "30"}
        ],
    },
    "Reino Agrário": {
        "escopo": "Reino",
        "moeda": "denários",
        "populacao": 150000,
        "renda_per_capita": 0.8,
        "taxa_imposto": 9.0,
        "tarifa_comercial": 5.0,
        "inflacao": 1.0,
        "recursos": [
            {"recurso": "trigo", "abundancia": "alta", "notas": "silos reais"},
            {"recurso": "gado", "abundancia": "média", "notas": "feiras sazonais"}
        ],
        "producao": [
            {"bem": "grãos", "quantidade": "10.000", "unidade": "ton/ano"}
        ],
        "rotas": [
            {"origem": "Planície", "destino": "Capitais", "bem": "grãos", "volume": "800 ton/ano"}
        ],
        "setores": [
            {"setor": "Agricultura", "participacao%": "65"},
            {"setor": "Comércio", "participacao%": "20"}
        ],
    },
}

# ----------------------------- Páginas -----------------------------
class PageBasico(QWidget):
    def __init__(self, eco: Economia, on_change):
        super().__init__()
        self.e = eco
        self.on_change = on_change
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Parâmetros Básicos</h2>"))
        form = QFormLayout()
        self.ed_nome = QLineEdit(self.e.nome)
        self.cb_escopo = QComboBox(); self.cb_escopo.addItems(["Cidade", "Reino", "Império", "Estação", "Planeta"]); self.cb_escopo.setCurrentText(self.e.escopo)
        self.ed_moeda = QLineEdit(self.e.moeda)
        self.sp_pop = QSpinBox(); self.sp_pop.setRange(0, 2000000000); self.sp_pop.setValue(self.e.populacao)
        self.dbl_renda = QDoubleSpinBox(); self.dbl_renda.setRange(0.1, 100.0); self.dbl_renda.setSingleStep(0.1); self.dbl_renda.setValue(self.e.renda_per_capita)
        self.dbl_taxa = QDoubleSpinBox(); self.dbl_taxa.setRange(0.0, 95.0); self.dbl_taxa.setSuffix(" %"); self.dbl_taxa.setValue(self.e.taxa_imposto)
        self.dbl_tarifa = QDoubleSpinBox(); self.dbl_tarifa.setRange(0.0, 95.0); self.dbl_tarifa.setSuffix(" %"); self.dbl_tarifa.setValue(self.e.tarifa_comercial)
        self.dbl_infl = QDoubleSpinBox(); self.dbl_infl.setRange(-50.0, 500.0); self.dbl_infl.setSuffix(" %"); self.dbl_infl.setValue(self.e.inflacao)
        form.addRow("Nome:", self.ed_nome)
        form.addRow("Escopo:", self.cb_escopo)
        form.addRow("Moeda:", self.ed_moeda)
        form.addRow("População:", self.sp_pop)
        form.addRow("Renda per capita (índice):", self.dbl_renda)
        form.addRow("Taxa média de imposto:", self.dbl_taxa)
        form.addRow("Tarifa comercial média:", self.dbl_tarifa)
        form.addRow("Inflação anual:", self.dbl_infl)
        layout.addLayout(form)
        btn = QPushButton("Salvar Básico")
        btn.clicked.connect(self.save)
        layout.addWidget(btn)
        layout.addStretch(1)

        # Atualiza indicadores imediatamente ao mudar impostos ou tarifas
        self.dbl_taxa.valueChanged.connect(self._autosave)
        self.dbl_tarifa.valueChanged.connect(self._autosave)

    def _autosave(self):
        """Atualiza o estado e dispara a atualização do resumo."""
        self._update_state()
        self.on_change()

    def save(self):
        self._update_state()
        self.on_change()

    def _update_state(self):
        self.e.nome = self.ed_nome.text().strip()
        self.e.escopo = self.cb_escopo.currentText()
        self.e.moeda = self.ed_moeda.text().strip()
        self.e.populacao = self.sp_pop.value()
        self.e.renda_per_capita = self.dbl_renda.value()
        self.e.taxa_imposto = self.dbl_taxa.value()
        self.e.tarifa_comercial = self.dbl_tarifa.value()
        self.e.inflacao = self.dbl_infl.value()

class _TableEdit(QWidget):
    """Componente simples para editar listas de dict em tabela."""
    def __init__(self, header: List[str], rows: List[Dict[str, str]]):
        super().__init__()
        self.header = header
        self.rows = rows
        v = QVBoxLayout(self)
        self.tbl = QTableWidget(0, len(header))
        self.tbl.setHorizontalHeaderLabels(header)
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.setEditTriggers(QAbstractItemView.AllEditTriggers)
        v.addWidget(self.tbl)
        hl = QHBoxLayout();
        self.btn_add = QPushButton("Adicionar")
        self.btn_del = QPushButton("Remover")
        hl.addWidget(self.btn_add); hl.addWidget(self.btn_del); hl.addStretch(1)
        v.addLayout(hl)
        self.btn_add.clicked.connect(self._add)
        self.btn_del.clicked.connect(self._del)
        self._load()

    def _load(self):
        self.tbl.setRowCount(0)
        for rdata in self.rows:
            r = self.tbl.rowCount(); self.tbl.insertRow(r)
            for c, key in enumerate(self.header):
                self.tbl.setItem(r, c, QTableWidgetItem(rdata.get(key.lower(), "")))

    def _add(self):
        r = self.tbl.rowCount(); self.tbl.insertRow(r)
        for c in range(len(self.header)):
            self.tbl.setItem(r, c, QTableWidgetItem(""))

    def _del(self):
        r = self.tbl.currentRow()
        if r >= 0:
            self.tbl.removeRow(r)

    def to_list(self) -> List[Dict[str, str]]:
        out = []
        for r in range(self.tbl.rowCount()):
            item = {}
            for c, key in enumerate(self.header):
                val = self.tbl.item(r, c).text() if self.tbl.item(r, c) else ""
                item[key.lower()] = val
            out.append(item)
        return out

    def refresh(self):
        """Recarrega os dados atuais na tabela."""
        self._load()

class PageRecursosProducao(QWidget):
    def __init__(self, eco: Economia, on_change):
        super().__init__()
        self.e = eco
        self.on_change = on_change
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Recursos & Produção</h2>"))
        # recursos
        box_r = QGroupBox("Recursos")
        v1 = QVBoxLayout(box_r)
        self.tab_rec = _TableEdit(["Recurso", "Abundancia", "Notas"], self.e.recursos)
        v1.addWidget(self.tab_rec)
        # produção
        box_p = QGroupBox("Produção")
        v2 = QVBoxLayout(box_p)
        self.tab_prod = _TableEdit(["Bem", "Quantidade", "Unidade"], self.e.producao)
        v2.addWidget(self.tab_prod)
        layout.addWidget(box_r)
        layout.addWidget(box_p)
        btn = QPushButton("Salvar Recursos & Produção")
        btn.clicked.connect(self.save)
        layout.addWidget(btn)
        layout.addStretch(1)

    def save(self):
        self.e.recursos = self.tab_rec.to_list()
        self.e.producao = self.tab_prod.to_list()
        self.on_change()

    def refresh(self):
        """Atualiza as tabelas com os dados atuais da economia."""
        self.tab_rec.rows = self.e.recursos
        self.tab_rec.refresh()
        self.tab_prod.rows = self.e.producao
        self.tab_prod.refresh()

class PageRotas(QWidget):
    def __init__(self, eco: Economia, on_change):
        super().__init__()
        self.e = eco
        self.on_change = on_change
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Rotas Comerciais</h2>"))
        self.tab = _TableEdit(["Origem", "Destino", "Bem", "Volume"], self.e.rotas)
        layout.addWidget(self.tab)
        btn = QPushButton("Salvar Rotas")
        btn.clicked.connect(self.save)
        layout.addWidget(btn)
        layout.addStretch(1)

    def save(self):
        self.e.rotas = self.tab.to_list()
        self.on_change()

class PagePoliticas(QWidget):
    def __init__(self, eco: Economia, on_change):
        super().__init__()
        self.e = eco
        self.on_change = on_change
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Políticas Fiscais & Setores</h2>"))
        # fiscais
        box_f = QGroupBox("Fiscais")
        form = QFormLayout(box_f)
        self.dbl_taxa = QDoubleSpinBox(); self.dbl_taxa.setRange(0.0, 95.0); self.dbl_taxa.setSuffix(" %"); self.dbl_taxa.setValue(self.e.taxa_imposto)
        self.dbl_tar = QDoubleSpinBox(); self.dbl_tar.setRange(0.0, 95.0); self.dbl_tar.setSuffix(" %"); self.dbl_tar.setValue(self.e.tarifa_comercial)
        self.dbl_inf = QDoubleSpinBox(); self.dbl_inf.setRange(-50.0, 500.0); self.dbl_inf.setSuffix(" %"); self.dbl_inf.setValue(self.e.inflacao)
        form.addRow("Imposto médio:", self.dbl_taxa)
        form.addRow("Tarifa média:", self.dbl_tar)
        form.addRow("Inflação alvo:", self.dbl_inf)
        # setores
        box_s = QGroupBox("Setores Econômicos (% participação)")
        v = QVBoxLayout(box_s)
        self.tab_set = _TableEdit(["Setor", "Participacao%"], self.e.setores)
        v.addWidget(self.tab_set)
        layout.addWidget(box_f)
        layout.addWidget(box_s)
        btn = QPushButton("Salvar Políticas & Setores")
        btn.clicked.connect(self.save)
        layout.addWidget(btn)
        layout.addStretch(1)

    def save(self):
        self.e.taxa_imposto = self.dbl_taxa.value()
        self.e.tarifa_comercial = self.dbl_tar.value()
        self.e.inflacao = self.dbl_inf.value()
        self.e.setores = self.tab_set.to_list()
        self.on_change()

class PageEventos(QWidget):
    def __init__(self, eco: Economia, on_change):
        super().__init__()
        self.e = eco
        self.on_change = on_change
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Eventos Econômicos</h2>"))
        layout.addWidget(self._row("Embargo (queda no comércio)", self.apply_embargo))
        layout.addWidget(self._row("Boom de Colheita (alta agrícola)", self.apply_boom))
        layout.addWidget(self._row("Recessão (queda geral)", self.apply_recessao))
        layout.addStretch(1)

    def _row(self, txt, slot):
        hl = QHBoxLayout()
        hl.addWidget(QLabel(txt))
        btn = QPushButton("Aplicar")
        btn.clicked.connect(slot)
        w = QWidget(); w.setLayout(hl)
        hl.addStretch(1); hl.addWidget(btn)
        return w

    def apply_embargo(self):
        self.e.tarifa_comercial = min(95.0, self.e.tarifa_comercial + 10)
        self.e.eventos.append("Embargo")
        self.on_change()

    def apply_boom(self):
        self.e.renda_per_capita *= 1.05
        self.e.eventos.append("Boom agrícola")
        self.on_change()

    def apply_recessao(self):
        self.e.renda_per_capita *= 0.95
        self.e.inflacao = max(-50.0, self.e.inflacao - 1.0)
        self.e.eventos.append("Recessão")
        self.on_change()

class PageResumo(QWidget):
    def __init__(self, eco: Economia):
        super().__init__()
        self.e = eco
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Resumo & Indicadores</h2>"))
        self.tx = QTextEdit(); self.tx.setReadOnly(True)
        layout.addWidget(self.tx)
        self.fig = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)
        self.refresh()

    def _calc_indicadores(self) -> Dict[str, float]:
        e = self.e
        # Cálculos simples (placeholders):
        pib = e.populacao * e.renda_per_capita
        arrec = pib * (e.taxa_imposto/100.0)

        def _parse_volume(txt: str) -> float:
            m = re.search(r"-?\d+(?:[.,]\d+)?", txt)
            return float(m.group(0).replace(',', '.')) if m else 0.0

        balanca = sum(_parse_volume(r.get('volume', '0')) for r in e.rotas)
        participacao = {}
        for s in e.setores:
            try:
                participacao[s.get('setor', '')] = float(s.get('participacao%', '0'))
            except ValueError:
                continue
        return {
            "PIB (índice)": round(pib, 2),
            "Arrecadação (índice)": round(arrec, 2),
            "Balança Comercial (índice)": round(balanca, 2),
            "Participação Setorial (%)": participacao,
        }

    def refresh(self):
        data = asdict(self.e)
        data["indicadores"] = self._calc_indicadores()
        self.tx.setPlainText(json.dumps(data, indent=2, ensure_ascii=False))
        self._plot_prod_consumo()

    def _plot_prod_consumo(self) -> None:
        """Exibe gráfico simples produção × consumo usando Matplotlib."""
        ax = self.fig.clear().add_subplot(111)

        def _parse(txt: str) -> float:
            m = re.search(r"-?\d+(?:[.,]\d+)?", txt)
            return float(m.group(0).replace(',', '.')) if m else 0.0

        prod: Dict[str, float] = {}
        for p in self.e.producao:
            try:
                prod[p.get("bem", "")] = _parse(str(p.get("quantidade", "0")))
            except ValueError:
                continue

        cons: Dict[str, float] = {}
        for r in self.e.rotas:
            b = r.get("bem", "")
            cons[b] = cons.get(b, 0.0) + _parse(r.get("volume", "0"))

        bens = sorted(set(prod) | set(cons))
        if not bens:
            self.canvas.draw_idle()
            return

        for i, b in enumerate(bens):
            ax.bar(i - 0.2, prod.get(b, 0.0), width=0.4, label="Produção" if i == 0 else "")
            ax.bar(i + 0.2, cons.get(b, 0.0), width=0.4, label="Consumo" if i == 0 else "")
        ax.set_xticks(range(len(bens)))
        ax.set_xticklabels(bens, rotation=45, ha="right")
        ax.legend()
        self.canvas.draw_idle()

# ----------------------------- Janela Principal -----------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Construtor Econômico – Wireframe")
        self.resize(1200, 720)

        self.economias: List[Economia] = []
        self.idx_atual = -1

        splitter = QSplitter(self)

        # esquerda
        left = QWidget(); vleft = QVBoxLayout(left)
        self.lst = QListWidget()
        hl = QHBoxLayout()
        self.btn_new = QPushButton("Nova")
        self.btn_tpl = QPushButton("Template…")
        self.btn_dup = QPushButton("Duplicar")
        self.btn_del = QPushButton("Excluir")
        hl.addWidget(self.btn_new); hl.addWidget(self.btn_tpl); hl.addWidget(self.btn_dup); hl.addWidget(self.btn_del)
        vleft.addWidget(QLabel("Economias"))
        vleft.addWidget(self.lst, 1)
        vleft.addLayout(hl)

        # direita
        self.stack = QStackedWidget()
        self.lbl_empty = QLabel("<i>Crie ou selecione uma economia…</i>")
        self.lbl_empty.setAlignment(Qt.AlignCenter)
        self.stack.addWidget(self.lbl_empty)

        splitter.addWidget(left)
        splitter.addWidget(self.stack)
        splitter.setStretchFactor(1, 1)
        self.setCentralWidget(splitter)

        # conexões
        self.btn_new.clicked.connect(self._nova)
        self.btn_tpl.clicked.connect(self._novo_de_template)
        self.btn_dup.clicked.connect(self._duplicar)
        self.btn_del.clicked.connect(self._excluir)
        self.lst.currentRowChanged.connect(self._trocar)

        # menu
        self._build_menu()

    def _build_menu(self):
        m = self.menuBar().addMenu("Arquivo")
        act_tpl = m.addAction("Novo de template…")
        act_tpl.triggered.connect(self._novo_de_template)
        m.addSeparator()
        act_exp = m.addAction("Exportar economia (JSON)")
        act_exp.triggered.connect(self._exportar)
        act_imp = m.addAction("Importar economia (JSON)")
        act_imp.triggered.connect(self._importar)
        act_imp_rec = m.addAction("Importar recursos de localidade")
        act_imp_rec.triggered.connect(self._importar_recursos)
        m.addSeparator()
        act_all = m.addAction("Exportar todas (JSON)")
        act_all.triggered.connect(self._exportar_todas)

    # --- CRUD ---
    def _nova(self):
        e = Economia(nome=f"Economia {len(self.economias)+1}")
        self.economias.append(e)
        self._refresh_lista()
        self.lst.setCurrentRow(len(self.economias)-1)

    def _novo_de_template(self):
        if not TEMPLATES_ECON:
            QMessageBox.information(self, "Templates", "Nenhum template disponível.")
            return
        items = list(TEMPLATES_ECON.keys())
        sel, ok = QInputDialog.getItem(self, "Novo de Template", "Escolha um template:", items, 0, False)
        if not ok:
            return
        base = TEMPLATES_ECON[sel]
        e = Economia(nome=sel)
        # aplica campos
        for k, v in base.items():
            if isinstance(v, list):
                setattr(e, k, list(v))
            else:
                setattr(e, k, v)
        self.economias.append(e)
        self._refresh_lista()
        self.lst.setCurrentRow(len(self.economias)-1)

    def _duplicar(self):
        i = self.lst.currentRow()
        if i < 0: return
        base = self.economias[i]
        copia = json.loads(json.dumps(asdict(base)))
        novo = Economia(**copia)
        novo.nome = base.nome + " (cópia)"
        self.economias.append(novo)
        self._refresh_lista()
        self.lst.setCurrentRow(len(self.economias)-1)

    def _excluir(self):
        i = self.lst.currentRow()
        if i < 0: return
        del self.economias[i]
        self._refresh_lista()
        self.stack.setCurrentIndex(0)

    def _refresh_lista(self):
        self.lst.clear()
        for e in self.economias:
            self.lst.addItem(e.nome)

    def _trocar(self, idx):
        if idx < 0 or idx >= len(self.economias):
            self.stack.setCurrentIndex(0)
            return
        self.idx_atual = idx
        e = self.economias[idx]
        self._montar_paginas(e)

    def _montar_paginas(self, e: Economia):
        while self.stack.count() > 1:
            w = self.stack.widget(1)
            self.stack.removeWidget(w)
            w.deleteLater()
        self.page_basico = PageBasico(e, self._on_change)
        self.page_rec = PageRecursosProducao(e, self._on_change)
        self.page_rotas = PageRotas(e, self._on_change)
        self.page_pol = PagePoliticas(e, self._on_change)
        self.page_evt = PageEventos(e, self._on_change)
        self.page_res = PageResumo(e)
        for w in [self.page_basico, self.page_rec, self.page_rotas, self.page_pol, self.page_evt, self.page_res]:
            wrap = QWidget(); v = QVBoxLayout(wrap); v.setContentsMargins(16,16,16,16); v.addWidget(w)
            self.stack.addWidget(wrap)
        self.stack.setCurrentIndex(1)

    def _on_change(self):
        if self.idx_atual >= 0:
            self.page_res.refresh()

    # --- Export/Import ---
    def _exportar(self):
        i = self.idx_atual
        if i < 0: return
        e = self.economias[i]
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Economia", f"{e.nome}.json", "JSON (*.json)")
        if not path: return
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(asdict(e), f, ensure_ascii=False, indent=2)

    def _importar(self):
        path, _ = QFileDialog.getOpenFileName(self, "Importar Economia", "", "JSON (*.json)")
        if not path: return
        try:
            data = json.loads(open(path, 'r', encoding='utf-8').read())
            e = Economia(**data)
            self.economias.append(e)
            self._refresh_lista()
        except Exception as err:
            QMessageBox.critical(self, "Erro", f"Falha ao importar: {err}")

    def _importar_recursos(self):
        i = self.idx_atual
        if i < 0:
            return
        path, _ = QFileDialog.getOpenFileName(self, "Importar Localidade", "", "JSON (*.json)")
        if not path:
            return
        try:
            data = json.loads(open(path, 'r', encoding='utf-8').read())
            recursos = data.get("recursos", [])
            if isinstance(recursos, list):
                econ = self.economias[i]
                existentes = {r.get("recurso") for r in econ.recursos}
                for r in recursos:
                    nome = r.get("recurso", "")
                    if nome in existentes:
                        continue
                    econ.recursos.append({
                        "recurso": nome,
                        "abundancia": r.get("abundancia", ""),
                        "notas": r.get("notas", ""),
                    })
                if hasattr(self, "page_rec"):
                    self.page_rec.refresh()
                self._on_change()
        except Exception as err:
            QMessageBox.critical(self, "Erro", f"Falha ao importar: {err}")

    def _exportar_todas(self):
        if not self.economias:
            QMessageBox.information(self, "Aviso", "Nenhuma economia para exportar.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Conjunto", "economias.json", "JSON (*.json)")
        if not path: return
        data = [asdict(e) for e in self.economias]
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
