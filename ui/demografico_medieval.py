# -*- coding: utf-8 -*-
"""
Construtor Demográfico Medieval (PyQt5)

Objetivo: fornecer uma interface navegável (protótipo) para o módulo,
com páginas/telas e campos principais. A lógica de simulação aqui é mínima
(somente placeholders). Depois podemos conectar ao seu editor principal.

Como executar:
  pip install PyQt5
  python demografico_medieval.py
"""
from dataclasses import dataclass, field
from typing import Dict, List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSplitter, QListWidget, QListWidgetItem,
    QStackedWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QComboBox,
    QPushButton, QSpinBox, QDoubleSpinBox, QGroupBox, QCheckBox, QTableWidget,
    QTableWidgetItem, QAbstractItemView, QFrame, QSlider, QFileDialog, QLineEdit
)
import sys
import random


# ----------------------------- Estado (modelo simples) -----------------------------
@dataclass
class AssentamentoState:
    tipo: str = "Vila"
    habitantes: int = 500
    densidade_urbana: float = 0.25  # 25% urbano por padrão
    distribuicao_rural: float = 0.75

    tamanho: float = 10.0  # km² aproximados
    economia_base: str = "agricultura"
    regime: str = "monarquia"
    taxa_urbanizacao: float = 0.25

    bioma: str = "planície"
    recursos: List[str] = field(default_factory=lambda: ["madeira", "alimentos"]) 
    expectativa_vida: int = 35
    taxa_natalidade: float = 2.8  # por 100 habitantes/ano (placeholder)
    taxa_mortalidade: float = 2.0

    # classes sociais (números aproximados)
    nobreza: int = 5
    clero: int = 20
    camponeses: int = 350
    artesoes: int = 60
    comerciantes: int = 40
    mineradores: int = 25

    # militar e defesa
    soldados: int = 20
    arqueiros: int = 10
    cavaleiros: int = 5
    milicia: int = 30
    muros: bool = False
    torres: bool = False
    castelos: int = 0

    # efeitos de eventos (aplicados cumulativamente nesta versão simples)
    eventos_aplicados: List[str] = field(default_factory=list)


# regra simples para presets por tipo
PRESETS = {
    "Vila":            dict(habitantes=500,  densidade_urbana=0.15, expectativa_vida=35),
    "Cidade Pequena":  dict(habitantes=3000, densidade_urbana=0.35, expectativa_vida=38),
    "Cidade Grande":   dict(habitantes=12000,densidade_urbana=0.55, expectativa_vida=40),
    "Metrópole":       dict(habitantes=45000,densidade_urbana=0.70, expectativa_vida=42),
    "Reino":           dict(habitantes=120000,densidade_urbana=0.45, expectativa_vida=40),
    "Império":         dict(habitantes=500000,densidade_urbana=0.50, expectativa_vida=42),
    "Novo Assentamento": dict(habitantes=80, densidade_urbana=0.05, expectativa_vida=30),
}


def calcular_nascimentos(state: AssentamentoState) -> float:
    """Calcula nascimentos esperados em um ano como número real.

    Uma pequena variação aleatória é aplicada para simular incertezas
    demográficas. O resultado é retornado como ``float``.
    """
    base = state.habitantes * (state.taxa_natalidade / 1000.0)
    variacao = random.uniform(-0.1, 0.1) * base
    return base + variacao


def calcular_mortes(state: AssentamentoState) -> float:
    """Calcula mortes esperadas em um ano como número real.

    Aplica a mesma variação aleatória usada em ``calcular_nascimentos``.
    """
    base = state.habitantes * (state.taxa_mortalidade / 1000.0)
    variacao = random.uniform(-0.1, 0.1) * base
    return base + variacao


def simular_ano(state: AssentamentoState) -> float:
    """Atualiza a população aplicando nascimentos e mortes.

    O novo total de habitantes é retornado como número real.
    """
    nascimentos = calcular_nascimentos(state)
    mortes = calcular_mortes(state)
    state.habitantes = max(0, int(state.habitantes + nascimentos - mortes))
    return float(state.habitantes)


def export_structured(state: AssentamentoState) -> Dict[str, object]:
    """Exporta o estado em um dicionário compatível com ``cidades_planetas``."""
    urbano = int(state.habitantes * state.taxa_urbanizacao)
    rural = state.habitantes - urbano
    return {
        "nome": state.tipo,
        "tipo": "Cidade",
        "populacao": state.habitantes,
        "bioma": state.bioma,
        "clima": "temperado",
        "recursos": state.recursos,
        "arquitetura": "",
        "governo": state.regime,
        "economia": state.economia_base,
        "notas": f"Tamanho: {state.tamanho} km². Urbano: {urbano}. Rural: {rural}",
        "distritos": [],
        "pontos_interesse": [],
    }


# ----------------------------- Páginas -----------------------------
class PaginaTipo(QWidget):
    def __init__(self, state: AssentamentoState, on_apply):
        super().__init__()
        self.state = state
        self.on_apply = on_apply

        layout = QVBoxLayout(self)
        title = QLabel("<h2>Tipo de Assentamento</h2>")
        subtitle = QLabel("Escolha o tipo para preencher parâmetros iniciais.")
        subtitle.setStyleSheet("color: #666")

        form = QFormLayout()
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(list(PRESETS.keys()))
        self.combo_tipo.setCurrentText(self.state.tipo)

        self.lbl_hab = QLabel(str(self.state.habitantes))
        self.lbl_den = QLabel(f"{int(self.state.densidade_urbana*100)}% urbano")
        self.lbl_exp = QLabel(str(self.state.expectativa_vida))

        form.addRow("Tipo:", self.combo_tipo)
        form.addRow("Habitantes (sugerido):", self.lbl_hab)
        form.addRow("Densidade Urbana (sugerido):", self.lbl_den)
        form.addRow("Expectativa de Vida (sugerido):", self.lbl_exp)

        btn_apply = QPushButton("Criar Assentamento")
        btn_apply.clicked.connect(self.apply)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(form)
        layout.addStretch(1)
        layout.addWidget(btn_apply)

        self.combo_tipo.currentTextChanged.connect(self._update_sugestoes)
        self._update_sugestoes(self.combo_tipo.currentText())

    def _update_sugestoes(self, tipo: str):
        p = PRESETS.get(tipo, {})
        self.lbl_hab.setText(str(p.get("habitantes", self.state.habitantes)))
        self.lbl_den.setText(f"{int(p.get("densidade_urbana", self.state.densidade_urbana)*100)}% urbano")
        self.lbl_exp.setText(str(p.get("expectativa_vida", self.state.expectativa_vida)))

    def apply(self):
        tipo = self.combo_tipo.currentText()
        p = PRESETS.get(tipo, {})
        self.state.tipo = tipo
        self.state.habitantes = p.get("habitantes", self.state.habitantes)
        self.state.densidade_urbana = p.get("densidade_urbana", self.state.densidade_urbana)
        self.state.taxa_urbanizacao = self.state.densidade_urbana
        self.state.distribuicao_rural = 1 - self.state.densidade_urbana
        self.state.expectativa_vida = p.get("expectativa_vida", self.state.expectativa_vida)
        self.on_apply()


class PaginaCenario(QWidget):
    def __init__(self, state: AssentamentoState, on_apply):
        super().__init__()
        self.state = state
        self.on_apply = on_apply

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Parâmetros de Cenário</h2>"))

        # Bioma e recursos
        box_amb = QGroupBox("Ambiente")
        amb_form = QFormLayout()
        self.combo_bioma = QComboBox()
        self.combo_bioma.addItems(["floresta", "planície", "montanha", "litoral", "deserto", "tundra"]) 
        self.combo_bioma.setCurrentText(self.state.bioma)
        amb_form.addRow("Bioma:", self.combo_bioma)
        box_amb.setLayout(amb_form)

        box_rec = QGroupBox("Recursos Disponíveis")
        rec_layout = QVBoxLayout()
        self.chk_madeira = QCheckBox("madeira")
        self.chk_ferro = QCheckBox("ferro")
        self.chk_ouro = QCheckBox("ouro")
        self.chk_alimentos = QCheckBox("alimentos")
        self.chk_gado = QCheckBox("gado")
        for chk in [self.chk_madeira, self.chk_ferro, self.chk_ouro, self.chk_alimentos, self.chk_gado]:
            chk.setChecked(chk.text() in self.state.recursos)
            rec_layout.addWidget(chk)
        box_rec.setLayout(rec_layout)

        # Vida, natalidade, mortalidade
        box_dem = QGroupBox("Vida e Demografia")
        dem_form = QFormLayout()
        self.spin_expect = QSpinBox(); self.spin_expect.setRange(15, 80); self.spin_expect.setValue(self.state.expectativa_vida)
        self.dbl_natal = QDoubleSpinBox(); self.dbl_natal.setRange(0.0, 10.0); self.dbl_natal.setSingleStep(0.1); self.dbl_natal.setValue(self.state.taxa_natalidade)
        self.dbl_mortal = QDoubleSpinBox(); self.dbl_mortal.setRange(0.0, 10.0); self.dbl_mortal.setSingleStep(0.1); self.dbl_mortal.setValue(self.state.taxa_mortalidade)
        dem_form.addRow("Expectativa de Vida:", self.spin_expect)
        dem_form.addRow("Taxa de Natalidade (\u2030):", self.dbl_natal)
        dem_form.addRow("Taxa de Mortalidade (\u2030):", self.dbl_mortal)
        box_dem.setLayout(dem_form)

        # Tamanho e aspectos sociais
        box_soc = QGroupBox("Estrutura Social")
        soc_form = QFormLayout()
        self.sp_tamanho = QDoubleSpinBox(); self.sp_tamanho.setRange(0.1, 1000000.0); self.sp_tamanho.setValue(self.state.tamanho)
        self.ed_econ = QLineEdit(self.state.economia_base)
        self.ed_regime = QLineEdit(self.state.regime)
        soc_form.addRow("Tamanho (km²):", self.sp_tamanho)
        soc_form.addRow("Economia Base:", self.ed_econ)
        soc_form.addRow("Regime:", self.ed_regime)
        box_soc.setLayout(soc_form)

        top = QHBoxLayout()
        top.addWidget(box_amb)
        top.addWidget(box_rec)
        layout.addLayout(top)
        layout.addWidget(box_soc)
        layout.addWidget(box_dem)

        btn = QPushButton("Gerar Estrutura Inicial")
        btn.clicked.connect(self.apply)
        layout.addStretch(1)
        layout.addWidget(btn)

    def apply(self):
        self.state.bioma = self.combo_bioma.currentText()
        recursos = []
        for chk in [self.chk_madeira, self.chk_ferro, self.chk_ouro, self.chk_alimentos, self.chk_gado]:
            if chk.isChecked():
                recursos.append(chk.text())
        self.state.recursos = recursos
        self.state.expectativa_vida = self.spin_expect.value()
        self.state.taxa_natalidade = self.dbl_natal.value()
        self.state.taxa_mortalidade = self.dbl_mortal.value()
        self.state.tamanho = self.sp_tamanho.value()
        self.state.economia_base = self.ed_econ.text().strip()
        self.state.regime = self.ed_regime.text().strip()
        self.on_apply()


class PaginaClasses(QWidget):
    def __init__(self, state: AssentamentoState, on_apply):
        super().__init__()
        self.state = state
        self.on_apply = on_apply

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Classes Sociais & Demografia</h2>"))

        # Tabela de classes
        box_classes = QGroupBox("Classes Sociais")
        v = QVBoxLayout()
        self.tbl = QTableWidget(6, 2)
        self.tbl.setHorizontalHeaderLabels(["Classe", "Pessoas"])
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.setEditTriggers(QAbstractItemView.AllEditTriggers)
        rows = [
            ("Nobreza", self.state.nobreza),
            ("Clero", self.state.clero),
            ("Camponeses", self.state.camponeses),
            ("Artesãos", self.state.artesoes),
            ("Comerciantes", self.state.comerciantes),
            ("Mineradores", self.state.mineradores),
        ]
        for r, (nome, val) in enumerate(rows):
            self.tbl.setItem(r, 0, QTableWidgetItem(nome))
            item = QTableWidgetItem(str(val))
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tbl.setItem(r, 1, item)
        v.addWidget(self.tbl)
        box_classes.setLayout(v)

        # Urbano vs rural (slider simples)
        box_ur = QGroupBox("Distribuição Urbana x Rural")
        h = QHBoxLayout()
        self.sld_urbano = QSlider(Qt.Horizontal); self.sld_urbano.setRange(0, 100)
        self.sld_urbano.setValue(int(self.state.taxa_urbanizacao * 100))
        self.lbl_urb = QLabel(f"Urbano: {int(self.state.taxa_urbanizacao*100)}%  |  Rural: {int((1-self.state.taxa_urbanizacao)*100)}%")
        h.addWidget(self.sld_urbano)
        h.addWidget(self.lbl_urb)
        box_ur.setLayout(h)

        btn = QPushButton("Aplicar Distribuição & Atualizar")
        btn.clicked.connect(self.apply)

        layout.addWidget(box_classes)
        layout.addWidget(box_ur)
        layout.addStretch(1)
        layout.addWidget(btn)

        self.sld_urbano.valueChanged.connect(self._update_ratio)

    def _update_ratio(self, val):
        self.lbl_urb.setText(f"Urbano: {val}%  |  Rural: {100-val}%")

    def apply(self):
        # salva classes
        self.state.nobreza      = int(self.tbl.item(0,1).text())
        self.state.clero        = int(self.tbl.item(1,1).text())
        self.state.camponeses   = int(self.tbl.item(2,1).text())
        self.state.artesoes     = int(self.tbl.item(3,1).text())
        self.state.comerciantes = int(self.tbl.item(4,1).text())
        self.state.mineradores  = int(self.tbl.item(5,1).text())
        # urbano/rural
        self.state.taxa_urbanizacao = self.sld_urbano.value()/100.0
        self.state.densidade_urbana = self.state.taxa_urbanizacao
        self.state.distribuicao_rural = 1 - self.state.taxa_urbanizacao
        self.on_apply()


class PaginaMilitar(QWidget):
    def __init__(self, state: AssentamentoState, on_apply):
        super().__init__()
        self.state = state
        self.on_apply = on_apply

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Militar & Defesa</h2>"))

        form = QFormLayout()
        self.sp_sold = QSpinBox(); self.sp_sold.setRange(0, 100000); self.sp_sold.setValue(self.state.soldados)
        self.sp_arq  = QSpinBox(); self.sp_arq.setRange(0, 100000);  self.sp_arq.setValue(self.state.arqueiros)
        self.sp_cav  = QSpinBox(); self.sp_cav.setRange(0, 100000);  self.sp_cav.setValue(self.state.cavaleiros)
        self.sp_mil  = QSpinBox(); self.sp_mil.setRange(0, 100000);  self.sp_mil.setValue(self.state.milicia)
        form.addRow("Soldados:", self.sp_sold)
        form.addRow("Arqueiros:", self.sp_arq)
        form.addRow("Cavaleiros:", self.sp_cav)
        form.addRow("Milícia:", self.sp_mil)

        box_def = QGroupBox("Estruturas Defensivas")
        def_lay = QHBoxLayout()
        self.chk_muros = QCheckBox("Muros"); self.chk_muros.setChecked(self.state.muros)
        self.chk_torres = QCheckBox("Torres"); self.chk_torres.setChecked(self.state.torres)
        self.sp_castelos = QSpinBox(); self.sp_castelos.setRange(0, 100); self.sp_castelos.setValue(self.state.castelos)
        def_lay.addWidget(self.chk_muros)
        def_lay.addWidget(self.chk_torres)
        def_lay.addWidget(QLabel("Castelos:"))
        def_lay.addWidget(self.sp_castelos)
        box_def.setLayout(def_lay)

        btn = QPushButton("Aplicar Militares & Defesa")
        btn.clicked.connect(self.apply)

        layout.addLayout(form)
        layout.addWidget(box_def)
        layout.addStretch(1)
        layout.addWidget(btn)

    def apply(self):
        self.state.soldados = self.sp_sold.value()
        self.state.arqueiros = self.sp_arq.value()
        self.state.cavaleiros = self.sp_cav.value()
        self.state.milicia = self.sp_mil.value()
        self.state.muros = self.chk_muros.isChecked()
        self.state.torres = self.chk_torres.isChecked()
        self.state.castelos = self.sp_castelos.value()
        self.on_apply()


class PaginaEventos(QWidget):
    def __init__(self, state: AssentamentoState, on_apply):
        super().__init__()
        self.state = state
        self.on_apply = on_apply

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Eventos</h2>"))
        layout.addWidget(self._evento_row("Guerra (reduz população, aumenta exército)", self.apply_guerra))
        layout.addWidget(self._evento_row("Peste (queda populacional, menor produtividade)", self.apply_peste))
        layout.addWidget(self._evento_row("Colheita Ruim (fome e instabilidade)", self.apply_colheita_ruim))
        layout.addWidget(self._evento_row("Colheita Boa (crescimento populacional)", self.apply_colheita_boa))
        layout.addStretch(1)

    def _evento_row(self, texto, slot):
        row = QHBoxLayout()
        row.addWidget(QLabel(texto))
        btn = QPushButton("Aplicar")
        btn.clicked.connect(slot)
        w = QWidget(); w.setLayout(row)
        row.addStretch(1)
        row.addWidget(btn)
        return w

    # efeitos simples (wireframe):
    def apply_guerra(self):
        self.state.habitantes = max(0, int(self.state.habitantes * 0.95))
        self.state.soldados += 10
        self.state.eventos_aplicados.append("Guerra")
        self.on_apply()

    def apply_peste(self):
        self.state.habitantes = max(0, int(self.state.habitantes * 0.90))
        self.state.taxa_mortalidade += 0.3
        self.state.eventos_aplicados.append("Peste")
        self.on_apply()

    def apply_colheita_ruim(self):
        self.state.habitantes = max(0, int(self.state.habitantes * 0.98))
        self.state.eventos_aplicados.append("Colheita Ruim")
        self.on_apply()

    def apply_colheita_boa(self):
        self.state.habitantes = int(self.state.habitantes * 1.02)
        self.state.eventos_aplicados.append("Colheita Boa")
        self.on_apply()


class PaginaResultados(QWidget):
    def __init__(self, state: AssentamentoState):
        super().__init__()
        self.state = state

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Resultados</h2>"))

        # Tabela consolidada simples
        self.tbl = QTableWidget(0, 2)
        self.tbl.setHorizontalHeaderLabels(["Indicador", "Valor"])
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.tbl)

        # Botões de export
        btns = QHBoxLayout()
        self.btn_export_csv = QPushButton("Exportar CSV")
        self.btn_export_csv.clicked.connect(self.export_csv)
        self.btn_export_pdf = QPushButton("Exportar PDF (placeholder)")
        self.btn_send_cp = QPushButton("Enviar para Cidades/Planetas")
        self.btn_send_cp.clicked.connect(self.send_to_cp)
        btns.addStretch(1)
        btns.addWidget(self.btn_export_csv)
        btns.addWidget(self.btn_export_pdf)
        btns.addWidget(self.btn_send_cp)
        layout.addLayout(btns)

        self.refresh()

    def refresh(self):
        def add_row(k, v):
            r = self.tbl.rowCount(); self.tbl.insertRow(r)
            self.tbl.setItem(r, 0, QTableWidgetItem(k))
            self.tbl.setItem(r, 1, QTableWidgetItem(str(v)))

        self.tbl.setRowCount(0)
        s = self.state
        add_row("Tipo", s.tipo)
        add_row("População Total", s.habitantes)
        urb = int(s.habitantes * s.taxa_urbanizacao)
        add_row("População Urbana", urb)
        add_row("População Rural", s.habitantes - urb)
        add_row("Taxa de Urbanização (%)", int(s.taxa_urbanizacao * 100))
        add_row("Expectativa de Vida", s.expectativa_vida)
        add_row("Natalidade (‰)", s.taxa_natalidade)
        add_row("Mortalidade (‰)", s.taxa_mortalidade)
        add_row("Nascimentos (simulados)", round(calcular_nascimentos(s), 2))
        add_row("Mortes (simuladas)", round(calcular_mortes(s), 2))
        add_row("Recursos", ", ".join(s.recursos) if s.recursos else "—")
        add_row("Tamanho (km²)", s.tamanho)
        add_row("Economia Base", s.economia_base)
        add_row("Regime", s.regime)

        # classes sociais
        add_row("Nobreza", s.nobreza)
        add_row("Clero", s.clero)
        add_row("Camponeses", s.camponeses)
        add_row("Artesãos", s.artesoes)
        add_row("Comerciantes", s.comerciantes)
        add_row("Mineradores", s.mineradores)

        # militar/defesa
        add_row("Soldados", s.soldados)
        add_row("Arqueiros", s.arqueiros)
        add_row("Cavaleiros", s.cavaleiros)
        add_row("Milícia", s.milicia)
        add_row("Muros", "Sim" if s.muros else "Não")
        add_row("Torres", "Sim" if s.torres else "Não")
        add_row("Castelos", s.castelos)

        if s.eventos_aplicados:
            add_row("Eventos Aplicados", ", ".join(s.eventos_aplicados))

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Salvar CSV", "resultados.csv", "CSV (*.csv)")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            for r in range(self.tbl.rowCount()):
                k = self.tbl.item(r, 0).text()
                v = self.tbl.item(r, 1).text()
                f.write(f"{k};{v}\n")

    def send_to_cp(self):
        from ui.cidades_planetas import MainWindow as CPWindow, Localidade
        data = export_structured(self.state)
        self._cp_win = CPWindow()
        self._cp_win.localidades.append(Localidade(**data))
        self._cp_win._refresh_lista()
        self._cp_win.show()


# ----------------------------- Janela principal -----------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Construtor Demográfico Medieval")
        self.resize(1200, 720)

        # estado compartilhado
        self.state = AssentamentoState()

        # layout com sidebar + páginas
        splitter = QSplitter(self)
        splitter.setChildrenCollapsible(False)

        # sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(260)
        for i, label in enumerate([
            "1. Tipo de Assentamento",
            "2. Parâmetros de Cenário",
            "3. Classes & Demografia",
            "4. Militar & Defesa",
            "5. Eventos",
            "6. Resultados",
        ]):
            item = QListWidgetItem(label)
            self.sidebar.addItem(item)
        self.sidebar.setCurrentRow(0)

        # páginas
        self.pages = QStackedWidget()
        self.p_tipo = PaginaTipo(self.state, self.refresh_results)
        self.p_cenario = PaginaCenario(self.state, self.refresh_results)
        self.p_classes = PaginaClasses(self.state, self.refresh_results)
        self.p_militar = PaginaMilitar(self.state, self.refresh_results)
        self.p_eventos = PaginaEventos(self.state, self.refresh_results)
        self.p_result = PaginaResultados(self.state)

        for w in [self.p_tipo, self.p_cenario, self.p_classes, self.p_militar, self.p_eventos, self.p_result]:
            page_wrap = QWidget(); lay = QVBoxLayout(page_wrap); lay.setContentsMargins(16,16,16,16); lay.addWidget(w)
            self.pages.addWidget(page_wrap)

        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.pages)
        splitter.setStretchFactor(1, 1)

        self.setCentralWidget(splitter)

        # conexões
        self.sidebar.currentRowChanged.connect(self.pages.setCurrentIndex)

    def refresh_results(self):
        # após qualquer "Aplicar" atualiza página de resultados
        self.p_result.refresh()


# ----------------------------- Execução -----------------------------
def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
