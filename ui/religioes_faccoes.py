# -*- coding: utf-8 -*-
"""
Construtor de Religiões, Facções e Grupos (PyQt5)

Objetivo: protótipo navegável para criar e gerenciar religiões, facções,
irmandades e grupos (inclusive criminosos), com templates e exportação.

Como executar:
  pip install PyQt5
  python religioes_faccoes.py
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict
import json
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSplitter, QListWidget,
    QStackedWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QTextEdit, QComboBox, QPushButton, QSpinBox, QDoubleSpinBox, QGroupBox,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QFileDialog, QMessageBox,
    QInputDialog, QCheckBox
)

# ----------------------------- Estado -----------------------------
@dataclass
class Grupo:
    nome: str = ""
    tipo: str = "Religião"  # Religião, Facção, Guilda, Corporação, Irmandade, Grupo Criminoso
    escopo: str = "Local"    # Local, Regional, Continental, Planetário, Interestelar
    fundacao: int = 0         # ano ou marco
    sede: str = ""
    simbolo: str = ""        # texto (placeholder)
    lema: str = ""

    # Doutrina / Código
    doutrina: str = ""
    objetivos: str = ""
    leis_tabus: str = ""

    # Estrutura & Pessoas
    hierarquia: List[Dict[str, str]] = field(default_factory=list)     # {cargo, descricao}
    membros_notaveis: List[Dict[str, str]] = field(default_factory=list) # {nome, papel}
    recrutamento: str = "Aberto"  # Aberto, Seletivo, Secreto

    # Operação
    financas: List[Dict[str, str]] = field(default_factory=list)   # {fonte, descricao}
    territorios: List[Dict[str, str]] = field(default_factory=list) # {local, controle}
    relacoes: List[Dict[str, str]] = field(default_factory=list)    # {grupo, relacao}

    # Cultura
    rituais: List[Dict[str, str]] = field(default_factory=list)     # {nome, descricao}
    tecnologias: str = ""      # magia/tecnologia permitida
    reputacao: str = "Neutra"  # Boa, Neutra, Má (livre)
    tags: List[str] = field(default_factory=list)

    # Histórico
    eventos: List[Dict[str, str]] = field(default_factory=list)      # {ano, evento}
    notas: str = ""

# ----------------------------- Templates -----------------------------
TEMPLATES_GRUPO: Dict[str, Dict] = {
    "Culto do Sol Invicto (Religião)": {
        "tipo": "Religião", "escopo": "Regional", "fundacao": -215,
        "sede": "Templo da Luz", "simbolo": "Sol raiado", "lema": "Onde a luz, não há medo.",
        "doutrina": "Veneração do Sol como fonte de ordem e verdade.",
        "objetivos": "Expandir templos; erradicar cultos sombrios.",
        "leis_tabus": "Proíbe práticas necromânticas; jejuns sazonais.",
        "hierarquia": [{"cargo": "Sumo Hierofante", "descricao": "Líder espiritual"}, {"cargo": "Aedos", "descricao": "Cantores do culto"}],
        "membros_notaveis": [{"nome": "Sóror Elara", "papel": "Oráculo"}],
        "recrutamento": "Seletivo",
        "financas": [{"fonte": "Dízimos", "descricao": "Ofertas dos fiéis"}],
        "territorios": [{"local": "Cidades do Vale", "controle": "influência"}],
        "relacoes": [{"grupo": "Ordem dos Corvos", "relacao": "aliança"}],
        "rituais": [{"nome": "Aurora", "descricao": "Cântico ao amanhecer"}],
        "tecnologias": "Magia solar; artefatos de luz.",
        "reputacao": "Boa",
        "eventos": [{"ano": "-200", "evento": "Fundação do Grande Templo"}]
    },
    "Ordem dos Corvos (Irmandade)": {
        "tipo": "Irmandade", "escopo": "Local", "fundacao": -12,
        "sede": "Torre do Corvo", "simbolo": "Corvo negro", "lema": "Pelo silêncio e pela sombra.",
        "doutrina": "Disciplina, sigilo, contratos de proteção.",
        "objetivos": "Proteger a cidade de ameaças externas.",
        "leis_tabus": "Juramento de silêncio; proíbe laços políticos.",
        "hierarquia": [{"cargo": "Mestre de Plumas", "descricao": "Comandante"}],
        "membros_notaveis": [{"nome": "Kael", "papel": "Batedor-chefe"}],
        "recrutamento": "Secreto",
        "financas": [{"fonte": "Contratos", "descricao": "Proteção de caravanas"}],
        "territorios": [{"local": "Distrito Norte", "controle": "patrulha"}],
        "relacoes": [{"grupo": "Guilda Mercantil", "relacao": "aliança"}],
        "rituais": [{"nome": "Voto das Plumas", "descricao": "Iniciação"}],
        "tecnologias": "Alquimia leve; arcos compostos.",
        "reputacao": "Neutra",
        "eventos": [{"ano": "15", "evento": "Derrota dos saqueadores"}]
    },
    "Guilda Mercantil do Âmbar (Facção)": {
        "tipo": "Facção", "escopo": "Regional", "fundacao": -80,
        "sede": "Casa do Âmbar", "simbolo": "Gema âmbar", "lema": "A corrente que move o mundo.",
        "doutrina": "Livre comércio; contratos sagrados.",
        "objetivos": "Controlar rotas de caravanas.",
        "leis_tabus": "Quebrar contrato é heresia.",
        "hierarquia": [{"cargo": "Arquimercador", "descricao": "Líder comercial"}],
        "membros_notaveis": [{"nome": "Dama Selene", "papel": "Emissária"}],
        "recrutamento": "Aberto",
        "financas": [{"fonte": "Tarifas", "descricao": "Taxas de intermediação"}],
        "territorios": [{"local": "Rotas do Sul", "controle": "cartel"}],
        "relacoes": [{"grupo": "Culto do Sol Invicto", "relacao": "aliança"}],
        "rituais": [{"nome": "Fecho de Selo", "descricao": "Cerimônia de contrato"}],
        "tecnologias": "Códigos de cifragem; contabilidade.",
        "reputacao": "Boa",
        "eventos": [{"ano": "-10", "evento": "Monopólio da rota litorânea"}]
    },
    "Corporação ArcTec (Sci‑Fi)": {
        "tipo": "Corporação", "escopo": "Interestelar", "fundacao": 2187,
        "sede": "Órbita de Procyon", "simbolo": "A estilizado", "lema": "Iterar para dominar.",
        "doutrina": "Progresso tecnológico acima de tradições.",
        "objetivos": "Patentes de IA e terraformação.",
        "leis_tabus": "Proíbe sindicatos; NDA perpétuo.",
        "hierarquia": [{"cargo": "CEO", "descricao": "Diretoria Executiva"}],
        "membros_notaveis": [{"nome": "Dr. Nadir", "papel": "Chefe de P&D"}],
        "recrutamento": "Seletivo",
        "financas": [{"fonte": "Patentes", "descricao": "Royalties de IA"}],
        "territorios": [{"local": "Colônias Beta", "controle": "concessões"}],
        "relacoes": [{"grupo": "Sindicatos dos Canais", "relacao": "inimigos"}],
        "rituais": [{"nome": "Demo-Day Orbital", "descricao": "Lançamento trimestral"}],
        "tecnologias": "IA proprietária; drones autônomos.",
        "reputacao": "Neutra",
        "eventos": [{"ano": "2210", "evento": "Aquisição da ExoLabs"}]
    },
    "Sindicatos dos Canais (Grupo Criminoso)": {
        "tipo": "Grupo Criminoso", "escopo": "Planetário", "fundacao": 2199,
        "sede": "Nível Submerso", "simbolo": "Tridente", "lema": "Nada impede o fluxo.",
        "doutrina": "Controle de contrabando como serviço público.",
        "objetivos": "Dominar alfândegas e zonas francas.",
        "leis_tabus": "Traição punida com exílio.",
        "hierarquia": [{"cargo": "Capitão de Doca", "descricao": "Coordena células"}],
        "membros_notaveis": [{"nome": "Rhea", "papel": "Chefe de rede"}],
        "recrutamento": "Secreto",
        "financas": [{"fonte": "Pedágio", "descricao": "Taxa sobre carga ilícita"}],
        "territorios": [{"local": "Portos Orbitais", "controle": "infiltração"}],
        "relacoes": [{"grupo": "Corporação ArcTec", "relacao": "inimigos"}],
        "rituais": [{"nome": "Juramento do Canal", "descricao": "Batismo em água reciclada"}],
        "tecnologias": "Encriptação de malha; impressoras clandestinas.",
        "reputacao": "Má",
        "eventos": [{"ano": "2204", "evento": "Tomada do Armazém 7"}]
    }
}

# ----------------------------- Componentes auxiliares -----------------------------
class _TableEdit(QWidget):
    """Editor de tabela genérico para listas de dicts."""
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
        hl = QHBoxLayout()
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

# ----------------------------- Páginas -----------------------------
class PageBasico(QWidget):
    def __init__(self, g: Grupo, on_change):
        super().__init__()
        self.g = g; self.on_change = on_change
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Identidade do Grupo</h2>"))
        form = QFormLayout()
        self.ed_nome = QLineEdit(self.g.nome)
        self.cb_tipo = QComboBox(); self.cb_tipo.addItems(["Religião", "Facção", "Guilda", "Corporação", "Irmandade", "Grupo Criminoso"]) ; self.cb_tipo.setCurrentText(self.g.tipo)
        self.cb_escopo = QComboBox(); self.cb_escopo.addItems(["Local", "Regional", "Continental", "Planetário", "Interestelar"]) ; self.cb_escopo.setCurrentText(self.g.escopo)
        self.sp_fund = QSpinBox(); self.sp_fund.setRange(-100000, 100000); self.sp_fund.setValue(self.g.fundacao)
        self.ed_sede = QLineEdit(self.g.sede)
        self.ed_simbolo = QLineEdit(self.g.simbolo)
        self.ed_lema = QLineEdit(self.g.lema)
        form.addRow("Nome:", self.ed_nome)
        form.addRow("Tipo:", self.cb_tipo)
        form.addRow("Escopo:", self.cb_escopo)
        form.addRow("Fundação:", self.sp_fund)
        form.addRow("Sede:", self.ed_sede)
        form.addRow("Símbolo:", self.ed_simbolo)
        form.addRow("Lema:", self.ed_lema)
        layout.addLayout(form)
        btn = QPushButton("Salvar Básico"); btn.clicked.connect(self.save)
        layout.addWidget(btn); layout.addStretch(1)

    def save(self):
        self.g.nome = self.ed_nome.text().strip()
        self.g.tipo = self.cb_tipo.currentText()
        self.g.escopo = self.cb_escopo.currentText()
        self.g.fundacao = self.sp_fund.value()
        self.g.sede = self.ed_sede.text().strip()
        self.g.simbolo = self.ed_simbolo.text().strip()
        self.g.lema = self.ed_lema.text().strip()
        self.on_change()

class PageDoutrina(QWidget):
    def __init__(self, g: Grupo, on_change):
        super().__init__()
        self.g = g; self.on_change = on_change
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Doutrina & Código</h2>"))
        form = QFormLayout()
        self.tx_doutrina = QTextEdit(self.g.doutrina)
        self.tx_obj = QTextEdit(self.g.objetivos)
        self.tx_leis = QTextEdit(self.g.leis_tabus)
        form.addRow("Doutrina:", self.tx_doutrina)
        form.addRow("Objetivos:", self.tx_obj)
        form.addRow("Leis/Tabus:", self.tx_leis)
        layout.addLayout(form)
        btn = QPushButton("Salvar Doutrina"); btn.clicked.connect(self.save)
        layout.addWidget(btn); layout.addStretch(1)

    def save(self):
        self.g.doutrina = self.tx_doutrina.toPlainText().strip()
        self.g.objetivos = self.tx_obj.toPlainText().strip()
        self.g.leis_tabus = self.tx_leis.toPlainText().strip()
        self.on_change()

class PageEstrutura(QWidget):
    def __init__(self, g: Grupo, on_change):
        super().__init__()
        self.g = g; self.on_change = on_change
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Estrutura & Pessoas</h2>"))
        # hierarquia
        box_h = QGroupBox("Hierarquia (cargo/descrição)")
        v1 = QVBoxLayout(box_h)
        self.tab_hier = _TableEdit(["Cargo", "Descricao"], self.g.hierarquia)
        v1.addWidget(self.tab_hier)
        # membros
        box_m = QGroupBox("Membros Notáveis (nome/papel)")
        v2 = QVBoxLayout(box_m)
        self.tab_mem = _TableEdit(["Nome", "Papel"], self.g.membros_notaveis)
        v2.addWidget(self.tab_mem)
        # recrutamento
        form = QFormLayout()
        self.cb_rec = QComboBox(); self.cb_rec.addItems(["Aberto", "Seletivo", "Secreto"]) ; self.cb_rec.setCurrentText(self.g.recrutamento)
        form.addRow("Recrutamento:", self.cb_rec)
        layout.addWidget(box_h)
        layout.addWidget(box_m)
        layout.addLayout(form)
        btn = QPushButton("Salvar Estrutura"); btn.clicked.connect(self.save)
        layout.addWidget(btn); layout.addStretch(1)

    def save(self):
        self.g.hierarquia = self.tab_hier.to_list()
        self.g.membros_notaveis = self.tab_mem.to_list()
        self.g.recrutamento = self.cb_rec.currentText()
        self.on_change()

class PageOperacao(QWidget):
    def __init__(self, g: Grupo, on_change):
        super().__init__()
        self.g = g; self.on_change = on_change
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Operação</h2>"))
        # finanças
        box_f = QGroupBox("Finanças (fonte/descrição)")
        v1 = QVBoxLayout(box_f)
        self.tab_fin = _TableEdit(["Fonte", "Descricao"], self.g.financas)
        v1.addWidget(self.tab_fin)
        # territórios
        box_t = QGroupBox("Territórios (local/controle)")
        v2 = QVBoxLayout(box_t)
        self.tab_ter = _TableEdit(["Local", "Controle"], self.g.territorios)
        v2.addWidget(self.tab_ter)
        # relações
        box_r = QGroupBox("Relações com outros grupos (grupo/relação)")
        v3 = QVBoxLayout(box_r)
        self.tab_rel = _TableEdit(["Grupo", "Relacao"], self.g.relacoes)
        v3.addWidget(self.tab_rel)
        layout.addWidget(box_f)
        layout.addWidget(box_t)
        layout.addWidget(box_r)
        btn = QPushButton("Salvar Operação"); btn.clicked.connect(self.save)
        layout.addWidget(btn); layout.addStretch(1)

    def save(self):
        self.g.financas = self.tab_fin.to_list()
        self.g.territorios = self.tab_ter.to_list()
        self.g.relacoes = self.tab_rel.to_list()
        self.on_change()

class PageCultura(QWidget):
    def __init__(self, g: Grupo, on_change):
        super().__init__()
        self.g = g; self.on_change = on_change
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Cultura</h2>"))
        # rituais
        box_ri = QGroupBox("Rituais (nome/descrição)")
        v1 = QVBoxLayout(box_ri)
        self.tab_rit = _TableEdit(["Nome", "Descricao"], self.g.rituais)
        v1.addWidget(self.tab_rit)
        # tecnologia/magia & reputação
        form = QFormLayout()
        self.tx_tec = QTextEdit(self.g.tecnologias)
        self.ed_rep = QLineEdit(self.g.reputacao)
        self.ed_tags = QLineEdit(",".join(self.g.tags))
        form.addRow("Tecnologia/Magia:", self.tx_tec)
        form.addRow("Reputação:", self.ed_rep)
        form.addRow("Tags (separadas por vírgula):", self.ed_tags)
        layout.addWidget(box_ri)
        layout.addLayout(form)
        btn = QPushButton("Salvar Cultura"); btn.clicked.connect(self.save)
        layout.addWidget(btn); layout.addStretch(1)

    def save(self):
        self.g.rituais = self.tab_rit.to_list()
        self.g.tecnologias = self.tx_tec.toPlainText().strip()
        self.g.reputacao = self.ed_rep.text().strip()
        self.g.tags = [t.strip() for t in self.ed_tags.text().split(',') if t.strip()]
        self.on_change()

class PageHistorico(QWidget):
    def __init__(self, g: Grupo, on_change):
        super().__init__()
        self.g = g; self.on_change = on_change
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Histórico</h2>"))
        self.tab_evt = _TableEdit(["Ano", "Evento"], self.g.eventos)
        layout.addWidget(self.tab_evt)
        self.tx_notas = QTextEdit(self.g.notas)
        layout.addWidget(QLabel("Notas"))
        layout.addWidget(self.tx_notas)
        btn = QPushButton("Salvar Histórico"); btn.clicked.connect(self.save)
        layout.addWidget(btn); layout.addStretch(1)

    def save(self):
        self.g.eventos = self.tab_evt.to_list()
        self.g.notas = self.tx_notas.toPlainText().strip()
        self.on_change()

class PageResumo(QWidget):
    def __init__(self, g: Grupo):
        super().__init__()
        self.g = g
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Resumo</h2>"))
        self.tx = QTextEdit(); self.tx.setReadOnly(True)
        layout.addWidget(self.tx)
        self.refresh()

    def refresh(self):
        self.tx.setPlainText(json.dumps(asdict(self.g), indent=2, ensure_ascii=False))

# ----------------------------- Janela Principal -----------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Construtor de Religiões, Facções e Grupos")
        self.resize(1200, 720)

        self.grupos: List[Grupo] = []
        self.idx_atual = -1

        splitter = QSplitter(self)

        # esquerda
        left = QWidget(); vleft = QVBoxLayout(left)
        self.lst = QListWidget()
        hl = QHBoxLayout()
        self.btn_new = QPushButton("Novo")
        self.btn_tpl = QPushButton("Template…")
        self.btn_dup = QPushButton("Duplicar")
        self.btn_del = QPushButton("Excluir")
        hl.addWidget(self.btn_new); hl.addWidget(self.btn_tpl); hl.addWidget(self.btn_dup); hl.addWidget(self.btn_del)
        vleft.addWidget(QLabel("Grupos"))
        vleft.addWidget(self.lst, 1)
        vleft.addLayout(hl)

        # direita
        self.stack = QStackedWidget()
        self.lbl_empty = QLabel("<i>Crie ou selecione um grupo…</i>")
        self.lbl_empty.setAlignment(Qt.AlignCenter)
        self.stack.addWidget(self.lbl_empty)

        splitter.addWidget(left)
        splitter.addWidget(self.stack)
        splitter.setStretchFactor(1, 1)
        self.setCentralWidget(splitter)

        # conexões
        self.btn_new.clicked.connect(self._novo)
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
        act_exp = m.addAction("Exportar grupo (JSON)")
        act_exp.triggered.connect(self._exportar)
        act_imp = m.addAction("Importar grupo (JSON)")
        act_imp.triggered.connect(self._importar)
        m.addSeparator()
        act_all = m.addAction("Exportar todos (JSON)")
        act_all.triggered.connect(self._exportar_todos)

    # --- CRUD ---
    def _novo(self):
        g = Grupo(nome=f"Grupo {len(self.grupos)+1}")
        self.grupos.append(g)
        self._refresh_lista()
        self.lst.setCurrentRow(len(self.grupos)-1)

    def _novo_de_template(self):
        if not TEMPLATES_GRUPO:
            QMessageBox.information(self, "Templates", "Nenhum template disponível.")
            return
        items = list(TEMPLATES_GRUPO.keys())
        sel, ok = QInputDialog.getItem(self, "Novo de Template", "Escolha um template:", items, 0, False)
        if not ok:
            return
        base = TEMPLATES_GRUPO[sel]
        g = Grupo(nome=sel)
        for k, v in base.items():
            if isinstance(v, list):
                setattr(g, k, list(v))
            else:
                setattr(g, k, v)
        self.grupos.append(g)
        self._refresh_lista()
        self.lst.setCurrentRow(len(self.grupos)-1)

    def _duplicar(self):
        i = self.lst.currentRow()
        if i < 0: return
        base = self.grupos[i]
        copia = json.loads(json.dumps(asdict(base)))
        novo = Grupo(**copia)
        novo.nome = base.nome + " (cópia)"
        self.grupos.append(novo)
        self._refresh_lista()
        self.lst.setCurrentRow(len(self.grupos)-1)

    def _excluir(self):
        i = self.lst.currentRow()
        if i < 0: return
        del self.grupos[i]
        self._refresh_lista()
        self.stack.setCurrentIndex(0)

    def _refresh_lista(self):
        self.lst.clear()
        for g in self.grupos:
            tags = ",".join(g.tags)
            label = f"{g.nome}  —  {g.tipo}  [{tags}]" if tags else f"{g.nome}  —  {g.tipo}"
            self.lst.addItem(label)

    def _trocar(self, idx):
        if idx < 0 or idx >= len(self.grupos):
            self.stack.setCurrentIndex(0)
            return
        self.idx_atual = idx
        g = self.grupos[idx]
        self._montar_paginas(g)

    def _montar_paginas(self, g: Grupo):
        while self.stack.count() > 1:
            w = self.stack.widget(1)
            self.stack.removeWidget(w)
            w.deleteLater()
        self.page_basico = PageBasico(g, self._on_change)
        self.page_doutrina = PageDoutrina(g, self._on_change)
        self.page_estrut = PageEstrutura(g, self._on_change)
        self.page_oper = PageOperacao(g, self._on_change)
        self.page_cult = PageCultura(g, self._on_change)
        self.page_hist = PageHistorico(g, self._on_change)
        self.page_res = PageResumo(g)
        for w in [self.page_basico, self.page_doutrina, self.page_estrut, self.page_oper, self.page_cult, self.page_hist, self.page_res]:
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
        g = self.grupos[i]
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Grupo", f"{g.nome}.json", "JSON (*.json)")
        if not path: return
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(asdict(g), f, ensure_ascii=False, indent=2)

    def _importar(self):
        path, _ = QFileDialog.getOpenFileName(self, "Importar Grupo", "", "JSON (*.json)")
        if not path: return
        try:
            data = json.loads(open(path, 'r', encoding='utf-8').read())
            g = Grupo(**data)
            self.grupos.append(g)
            self._refresh_lista()
        except Exception as err:
            QMessageBox.critical(self, "Erro", f"Falha ao importar: {err}")

    def _exportar_todos(self):
        if not self.grupos:
            QMessageBox.information(self, "Aviso", "Nenhum grupo para exportar.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Conjunto", "grupos.json", "JSON (*.json)")
        if not path: return
        data = [asdict(g) for g in self.grupos]
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
