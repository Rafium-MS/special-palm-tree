# -*- coding: utf-8 -*-
"""
Editor de Textos para Escritores (PyQt5)

▶ Layout: divisor central (splitter)
   • Esquerda: árvore de arquivos da pasta de trabalho
   • Direita: editor de texto

Recursos:
- Escolher/alterar pasta de trabalho (padrão: ./workspace)
- Abrir arquivos clicando na árvore
- Novo arquivo / Nova pasta
- Salvar, Salvar Como
- Renomear, Excluir (com confirmação)
- Autosave opcional a cada 30s (cria .autosave/<nome>.bak)
- Contador de palavras e caracteres
- Barra de busca (Ctrl+F) com próximo/anterior
- Tema claro/escuro (toggle)
- Atalhos: Ctrl+N, Ctrl+S, Ctrl+Shift+S, Ctrl+F, Ctrl+W
- Confirma saída/alteração sem salvar

Requisitos: PyQt5
pip install PyQt5

Execução:
python main.py
"""
import os
import sys
import json
import shutil
import re
from pathlib import Path

from PyQt5.QtCore import Qt, QTimer, QModelIndex, QRegExp
from PyQt5.QtGui import (
    QCloseEvent,
    QKeySequence,
    QSyntaxHighlighter,
    QTextCharFormat,
    QColor,
    QFont,
    QTextDocument,
    QTextCursor,
    QIcon,
    QStandardItem,
    QStandardItemModel,
)

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QSplitter,
    QFileSystemModel,
    QTreeView,
    QPlainTextEdit,
    QTextEdit,
    QTextBrowser,
    QVBoxLayout,
    QHBoxLayout,
    QToolBar,
    QAction,
    QFileDialog,
    QMessageBox,
    QStatusBar,
    QLabel,
    QLineEdit,
    QPushButton,
    QStyle,
    QInputDialog,
    QMenu,
)
from PyQt5.QtPrintSupport import QPrinter

from spellchecker import SpellChecker
from collections import Counter

APP_NAME = "Editor de Textos"
DEFAULT_WORKSPACE = Path.cwd() / "workspace"
CONFIG_FILE = Path.cwd() / ".editor_config.json"
AUTOSAVE_DIRNAME = ".autosave"
SUPPORTED_TEXT_EXTS = {".txt", ".md", ".markdown", ".json", ".yaml", ".yml", ".ini", ".cfg", ".csv"}


def compute_stats(text: str, wpm: int = 200, top_n: int = 5):
    """Compute word/character counts, reading time and top words."""
    words_list = re.findall(r"\b\w+\b", text.lower())
    word_count = len(words_list)
    char_count = len(text)
    reading_time = word_count / float(wpm) if wpm else 0
    freq = Counter(words_list)
    top_words = freq.most_common(top_n)
    return {
        "words": word_count,
        "characters": char_count,
        "reading_time": reading_time,
        "top_words": top_words,
    }


def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def load_config():
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_config(cfg: dict):
    try:
        CONFIG_FILE.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


class FavoriteFileSystemModel(QFileSystemModel):
    """File system model that highlights favorite paths."""

    def __init__(self, favorites: set[str], parent=None):
        super().__init__(parent)
        self.favorites = favorites
        self.favorite_icon = QIcon.fromTheme("star")
        if self.favorite_icon.isNull():
            self.favorite_icon = QApplication.style().standardIcon(QStyle.SP_DialogYesButton)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if role == Qt.DecorationRole and index.column() == 0:
            path = self.filePath(index)
            if path in self.favorites:
                return self.favorite_icon
        return super().data(index, role)

class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)

    def _apply_format_range(self, start, end, fmt):
        if start < 0 or end <= start:
            return
        self.setFormat(start, end - start, fmt)

    def highlightBlock(self, text: str):
        # ----- cercas de código ``` -----
        fence = "```"
        in_code = self.previousBlockState() == 1
        if in_code:
            code_fmt = QTextCharFormat()
            code_fmt.setForeground(QColor("#dcdcdc"))
            self._apply_format_range(0, len(text), code_fmt)
            if text.strip().startswith(fence):
                self.setCurrentBlockState(0)
            else:
                self.setCurrentBlockState(1)
                return
        if text.strip().startswith(fence):
            fence_fmt = QTextCharFormat()
            fence_fmt.setForeground(QColor("#9cdcfe"))
            self._apply_format_range(0, len(text), fence_fmt)
            self.setCurrentBlockState(1)
            return

        # ----- títulos (#, ##, ...) -----
        if text.startswith('#'):
            h_fmt = QTextCharFormat()
            h_fmt.setForeground(QColor("#5b9cff"))
            h_fmt.setFontWeight(QFont.Bold)
            self._apply_format_range(0, len(text), h_fmt)

        # ----- citações > -----
        if text.lstrip().startswith('>'):
            q_fmt = QTextCharFormat()
            q_fmt.setForeground(QColor("#6a9955"))
            q_fmt.setFontItalic(True)
            self._apply_format_range(0, len(text), q_fmt)

        # ----- linhas horizontais (---, ***, ___) -----
        s = text.strip()
        if s and len(s) >= 3 and (set(s) <= {'-'} or set(s) <= {'*'} or set(s) <= {'_'}):
            hr_fmt = QTextCharFormat()
            hr_fmt.setForeground(QColor("#888888"))
            self._apply_format_range(0, len(text), hr_fmt)

        # ----- listas -, *, + ou 1. 2. -----
        ls = text.lstrip()
        if ls.startswith(('- ', '* ', '+ ')):
            li_fmt = QTextCharFormat()
            li_fmt.setForeground(QColor("#b5cea8"))
            li_fmt.setFontWeight(QFont.Bold)
            start = text.index(ls)
            self._apply_format_range(start, start + 2, li_fmt)
        else:
            i = 0
            while i < len(ls) and ls[i].isdigit():
                i += 1
            if i > 0 and i + 1 < len(ls) and ls[i] == '.' and ls[i+1] == ' ':
                li_fmt = QTextCharFormat()
                li_fmt.setForeground(QColor("#b5cea8"))
                li_fmt.setFontWeight(QFont.Bold)
                start = text.index(ls)
                self._apply_format_range(start, start + i + 1, li_fmt)

        # ----- código inline `code` -----
        code_fmt = QTextCharFormat()
        code_fmt.setForeground(QColor("#9cdcfe"))
        start = 0
        while True:
            a = text.find('`', start)
            if a == -1: break
            b = text.find('`', a + 1)
            if b == -1: break
            self._apply_format_range(a, b + 1, code_fmt)
            start = b + 1

        # ----- negrito ** ** e __ __ -----
        bold_fmt = QTextCharFormat()
        bold_fmt.setForeground(QColor("#e07a00"))
        bold_fmt.setFontWeight(QFont.Bold)
        for marker in ('**', '__'):
            start = 0
            while True:
                a = text.find(marker, start)
                if a == -1: break
                b = text.find(marker, a + len(marker))
                if b == -1: break
                self._apply_format_range(a, b + len(marker), bold_fmt)
                start = b + len(marker)

        # ----- itálico * * e _ _ (simples, não sobrepõe negrito) -----
        ital_fmt = QTextCharFormat()
        ital_fmt.setForeground(QColor("#c678dd"))
        ital_fmt.setFontItalic(True)
        for marker in ('*', '_'):
            start = 0
            while True:
                a = text.find(marker, start)
                if a == -1: break
                # pula ** ou __ (negrito)
                if a + 1 < len(text) and text[a+1] == marker:
                    start = a + 2
                    continue
                b = text.find(marker, a + 1)
                if b == -1: break
                self._apply_format_range(a, b + 1, ital_fmt)
                start = b + 1

        # ----- links [texto](url) -----
        link_fmt = QTextCharFormat()
        link_fmt.setForeground(QColor("#4fc1ff"))
        link_fmt.setFontUnderline(True)
        start = 0
        while True:
            a = text.find('[', start)
            if a == -1: break
            mid = text.find(']', a + 1)
            if mid == -1 or mid + 1 >= len(text) or text[mid + 1] != '(':
                start = a + 1
                continue
            b = text.find(')', mid + 2)
            if b == -1: break
            self._apply_format_range(a, b + 1, link_fmt)
            start = b + 1

        self.setCurrentBlockState(0)

class FindBar(QWidget):
    """Barra de busca simples com próximo/anterior"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVisible(False)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        self.input = QLineEdit(self)
        self.input.setPlaceholderText("Buscar no texto…")
        self.btn_prev = QPushButton("Anterior")
        self.btn_next = QPushButton("Próximo")
        self.btn_close = QPushButton(self.style().standardIcon(QStyle.SP_DialogCloseButton), "")
        self.btn_close.setToolTip("Fechar busca (Esc)")
        layout.addWidget(QLabel("Buscar:"))
        layout.addWidget(self.input, 1)
        layout.addWidget(self.btn_prev)
        layout.addWidget(self.btn_next)
        layout.addWidget(self.btn_close)
        self.setLayout(layout)


class SpellPlainTextEdit(QPlainTextEdit):
    """Editor com correção ortográfica no menu de contexto."""

    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        cursor = self.cursorForPosition(event.pos())
        cursor.select(QTextCursor.WordUnderCursor)
        word = cursor.selectedText()
        misspelled = getattr(self.main_window, "misspelled_words", set())
        if word and word.lower() in misspelled:
            menu.addSeparator()
            suggestions = list(self.main_window.spell_checker.candidates(word.lower()))[:5]
            for s in suggestions:
                act = menu.addAction(s)
                act.triggered.connect(
                    lambda _, c=QTextCursor(cursor), w=s: self._replace_word(c, w)
                )
        menu.exec_(event.globalPos())

    def _replace_word(self, cursor, new_word):
        cursor.beginEditBlock()
        cursor.insertText(new_word)
        cursor.endEditBlock()
        self.main_window.check_spelling()


class EditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1100, 700)

        cfg = load_config()
        workspace = Path(cfg.get("workspace", str(DEFAULT_WORKSPACE)))
        ensure_dir(workspace)
        self.workspace = workspace

        self.favorites: set[str] = set(cfg.get("favorites", []))
        self.icon_favorite = QIcon.fromTheme("star")
        if self.icon_favorite.isNull():
            self.icon_favorite = self.style().standardIcon(QStyle.SP_DialogYesButton)

        self.spell_checker = SpellChecker(language="pt")
        self.misspelled_words = set()
        self._spell_timer = QTimer(self)
        self._spell_timer.setSingleShot(True)
        self._spell_timer.setInterval(500)
        self._spell_timer.timeout.connect(self.check_spelling)

        # Estado do documento
        self.current_file: Path | None = None
        self.dirty = False
        self.dark_mode = bool(cfg.get("dark_mode", False))

        # Autosave
        self.autosave_enabled = True
        self.autosave_timer = QTimer(self)
        self.autosave_timer.setInterval(30_000)  # 30s
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start()

        self._build_ui()
        self._apply_theme(self.dark_mode)
        self._connect_signals()

    # UI ------------------------------------------------------------------
    def _build_ui(self):
        central = QWidget(self)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.toolbar = QToolBar("Ferramentas", self)
        self.toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)
        self._build_actions()
        menu_tools = self.menuBar().addMenu("Ferramentas")
        menu_tools.addAction(self.act_show_stats)

        self.find_bar = FindBar(self)
        root.addWidget(self.find_bar)

        tree_splitter = QSplitter(Qt.Horizontal, self)
        editor_splitter = QSplitter(Qt.Horizontal, self)

        self.fs_model = FavoriteFileSystemModel(self.favorites, self)
        self.fs_model.setRootPath(str(self.workspace))
        self.fs_model.setReadOnly(False)

        self.tree = QTreeView(self)
        self.tree.setModel(self.fs_model)
        self.tree.setRootIndex(self.fs_model.index(str(self.workspace)))
        self.tree.setColumnWidth(0, 280)
        for i in range(1, 4):
            self.tree.hideColumn(i)
        self.tree.setHeaderHidden(True)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)

        self.fav_model = QStandardItemModel(self)
        self.fav_view = QTreeView(self)
        self.fav_view.setModel(self.fav_model)
        self.fav_view.setHeaderHidden(True)
        self.fav_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.fav_view.setFixedHeight(120)

        fav_label = QLabel("Favoritos", self)

        tree_container = QWidget(self)
        tree_layout = QVBoxLayout(tree_container)
        tree_layout.setContentsMargins(0, 0, 0, 0)
        tree_layout.setSpacing(0)
        tree_layout.addWidget(fav_label)
        tree_layout.addWidget(self.fav_view)
        tree_layout.addWidget(self.tree, 1)

        self.editor = SpellPlainTextEdit(self)
        self.editor.setPlaceholderText("Escreva aqui…")

        try:
            self.editor.setTabStopDistance(4 * self.editor.fontMetrics().width(' '))
        except Exception:
            pass

        f = self.editor.font()
        f.setStyleHint(QFont.Monospace)
        f.setFamily("Consolas, 'Courier New', monospace")
        self.editor.setFont(f)

        self.highlighter = MarkdownHighlighter(self.editor.document())

        self.preview = QTextBrowser(self)
        self.preview.setOpenExternalLinks(True)

        editor_splitter.addWidget(self.editor)
        editor_splitter.addWidget(self.preview)
        editor_splitter.setStretchFactor(0, 1)

        tree_splitter.addWidget(tree_container)
        tree_splitter.addWidget(editor_splitter)
        tree_splitter.setStretchFactor(1, 1)

        root.addWidget(tree_splitter, 1)

        self._update_preview()
        self._refresh_favorites_view()

        sb = QStatusBar(self)
        self.lbl_path = QLabel("Pasta: " + str(self.workspace))
        self.lbl_stats = QLabel("0 palavras • 0 caracteres • 0 min")
        sb.addWidget(self.lbl_path, 1)
        sb.addPermanentWidget(self.lbl_stats)
        self.setStatusBar(sb)

        self.setCentralWidget(central)

    def _update_stats(self):
        stats = compute_stats(self.editor.toPlainText())
        self.current_stats = stats
        if hasattr(self, "lbl_stats"):
            rt = f"{stats['reading_time']:.1f} min"
            label = f"{stats['words']} palavras • {stats['characters']} caracteres • {rt}"
            if stats["top_words"]:
                top = ", ".join(w for w, _ in stats["top_words"][:3])
                label += f" • {top}"
            self.lbl_stats.setText(label)

    def _update_preview(self):
        text = self.editor.toPlainText()
        try:
            import markdown
            html = markdown.markdown(text)
        except Exception:
            doc = QTextDocument()
            doc.setPlainText(text)
            html = doc.toHtml()
        self.preview.setHtml(html)

    def show_stats_dialog(self):
        stats = getattr(self, "current_stats", None)
        if not stats:
            stats = compute_stats(self.editor.toPlainText())
        top = "\n".join(f"{w}: {c}" for w, c in stats["top_words"])
        rt = f"{stats['reading_time']:.1f} min"
        msg = (
            f"Palavras: {stats['words']}\n"
            f"Caracteres: {stats['characters']}\n"
            f"Tempo de leitura: {rt}"
        )
        if top:
            msg += "\nPalavras-chave:\n" + top
        QMessageBox.information(self, "Estatísticas", msg)

    def check_spelling(self):
        text = self.editor.toPlainText()
        words = re.findall(r"\b\w+\b", text.lower())
        misspelled = self.spell_checker.unknown(words)
        self.misspelled_words = misspelled
        doc = self.editor.document()
        selections = []
        fmt = QTextCharFormat()
        fmt.setUnderlineColor(QColor("red"))
        fmt.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
        for word in misspelled:
            cursor = QTextCursor(doc)
            while True:
                cursor = doc.find(word, cursor, QTextDocument.FindWholeWords)
                if cursor.isNull():
                    break
                sel = QTextEdit.ExtraSelection()
                sel.cursor = cursor
                sel.format = fmt
                selections.append(sel)
        self.editor.setExtraSelections(selections)

    def _apply_theme(self, dark: bool):
        """Tema literário: claro sépia e escuro de alto contraste suave."""
        if dark:
            bg = "#131417"  # fundo
            panel = "#1a1c22"  # painéis
            text = "#e6e6e6"  # texto principal
            muted = "#9aa3ad"  # texto secundário
            accent = "#86b7ff"  # destaque
            border = "#2a2d36"
        else:
            bg = "#f5efe6"  # sépia claro
            panel = "#fffaf2"  # painel quase branco
            text = "#2b2a27"  # marrom grafite
            muted = "#6a655d"  # marrom suave
            accent = "#3b6fb6"  # azul editorial
            border = "#e2d7c7"

        self.setStyleSheet(f"""
            QMainWindow {{ background: {bg}; color: {text}; }}
            QToolBar {{ background: {panel}; border: 0; }}
            QTreeView {{ background: {panel}; color: {text}; border-right: 1px solid {border}; }}
            QPlainTextEdit {{ background: {panel}; color: {text}; selection-background-color: {accent}; }}
            QStatusBar {{ background: {panel}; color: {text}; border-top: 1px solid {border}; }}
            QLineEdit, QPushButton {{ background: {panel}; color: {text}; border: 1px solid {border}; padding: 4px 8px; }}
            QPushButton:hover {{ border-color: {accent}; }}
            QMenu {{ background: {panel}; color: {text}; border: 1px solid {border}; }}
        """)

    def _build_actions(self):
        style = self.style()
        # Pasta de trabalho
        self.act_choose_workspace = QAction(style.standardIcon(QStyle.SP_DirIcon), "Selecionar Pasta", self)
        self.act_open_in_explorer = QAction("Abrir no Explorer/Finder", self)

        # Arquivos
        self.act_new_file = QAction(style.standardIcon(QStyle.SP_FileIcon), "Novo Arquivo (Ctrl+N)", self)
        self.act_save = QAction(style.standardIcon(QStyle.SP_DialogSaveButton), "Salvar (Ctrl+S)", self)
        self.act_save_as = QAction("Salvar Como… (Ctrl+Shift+S)", self)
        self.act_export = QAction("Exportar…", self)
        self.act_rename = QAction("Renomear…", self)
        self.act_delete = QAction("Excluir…", self)

        # Busca e tema
        self.act_find = QAction("Buscar (Ctrl+F)", self)
        self.act_toggle_theme = QAction("Alternar Tema Claro/Escuro", self)
        self.act_show_stats = QAction("Estatísticas…", self)

        # Sair
        self.act_close_tab = QAction("Fechar Arquivo (Ctrl+W)", self)

        # Atalhos
        self.act_new_file.setShortcut(QKeySequence.New)
        self.act_save.setShortcut(QKeySequence.Save)
        self.act_save_as.setShortcut(QKeySequence.SaveAs)
        self.act_find.setShortcut(QKeySequence.Find)
        self.act_close_tab.setShortcut(QKeySequence.Close)

        # Add to toolbar
        self.toolbar.addAction(self.act_choose_workspace)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.act_new_file)
        self.toolbar.addAction(self.act_save)
        self.toolbar.addAction(self.act_save_as)
        self.toolbar.addAction(self.act_export)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.act_find)
        self.toolbar.addAction(self.act_toggle_theme)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.act_open_in_explorer)
        self.toolbar.addAction(self.act_show_stats)

    def _connect_signals(self):
        self.editor.textChanged.connect(self._on_text_changed)
        self.editor.textChanged.connect(self._update_preview)
        self.tree.doubleClicked.connect(self._on_tree_double_clicked)
        self.tree.customContextMenuRequested.connect(self._on_tree_context_menu)
        self.fav_view.doubleClicked.connect(self._on_fav_double_clicked)
        self.fav_view.customContextMenuRequested.connect(self._on_fav_context_menu)

        self.act_choose_workspace.triggered.connect(self.choose_workspace)
        self.act_open_in_explorer.triggered.connect(self.open_workspace_in_explorer)
        self.act_new_file.triggered.connect(self.new_file)
        self.act_save.triggered.connect(self.save_file)
        self.act_save_as.triggered.connect(self.save_file_as)
        self.act_export.triggered.connect(self.export_document)
        self.act_rename.triggered.connect(self.rename_current_file)
        self.act_delete.triggered.connect(self.delete_current_file)
        self.act_find.triggered.connect(self.toggle_find)
        self.act_toggle_theme.triggered.connect(self.toggle_theme)
        self.act_close_tab.triggered.connect(self.close_current_file)
        self.act_show_stats.triggered.connect(self.show_stats_dialog)

        self.find_bar.btn_close.clicked.connect(lambda: self.find_bar.setVisible(False))
        self.find_bar.btn_next.clicked.connect(lambda: self.find_next(True))
        self.find_bar.btn_prev.clicked.connect(lambda: self.find_next(False))
        self.find_bar.input.returnPressed.connect(lambda: self.find_next(True))
        
    # Favoritos -----------------------------------------------------------
    def _refresh_favorites_view(self):
        self.fav_model.clear()
        for path_str in sorted(self.favorites):
            path = Path(path_str)
            item = QStandardItem(path.name)
            item.setEditable(False)
            item.setData(path_str, Qt.UserRole)
            item.setIcon(self.icon_favorite)
            self.fav_model.appendRow(item)

    def add_favorite(self, path: Path):
        path_str = str(path)
        if path_str in self.favorites:
            return
        self.favorites.add(path_str)
        self._refresh_favorites_view()
        idx = self.fs_model.index(path_str)
        if idx.isValid():
            self.fs_model.dataChanged.emit(idx, idx)
        self.save_favorites()

    def remove_favorite(self, path: Path):
        path_str = str(path)
        if path_str not in self.favorites:
            return
        self.favorites.remove(path_str)
        self._refresh_favorites_view()
        idx = self.fs_model.index(path_str)
        if idx.isValid():
            self.fs_model.dataChanged.emit(idx, idx)
        self.save_favorites()

    def save_favorites(self):
        cfg = load_config()
        cfg["favorites"] = list(self.favorites)
        save_config(cfg)

    def _on_fav_double_clicked(self, index: QModelIndex):
        if not index.isValid():
            return
        path = Path(index.data(Qt.UserRole))
        if path.is_file():
            if not self.maybe_save_changes():
                return
            self.open_file(path)

    def _on_fav_context_menu(self, pos):
        index = self.fav_view.indexAt(pos)
        if not index.isValid():
            return
        path = Path(index.data(Qt.UserRole))
        menu = QMenu(self)
        act_remove = menu.addAction("Remover dos Favoritos")
        chosen = menu.exec_(self.fav_view.viewport().mapToGlobal(pos))
        if chosen == act_remove:
            self.remove_favorite(path)

    # Ações ---------------------------------------------------------------
    def choose_workspace(self):
        path = QFileDialog.getExistingDirectory(self, "Selecionar pasta de trabalho", str(self.workspace))
        if path:
            # Verifica alterações não salvas
            if not self.maybe_save_changes():
                return
            self.workspace = Path(path)
            ensure_dir(self.workspace)
            self.lbl_path.setText("Pasta: " + str(self.workspace))
            self.fs_model.setRootPath(str(self.workspace))
            self.tree.setRootIndex(self.fs_model.index(str(self.workspace)))
            self.current_file = None
            self.editor.clear()
            self.dirty = False
            cfg = load_config()
            cfg["workspace"] = str(self.workspace)
            save_config(cfg)

    def open_workspace_in_explorer(self):
        # Abre pasta no explorador do SO
        path = str(self.workspace)
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            os.system(f"open '{path}'")
        else:
            os.system(f"xdg-open '{path}'")

    def new_file(self):
        name, ok = QInputDialog.getText(self, "Novo arquivo", "Nome do arquivo (ex.: texto.md):")
        if not ok or not name.strip():
            return
        file_path = (self.workspace / name).resolve()
        if file_path.exists():
            QMessageBox.warning(self, APP_NAME, "Já existe um arquivo com esse nome.")
            return
        try:
            ensure_dir(file_path.parent)
            file_path.write_text("", encoding="utf-8")
        except Exception as e:
            QMessageBox.critical(self, APP_NAME, f"Erro ao criar arquivo:\n{e}")
            return
        # Seleciona e abre
        idx = self.fs_model.index(str(file_path))
        if idx.isValid():
            self.tree.setCurrentIndex(idx)
        self.open_file(file_path)

    def save_file(self):
        if not self.current_file:
            return self.save_file_as()
        try:
            text = self.editor.toPlainText()
            self.current_file.write_text(text, encoding="utf-8")
            self.dirty = False
            self.statusBar().showMessage("Salvo.", 2000)
        except Exception as e:
            QMessageBox.critical(self, APP_NAME, f"Erro ao salvar:\n{e}")

    def save_file_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Salvar como", str(self.workspace), "Textos (*.txt *.md *.markdown *.json *.yaml *.yml *.ini *.cfg *.csv);;Todos (*.*)")
        if not path:
            return
        self.current_file = Path(path)
        self.save_file()

    def export_document(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar documento",
            str(self.workspace),
            "TXT (*.txt);;Markdown (*.md);;HTML (*.html);;PDF (*.pdf)",
        )
        if not path:
            return
        text = self.editor.toPlainText()
        ext = Path(path).suffix.lower()
        try:
            if ext == ".txt":
                Path(path).write_text(text, encoding="utf-8")
            elif ext == ".md":
                Path(path).write_text(text, encoding="utf-8")
            elif ext in {".html", ".htm"}:
                try:
                    import markdown

                    body = markdown.markdown(text)
                except Exception:
                    doc = QTextDocument()
                    doc.setPlainText(text)
                    body = doc.toHtml()
                css = "body { font-family: 'Consolas', 'Courier New', monospace; padding: 1em; }"
                html = (
                    "<!DOCTYPE html><html><head><meta charset='utf-8'><style>"
                    + css
                    + "</style></head><body>"
                    + body
                    + "</body></html>"
                )
                Path(path).write_text(html, encoding="utf-8")
            elif ext == ".pdf":
                doc = QTextDocument()
                try:
                    import markdown

                    doc.setHtml(markdown.markdown(text))
                except Exception:
                    doc.setPlainText(text)
                printer = QPrinter(QPrinter.HighResolution)
                printer.setOutputFormat(QPrinter.PdfFormat)
                printer.setOutputFileName(path)
                doc.print_(printer)
            else:
                QMessageBox.warning(self, APP_NAME, "Formato de exportação desconhecido.")
                return
            self.statusBar().showMessage("Documento exportado.", 2000)
        except Exception as e:
            QMessageBox.critical(self, APP_NAME, f"Erro ao exportar:\n{e}")

    def rename_current_file(self):
        if not self.current_file:
            QMessageBox.information(self, APP_NAME, "Nenhum arquivo aberto.")
            return
        new_name, ok = QInputDialog.getText(self, "Renomear arquivo", "Novo nome:", text=self.current_file.name)
        if not ok or not new_name.strip():
            return
        new_path = self.current_file.with_name(new_name)
        if new_path.exists():
            QMessageBox.warning(self, APP_NAME, "Já existe um arquivo com esse nome.")
            return
        try:
            self.current_file.rename(new_path)
            self.current_file = new_path
            self.statusBar().showMessage("Arquivo renomeado.", 2000)
        except Exception as e:
            QMessageBox.critical(self, APP_NAME, f"Erro ao renomear:\n{e}")

    def delete_current_file(self):
        if not self.current_file:
            QMessageBox.information(self, APP_NAME, "Nenhum arquivo aberto.")
            return
        resp = QMessageBox.question(self, APP_NAME, f"Excluir definitivamente\n{self.current_file.name}?", QMessageBox.Yes | QMessageBox.No)
        if resp == QMessageBox.Yes:
            try:
                self.current_file.unlink()
                self.current_file = None
                self.editor.clear()
                self.dirty = False
                self.statusBar().showMessage("Arquivo excluído.", 2000)
            except Exception as e:
                QMessageBox.critical(self, APP_NAME, f"Erro ao excluir:\n{e}")

    def toggle_find(self):
        self.find_bar.setVisible(not self.find_bar.isVisible())
        if self.find_bar.isVisible():
            self.find_bar.input.setFocus()
            self.find_bar.input.selectAll()

    def find_next(self, forward=True):
        pattern = self.find_bar.input.text()
        if not pattern:
            return
        doc = self.editor.document()
        cursor = self.editor.textCursor()
        flags = Qt.MatchFlags()
        # QPlainTextEdit possui find simplificado via .find(), usa regex plain
        found = self.editor.find(pattern) if forward else self.editor.find(pattern, QTextDocument.FindBackward)  # type: ignore[name-defined]
        if not found:
            # reinicia do começo/fim
            cursor.movePosition(cursor.Start if forward else cursor.End)
            self.editor.setTextCursor(cursor)
            self.editor.find(pattern) if forward else self.editor.find(pattern, QTextDocument.FindBackward)  # type: ignore[name-defined]

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self._apply_theme(self.dark_mode)
        cfg = load_config()
        cfg["dark_mode"] = self.dark_mode
        save_config(cfg)

    def close_current_file(self):
        if not self.maybe_save_changes():
            return
        self.current_file = None
        self.editor.clear()
        self.dirty = False

    # Helpers -------------------------------------------------------------
    def _on_text_changed(self):
        self.dirty = True
        self._update_stats()
        self._spell_timer.start()

    def _on_tree_double_clicked(self, index: QModelIndex):
        if not index.isValid():
            return
        file_path = Path(self.fs_model.filePath(index))
        if file_path.is_file():
            # Verifica mudanças não salvas antes de trocar
            if not self.maybe_save_changes():
                return
            self.open_file(file_path)

    def _on_tree_context_menu(self, pos):
        index = self.tree.indexAt(pos)
        menu = QMenu(self)
        act_new_file = menu.addAction("Novo arquivo…")
        act_new_folder = menu.addAction("Nova pasta…")
        act_favorite = None
        file_path = None
        if index.isValid():
            file_path = Path(self.fs_model.filePath(index))
            if str(file_path) in self.favorites:
                act_favorite = menu.addAction("Remover dos Favoritos")
            else:
                act_favorite = menu.addAction("Adicionar aos Favoritos")
            if file_path.is_file():
                menu.addSeparator()
                act_rename = menu.addAction("Renomear…")
                act_delete = menu.addAction("Excluir…")
        chosen = menu.exec_(self.tree.viewport().mapToGlobal(pos))
        base_dir = self.workspace if not index.isValid() else Path(self.fs_model.filePath(index))
        if base_dir.is_file():
            base_dir = base_dir.parent

        if chosen == act_new_file:
            name, ok = QInputDialog.getText(self, "Novo arquivo", "Nome do arquivo:")
            if ok and name.strip():
                (base_dir / name).write_text("", encoding="utf-8")
        elif chosen == act_new_folder:
            name, ok = QInputDialog.getText(self, "Nova pasta", "Nome da pasta:")
            if ok and name.strip():
                ensure_dir(base_dir / name)
        elif chosen == act_favorite and file_path is not None:
            if str(file_path) in self.favorites:
                self.remove_favorite(file_path)
            else:
                self.add_favorite(file_path)
        elif index.isValid() and file_path and file_path.is_file():
            if chosen and chosen.text().startswith("Renomear"):
                new_name, ok = QInputDialog.getText(self, "Renomear", "Novo nome:", text=file_path.name)
                if ok and new_name.strip():
                    new_path = file_path.with_name(new_name)
                    if new_path.exists():
                        QMessageBox.warning(self, APP_NAME, "Já existe um item com esse nome.")
                    else:
                        file_path.rename(new_path)
            elif chosen and chosen.text().startswith("Excluir"):
                resp = QMessageBox.question(self, APP_NAME, f"Excluir {file_path.name}?", QMessageBox.Yes | QMessageBox.No)
                if resp == QMessageBox.Yes:
                    file_path.unlink()

    def _apply_theme(self, dark: bool):
        if dark:

            # Tema escuro literário (contraste reduzido)
            palette = {
                "--bg": "#1e1e1e",
                "--panel": "#252526",
                "--text": "#dcdcdc",
                "--muted": "#808080",
                "--accent": "#569cd6",
            }
        else:
            # Tema claro sépia
            palette = {
                "--bg": "#fdf6e3",
                "--panel": "#fffaf0",
                "--text": "#3e2f1c",
                "--muted": "#8b7765",
                "--accent": "#b58900",
            }
        self.setStyleSheet(
            f"""
        QMainWindow {{ background: {palette['--bg']}; color: {palette['--text']}; }}
        QPlainTextEdit {{ background: {palette['--panel']}; color: {palette['--text']}; selection-background-color: {palette['--accent']}; }}
        QTreeView {{ background: {palette['--panel']}; color: {palette['--text']}; }}
        QStatusBar {{ background: {palette['--panel']}; color: {palette['--text']}; }}
        QToolBar {{ background: {palette['--panel']}; }}
        QLabel {{ color: {palette['--text']}; }}
        QLineEdit {{ background: {palette['--panel']}; color: {palette['--text']}; border: 1px solid {palette['--muted']}; }}
        QPushButton {{ background: {palette['--panel']}; color: {palette['--text']}; border: 1px solid {palette['--muted']}; padding: 4px 8px; }}
        QPushButton:hover {{ border-color: {palette['--accent']}; }}
        """
        )
        # Aplica via stylesheet simples
        self.setStyleSheet(
            f"""
            QMainWindow {{ background: {palette['--bg']}; color: {palette['--text']}; }}
            QToolBar {{ background: {palette['--panel']}; border: 0; }}
            QTreeView {{ background: {palette['--panel']}; color: {palette['--text']}; border-right: 1px solid rgba(0,0,0,0.1); }}
            QPlainTextEdit {{ background: {palette['--panel']}; color: {palette['--text']}; selection-background-color: {palette['--accent']}; }}
            QStatusBar {{ background: {palette['--panel']}; color: {palette['--text']}; }}
            QLineEdit {{ background: {palette['--panel']}; color: {palette['--text']}; border: 1px solid rgba(0,0,0,0.25); padding: 4px; }}
            QPushButton {{ background: {palette['--panel']}; color: {palette['--text']}; border: 1px solid rgba(0,0,0,0.25); padding: 4px 8px; }}
            QPushButton:hover {{ border-color: {palette['--accent']}; }}
            QMenu {{ background: {palette['--panel']}; color: {palette['--text']}; }}
            """
        )

    def open_file(self, file_path: Path):
        try:
            text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Tenta latin-1
            try:
                text = file_path.read_text(encoding="latin-1")
            except Exception as e:
                QMessageBox.critical(self, APP_NAME, f"Não foi possível abrir o arquivo como texto.\n{e}")
                return
        except Exception as e:
            QMessageBox.critical(self, APP_NAME, f"Erro ao abrir:\n{e}")
            return
        self.current_file = file_path
        self.editor.setPlainText(text)
        self.editor.setFocus()
        self.dirty = False
        self.setWindowTitle(f"{APP_NAME} — {file_path.name}")

    def maybe_save_changes(self) -> bool:
        if not self.dirty:
            return True
        resp = QMessageBox.question(self, APP_NAME, "O arquivo foi modificado. Salvar alterações?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        if resp == QMessageBox.Yes:
            self.save_file()
            return not self.dirty
        return resp != QMessageBox.Cancel

    def autosave(self):
        if not self.autosave_enabled or not self.dirty:
            return
        if not self.current_file:
            return
        autosave_dir = self.workspace / AUTOSAVE_DIRNAME
        ensure_dir(autosave_dir)
        backup_path = autosave_dir / (self.current_file.name + ".bak")
        try:
            backup_path.write_text(self.editor.toPlainText(), encoding="utf-8")
            self.statusBar().showMessage("Autosave concluído.", 1500)
        except Exception:
            pass

    # Eventos -------------------------------------------------------------
    def closeEvent(self, event: QCloseEvent):
        if not self.maybe_save_changes():
            event.ignore()
            return
        # salva config
        cfg = load_config()
        cfg["workspace"] = str(self.workspace)
        cfg["dark_mode"] = self.dark_mode
        cfg["favorites"] = list(self.favorites)
        save_config(cfg)
        event.accept()


def main():
    ensure_dir(DEFAULT_WORKSPACE)
    app = QApplication(sys.argv)
    w = EditorWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
