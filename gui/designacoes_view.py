from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QDateEdit, QMessageBox
)
from PyQt5.QtCore import QDate
from datetime import datetime, timedelta
from modules.designacoes import (
    listar_designacoes, criar_designacao, atualizar_designacao, remover_designacao
)
from modules.territorios import listar_territorios
from modules.saidas import listar_saidas
from gui.notificacoes import sucesso, erro, aviso
from gui.toast_notification import ToastNotification
from utils.logger import log
from database.db_manager import get_connection

class DesignacoesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Designações de Territórios")
        self.setMinimumWidth(900)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.parent_window = parent

        # 🔘 Botões e filtro de meses
        layout_botoes = QHBoxLayout()
        self.btn_gerar_otimizado = QPushButton("Gerar Designação Otimizada")
        self.btn_gerar_otimizado.clicked.connect(self.gerar_designacao_otimizada)

        self.combo_meses = QComboBox()
        self.combo_meses.addItems(["3", "6", "12"])
        self.combo_meses.setCurrentText("3")

        layout_botoes.addWidget(QLabel("Evitar repetição nos últimos"))
        layout_botoes.addWidget(self.combo_meses)
        layout_botoes.addWidget(QLabel("meses"))
        layout_botoes.addStretch()
        layout_botoes.addWidget(self.btn_gerar_otimizado)
        self.layout.addLayout(layout_botoes)

        # 📋 Tabela
        self.tabela = QTableWidget()
        self.layout.addWidget(self.tabela)

        # 🔽 Seletores
        form_layout = QHBoxLayout()
        self.combo_territorio = QComboBox()
        self.combo_saida = QComboBox()
        self.data_inicio = QDateEdit()
        self.data_fim = QDateEdit()
        self.status_combo = QComboBox()

        self.data_inicio.setDate(QDate.currentDate())
        self.data_fim.setDate(QDate.currentDate())
        self.data_inicio.setCalendarPopup(True)
        self.data_fim.setCalendarPopup(True)

        self.status_combo.addItems(["pendente", "concluída", "cancelada"])

        form_layout.addWidget(QLabel("Território:"))
        form_layout.addWidget(self.combo_territorio)
        form_layout.addWidget(QLabel("Saída:"))
        form_layout.addWidget(self.combo_saida)
        form_layout.addWidget(QLabel("Início:"))
        form_layout.addWidget(self.data_inicio)
        form_layout.addWidget(QLabel("Fim:"))
        form_layout.addWidget(self.data_fim)
        form_layout.addWidget(QLabel("Status:"))
        form_layout.addWidget(self.status_combo)
        self.layout.addLayout(form_layout)

        # Botões
        botoes_layout = QHBoxLayout()
        self.btn_adicionar = QPushButton("Adicionar")
        self.btn_atualizar = QPushButton("Atualizar Status")
        self.btn_remover = QPushButton("Remover")

        self.btn_adicionar.clicked.connect(self.adicionar)
        self.btn_atualizar.clicked.connect(self.atualizar)
        self.btn_remover.clicked.connect(self.remover)

        botoes_layout.addWidget(self.btn_adicionar)
        botoes_layout.addWidget(self.btn_atualizar)
        botoes_layout.addWidget(self.btn_remover)
        self.layout.addLayout(botoes_layout)

        self.id_map_territorio = {}
        self.id_map_saida = {}

        self.carregar_seletores()
        self.carregar_tabela()

    def show_toast(self, mensagem, tipo="info"):
        if self.parent_window:
            self.parent_window.show_toast(mensagem, tipo)
            self.parent_window.atualizar_status(mensagem, tipo)

    def carregar_seletores(self):
        self.combo_territorio.clear()
        self.combo_saida.clear()
        self.id_map_territorio = {}
        self.id_map_saida = {}

        for id_, nome, *_ in listar_territorios():
            self.combo_territorio.addItem(nome)
            self.id_map_territorio[nome] = id_

        for id_, data, grupo, dirigente, *_ in listar_saidas():
            descricao = f"{grupo} - {data}"
            self.combo_saida.addItem(descricao)
            self.id_map_saida[descricao] = id_

    def carregar_tabela(self):
        dados = listar_designacoes()
        colunas = ["ID", "Território", "Grupo", "Data Saída", "Início", "Fim", "Status"]

        self.tabela.setColumnCount(len(colunas))
        self.tabela.setHorizontalHeaderLabels(colunas)
        self.tabela.setRowCount(len(dados))

        for i, linha in enumerate(dados):
            for j, valor in enumerate(linha):
                self.tabela.setItem(i, j, QTableWidgetItem(str(valor)))

    def get_linha_selecionada(self):
        linha = self.tabela.currentRow()
        if linha < 0:
            self.show_toast("Selecione uma designação.", "aviso")
            return None
        return linha

    def adicionar(self):
        nome_territorio = self.combo_territorio.currentText()
        desc_saida = self.combo_saida.currentText()

        if not nome_territorio or not desc_saida:
            self.show_toast("Selecione um território e uma saída.", "erro")
            return

        territorio_id = self.id_map_territorio[nome_territorio]
        saida_id = self.id_map_saida[desc_saida]
        inicio = self.data_inicio.date().toString("yyyy-MM-dd")
        fim = self.data_fim.date().toString("yyyy-MM-dd")
        status = self.status_combo.currentText()

        criar_designacao(territorio_id, saida_id, inicio, fim, status)
        log(f"Designação criada: Território '{nome_territorio}', Saída '{desc_saida}'", "info")
        self.show_toast("Designação adicionada com sucesso!", "sucesso")
        self.carregar_tabela()

    def atualizar(self):
        linha = self.get_linha_selecionada()
        if linha is None:
            return
        id_ = int(self.tabela.item(linha, 0).text())
        status = self.status_combo.currentText()
        atualizar_designacao(id_, status=status)
        log(f"Status da designação ID {id_} atualizado para '{status}'", "info")
        self.show_toast("Status atualizado com sucesso!", "sucesso")
        self.carregar_tabela()

    def remover(self):
        linha = self.get_linha_selecionada()
        if linha is None:
            return
        id_ = int(self.tabela.item(linha, 0).text())
        confirma = QMessageBox.question(self, "Confirmar", f"Deseja remover a designação ID {id_}?")
        if confirma == QMessageBox.Yes:
            remover_designacao(id_)
            log(f"Designação ID {id_} removida", "aviso")
            self.show_toast("Designação removida com sucesso.", "sucesso")
            self.carregar_tabela()

    def numero_recente(self, rua_id, numero, meses=3):
        conn = get_connection()
        cur = conn.cursor()

        limite = datetime.now() - timedelta(days=30*meses)
        limite_str = limite.strftime("%Y-%m-%d")

        cur.execute("""
            SELECT COUNT(*)
            FROM numeros
            WHERE rua_id = ?
            AND numero = ?
            AND DATE(data_coleta) >= DATE(?)
        """, (rua_id, numero, limite_str))

        resultado = cur.fetchone()[0]
        conn.close()
        return resultado > 0

    def gerar_designacao_otimizada(self):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT id, nome FROM territorios")
        territorios = cur.fetchall()
        designacoes = []
        meses = int(self.combo_meses.currentText())

        for territorio_id, nome_territorio in territorios:
            cur.execute("SELECT id, nome FROM ruas WHERE territorio_id = ?", (territorio_id,))
            ruas = cur.fetchall()

            for rua_id, nome_rua in ruas:
                cur.execute("""
                    SELECT DISTINCT numero, tipo, status
                    FROM numeros
                    WHERE rua_id = ?
                    ORDER BY data_coleta DESC
                """, (rua_id,))
                numeros = cur.fetchall()

                for numero, tipo, status in numeros:
                    if not self.numero_recente(rua_id, numero, meses=meses):
                        designacoes.append([nome_territorio, nome_rua, numero, tipo, status])
                        break

        conn.close()

        self.tabela.setRowCount(len(designacoes))
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(["Território", "Rua", "Número", "Tipo", "Status"])

        for i, linha in enumerate(designacoes):
            for j, valor in enumerate(linha):
                self.tabela.setItem(i, j, QTableWidgetItem(str(valor)))

        if self.parent_window:
            self.parent_window.atualizar_status("Designação otimizada gerada com sucesso.", "sucesso")
