# -*- coding: utf-8 -*-
"""
Construtor de Linha do Tempo (PyQt5)

Objetivo: protótipo navegável para criar cronologias (eras, eventos,
dependências) para mundos de fantasia e ficção científica.

Como executar:
  pip install PyQt5
  python linha_do_tempo.py
"""
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
import json
import sys

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSplitter, QListWidget,
    QStackedWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QTextEdit, QComboBox, QPushButton, QSpinBox, QDoubleSpinBox, QGroupBox,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QFileDialog, QMessageBox,
    QInputDialog
)
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsItem
from PyQt5.QtGui import QPen, QBrush, QColor, QImage, QPainter
from PyQt5.QtSvg import QSvgGenerator

# ----------------------------- Estado -----------------------------
@dataclass
class Era:
    nome: str
    inicio: int  # marco numérico (ex.: ano)
    fim: int     # exclusivo (fim > inicio)
    descricao: str = ""
    cor: str = ""  # placeholder (não utilizado no wireframe)

from core.timeline.service import Evento, TimelineService, timeline_service

@dataclass
class Timeline:
    nome: str = ""
    escala: str = "Anos"  # Dias, Meses, Anos, Séculos
    zero_significado: str = "Fundação do Reino"
    offset_zero: int = 0  # onde o zero cai no seu calendário
    eras: List[Era] = field(default_factory=list)
    eventos: List[Evento] = field(default_factory=list)
    notas: str = ""
    nascimentos: Dict[str, int] = field(default_factory=dict)  # id -> ano de nascimento

# ----------------------------- Templates -----------------------------
TEMPLATES_TL: Dict[str, Dict] = {
    "Reino em Formação": {
        "escala": "Anos",
        "zero_significado": "Coroação do Primeiro Rei",
        "eras": [
            {"nome": "Guerras Tribais", "inicio": -80, "fim": -2, "descricao": "Clãs disputam territórios."},
            {"nome": "Unificação", "inicio": -2, "fim": 20, "descricao": "Ascensão do clã vencedor."},
            {"nome": "Pax Regnum", "inicio": 20, "fim": 120, "descricao": "Estabilidade e reformas."}
        ],
        "eventos": [
            {"titulo": "Batalha do Vale", "instante": -10, "tipo": "Guerra", "importancia": 4},
            {"titulo": "Coroação", "instante": 0, "tipo": "Política", "importancia": 5},
            {"titulo": "Reforma Agrária", "instante": 25, "tipo": "Economia", "importancia": 3}
        ]
    },
    "Era das Explorações": {
        "escala": "Anos",
        "zero_significado": "Primeira Caravela ao Oeste",
        "eras": [
            {"nome": "Pré-Exploração", "inicio": -50, "fim": 0, "descricao": "Preparativos e mapas."},
            {"nome": "Explorações", "inicio": 0, "fim": 80, "descricao": "Rotas e descobertas."}
        ],
        "eventos": [
            {"titulo": "Descoberta do Arquipélago", "instante": 12, "tipo": "Descoberta", "importancia": 4},
            {"titulo": "Tratado das Rotas", "instante": 40, "tipo": "Política", "importancia": 3}
        ]
    },
    "Colônia Interestelar": {
        "escala": "Anos",
        "zero_significado": "Pouso da Arca",
        "eras": [
            {"nome": "Viagem", "inicio": -120, "fim": 0, "descricao": "Séculos a bordo."},
            {"nome": "Assentamento", "inicio": 0, "fim": 60, "descricao": "Cúpulas e biosferas."},
            {"nome": "Autonomia", "inicio": 60, "fim": 200, "descricao": "Independência da colônia."}
        ],
        "eventos": [
            {"titulo": "Primeira Cúpula", "instante": 5, "tipo": "Tecnologia", "importancia": 5},
            {"titulo": "Revolta dos Mineradores", "instante": 72, "tipo": "Política", "importancia": 4}
        ]
    }
}

# ----------------------------- Páginas -----------------------------
class PageBasico(QWidget):
    def __init__(self, tl: Timeline, on_change):
        super().__init__()
        self.tl = tl
        self.on_change = on_change
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Parâmetros Básicos</h2>"))
        form = QFormLayout()
        self.ed_nome = QLineEdit(self.tl.nome)
        self.cb_escala = QComboBox(); self.cb_escala.addItems(["Dias", "Meses", "Anos", "Séculos"]); self.cb_escala.setCurrentText(self.tl.escala)
        self.ed_zero = QLineEdit(self.tl.zero_significado)
        self.sp_offset = QSpinBox(); self.sp_offset.setRange(-1000000, 1000000); self.sp_offset.setValue(self.tl.offset_zero)
        form.addRow("Nome:", self.ed_nome)
        form.addRow("Escala:", self.cb_escala)
        form.addRow("Zero significa:", self.ed_zero)
        form.addRow("Offset do zero:", self.sp_offset)
        layout.addLayout(form)
        btn = QPushButton("Salvar Básico")
        btn.clicked.connect(self.save)
        layout.addWidget(btn)
        layout.addStretch(1)

    def save(self):
        self.tl.nome = self.ed_nome.text().strip()
        self.tl.escala = self.cb_escala.currentText()
        self.tl.zero_significado = self.ed_zero.text().strip()
        self.tl.offset_zero = self.sp_offset.value()
        self.on_change()

class PageEras(QWidget):
    def __init__(self, tl: Timeline, on_change):
        super().__init__()
        self.tl = tl
        self.on_change = on_change
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Eras</h2>"))
        self.tbl = QTableWidget(0, 4)
        self.tbl.setHorizontalHeaderLabels(["Nome", "Início", "Fim", "Descrição"])
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.setEditTriggers(QAbstractItemView.AllEditTriggers)
        layout.addWidget(self.tbl)
        hl = QHBoxLayout()
        btn_add = QPushButton("Adicionar Era")
        btn_del = QPushButton("Remover Selecionada")
        hl.addWidget(btn_add); hl.addWidget(btn_del); hl.addStretch(1)
        layout.addLayout(hl)
        btn_save = QPushButton("Salvar Eras")
        btn_save.clicked.connect(self.save)
        layout.addWidget(btn_save)
        layout.addStretch(1)
        btn_add.clicked.connect(self._add)
        btn_del.clicked.connect(self._del)
        self._load()

    def _load(self):
        self.tbl.setRowCount(0)
        for e in sorted(self.tl.eras, key=lambda x: (x.inicio, x.fim)):
            r = self.tbl.rowCount(); self.tbl.insertRow(r)
            self.tbl.setItem(r, 0, QTableWidgetItem(e.nome))
            self.tbl.setItem(r, 1, QTableWidgetItem(str(e.inicio)))
            self.tbl.setItem(r, 2, QTableWidgetItem(str(e.fim)))
            self.tbl.setItem(r, 3, QTableWidgetItem(e.descricao))

    def _add(self):
        r = self.tbl.rowCount(); self.tbl.insertRow(r)
        self.tbl.setItem(r, 0, QTableWidgetItem("Nova Era"))
        self.tbl.setItem(r, 1, QTableWidgetItem("0"))
        self.tbl.setItem(r, 2, QTableWidgetItem("10"))
        self.tbl.setItem(r, 3, QTableWidgetItem("Descrição"))

    def _del(self):
        r = self.tbl.currentRow()
        if r >= 0:
            self.tbl.removeRow(r)

    def save(self):
        eras = []
        for r in range(self.tbl.rowCount()):
            try:
                nome = self.tbl.item(r, 0).text() if self.tbl.item(r, 0) else ""
                inicio = int(self.tbl.item(r, 1).text())
                fim = int(self.tbl.item(r, 2).text())
                desc = self.tbl.item(r, 3).text() if self.tbl.item(r, 3) else ""
                if fim <= inicio:
                    raise ValueError("Fim deve ser maior que início")
                eras.append(Era(nome, inicio, fim, desc))
            except Exception as err:
                QMessageBox.critical(self, "Erro", f"Linha {r+1}: {err}")
                return
        self.tl.eras = eras
        self.on_change()

class PageEventos(QWidget):
    def __init__(self, tl: Timeline, on_change):
        super().__init__()
        self.tl = tl
        self.on_change = on_change
        self.service = timeline_service
        # sincroniza serviço com eventos do timeline atual
        self.service.eventos = self.tl.eventos

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Eventos</h2>"))
        self.tbl = QTableWidget(0, 9)
        self.tbl.setHorizontalHeaderLabels([
            "Título",
            "Instante",
            "Tipo",
            "Importância",
            "Escopo",
            "Era",
            "Personagens (IDs ,)",
            "Lugares (IDs ,)",
            "Tags (,)",
        ])
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.setEditTriggers(QAbstractItemView.AllEditTriggers)
        layout.addWidget(self.tbl)
        hl = QHBoxLayout()
        btn_add = QPushButton("Adicionar Evento")
        btn_del = QPushButton("Remover Selecionado")
        btn_view = QPushButton("Ver Ligações")
        hl.addWidget(btn_add); hl.addWidget(btn_del); hl.addWidget(btn_view); hl.addStretch(1)
        layout.addLayout(hl)
        btn_save = QPushButton("Salvar Eventos")
        btn_save.clicked.connect(self.save)
        layout.addWidget(btn_save)
        layout.addStretch(1)
        btn_add.clicked.connect(self._add)
        btn_del.clicked.connect(self._del)
        btn_view.clicked.connect(self._ver_ligacoes)
        self._load()

    def _load(self):
        self.tbl.setRowCount(0)
        self.service.sort_events()
        for ev in self.service.eventos:
            r = self.tbl.rowCount(); self.tbl.insertRow(r)
            self.tbl.setItem(r, 0, QTableWidgetItem(ev.titulo))
            self.tbl.setItem(r, 1, QTableWidgetItem(str(ev.instante)))
            self.tbl.setItem(r, 2, QTableWidgetItem(ev.tipo))
            self.tbl.setItem(r, 3, QTableWidgetItem(str(ev.importancia)))
            self.tbl.setItem(r, 4, QTableWidgetItem(ev.escopo))
            self.tbl.setItem(r, 5, QTableWidgetItem(ev.era))
            self.tbl.setItem(r, 6, QTableWidgetItem(",".join(ev.personagens)))
            self.tbl.setItem(r, 7, QTableWidgetItem(",".join(ev.lugares)))
            self.tbl.setItem(r, 8, QTableWidgetItem(",".join(ev.tags)))

    def _add(self):
        r = self.tbl.rowCount(); self.tbl.insertRow(r)
        self.tbl.setItem(r, 0, QTableWidgetItem("Novo Evento"))
        self.tbl.setItem(r, 1, QTableWidgetItem("0"))
        self.tbl.setItem(r, 2, QTableWidgetItem("Geral"))
        self.tbl.setItem(r, 3, QTableWidgetItem("3"))
        self.tbl.setItem(r, 4, QTableWidgetItem("local"))
        self.tbl.setItem(r, 5, QTableWidgetItem(""))
        self.tbl.setItem(r, 6, QTableWidgetItem(""))
        self.tbl.setItem(r, 7, QTableWidgetItem(""))
        self.tbl.setItem(r, 8, QTableWidgetItem(""))

    def _del(self):
        r = self.tbl.currentRow()
        if r >= 0:
            self.tbl.removeRow(r)

    def _ver_ligacoes(self):
        r = self.tbl.currentRow()
        if r < 0:
            return
        pers = self.tbl.item(r, 6).text() if self.tbl.item(r, 6) else ""
        lugs = self.tbl.item(r, 7).text() if self.tbl.item(r, 7) else ""
        QMessageBox.information(
            self,
            "Ligações",
            f"Personagens: {pers or '-'}\nLugares: {lugs or '-'}",
        )

    def save(self):
        self.service.eventos.clear()
        eras_nomes = {e.nome for e in self.tl.eras}
        for r in range(self.tbl.rowCount()):
            try:
                titulo = self.tbl.item(r, 0).text() if self.tbl.item(r, 0) else ""
                instante = int(self.tbl.item(r, 1).text())
                tipo = self.tbl.item(r, 2).text() if self.tbl.item(r, 2) else "Geral"
                importancia = int(self.tbl.item(r, 3).text())
                escopo = self.tbl.item(r, 4).text() if self.tbl.item(r, 4) else "local"
                era = self.tbl.item(r, 5).text() if self.tbl.item(r, 5) else ""
                pers = [
                    e.strip()
                    for e in (self.tbl.item(r, 6).text() or "").split(",")
                    if e.strip()
                ]
                lugs = [
                    e.strip()
                    for e in (self.tbl.item(r, 7).text() or "").split(",")
                    if e.strip()
                ]
                tags = [
                    t.strip()
                    for t in (self.tbl.item(r, 8).text() or "").split(",")
                    if t.strip()
                ]
                if era and (era not in eras_nomes):
                    raise ValueError(f"Era '{era}' não existe")
                for pid in pers:
                    nasc = self.tl.nascimentos.get(pid)
                    if nasc is not None and instante < nasc:
                        raise ValueError(
                            f"Personagem '{pid}' aparece antes de nascer"
                        )
                self.service.add_event(
                    Evento(
                        titulo=titulo,
                        instante=instante,
                        tipo=tipo,
                        importancia=importancia,
                        escopo=escopo,
                        era=era,
                        tags=tags,
                        personagens=pers,
                        lugares=lugs,
                    )
                )
            except Exception as err:
                QMessageBox.critical(self, "Erro", f"Linha {r+1}: {err}")
                return
        conflicts = self.service.resolve_conflicts()
        if conflicts:
            QMessageBox.critical(
                self,
                "Erro",
                f"IDs de eventos com datas conflitantes: {', '.join(conflicts)}",
            )
            return
        # sincroniza lista do timeline
        self.tl.eventos = self.service.eventos
        self.on_change()

class PageDependencias(QWidget):
    def __init__(self, tl: Timeline, on_change):
        super().__init__()
        self.tl = tl
        self.on_change = on_change
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Dependências / Causa e Efeito</h2>"))
        self.tbl = QTableWidget(0, 2)
        self.tbl.setHorizontalHeaderLabels(["Evento", "Depende de (título)"])
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.setEditTriggers(QAbstractItemView.AllEditTriggers)
        layout.addWidget(self.tbl)
        hl = QHBoxLayout()
        btn_add = QPushButton("Adicionar")
        btn_del = QPushButton("Remover")
        hl.addWidget(btn_add); hl.addWidget(btn_del); hl.addStretch(1)
        layout.addLayout(hl)
        btn_save = QPushButton("Salvar Dependências")
        btn_save.clicked.connect(self.save)
        layout.addWidget(btn_save)
        layout.addStretch(1)

        btn_add.clicked.connect(self._add)
        btn_del.clicked.connect(self._del)
        self._load()

    def _load(self):
        self.tbl.setRowCount(0)
        titulos = [e.titulo for e in self.tl.eventos]
        for ev in self.tl.eventos:
            if not ev.depende_de:
                continue
            for dep in ev.depende_de:
                r = self.tbl.rowCount(); self.tbl.insertRow(r)
                self.tbl.setItem(r, 0, QTableWidgetItem(ev.titulo))
                self.tbl.setItem(r, 1, QTableWidgetItem(dep))

    def _add(self):
        r = self.tbl.rowCount(); self.tbl.insertRow(r)
        self.tbl.setItem(r, 0, QTableWidgetItem("Evento"))
        self.tbl.setItem(r, 1, QTableWidgetItem("Depende de"))

    def _del(self):
        r = self.tbl.currentRow()
        if r >= 0:
            self.tbl.removeRow(r)

    def save(self):
        deps_map: Dict[str, List[str]] = {e.titulo: [] for e in self.tl.eventos}
        titulos = set(deps_map.keys())
        for r in range(self.tbl.rowCount()):
            ev = self.tbl.item(r, 0).text() if self.tbl.item(r, 0) else ""
            dep = self.tbl.item(r, 1).text() if self.tbl.item(r, 1) else ""
            if ev not in titulos:
                QMessageBox.critical(self, "Erro", f"Linha {r+1}: evento '{ev}' não existe")
                return
            if dep and dep not in titulos:
                QMessageBox.critical(self, "Erro", f"Linha {r+1}: dependência '{dep}' não existe")
                return
            if dep:
                deps_map[ev].append(dep)
        # aplica
        for e in self.tl.eventos:
            e.depende_de = deps_map.get(e.titulo, [])
        self.on_change()
class PageVisualizacao(QWidget):
    """
    Visualização simples tipo Gantt:
      - Barras horizontais para ERAS (posicionadas por início/fim)
      - Marcadores para EVENTOS (pontos no eixo do tempo)
    """
    def __init__(self, tl: Timeline):
        super().__init__()
        self.tl = tl
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(self.view.renderHints())
        self.btn_redraw = QPushButton("Atualizar")
        self.btn_redraw.clicked.connect(self.redraw)
        self.sp_ini = QSpinBox(); self.sp_ini.setRange(-1000000, 1000000)
        self.sp_fim = QSpinBox(); self.sp_fim.setRange(-1000000, 1000000)
        self.ed_filtro = QLineEdit()

        t0, t1 = self._range_tempo()
        self.sp_ini.setValue(t0)
        self.sp_fim.setValue(t1)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Visualização (Gantt)</h2>"))
        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("Início:"))
        ctrl.addWidget(self.sp_ini)
        ctrl.addWidget(QLabel("Fim:"))
        ctrl.addWidget(self.sp_fim)
        ctrl.addWidget(QLabel("Entidade:"))
        ctrl.addWidget(self.ed_filtro)
        ctrl.addWidget(self.btn_redraw)
        layout.addLayout(ctrl)
        layout.addWidget(self.view, 1)
        self.redraw()

    def export_png(self, path: str):
        """Exporta a cena atual como imagem PNG."""
        rect = self.scene.sceneRect()
        image = QImage(int(rect.width()), int(rect.height()), QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        painter = QPainter(image)
        self.scene.render(painter)
        painter.end()
        image.save(path, "PNG")

    def export_svg(self, path: str):
        """Exporta a cena atual como SVG vetorial."""
        rect = self.scene.sceneRect()
        generator = QSvgGenerator()
        generator.setFileName(path)
        generator.setSize(QSize(int(rect.width()), int(rect.height())))
        generator.setViewBox(rect.toRect())
        painter = QPainter(generator)
        self.scene.render(painter)
        painter.end()

    def _range_tempo(self):
        xs = []
        for e in self.tl.eras:
            xs.append(e.inicio)
            xs.append(e.fim)
        for ev in self.tl.eventos:
            xs.append(ev.instante)
        if not xs:
            xs = [0, 10]
        lo = min(xs)
        hi = max(xs)
        if lo == hi:
            lo -= 5; hi += 5
        # margem nas pontas
        span = hi - lo
        return lo - max(1, int(0.05*span)), hi + max(1, int(0.05*span))

    def redraw(self):
        self.scene.clear()

        # parâmetros de layout
        left_pad = 100
        top_pad = 40
        right_pad = 30
        row_h = 28
        era_bar_h = 16
        width = 1000
        height = max(300, top_pad + 80 + max(len(self.tl.eras), 1)*row_h)

        self.view.setSceneRect(0, 0, width, height)

        t0, t1 = self.sp_ini.value(), self.sp_fim.value()
        span = float(t1 - t0)
        if span <= 0:
            span = 1.0
            t1 = t0 + 1

        def xmap(x):
            return left_pad + (width - left_pad - right_pad) * ((x - t0) / span)

        pen_axis = QPen(QColor("#888"))
        pen_era = QPen(QColor("#3b82f6"))  # azul
        brush_era = QBrush(QColor(59, 130, 246, 90))
        pen_event = QPen(QColor("#ef4444"))  # vermelho
        brush_event = QBrush(QColor("#ef4444"))

        # eixo do tempo
        y_axis = top_pad + 20 + len(self.tl.eras)*row_h
        self.scene.addLine(left_pad, y_axis, width - right_pad, y_axis, pen_axis)

        # ticks básicos (5 divisões)
        for i in range(6):
            tx = t0 + (span * i/5.0)
            px = xmap(tx)
            self.scene.addLine(px, y_axis-4, px, y_axis+4, pen_axis)
            lbl = self.scene.addText(str(int(tx)))
            lbl.setDefaultTextColor(QColor("#666"))
            lbl.setPos(px-10, y_axis+6)

        # desenhar ERAS (cada uma numa linha)
        for idx, era in enumerate(sorted(self.tl.eras, key=lambda e: (e.inicio, e.fim))):
            y = top_pad + idx*row_h
            x0 = xmap(era.inicio)
            x1 = xmap(era.fim)
            rect = self.scene.addRect(x0, y, max(2.0, x1-x0), era_bar_h, pen_era, brush_era)
            # label da era
            label = self.scene.addText(era.nome)
            label.setDefaultTextColor(QColor("#1f2937"))
            label.setPos(10, y - 2)

        # eventos como marcadores (círculos) sobre o eixo
        filtro = self.ed_filtro.text().strip().lower()

        def inv_xmap(px: float) -> float:
            return t0 + (px - left_pad) * span / (width - left_pad - right_pad)

        class EventItem(QGraphicsEllipseItem):
            def __init__(self, ev: Evento, x: float, y: float, r: float):
                super().__init__(x - r, y - r, 2 * r, 2 * r)
                self.ev = ev
                self.r = r
                self.y_fixed = y - r
                self.setPen(pen_event)
                self.setBrush(brush_event)
                self.setFlag(QGraphicsItem.ItemIsMovable, True)
                self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

            def itemChange(self, change, value):
                if change == QGraphicsItem.ItemPositionChange:
                    value.setY(self.y_fixed)
                    self.ev.instante = int(round(inv_xmap(value.x() + self.r)))
                    return value
                return super().itemChange(change, value)

        for ev in sorted(self.tl.eventos, key=lambda e: (e.instante, e.titulo)):
            all_links = [s.lower() for s in (ev.personagens + ev.lugares)]
            if filtro and filtro not in all_links:
                continue
            x = xmap(ev.instante)
            r = 5
            item = EventItem(ev, x, y_axis, r)
            self.scene.addItem(item)
            tag = f"{ev.titulo} ({ev.instante})"
            lbl = self.scene.addText(tag)
            lbl.setDefaultTextColor(QColor("#7f1d1d"))
            lbl.setPos(x + 6, y_axis - 18)

class PageResumo(QWidget):
    def __init__(self, tl: Timeline):
        super().__init__()
        self.tl = tl
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Resumo</h2>"))
        self.tx = QTextEdit(); self.tx.setReadOnly(True)
        layout.addWidget(self.tx)
        self.refresh()

    def refresh(self):
        # ordena e monta um JSON legível
        tl = asdict(self.tl)
        tl["eras"] = sorted(tl["eras"], key=lambda e: (e["inicio"], e["fim"]))
        tl["eventos"] = sorted(tl["eventos"], key=lambda e: (e["instante"], e["titulo"]))
        self.tx.setPlainText(json.dumps(tl, indent=2, ensure_ascii=False))

# ----------------------------- Janela Principal -----------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Construtor de Linha do Tempo")
        self.resize(1200, 720)

        self.timelines: List[Timeline] = []
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
        vleft.addWidget(QLabel("Linhas do Tempo"))
        vleft.addWidget(self.lst, 1)
        vleft.addLayout(hl)

        # direita
        self.stack = QStackedWidget()
        self.lbl_empty = QLabel("<i>Crie ou selecione uma linha do tempo…</i>")
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
        act_exp = m.addAction("Exportar (JSON)")
        act_exp.triggered.connect(self._exportar)
        act_imp = m.addAction("Importar (JSON)")
        act_imp.triggered.connect(self._importar)
        m.addSeparator()
        act_png = m.addAction("Exportar visualização (PNG)")
        act_png.triggered.connect(self._exportar_png)
        act_svg = m.addAction("Exportar visualização (SVG)")
        act_svg.triggered.connect(self._exportar_svg)
        m.addSeparator()
        act_all = m.addAction("Exportar todas (JSON)")
        act_all.triggered.connect(self._exportar_todas)

    # --- CRUD ---
    def _nova(self):
        t = Timeline(nome=f"Linha do Tempo {len(self.timelines)+1}")
        self.timelines.append(t)
        self._refresh_lista()
        self.lst.setCurrentRow(len(self.timelines)-1)

    def _novo_de_template(self):
        if not TEMPLATES_TL:
            QMessageBox.information(self, "Templates", "Nenhum template disponível.")
            return
        items = list(TEMPLATES_TL.keys())
        sel, ok = QInputDialog.getItem(self, "Novo de Template", "Escolha um template:", items, 0, False)
        if not ok:
            return
        base = TEMPLATES_TL[sel]
        t = Timeline(nome=sel)
        t.escala = base.get("escala", t.escala)
        t.zero_significado = base.get("zero_significado", t.zero_significado)
        t.eras = [Era(**e) for e in base.get("eras", [])]
        t.eventos = [Evento(**ev) for ev in base.get("eventos", [])]
        self.timelines.append(t)
        self._refresh_lista()
        self.lst.setCurrentRow(len(self.timelines)-1)

    def _duplicar(self):
        i = self.lst.currentRow()
        if i < 0: return
        base = self.timelines[i]
        copia = json.loads(json.dumps(asdict(base)))
        novo = Timeline(
            nome=base.nome + " (cópia)",
            escala=copia.get("escala", base.escala),
            zero_significado=copia.get("zero_significado", base.zero_significado),
            offset_zero=copia.get("offset_zero", base.offset_zero),
            eras=[Era(**e) for e in copia.get("eras", [])],
            eventos=[Evento(**ev) for ev in copia.get("eventos", [])],
            notas=copia.get("notas", base.notas)
        )
        self.timelines.append(novo)
        self._refresh_lista()
        self.lst.setCurrentRow(len(self.timelines)-1)

    def _excluir(self):
        i = self.lst.currentRow()
        if i < 0: return
        del self.timelines[i]
        self._refresh_lista()
        self.stack.setCurrentIndex(0)

    def _refresh_lista(self):
        self.lst.clear()
        for t in self.timelines:
            self.lst.addItem(t.nome or "(sem nome)")

    def _trocar(self, idx):
        if idx < 0 or idx >= len(self.timelines):
            self.stack.setCurrentIndex(0)
            return
        self.idx_atual = idx
        t = self.timelines[idx]
        self._montar_paginas(t)

    def _montar_paginas(self, t: Timeline):
        timeline_service.eventos = t.eventos
        while self.stack.count() > 1:
            w = self.stack.widget(1)
            self.stack.removeWidget(w)
            w.deleteLater()
        self.page_basico = PageBasico(t, self._on_change)
        self.page_eras = PageEras(t, self._on_change)
        self.page_ev = PageEventos(t, self._on_change)
        self.page_dep = PageDependencias(t, self._on_change)
        self.page_vis = PageVisualizacao(t)  # << NOVO
        self.page_res = PageResumo(t)

        for w in [self.page_basico, self.page_eras, self.page_ev, self.page_dep, self.page_vis, self.page_res]:
            wrap = QWidget();
            v = QVBoxLayout(wrap);
            v.setContentsMargins(16, 16, 16, 16);
            v.addWidget(w)
            self.stack.addWidget(wrap)
        self.stack.setCurrentIndex(1)

    def _on_change(self):
        if self.idx_atual >= 0:
            self.page_res.refresh()
            if hasattr(self, "page_vis"):
                self.page_vis.redraw()

    # --- Export/Import ---
    def _exportar_png(self):
        i = self.idx_atual
        if i < 0 or not hasattr(self, "page_vis"):
            return
        t = self.timelines[i]
        path, _ = QFileDialog.getSaveFileName(self, "Exportar Visualização", f"{t.nome}.png", "PNG (*.png)")
        if not path:
            return
        self.page_vis.export_png(path)

    def _exportar_svg(self):
        i = self.idx_atual
        if i < 0 or not hasattr(self, "page_vis"):
            return
        t = self.timelines[i]
        path, _ = QFileDialog.getSaveFileName(self, "Exportar Visualização", f"{t.nome}.svg", "SVG (*.svg)")
        if not path:
            return
        self.page_vis.export_svg(path)

    def _exportar(self):
        i = self.idx_atual
        if i < 0: return
        t = self.timelines[i]
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Linha do Tempo", f"{t.nome}.json", "JSON (*.json)")
        if not path: return
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(asdict(t), f, ensure_ascii=False, indent=2)

    def _importar(self):
        path, _ = QFileDialog.getOpenFileName(self, "Importar Linha do Tempo", "", "JSON (*.json)")
        if not path: return
        try:
            data = json.loads(open(path, 'r', encoding='utf-8').read())
            t = Timeline(
                nome=data.get('nome', ''),
                escala=data.get('escala', 'Anos'),
                zero_significado=data.get('zero_significado', ''),
                offset_zero=data.get('offset_zero', 0),
                eras=[Era(**e) for e in data.get('eras', [])],
                eventos=[Evento(**ev) for ev in data.get('eventos', [])],
                notas=data.get('notas', '')
            )
            self.timelines.append(t)
            self._refresh_lista()
        except Exception as err:
            QMessageBox.critical(self, "Erro", f"Falha ao importar: {err}")

    def _exportar_todas(self):
        if not self.timelines:
            QMessageBox.information(self, "Aviso", "Nenhuma linha do tempo para exportar.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Conjunto", "linhas_do_tempo.json", "JSON (*.json)")
        if not path: return
        data = [asdict(t) for t in self.timelines]
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
