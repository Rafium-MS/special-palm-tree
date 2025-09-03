# -*- coding: utf-8 -*-
"""
Construtor de Personagens (PyQt5)

Objetivo: protótipo navegável para criação e gestão de personagens
aplicável a fantasia e ficção científica. Mantém um estado em memória
(com possibilidade de exportar/importar depois).

Como executar:
  pip install PyQt5
  python personagens.py
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
    QTableWidget, QTableWidgetItem, QAbstractItemView, QFileDialog, QMessageBox,
    QCheckBox
, QInputDialog)


# ----------------------------- Estado -----------------------------
@dataclass
class Personagem:
    nome: str = ""
    idade: int = 25
    genero: str = ""
    especie: str = "Humano"
    origem: str = ""
    papel: str = "Protagonista"  # Protagonista, Antagonista, Coadjuvante
    afiliacao: str = ""  # facção/clã/corporação

    personalidade: str = ""  # texto livre (Big5, MBTI, traços livres)
    virtudes: List[str] = field(default_factory=list)
    defeitos: List[str] = field(default_factory=list)
    motivacoes: str = ""
    segredos: str = ""

    atributos: Dict[str, int] = field(default_factory=lambda: {
        "Força": 1, "Agilidade": 1, "Intelecto": 1, "Carisma": 1, "Vontade": 1
    })
    pericias: List[Dict[str, str]] = field(default_factory=list)  # {nome, nivel}

    relacoes: List[Dict[str, str]] = field(default_factory=list)  # {pessoa, tipo}

    equipamentos: List[str] = field(default_factory=list)
    inventario: List[str] = field(default_factory=list)

    arco: str = ""  # arco de personagem
    status_arco: str = "Em desenvolvimento"  # Em desenvolvimento, Concluído, Em pausa

    tags: List[str] = field(default_factory=list)
    notas: str = ""


# Templates prontos (fantasia & sci-fi)
TEMPLATES: Dict[str, Dict] = {
    "Cavaleiro (Fantasia)": {
        "papel": "Protagonista",
        "atributos": {"Força": 7, "Agilidade": 4, "Intelecto": 3, "Carisma": 5, "Vontade": 6},
        "pericias": [{"nome": "Espada Longa", "nivel": "4"}, {"nome": "Montaria", "nivel": "3"}, {"nome": "Tática", "nivel": "2"}],
        "equipamentos": ["Armadura de placas", "Espada longa", "Escudo"],
        "tags": ["#fantasia", "#cavaleiro"],
        "personalidade": "Honra acima de tudo; senso de dever; conflito entre lealdade e compaixão.",
    },
    "Mago (Fantasia)": {
        "papel": "Coadjuvante",
        "atributos": {"Força": 1, "Agilidade": 3, "Intelecto": 8, "Carisma": 4, "Vontade": 7},
        "pericias": [{"nome": "Arcanismo", "nivel": "5"}, {"nome": "Alquimia", "nivel": "3"}],
        "equipamentos": ["Cajado rúnico", "Grimório"],
        "tags": ["#fantasia", "#mago"],
        "personalidade": "Curioso, reservado, obcecado por conhecimento proibido.",
    },
    "Ladino (Fantasia)": {
        "papel": "Coadjuvante",
        "atributos": {"Força": 3, "Agilidade": 7, "Intelecto": 4, "Carisma": 5, "Vontade": 4},
        "pericias": [{"nome": "Furtividade", "nivel": "5"}, {"nome": "Arrombamento", "nivel": "4"}],
        "equipamentos": ["Adagas", "Gazuas"],
        "tags": ["#fantasia", "#ladino"],
        "personalidade": "Sarcasmo como defesa; código moral próprio.",
    },
    "Piloto (Sci‑Fi)": {
        "papel": "Protagonista",
        "atributos": {"Força": 3, "Agilidade": 8, "Intelecto": 5, "Carisma": 4, "Vontade": 6},
        "pericias": [{"nome": "Pilotagem", "nivel": "5"}, {"nome": "Astrogração", "nivel": "3"}],
        "equipamentos": ["Jaqueta de vôo", "Comunicador"],
        "tags": ["#scifi", "#piloto"],
        "personalidade": "Audaz, acostumado a riscos calculados.",
    },
    "Cientista (Sci‑Fi)": {
        "papel": "Coadjuvante",
        "atributos": {"Força": 2, "Agilidade": 3, "Intelecto": 9, "Carisma": 3, "Vontade": 6},
        "pericias": [{"nome": "Pesquisa", "nivel": "5"}, {"nome": "Engenharia", "nivel": "4"}],
        "equipamentos": ["Tablet de laboratório", "Kit de amostras"],
        "tags": ["#scifi", "#cientista"],
        "personalidade": "Cético, metódico, empatia discreta.",
    },
    "Mercenário (Sci‑Fi)": {
        "papel": "Antagonista",
        "atributos": {"Força": 6, "Agilidade": 6, "Intelecto": 3, "Carisma": 3, "Vontade": 5},
        "pericias": [{"nome": "Armas leves", "nivel": "4"}, {"nome": "Sobrevivência", "nivel": "3"}],
        "equipamentos": ["Arma de pulso", "Armadura leve"],
        "tags": ["#scifi", "#mercenario"],
        "personalidade": "Pragmático; lealdade ao melhor contrato.",
    },
}

# ----------------------------- Páginas -----------------------------
class PageBasico(QWidget):
    def __init__(self, personagem: Personagem, on_change):
        super().__init__()
        self.p = personagem
        self.on_change = on_change
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Informações Básicas</h2>"))
        form = QFormLayout()
        self.ed_nome = QLineEdit(self.p.nome)
        self.sp_idade = QSpinBox(); self.sp_idade.setRange(0, 500); self.sp_idade.setValue(self.p.idade)
        self.cb_genero = QComboBox(); self.cb_genero.addItems(["", "Feminino", "Masculino", "Não-binário", "Outro"]) ; self.cb_genero.setCurrentText(self.p.genero)
        self.ed_especie = QLineEdit(self.p.especie)
        self.ed_origem = QLineEdit(self.p.origem)
        self.cb_papel = QComboBox(); self.cb_papel.addItems(["Protagonista", "Antagonista", "Coadjuvante"]) ; self.cb_papel.setCurrentText(self.p.papel)
        self.ed_afiliacao = QLineEdit(self.p.afiliacao)
        form.addRow("Nome:", self.ed_nome)
        form.addRow("Idade:", self.sp_idade)
        form.addRow("Gênero:", self.cb_genero)
        form.addRow("Espécie:", self.ed_especie)
        form.addRow("Origem:", self.ed_origem)
        form.addRow("Papel:", self.cb_papel)
        form.addRow("Afiliação:", self.ed_afiliacao)
        layout.addLayout(form)
        btn = QPushButton("Salvar Básico")
        btn.clicked.connect(self.save)
        layout.addWidget(btn)
        layout.addStretch(1)

    def save(self):
        self.p.nome = self.ed_nome.text().strip()
        self.p.idade = self.sp_idade.value()
        self.p.genero = self.cb_genero.currentText()
        self.p.especie = self.ed_especie.text().strip()
        self.p.origem = self.ed_origem.text().strip()
        self.p.papel = self.cb_papel.currentText()
        self.p.afiliacao = self.ed_afiliacao.text().strip()
        self.on_change()


class PagePersonalidade(QWidget):
    def __init__(self, personagem: Personagem, on_change):
        super().__init__()
        self.p = personagem
        self.on_change = on_change
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Personalidade & Fundamentos</h2>"))

        form = QFormLayout()
        self.tx_person = QTextEdit(self.p.personalidade)
        self.tx_motiv = QTextEdit(self.p.motivacoes)
        self.tx_seg = QTextEdit(self.p.segredos)
        form.addRow("Personalidade (traços, MBTI/Big5 opcional):", self.tx_person)
        form.addRow("Motivações:", self.tx_motiv)
        form.addRow("Segredos:", self.tx_seg)

        # virtudes/defeitos
        row = QHBoxLayout()
        self.ed_virt = QLineEdit(); self.ed_virt.setPlaceholderText("Adicionar virtude e Enter…")
        self.ed_def = QLineEdit(); self.ed_def.setPlaceholderText("Adicionar defeito e Enter…")
        self.lst_virt = QListWidget(); self.lst_def = QListWidget()
        row.addWidget(self._group("Virtudes", self.ed_virt, self.lst_virt))
        row.addWidget(self._group("Defeitos", self.ed_def, self.lst_def))

        layout.addLayout(form)
        layout.addLayout(row)
        btn = QPushButton("Salvar Personalidade")
        btn.clicked.connect(self.save)
        layout.addWidget(btn)
        layout.addStretch(1)

        self.ed_virt.returnPressed.connect(lambda: self._add_to(self.ed_virt, self.lst_virt))
        self.ed_def.returnPressed.connect(lambda: self._add_to(self.ed_def, self.lst_def))

    def _group(self, title, edit, listw):
        box = QGroupBox(title)
        v = QVBoxLayout(box)
        v.addWidget(edit)
        v.addWidget(listw)
        return box

    def _list_to_py(self, listw):
        return [listw.item(i).text() for i in range(listw.count())]

    def _add_to(self, edit: QLineEdit, listw: QListWidget):
        txt = edit.text().strip()
        if txt:
            listw.addItem(txt)
            edit.clear()

    def save(self):
        self.p.personalidade = self.tx_person.toPlainText().strip()
        self.p.motivacoes = self.tx_motiv.toPlainText().strip()
        self.p.segredos = self.tx_seg.toPlainText().strip()
        self.p.virtudes = self._list_to_py(self.lst_virt)
        self.p.defeitos = self._list_to_py(self.lst_def)
        self.on_change()


class PageAtributos(QWidget):
    def __init__(self, personagem: Personagem, on_change):
        super().__init__()
        self.p = personagem
        self.on_change = on_change
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Atributos & Perícias</h2>"))

        # atributos simples
        atr_group = QGroupBox("Atributos")
        atr_form = QFormLayout(atr_group)
        self.sp_atr = {}
        for nome in ["Força", "Agilidade", "Intelecto", "Carisma", "Vontade"]:
            sp = QSpinBox(); sp.setRange(0, 10); sp.setValue(self.p.atributos.get(nome, 1))
            atr_form.addRow(nome + ":", sp)
            self.sp_atr[nome] = sp

        # perícias em tabela (nome, nível)
        per_group = QGroupBox("Perícias")
        per_layout = QVBoxLayout(per_group)
        self.tbl_per = QTableWidget(0, 2)
        self.tbl_per.setHorizontalHeaderLabels(["Perícia", "Nível"]) ; self.tbl_per.verticalHeader().setVisible(False)
        self.tbl_per.setEditTriggers(QAbstractItemView.AllEditTriggers)
        btn_add_per = QPushButton("Adicionar Perícia")
        btn_del_per = QPushButton("Remover Selecionada")
        hl = QHBoxLayout(); hl.addWidget(btn_add_per); hl.addWidget(btn_del_per); hl.addStretch(1)
        per_layout.addWidget(self.tbl_per)
        per_layout.addLayout(hl)

        layout.addWidget(atr_group)
        layout.addWidget(per_group)
        btn = QPushButton("Salvar Atributos & Perícias")
        btn.clicked.connect(self.save)
        layout.addWidget(btn)
        layout.addStretch(1)

        btn_add_per.clicked.connect(self._add_pericia)
        btn_del_per.clicked.connect(self._del_pericia)
        self._load_pericias()

    def _load_pericias(self):
        self.tbl_per.setRowCount(0)
        for item in self.p.pericias:
            r = self.tbl_per.rowCount(); self.tbl_per.insertRow(r)
            self.tbl_per.setItem(r, 0, QTableWidgetItem(item.get("nome", "")))
            self.tbl_per.setItem(r, 1, QTableWidgetItem(item.get("nivel", "")))

    def _add_pericia(self):
        r = self.tbl_per.rowCount(); self.tbl_per.insertRow(r)
        self.tbl_per.setItem(r, 0, QTableWidgetItem("Nova perícia"))
        self.tbl_per.setItem(r, 1, QTableWidgetItem("1"))

    def _del_pericia(self):
        r = self.tbl_per.currentRow()
        if r >= 0:
            self.tbl_per.removeRow(r)

    def save(self):
        for nome, sp in self.sp_atr.items():
            self.p.atributos[nome] = sp.value()
        # salva perícias
        self.p.pericias = []
        for r in range(self.tbl_per.rowCount()):
            nome = self.tbl_per.item(r, 0).text() if self.tbl_per.item(r, 0) else ""
            nivel = self.tbl_per.item(r, 1).text() if self.tbl_per.item(r, 1) else ""
            self.p.pericias.append({"nome": nome, "nivel": nivel})
        self.on_change()


class PageRelacoes(QWidget):
    def __init__(self, personagem: Personagem, on_change):
        super().__init__()
        self.p = personagem
        self.on_change = on_change
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Relações</h2>"))

        self.tbl = QTableWidget(0, 2)
        self.tbl.setHorizontalHeaderLabels(["Pessoa", "Tipo de Relação"])
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self._load()

        hl = QHBoxLayout()
        btn_add = QPushButton("Adicionar")
        btn_del = QPushButton("Remover")
        hl.addWidget(btn_add); hl.addWidget(btn_del); hl.addStretch(1)

        btn_add.clicked.connect(self._add)
        btn_del.clicked.connect(self._del)

        btn = QPushButton("Salvar Relações")
        btn.clicked.connect(self.save)

        layout.addWidget(self.tbl)
        layout.addLayout(hl)
        layout.addWidget(btn)
        layout.addStretch(1)

    def _load(self):
        self.tbl.setRowCount(0)
        for r_item in self.p.relacoes:
            r = self.tbl.rowCount(); self.tbl.insertRow(r)
            self.tbl.setItem(r, 0, QTableWidgetItem(r_item.get("pessoa", "")))
            self.tbl.setItem(r, 1, QTableWidgetItem(r_item.get("tipo", "")))

    def _add(self):
        r = self.tbl.rowCount(); self.tbl.insertRow(r)
        self.tbl.setItem(r, 0, QTableWidgetItem("Nome"))
        self.tbl.setItem(r, 1, QTableWidgetItem("Aliado"))

    def _del(self):
        r = self.tbl.currentRow()
        if r >= 0:
            self.tbl.removeRow(r)

    def save(self):
        self.p.relacoes = []
        for r in range(self.tbl.rowCount()):
            pessoa = self.tbl.item(r, 0).text() if self.tbl.item(r, 0) else ""
            tipo = self.tbl.item(r, 1).text() if self.tbl.item(r, 1) else ""
            self.p.relacoes.append({"pessoa": pessoa, "tipo": tipo})
        self.on_change()


class PageEquip(QWidget):
    def __init__(self, personagem: Personagem, on_change):
        super().__init__()
        self.p = personagem
        self.on_change = on_change
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Equipamentos & Inventário</h2>"))

        # equipamentos e inventário (listas simples)
        self.ed_equip = QLineEdit(); self.ed_equip.setPlaceholderText("Adicionar equipamento e Enter…")
        self.ed_inv = QLineEdit(); self.ed_inv.setPlaceholderText("Adicionar item ao inventário e Enter…")
        from PyQt5.QtWidgets import QListWidget
        self.lst_equip = QListWidget(); self.lst_inv = QListWidget()

        row = QHBoxLayout()
        row.addWidget(self._group("Equipamentos", self.ed_equip, self.lst_equip))
        row.addWidget(self._group("Inventário", self.ed_inv, self.lst_inv))

        btn = QPushButton("Salvar Itens")
        btn.clicked.connect(self.save)

        layout.addLayout(row)
        layout.addWidget(btn)
        layout.addStretch(1)

        self.ed_equip.returnPressed.connect(lambda: self._add_to(self.ed_equip, self.lst_equip))
        self.ed_inv.returnPressed.connect(lambda: self._add_to(self.ed_inv, self.lst_inv))

    def _group(self, title, edit, listw):
        box = QGroupBox(title)
        v = QVBoxLayout(box)
        v.addWidget(edit)
        v.addWidget(listw)
        return box

    def _list_to_py(self, listw):
        return [listw.item(i).text() for i in range(listw.count())]

    def _add_to(self, edit: QLineEdit, listw):
        txt = edit.text().strip()
        if txt:
            listw.addItem(txt)
            edit.clear()

    def save(self):
        self.p.equipamentos = self._list_to_py(self.lst_equip)
        self.p.inventario = self._list_to_py(self.lst_inv)
        self.on_change()


class PageArco(QWidget):
    def __init__(self, personagem: Personagem, on_change):
        super().__init__()
        self.p = personagem
        self.on_change = on_change
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Arco & Motivação</h2>"))
        form = QFormLayout()
        self.tx_arco = QTextEdit(self.p.arco)
        self.cb_status = QComboBox(); self.cb_status.addItems(["Em desenvolvimento", "Concluído", "Em pausa"]) ; self.cb_status.setCurrentText(self.p.status_arco)
        form.addRow("Arco (resumo):", self.tx_arco)
        form.addRow("Status do Arco:", self.cb_status)

        # tags / notas
        self.ed_tag = QLineEdit(); self.ed_tag.setPlaceholderText("Adicionar tag e Enter… (ex.: #fantasia, #cyberpunk)")
        from PyQt5.QtWidgets import QListWidget
        self.lst_tags = QListWidget()
        self.tx_notas = QTextEdit(self.p.notas)

        layout.addLayout(form)
        box_tags = QGroupBox("Tags")
        v = QVBoxLayout(box_tags)
        v.addWidget(self.ed_tag)
        v.addWidget(self.lst_tags)
        layout.addWidget(box_tags)
        layout.addWidget(QLabel("Notas"))
        layout.addWidget(self.tx_notas)

        btn = QPushButton("Salvar Arco & Notas")
        btn.clicked.connect(self.save)
        layout.addWidget(btn)
        layout.addStretch(1)

        self.ed_tag.returnPressed.connect(lambda: self._add_tag())

    def _add_tag(self):
        txt = self.ed_tag.text().strip()
        if txt:
            self.lst_tags.addItem(txt)
            self.ed_tag.clear()

    def _tags_to_py(self):
        return [self.lst_tags.item(i).text() for i in range(self.lst_tags.count())]

    def save(self):
        self.p.arco = self.tx_arco.toPlainText().strip()
        self.p.status_arco = self.cb_status.currentText()
        self.p.tags = self._tags_to_py()
        self.p.notas = self.tx_notas.toPlainText().strip()
        self.on_change()


class PageResumo(QWidget):
    def __init__(self, personagem: Personagem):
        super().__init__()
        self.p = personagem
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Resumo</h2>"))
        self.tx = QTextEdit(); self.tx.setReadOnly(True)
        layout.addWidget(self.tx)
        self.refresh()

    def refresh(self):
        p = self.p
        data = asdict(p)
        # resumo simples em JSON legível
        self.tx.setPlainText(json.dumps(data, indent=2, ensure_ascii=False))


# ----------------------------- Janela Principal -----------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Construtor de Personagens – Wireframe")
        self.resize(1200, 720)

        # lista de personagens em memória e índice atual
        self.personagens: List[Personagem] = []
        self.idx_atual: int = -1

        # layout geral com esquerda: listagem; direita: páginas
        splitter = QSplitter(self)

        # --- esquerda: lista e ações ---
        left = QWidget(); vleft = QVBoxLayout(left)
        self.lst_chars = QListWidget()
        self.ed_filtro = QLineEdit(); self.ed_filtro.setPlaceholderText("Filtrar por nome/tag…")
        hl = QHBoxLayout()
        self.btn_novo = QPushButton("Novo")
        self.btn_tpl = QPushButton("Template…")
        self.btn_dup = QPushButton("Duplicar")
        self.btn_del = QPushButton("Excluir")
        hl.addWidget(self.btn_novo); hl.addWidget(self.btn_tpl); hl.addWidget(self.btn_dup); hl.addWidget(self.btn_del)
        vleft.addWidget(QLabel("Personagens"))
        vleft.addWidget(self.ed_filtro)
        vleft.addWidget(self.lst_chars, 1)
        vleft.addLayout(hl)

        # --- direita: páginas do personagem selecionado ---
        self.stack = QStackedWidget()
        self.lbl_empty = QLabel("<i>Crie um personagem ou selecione um da lista…</i>")
        self.lbl_empty.setAlignment(Qt.AlignCenter)
        self.stack.addWidget(self.lbl_empty)

        splitter.addWidget(left)
        splitter.addWidget(self.stack)
        splitter.setStretchFactor(1, 1)
        self.setCentralWidget(splitter)

        # conexões da esquerda
        self.btn_novo.clicked.connect(self._novo_personagem)
        self.btn_tpl.clicked.connect(self._novo_de_template)
        self.btn_dup.clicked.connect(self._duplicar_personagem)
        self.btn_del.clicked.connect(self._excluir_personagem)
        self.lst_chars.currentRowChanged.connect(self._trocar_personagem)
        self.ed_filtro.textChanged.connect(self._aplicar_filtro)

        # menu de arquivo (Export/Import JSON)
        self._build_menu()

    def _build_menu(self):
        m = self.menuBar().addMenu("Arquivo")
        act_new_tpl = m.addAction("Novo de template…")
        act_new_tpl.triggered.connect(self._novo_de_template)
        m.addSeparator()
        act_exp = m.addAction("Exportar personagem (JSON)")
        act_exp.triggered.connect(self._exportar_personagem)
        act_imp = m.addAction("Importar personagem (JSON)")
        act_imp.triggered.connect(self._importar_personagem)
        m.addSeparator()
        act_all = m.addAction("Exportar todos (JSON)")
        act_all.triggered.connect(self._exportar_todos)

    # --- CRUD personagens ---
    def _novo_personagem(self):
        p = Personagem(nome=f"Personagem {len(self.personagens)+1}")
        self.personagens.append(p)
        self._refresh_lista()
        self.lst_chars.setCurrentRow(len(self.personagens)-1)

    def _novo_de_template(self):
        if not TEMPLATES:
            QMessageBox.information(self, "Templates", "Nenhum template disponível.")
            return
        items = list(TEMPLATES.keys())
        sel, ok = QInputDialog.getItem(self, "Novo de Template", "Escolha um template:", items, 0, False)
        if not ok:
            return
        base = TEMPLATES[sel]
        p = Personagem(nome=sel)
        # aplicar campos do template
        p.papel = base.get("papel", p.papel)
        p.personalidade = base.get("personalidade", p.personalidade)
        if "atributos" in base:
            for k, v in base["atributos"].items():
                p.atributos[k] = v
        p.pericias = list(base.get("pericias", []))
        p.equipamentos = list(base.get("equipamentos", []))
        p.tags = list(base.get("tags", []))
        self.personagens.append(p)
        self._refresh_lista()
        self.lst_chars.setCurrentRow(len(self.personagens)-1)

    def _duplicar_personagem(self):
        i = self.lst_chars.currentRow()
        if i < 0: return
        base = self.personagens[i]
        copia = json.loads(json.dumps(asdict(base)))
        novo = Personagem(**copia)
        novo.nome = base.nome + " (cópia)"
        self.personagens.append(novo)
        self._refresh_lista()
        self.lst_chars.setCurrentRow(len(self.personagens)-1)

    def _excluir_personagem(self):
        i = self.lst_chars.currentRow()
        if i < 0: return
        del self.personagens[i]
        self._refresh_lista()
        self.stack.setCurrentIndex(0)

    def _refresh_lista(self):
        filtro = self.ed_filtro.text().strip().lower()
        self.lst_chars.clear()
        for p in self.personagens:
            tags = ",".join(p.tags)
            label = f"{p.nome}  —  {p.papel}  [{tags}]" if tags else f"{p.nome}  —  {p.papel}"
            if not filtro or filtro in p.nome.lower() or any(filtro in t.lower() for t in p.tags):
                self.lst_chars.addItem(label)

    def _aplicar_filtro(self, _):
        self._refresh_lista()

    def _trocar_personagem(self, idx):
        if idx < 0 or idx >= len(self.personagens):
            self.stack.setCurrentIndex(0)
            return
        self.idx_atual = idx
        p = self.personagens[idx]
        self._montar_paginas(p)

    def _on_change(self):
        # atualizar resumo e lista
        i = self.idx_atual
        if i >= 0:
            self.page_resumo.refresh()
        self._refresh_lista()

    def _montar_paginas(self, p: Personagem):
        # limpar páginas antigas (mantém o placeholder na posição 0)
        while self.stack.count() > 1:
            w = self.stack.widget(1)
            self.stack.removeWidget(w)
            w.deleteLater()
        # recriar páginas do personagem
        self.page_basico = PageBasico(p, self._on_change)
        self.page_pers = PagePersonalidade(p, self._on_change)
        self.page_atr = PageAtributos(p, self._on_change)
        self.page_rel = PageRelacoes(p, self._on_change)
        self.page_equip = PageEquip(p, self._on_change)
        self.page_arco = PageArco(p, self._on_change)
        self.page_resumo = PageResumo(p)
        for w in [self.page_basico, self.page_pers, self.page_atr, self.page_rel, self.page_equip, self.page_arco, self.page_resumo]:
            wrap = QWidget(); v = QVBoxLayout(wrap); v.setContentsMargins(16,16,16,16); v.addWidget(w)
            self.stack.addWidget(wrap)
        self.stack.setCurrentIndex(1)

    # --- Export/Import ---
    def _exportar_personagem(self):
        i = self.idx_atual
        if i < 0: return
        p = self.personagens[i]
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Personagem", f"{p.nome}.json", "JSON (*.json)")
        if not path: return
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(asdict(p), f, ensure_ascii=False, indent=2)

    def _importar_personagem(self):
        path, _ = QFileDialog.getOpenFileName(self, "Importar Personagem", "", "JSON (*.json)")
        if not path: return
        try:
            data = json.loads(open(path, 'r', encoding='utf-8').read())
            p = Personagem(**data)
            self.personagens.append(p)
            self._refresh_lista()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao importar: {e}")

    def _exportar_todos(self):
        if not self.personagens:
            QMessageBox.information(self, "Aviso", "Nenhum personagem para exportar.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Conjunto", "personagens.json", "JSON (*.json)")
        if not path: return
        data = [asdict(p) for p in self.personagens]
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
