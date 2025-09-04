# modulo_linguas.py
# ruff: noqa
# mypy: ignore-errors
from __future__ import annotations

import sqlite3

from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from . import lingua_repo as repo
from .lingua_engine import apply_rules, detokenize, tokenize, translate
from .lingua_models import Language, Lexeme, LexiconMap, Rule


class ConlangWidget(QWidget):
    def __init__(self, conn: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.conn = conn
        repo.create_schema(self.conn)

        self.langs = repo.list_languages(self.conn)
        if not self.langs:
            lid = repo.add_language(
                self.conn, Language(id=None, name="Nova Língua", code="nvl")
            )
            self.langs = repo.list_languages(self.conn)
        self.active_lang: Language = self.langs[0]

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_lexicon_tab(), "Léxico")
        self.tabs.addTab(self._build_grammar_tab(), "Gramática")
        self.tabs.addTab(self._build_translate_tab(), "Tradutor")

        root = QVBoxLayout(self)
        root.addLayout(self._lang_header())
        root.addWidget(self.tabs)

    # header de línguas
    def _lang_header(self):
        row = QHBoxLayout()
        row.addWidget(QLabel("Língua:"))
        self.cmb_lang = QComboBox()
        for lg in self.langs:
            self.cmb_lang.addItem(f"{lg.name} ({lg.code})", lg.id)
        self.cmb_lang.currentIndexChanged.connect(self._on_lang_change)
        row.addWidget(self.cmb_lang, 1)

        self.ed_new_name = QLineEdit()
        self.ed_new_name.setPlaceholderText("Nova língua (nome)")
        self.ed_new_code = QLineEdit()
        self.ed_new_code.setPlaceholderText("código (3 letras)")
        btn_add = QPushButton("Criar")
        btn_add.clicked.connect(self._create_language)
        row.addWidget(self.ed_new_name)
        row.addWidget(self.ed_new_code)
        row.addWidget(btn_add)
        row.addStretch(1)
        return row

    def _on_lang_change(self, idx: int):
        lang_id = self.cmb_lang.itemData(idx)
        self.active_lang = next(l for l in self.langs if l.id == lang_id)
        self._reload_lexicon()
        self._reload_rules()

    def _create_language(self):
        name = self.ed_new_name.text().strip()
        code = (self.ed_new_code.text().strip() or "new")[:8]
        if not name:
            QMessageBox.warning(self, "Aviso", "Informe um nome para a língua.")
            return
        try:
            repo.add_language(self.conn, Language(id=None, name=name, code=code))
        except Exception as e:
            QMessageBox.critical(
                self, "Erro", f"Não foi possível criar a língua.\\n{e}"
            )
            return
        self.langs = repo.list_languages(self.conn)
        self.cmb_lang.clear()
        for lg in self.langs:
            self.cmb_lang.addItem(f"{lg.name} ({lg.code})", lg.id)
        self.cmb_lang.setCurrentIndex(len(self.langs) - 1)
        self.ed_new_name.clear()
        self.ed_new_code.clear()

    # --- Léxico
    def _build_lexicon_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        row = QHBoxLayout()
        self.ed_lemma = QLineEdit()
        self.ed_lemma.setPlaceholderText("lemma")
        self.ed_pos = QLineEdit()
        self.ed_pos.setPlaceholderText("POS ex.: N/V/ADJ")
        self.ed_pos.setFixedWidth(120)
        self.ed_gloss = QLineEdit()
        self.ed_gloss.setPlaceholderText("glosa")
        self.ed_ipa = QLineEdit()
        self.ed_ipa.setPlaceholderText("IPA")
        self.ed_ipa.setFixedWidth(160)
        self.ed_tags = QLineEdit()
        self.ed_tags.setPlaceholderText("tags;separadas;por;ponto-e-vírgula")
        btn_add = QPushButton("Adicionar")
        btn_add.clicked.connect(self._add_lexeme)
        for wdg in [
            self.ed_lemma,
            self.ed_pos,
            self.ed_gloss,
            self.ed_ipa,
            self.ed_tags,
            btn_add,
        ]:
            row.addWidget(wdg)
        lay.addLayout(row)

        self.tbl_lex = QTableWidget(0, 5)
        self.tbl_lex.setHorizontalHeaderLabels(["Lemma", "POS", "Gloss", "IPA", "Tags"])
        self.tbl_lex.horizontalHeader().setStretchLastSection(True)
        lay.addWidget(self.tbl_lex, 1)

        tr = QHBoxLayout()
        tr.addWidget(QLabel("Mapeamento PT/EN → Conlang:"))
        self.ed_src = QLineEdit()
        self.ed_src.setPlaceholderText("origem (ex.: casa)")
        self.ed_tgt = QLineEdit()
        self.ed_tgt.setPlaceholderText("alvo (ex.: dom)")
        btn_map = QPushButton("Adicionar Mapeamento")
        btn_map.clicked.connect(self._add_map)
        for wdg in [self.ed_src, self.ed_tgt, btn_map]:
            tr.addWidget(wdg)
        lay.addLayout(tr)

        self._reload_lexicon()
        return w

    def _reload_lexicon(self):
        data = repo.list_lexemes(self.conn, self.active_lang.id)
        self.tbl_lex.setRowCount(0)
        for lx in data:
            r = self.tbl_lex.rowCount()
            self.tbl_lex.insertRow(r)
            self.tbl_lex.setItem(r, 0, QTableWidgetItem(lx.lemma))
            self.tbl_lex.setItem(r, 1, QTableWidgetItem(lx.pos))
            self.tbl_lex.setItem(r, 2, QTableWidgetItem(lx.gloss))
            self.tbl_lex.setItem(r, 3, QTableWidgetItem(lx.ipa))
            self.tbl_lex.setItem(r, 4, QTableWidgetItem(lx.tags))

    def _add_lexeme(self):
        if not self.ed_lemma.text().strip() or not self.ed_pos.text().strip():
            QMessageBox.warning(self, "Aviso", "Preencha lemma e POS.")
            return
        repo.add_lexeme(
            self.conn,
            Lexeme(
                id=None,
                language_id=self.active_lang.id,
                lemma=self.ed_lemma.text().strip(),
                pos=self.ed_pos.text().strip(),
                gloss=self.ed_gloss.text().strip(),
                ipa=self.ed_ipa.text().strip(),
                tags=self.ed_tags.text().strip(),
            ),
        )
        for e in [self.ed_lemma, self.ed_pos, self.ed_gloss, self.ed_ipa, self.ed_tags]:
            e.clear()
        self._reload_lexicon()

    def _add_map(self):
        s, t = self.ed_src.text().strip(), self.ed_tgt.text().strip()
        if not s or not t:
            QMessageBox.warning(self, "Aviso", "Informe origem e alvo.")
            return
        repo.add_lexicon_map(
            self.conn,
            LexiconMap(id=None, language_id=self.active_lang.id, source=s, target=t),
        )
        self.ed_src.clear()
        self.ed_tgt.clear()
        QMessageBox.information(self, "OK", "Mapeamento adicionado.")

    # --- Gramática
    def _build_grammar_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        row = QHBoxLayout()
        self.ed_rule_name = QLineEdit()
        self.ed_rule_name.setPlaceholderText("nome")
        self.cmb_scope = QComboBox()
        self.cmb_scope.addItems(["phonology", "orthography", "morphology", "syntax"])
        self.ed_pattern = QLineEdit()
        self.ed_pattern.setPlaceholderText("regex (ex.: c)")
        self.ed_repl = QLineEdit()
        self.ed_repl.setPlaceholderText("replacement (ex.: k)")
        self.ed_env = QLineEdit()
        self.ed_env.setPlaceholderText("/ _ [aou] (opcional)")
        self.spn_pri = QSpinBox()
        self.spn_pri.setRange(0, 9999)
        self.spn_pri.setValue(100)
        self.chk_enabled = QCheckBox("Ativa")
        self.chk_enabled.setChecked(True)
        btn_add = QPushButton("Adicionar")
        btn_add.clicked.connect(self._add_rule)
        for wdg in [
            self.ed_rule_name,
            self.cmb_scope,
            self.ed_pattern,
            self.ed_repl,
            self.ed_env,
            self.spn_pri,
            self.chk_enabled,
            btn_add,
        ]:
            row.addWidget(wdg)
        lay.addLayout(row)

        self.tbl_rules = QTableWidget(0, 6)
        self.tbl_rules.setHorizontalHeaderLabels(
            ["Nome", "Escopo", "Padrão", "Subst.", "Ambiente", "Prioridade"]
        )
        self.tbl_rules.horizontalHeader().setStretchLastSection(True)
        lay.addWidget(self.tbl_rules, 1)

        trow = QHBoxLayout()
        self.txt_in = QLineEdit()
        self.txt_in.setPlaceholderText("Texto para testar regras…")
        btn_apply = QPushButton("Aplicar Regras")
        btn_apply.clicked.connect(self._test_rules)
        self.txt_out = QLineEdit()
        self.txt_out.setReadOnly(True)
        trow.addWidget(self.txt_in, 2)
        trow.addWidget(btn_apply)
        trow.addWidget(self.txt_out, 2)
        lay.addLayout(trow)

        self._reload_rules()
        return w

    def _reload_rules(self):
        rules = repo.list_rules(
            self.conn, self.active_lang.id, scope=None, only_enabled=False
        )
        self.tbl_rules.setRowCount(0)
        for rl in rules:
            r = self.tbl_rules.rowCount()
            self.tbl_rules.insertRow(r)
            self.tbl_rules.setItem(r, 0, QTableWidgetItem(rl.name))
            self.tbl_rules.setItem(r, 1, QTableWidgetItem(rl.scope))
            self.tbl_rules.setItem(r, 2, QTableWidgetItem(rl.pattern))
            self.tbl_rules.setItem(r, 3, QTableWidgetItem(rl.replacement))
            self.tbl_rules.setItem(r, 4, QTableWidgetItem(rl.environment))
            self.tbl_rules.setItem(r, 5, QTableWidgetItem(str(rl.priority)))

    def _add_rule(self):
        if not self.ed_rule_name.text().strip() or not self.ed_pattern.text():
            QMessageBox.warning(self, "Aviso", "Preencha nome e padrão.")
            return
        rl = Rule(
            id=None,
            language_id=self.active_lang.id,
            name=self.ed_rule_name.text().strip(),
            scope=self.cmb_scope.currentText(),
            pattern=self.ed_pattern.text(),
            replacement=self.ed_repl.text(),
            environment=self.ed_env.text(),
            priority=self.spn_pri.value(),
            enabled=self.chk_enabled.isChecked(),
        )
        repo.add_rule(self.conn, rl)
        for e in [self.ed_rule_name, self.ed_pattern, self.ed_repl, self.ed_env]:
            e.clear()
        self.spn_pri.setValue(100)
        self.chk_enabled.setChecked(True)
        self._reload_rules()

    def _test_rules(self):
        text = self.txt_in.text()
        rules = repo.list_rules(
            self.conn, self.active_lang.id, scope=None, only_enabled=True
        )
        self.txt_out.setText(apply_rules(text, rules))

    # --- Tradutor
    def _build_translate_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        self.chk_use_map = QCheckBox("Usar mapeamento PT/EN → Conlang (léxico)")
        self.chk_use_map.setChecked(True)
        self.chk_use_phon = QCheckBox("Aplicar: fonologia")
        self.chk_use_phon.setChecked(True)
        self.chk_use_orth = QCheckBox("Aplicar: ortografia")
        self.chk_use_orth.setChecked(True)
        self.chk_use_morph = QCheckBox("Aplicar: morfologia")
        self.chk_use_morph.setChecked(False)
        opt = QHBoxLayout()
        for c in [
            self.chk_use_map,
            self.chk_use_phon,
            self.chk_use_orth,
            self.chk_use_morph,
        ]:
            opt.addWidget(c)
        opt.addStretch(1)
        lay.addLayout(opt)

        self.ed_src_txt = QTextEdit()
        self.ed_src_txt.setPlaceholderText("Digite o texto origem…")
        self.ed_dst_txt = QTextEdit()
        self.ed_dst_txt.setReadOnly(True)
        btn_tr = QPushButton("Traduzir →")
        btn_tr.clicked.connect(self._do_translate)
        lay.addWidget(self.ed_src_txt, 2)
        lay.addWidget(btn_tr)
        lay.addWidget(self.ed_dst_txt, 2)
        return w

    def _do_translate(self):
        toks = tokenize(self.ed_src_txt.toPlainText())
        if self.chk_use_map.isChecked():
            m = repo.list_lexicon_map(self.conn, self.active_lang.id)
            toks = translate(toks, m)
        out = detokenize(toks)
        scopes = []
        if self.chk_use_phon.isChecked():
            scopes.append("phonology")
        if self.chk_use_orth.isChecked():
            scopes.append("orthography")
        if self.chk_use_morph.isChecked():
            scopes.append("morphology")
        for sc in scopes:
            rules = repo.list_rules(
                self.conn, self.active_lang.id, scope=sc, only_enabled=True
            )
            out = apply_rules(out, rules)
        self.ed_dst_txt.setText(out)
