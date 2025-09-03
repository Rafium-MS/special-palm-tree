"""Simple editor for Regions, Realms and Settlements with route management."""

from __future__ import annotations

from typing import List, cast

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.geo.models import Realm, RealmType, Region, Settlement, SettlementType
from core.geo.routes import RoutesGraph, RouteType


class MainWindow(QMainWindow):
    """Very small UI to manage geographic hierarchy and routes."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Editor Geográfico")
        self.resize(900, 600)

        self.regions: List[Region] = []
        self.routes = RoutesGraph()

        root = QWidget()
        layout = QHBoxLayout(root)
        left = QVBoxLayout()
        self.list_regions = QListWidget()
        left.addWidget(self.list_regions)
        btn_region = QPushButton("Adicionar Região")
        btn_realm = QPushButton("Adicionar Reino")
        btn_set = QPushButton("Adicionar Cidade")
        btn_route = QPushButton("Adicionar Rota")
        for btn in [btn_region, btn_realm, btn_set, btn_route]:
            left.addWidget(btn)
        layout.addLayout(left)

        self.detail = QLabel("<i>Nenhuma região selecionada</i>")
        self.detail.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.detail, 1)

        self.setCentralWidget(root)

        self.list_regions.currentRowChanged.connect(self._refresh_detail)
        btn_region.clicked.connect(self._add_region)
        btn_realm.clicked.connect(self._add_realm)
        btn_set.clicked.connect(self._add_settlement)
        btn_route.clicked.connect(self._add_route)

    # ------------------------------------------------------------------
    def _add_region(self) -> None:
        name, ok = QInputDialog.getText(self, "Nova Região", "Nome:")
        if not ok or not name:
            return
        region = Region(name=name)
        self.regions.append(region)
        self.list_regions.addItem(region.name)
        # permite adicionar reino logo após criação
        self._add_realm(len(self.regions) - 1)

    def _add_realm(self, region_index: int | None = None) -> None:
        if region_index is None:
            region_index = self.list_regions.currentRow()
        if region_index < 0 or region_index >= len(self.regions):
            return
        reg = self.regions[region_index]
        name, ok = QInputDialog.getText(self, "Novo Reino/Império", "Nome:")
        if not ok or not name:
            return
        tipo, ok = QInputDialog.getItem(
            self, "Tipo", "Tipo:", ["Reino", "Imperio"], 0, False
        )
        if not ok:
            return
        realm = Realm(name=name, tipo=cast(RealmType, tipo))
        reg.add_realm(realm)
        # permite adicionar cidade após criação do reino
        self._add_settlement(region_index, len(reg.realms) - 1)
        self._refresh_detail(region_index)

    def _add_settlement(
        self, region_index: int | None = None, realm_index: int | None = None
    ) -> None:
        if region_index is None:
            region_index = self.list_regions.currentRow()
        if region_index < 0 or region_index >= len(self.regions):
            return
        reg = self.regions[region_index]
        if not reg.realms:
            QMessageBox.information(self, "Aviso", "Adicione um reino primeiro.")
            return
        if realm_index is None:
            nomes = [r.name for r in reg.realms]
            nome, ok = QInputDialog.getItem(
                self, "Reino", "Escolha o reino:", nomes, 0, False
            )
            if not ok:
                return
            realm = reg.realms[nomes.index(nome)]
        else:
            realm = reg.realms[realm_index]
        name, ok = QInputDialog.getText(self, "Nova Cidade/Aldeia", "Nome:")
        if not ok or not name:
            return
        tipo, ok = QInputDialog.getItem(
            self, "Tipo", "Tipo:", ["Cidade", "Aldeia"], 0, False
        )
        if not ok:
            return
        settlement = Settlement(name=name, tipo=cast(SettlementType, tipo))
        realm.add_settlement(settlement)
        self.routes.add_settlement(settlement.name)
        self._refresh_detail(region_index)

    def _all_settlement_names(self) -> List[str]:
        names: List[str] = []
        for reg in self.regions:
            for realm in reg.realms:
                for s in realm.settlements:
                    names.append(s.name)
        return names

    def _add_route(self) -> None:
        names = self._all_settlement_names()
        if len(names) < 2:
            QMessageBox.information(
                self, "Aviso", "Crie ao menos duas cidades para ligar."
            )
            return
        origem, ok = QInputDialog.getItem(
            self, "Origem", "Cidade de origem:", names, 0, False
        )
        if not ok:
            return
        destino, ok = QInputDialog.getItem(
            self, "Destino", "Cidade de destino:", names, 0, False
        )
        if not ok:
            return
        tipo, ok = QInputDialog.getItem(
            self,
            "Tipo de Rota",
            "Tipo:",
            ["terrestre", "fluvial", "maritimo"],
            0,
            False,
        )
        if not ok:
            return
        self.routes.add_route(origem, destino, cast(RouteType, tipo))
        self._refresh_detail(self.list_regions.currentRow())

    def _refresh_detail(self, idx: int) -> None:
        if idx < 0 or idx >= len(self.regions):
            self.detail.setText("<i>Nenhuma região selecionada</i>")
            return
        reg = self.regions[idx]
        lines = [f"<h2>{reg.name}</h2>"]
        for realm in reg.realms:
            lines.append(f"<b>{realm.tipo}: {realm.name}</b>")
            for s in realm.settlements:
                lines.append(f"- {s.tipo}: {s.name}")
        rotas = list(self.routes.routes())
        if rotas:
            lines.append("<h3>Rotas</h3>")
            for a, b, t in rotas:
                lines.append(f"{a} ↔ {b} ({t})")
        self.detail.setText("<br>".join(lines))


def main() -> None:
    app = QApplication([])
    w = MainWindow()
    w.show()
    app.exec_()


if __name__ == "__main__":  # pragma: no cover - manual execution
    main()
