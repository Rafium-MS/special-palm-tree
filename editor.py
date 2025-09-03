import os
import sys
import json
import shutil
import re
from datetime import datetime
from pathlib import Path

from PyQt5.QtCore import (
    Qt,
    QTimer,
    QModelIndex,
    QRegExp,
    QSortFilterProxyModel,
    QThread,
    pyqtSignal,
)
from PyQt5.QtGui import (
    QCloseEvent,
    QKeySequence,
    QSyntaxHighlighter,
    QTextCharFormat,
    QColor,
    QFont,
    QTextDocument,
    QTextCursor,
    QTextBlockFormat,
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
    QListWidget,
    QDialog,
    QListWidgetItem,
    QFontDialog,
    QProgressBar,
)
from PyQt5.QtPrintSupport import QPrinter

from spellchecker import SpellChecker

from constants import (
    APP_NAME,
    DEFAULT_WORKSPACE,
    AUTOSAVE_DIRNAME,
    HISTORY_DIRNAME,
    MAX_SNAPSHOTS,
)
from utils import (
    compute_stats,
    ensure_dir,
    load_config,
    save_config,
    read_file_text,
    search_workspace,
)
from demografico_medieval import MainWindow as DemograficoWindow
from personagens import MainWindow as PersonagensWindow
from economico import MainWindow as EconomicoWindow
from linha_do_tempo import MainWindow as LinhaDoTempoWindow
from religioes_faccoes import MainWindow as ReligioesFaccoesWindow
from cidades_planetas import MainWindow as CidadesPlanetasWindow
from theme import apply_theme, THEMES as AVAILABLE_THEMES

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


class ProjectNode(QStandardItem):
    """Node representing a book, chapter or scene."""

    def __init__(self, name: str, path: Path, node_type: str):
        super().__init__(name)
        self.path = Path(path)
        self.node_type = node_type
        self.setEditable(False)


class ProjectTreeModel(QStandardItemModel):
    """Tree model organizing books, chapters and scenes."""

    def __init__(self, root_path: Path, favorites: set[str], parent=None):
        super().__init__(parent)
        self.root_path = Path(root_path)
        self.favorites = favorites
        self.favorite_icon = QIcon.fromTheme("star")
        if self.favorite_icon.isNull():
            self.favorite_icon = QApplication.style().standardIcon(QStyle.SP_DialogYesButton)
        self.load_project()

    def _set_icon(self, item: ProjectNode):
        if str(item.path) in self.favorites:
            item.setIcon(self.favorite_icon)
        else:
            item.setIcon(QIcon())

    def load_project(self):
        self.clear()
        self.setHorizontalHeaderLabels(["Projeto"])
        root = self.invisibleRootItem()
        if not self.root_path.exists():
            return
        for book_dir in sorted(self.root_path.iterdir()):
            if not book_dir.is_dir():
                continue
            book_item = ProjectNode(book_dir.name, book_dir, "book")
            self._set_icon(book_item)
            root.appendRow(book_item)
            for chapter_dir in sorted(book_dir.iterdir()):
                if not chapter_dir.is_dir():
                    continue
                chap_item = ProjectNode(chapter_dir.name, chapter_dir, "chapter")
                self._set_icon(chap_item)
                book_item.appendRow(chap_item)
                for scene_file in sorted(chapter_dir.glob("*.txt")):
                    scene_item = ProjectNode(scene_file.stem, scene_file, "scene")
                    self._set_icon(scene_item)
                    chap_item.appendRow(scene_item)

    def node_from_index(self, index: QModelIndex) -> ProjectNode | None:
        item = self.itemFromIndex(index)
        return item if isinstance(item, ProjectNode) else None

    def filePath(self, index: QModelIndex) -> str:  # type: ignore[override]
        node = self.node_from_index(index)
        if node:
            return str(node.path)
        return str(self.root_path)

    def index_from_path(self, path: Path) -> QModelIndex:
        path = Path(path)

        def _search(parent: ProjectNode) -> QModelIndex:
            for i in range(parent.rowCount()):
                child = parent.child(i)
                if isinstance(child, ProjectNode):
                    if child.path == path:
                        return child.index()
                    res = _search(child)
                    if res.isValid():
                        return res
            return QModelIndex()

        return _search(self.invisibleRootItem())

    def set_root_path(self, path: Path):
        self.root_path = Path(path)
        self.load_project()

    def create_book(self, name: str) -> QModelIndex:
        book_dir = self.root_path / name
        ensure_dir(book_dir)
        item = ProjectNode(name, book_dir, "book")
        self._set_icon(item)
        self.invisibleRootItem().appendRow(item)
        return item.index()

    def create_chapter(self, book_node: ProjectNode, name: str) -> QModelIndex:
        chapter_dir = book_node.path / name
        ensure_dir(chapter_dir)
        item = ProjectNode(name, chapter_dir, "chapter")
        self._set_icon(item)
        book_node.appendRow(item)
        return item.index()

    def create_scene(self, chapter_node: ProjectNode, name: str) -> QModelIndex:
        scene_path = chapter_node.path / f"{name}.txt"
        if not scene_path.exists():
            scene_path.write_text("", encoding="utf-8")
        item = ProjectNode(name, scene_path, "scene")
        self._set_icon(item)
        chapter_node.appendRow(item)
        return item.index()

    def update_favorite_icon(self, path: Path):
        idx = self.index_from_path(path)
        if idx.isValid():
            item = self.node_from_index(idx)
            if item:
                self._set_icon(item)


class TagFilterProxyModel(QSortFilterProxyModel):
    """Proxy model that filters items based on assigned tags."""

    def __init__(self, tags: dict[str, list[str]], parent=None):
        super().__init__(parent)
        self.tags = tags
        self.filter_tag: str = ""

    def set_filter_tag(self, tag: str):
        self.filter_tag = tag
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:  # type: ignore[override]
        if not self.filter_tag:
            return True
        index = self.sourceModel().index(source_row, 0, source_parent)
        path = self.sourceModel().filePath(index)
        if os.path.isdir(path):
            for i in range(self.sourceModel().rowCount(index)):
                if self.filterAcceptsRow(i, index):
                    return True
            return False
        tags = self.tags.get(path, [])
        return self.filter_tag in tags

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



class SearchWorker(QThread):
    """Thread that searches files for a given pattern."""

    result_found = pyqtSignal(Path, int, str)
    finished = pyqtSignal()

    def __init__(self, pattern: str):
        super().__init__()
        self.pattern = pattern

    def run(self):
        for path, lineno, line in search_workspace(self.pattern):
            self.result_found.emit(path, lineno, line)
        self.finished.emit()


class GlobalSearchDialog(QDialog):
    """Simple dialog to perform a search across the workspace."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Busca no Workspace")
        layout = QVBoxLayout(self)
        self.input = QLineEdit(self)
        self.input.setPlaceholderText("Buscar…")
        layout.addWidget(self.input)
        self.list = QListWidget(self)
        layout.addWidget(self.list, 1)
        self.status = QLabel("", self)
        layout.addWidget(self.status)

        self.worker: SearchWorker | None = None
        self.input.returnPressed.connect(self.start_search)
        self.list.itemDoubleClicked.connect(self.open_result)

    def start_search(self):
        pattern = self.input.text().strip()
        if not pattern:
            return
        self.list.clear()
        self.status.setText("Buscando…")
        self.worker = SearchWorker(pattern)
        self.worker.result_found.connect(self._add_result)
        self.worker.finished.connect(self._finished)
        self.worker.start()

    def _add_result(self, path: Path, lineno: int, line: str):
        item = QListWidgetItem(f"{path}:{lineno} - {line}")
        item.setData(Qt.UserRole, (str(path), lineno))
        self.list.addItem(item)

    def _finished(self):
        self.status.setText(f"{self.list.count()} resultado(s)")

    def open_result(self, item: QListWidgetItem):
        data = item.data(Qt.UserRole)
        if not data:
            return
        path_str, lineno = data
        self.parent().open_file(Path(path_str))
        cursor = self.parent().editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, lineno - 1)
        self.parent().editor.setTextCursor(cursor)
        self.parent().editor.setFocus()
        self.accept()


class PomodoroDialog(QDialog):
    """Dialogo simples de Pomodoro para ciclos de trabalho/pausa."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pomodoro")
        self.work_duration = 25 * 60
        self.break_duration = 5 * 60
        self.remaining = self.work_duration
        self.is_work = True
        self.sessions = 0
        self.session_words: list[int] = []
        self.start_words = 0

        layout = QVBoxLayout(self)
        self.lbl_phase = QLabel("Trabalho", self)
        self.lbl_phase.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_phase)
        self.lbl_timer = QLabel(self._fmt(self.remaining), self)
        self.lbl_timer.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_timer)
        self.lbl_sessions = QLabel("Sessões concluídas: 0", self)
        layout.addWidget(self.lbl_sessions)
        self.lbl_last = QLabel("Última sessão: 0 palavras", self)
        layout.addWidget(self.lbl_last)

        btns = QHBoxLayout()
        self.btn_start = QPushButton("Iniciar", self)
        self.btn_pause = QPushButton("Pausar", self)
        self.btn_reset = QPushButton("Resetar", self)
        btns.addWidget(self.btn_start)
        btns.addWidget(self.btn_pause)
        btns.addWidget(self.btn_reset)
        layout.addLayout(btns)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)

        self.btn_start.clicked.connect(self.start)
        self.btn_pause.clicked.connect(self.pause)
        self.btn_reset.clicked.connect(self.reset)

    def _fmt(self, secs: int) -> str:
        return f"{secs // 60:02d}:{secs % 60:02d}"

    def start(self):
        if not self.timer.isActive():
            self.timer.start(1000)
            parent = self.parent()
            if parent and hasattr(parent, "current_stats"):
                self.start_words = parent.current_stats.get("words", 0)

    def pause(self):
        if self.timer.isActive():
            self.timer.stop()

    def reset(self):
        self.timer.stop()
        self.is_work = True
        self.remaining = self.work_duration
        self.lbl_phase.setText("Trabalho")
        self.lbl_timer.setText(self._fmt(self.remaining))

    def _tick(self):
        self.remaining -= 1
        if self.remaining <= 0:
            parent = self.parent()
            if self.is_work:
                self.sessions += 1
                words = 0
                if parent and hasattr(parent, "current_stats"):
                    words = parent.current_stats.get("words", 0) - self.start_words
                self.session_words.append(words)
                self.lbl_sessions.setText(f"Sessões concluídas: {self.sessions}")
                self.lbl_last.setText(f"Última sessão: {words} palavras")
                self.remaining = self.break_duration
                self.is_work = False
                self.lbl_phase.setText("Pausa")
            else:
                self.remaining = self.work_duration
                self.is_work = True
                self.lbl_phase.setText("Trabalho")
                if parent and hasattr(parent, "current_stats"):
                    self.start_words = parent.current_stats.get("words", 0)
        self.lbl_timer.setText(self._fmt(self.remaining))

class EditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1570, 820)

        cfg = load_config()
        workspace = Path(cfg.get("workspace", str(DEFAULT_WORKSPACE)))
        ensure_dir(workspace)
        self.workspace = workspace

        self.favorites: set[str] = set(cfg.get("favorites", []))
        self.tags: dict[str, list[str]] = cfg.get("tags", {})
        self.shortcuts: dict[str, str] = cfg.get("shortcuts", {})
        self.focus_mode = False
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
        self.theme = cfg.get("theme", "light")

        # Daily writing stats
        self.daily_word_goal = int(cfg.get("daily_word_goal", 0))
        self.daily_words_written = 0
        self.last_word_count = 0
        self.stats_date = datetime.now().date()

        # Autosave
        self.autosave_enabled = True
        self.autosave_interval = int(cfg.get("autosave_interval", 30_000))
        autosave_dir = cfg.get("autosave_dir")
        self.autosave_dir = Path(autosave_dir) if autosave_dir else (self.workspace / AUTOSAVE_DIRNAME)
        ensure_dir(self.autosave_dir)
        self.autosave_timer = QTimer(self)
        self.autosave_timer.setInterval(self.autosave_interval)
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start()

        self._build_ui()

        # Apply saved font settings
        font_family = cfg.get("font_family")
        font_size = cfg.get("font_size")
        if font_family or font_size:
            f = self.editor.font()
            if font_family:
                f.setFamily(font_family)
            if font_size:
                try:
                    f.setPointSize(int(font_size))
                except Exception:
                    pass
            self.editor.setFont(f)

        line_spacing = float(cfg.get("line_spacing", 1.0))
        self.set_line_spacing(line_spacing)

        apply_theme(self.theme)
        self._connect_signals()
        self._update_stats()

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
        menu_tools.addAction(self.act_toggle_sidebar)
        menu_tools.addAction(self.act_focus_mode)
        menu_tools.addSeparator()
        menu_tools.addAction(self.act_set_font)
        menu_tools.addAction(self.act_autosave_settings)
        menu_tools.addAction(self.act_set_daily_goal)
        menu_tools.addSeparator()
        menu_tools.addAction(self.act_open_demografico)
        menu_tools.addAction(self.act_open_personagens)
        menu_tools.addAction(self.act_open_economico)
        menu_tools.addAction(self.act_open_linha_tempo)
        menu_tools.addAction(self.act_open_religioes)
        menu_tools.addAction(self.act_open_cidades_planetas)
        self.menu_history = self.menuBar().addMenu("Histórico de versões")
        self.menu_history.aboutToShow.connect(self._populate_history_menu)

        self.find_bar = FindBar(self)
        root.addWidget(self.find_bar)

        tree_splitter = QSplitter(Qt.Horizontal, self)
        editor_splitter = QSplitter(Qt.Horizontal, self)

        self.project_model = ProjectTreeModel(self.workspace, self.favorites, self)

        self.tag_proxy = TagFilterProxyModel(self.tags, self)
        self.tag_proxy.setSourceModel(self.project_model)

        self.tree = QTreeView(self)
        self.tree.setModel(self.tag_proxy)
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

        tag_label = QLabel("Tags", self)
        self.tag_filter_input = QLineEdit(self)
        self.tag_filter_input.setPlaceholderText("Filtrar por tag…")
        self.tag_filter_input.returnPressed.connect(lambda: self.filter_tree_by_tag(self.tag_filter_input.text()))
        self.tag_list = QListWidget(self)
        self.tag_list.setFixedHeight(80)
        self.tag_list.itemClicked.connect(lambda item: self.filter_tree_by_tag(item.text()))
        btn_clear_tags = QPushButton("Limpar filtro", self)
        btn_clear_tags.clicked.connect(lambda: self.filter_tree_by_tag(""))

        tree_container = QWidget(self)
        self.tree_container = tree_container
        tree_layout = QVBoxLayout(tree_container)
        tree_layout.setContentsMargins(0, 0, 0, 0)
        tree_layout.setSpacing(0)
        tree_layout.addWidget(tag_label)
        tree_layout.addWidget(self.tag_filter_input)
        tree_layout.addWidget(self.tag_list)
        tree_layout.addWidget(btn_clear_tags)
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
        self.notes = QPlainTextEdit(self)
        self.notes.setPlaceholderText("Anotações…")
        self.notes.setMinimumWidth(150)
        editor_splitter.addWidget(self.notes)
        editor_splitter.setStretchFactor(0, 1)

        tree_splitter.addWidget(tree_container)
        tree_splitter.addWidget(editor_splitter)
        tree_splitter.setStretchFactor(1, 1)

        root.addWidget(tree_splitter, 1)

        self._update_preview()
        self._refresh_tags_view()
        self._refresh_favorites_view()

        sb = QStatusBar(self)
        self.lbl_path = QLabel("Pasta: " + str(self.workspace))
        self.lbl_stats = QLabel("0 palavras • 0 caracteres • 0 min")
        sb.addWidget(self.lbl_path, 1)
        sb.addPermanentWidget(self.lbl_stats)
        self.progress = QProgressBar(self)
        self.progress.setMaximumWidth(150)
        self.progress.setTextVisible(True)
        self.progress.setFormat("%v/%m")
        self.progress.setRange(0, max(self.daily_word_goal, 1))
        sb.addPermanentWidget(self.progress)
        self.setStatusBar(sb)

        self.setCentralWidget(central)

    def _update_stats(self):
        stats = compute_stats(self.editor.toPlainText())
        self.current_stats = stats

        # Daily word tracking
        today = datetime.now().date()
        if today != self.stats_date:
            self.stats_date = today
            self.daily_words_written = 0
            self.last_word_count = stats["words"]
        delta = stats["words"] - self.last_word_count
        if delta > 0:
            self.daily_words_written += delta
        self.last_word_count = stats["words"]

        if hasattr(self, "lbl_stats"):
            rt = f"{stats['reading_time']:.1f} min"
            label = f"{stats['words']} palavras • {stats['characters']} caracteres • {rt}"
            if stats["top_words"]:
                top = ", ".join(w for w, _ in stats["top_words"][:3])
                label += f" • {top}"
            self.lbl_stats.setText(label)

        if hasattr(self, "progress"):
            if self.daily_word_goal:
                self.progress.setRange(0, self.daily_word_goal)
                self.progress.setValue(min(self.daily_words_written, self.daily_word_goal))
                self.progress.setFormat(f"{self.daily_words_written}/{self.daily_word_goal}")
            else:
                self.progress.setRange(0, max(self.daily_words_written, 1))
                self.progress.setValue(self.daily_words_written)
                self.progress.setFormat(str(self.daily_words_written))

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

    def show_pomodoro_dialog(self):
        if not hasattr(self, "pomodoro_dialog"):
            self.pomodoro_dialog = PomodoroDialog(self)
        self.pomodoro_dialog.show()
        self.pomodoro_dialog.raise_()
        self.pomodoro_dialog.activateWindow()

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

    def open_demografico_medieval(self):
        if not hasattr(self, "demografico_window"):
            self.demografico_window = DemograficoWindow()
        self.demografico_window.show()
        self.demografico_window.raise_()
        self.demografico_window.activateWindow()
    def open_personagens(self):
        if not hasattr(self, "personagens_window"):
            self.personagens_window = PersonagensWindow()
        self.personagens_window.show()
        self.personagens_window.raise_()
        self.personagens_window.activateWindow()

    def open_economico(self):
        if not hasattr(self, "economico_window"):
            self.economico_window = EconomicoWindow()
        self.economico_window.show()
        self.economico_window.raise_()
        self.economico_window.activateWindow()

    def open_linha_do_tempo(self):
        if not hasattr(self, "linha_tempo_window"):
            self.linha_tempo_window = LinhaDoTempoWindow()
        self.linha_tempo_window.show()
        self.linha_tempo_window.raise_()
        self.linha_tempo_window.activateWindow()

    def open_religioes_faccoes(self):
        if not hasattr(self, "religioes_window"):
            self.religioes_window = ReligioesFaccoesWindow()
        self.religioes_window.show()
        self.religioes_window.raise_()
        self.religioes_window.activateWindow()

    def open_cidades_planetas(self):
        if not hasattr(self, "cidades_window"):
            self.cidades_window = CidadesPlanetasWindow()
        self.cidades_window.show()
        self.cidades_window.raise_()
        self.cidades_window.activateWindow()

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

    def _build_actions(self):
        style = self.style()
        # Pasta de trabalho
        self.act_choose_workspace = QAction(style.standardIcon(QStyle.SP_DirIcon), "Selecionar Pasta", self)
        self.act_open_in_explorer = QAction("Abrir no Explorer/Finder", self)

        # Arquivos
        self.act_new_file = QAction(style.standardIcon(QStyle.SP_FileIcon), "Novo Arquivo (Ctrl+N)", self)
        self.act_open_file = QAction(style.standardIcon(QStyle.SP_DialogOpenButton), "Abrir Arquivo (Ctrl+O)", self)
        self.act_save = QAction(style.standardIcon(QStyle.SP_DialogSaveButton), "Salvar (Ctrl+S)", self)
        self.act_save_as = QAction("Salvar Como… (Ctrl+Shift+S)", self)
        self.act_export = QAction("Exportar…", self)
        self.act_rename = QAction("Renomear…", self)
        self.act_delete = QAction("Excluir…", self)

        # Busca e tema
        self.act_find = QAction("Buscar (Ctrl+F)", self)
        self.act_global_find = QAction("Buscar no Workspace (Ctrl+Shift+F)", self)
        self.act_toggle_theme = QAction("Alternar Tema", self)
        self.act_show_stats = QAction("Estatísticas…", self)
        self.act_start_pomodoro = QAction(style.standardIcon(QStyle.SP_MediaPlay), "Pomodoro (Ctrl+Alt+P)", self)

        # Interface
        self.act_toggle_sidebar = QAction("Alternar Barra Lateral", self)
        self.act_toggle_sidebar.setCheckable(True)
        self.act_toggle_sidebar.setChecked(True)
        self.act_focus_mode = QAction("Modo Foco", self)
        self.act_focus_mode.setCheckable(True)
        self.act_focus_mode.setShortcut(QKeySequence("F11"))
        self.act_set_font = QAction("Configurar Fonte e Espaçamento…", self)
        self.act_autosave_settings = QAction("Configurar Autosave…", self)
        self.act_set_daily_goal = QAction("Definir Meta Diária…", self)
        self.act_open_demografico = QAction("Construtor Demográfico Medieval…", self)
        self.act_open_personagens = QAction("Gerenciador de Personagens…", self)
        self.act_open_economico = QAction("Construtor Econômico…", self)
        self.act_open_linha_tempo = QAction("Construtor de Linha do Tempo…", self)
        self.act_open_religioes = QAction("Gerenciador de Religiões e Facções…", self)
        self.act_open_cidades_planetas = QAction("Construtor de Cidades/Planetas…", self)

        # Sair
        self.act_close_tab = QAction("Fechar Arquivo (Ctrl+W)", self)

        # Atalhos
        self.act_new_file.setShortcut(QKeySequence.New)
        self.act_open_file.setShortcut(QKeySequence.Open)
        self.act_save.setShortcut(QKeySequence.Save)
        self.act_save_as.setShortcut(QKeySequence.SaveAs)
        self.act_find.setShortcut(QKeySequence.Find)
        self.act_global_find.setShortcut(QKeySequence("Ctrl+Shift+F"))
        self.act_close_tab.setShortcut(QKeySequence.Close)
        self.act_toggle_sidebar.setShortcut(QKeySequence("F9"))
        self.act_start_pomodoro.setShortcut(QKeySequence("Ctrl+Alt+P"))

        # Add to toolbar
        self.toolbar.addAction(self.act_choose_workspace)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.act_new_file)
        self.toolbar.addAction(self.act_open_file)
        self.toolbar.addAction(self.act_save)
        self.toolbar.addAction(self.act_save_as)
        self.toolbar.addAction(self.act_export)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.act_find)
        self.toolbar.addAction(self.act_global_find)
        self.toolbar.addAction(self.act_toggle_theme)
        self.toolbar.addAction(self.act_toggle_sidebar)
        self.toolbar.addAction(self.act_focus_mode)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.act_open_in_explorer)
        self.toolbar.addAction(self.act_start_pomodoro)
        self.toolbar.addAction(self.act_show_stats)

        self._apply_shortcuts()

    def _apply_shortcuts(self):
        mapping = {
            "new_file": self.act_new_file,
            "open_file": self.act_open_file,
            "save": self.act_save,
            "save_as": self.act_save_as,
            "find": self.act_find,
            "global_find": self.act_global_find,
            "toggle_theme": self.act_toggle_theme,
            "close_file": self.act_close_tab,
            "toggle_sidebar": self.act_toggle_sidebar,
            "focus_mode": self.act_focus_mode,
            "start_pomodoro": self.act_start_pomodoro,
        }
        for name, seq in self.shortcuts.items():
            act = mapping.get(name)
            if act:
                act.setShortcut(QKeySequence(seq))

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
        self.act_open_file.triggered.connect(self.open_file_dialog)
        self.act_save.triggered.connect(self.save_file)
        self.act_save_as.triggered.connect(self.save_file_as)
        self.act_export.triggered.connect(self.export_document)
        self.act_rename.triggered.connect(self.rename_current_file)
        self.act_delete.triggered.connect(self.delete_current_file)
        self.act_find.triggered.connect(self.toggle_find)
        self.act_global_find.triggered.connect(self.open_global_search)
        self.act_toggle_theme.triggered.connect(self.toggle_theme)
        self.act_close_tab.triggered.connect(self.close_current_file)
        self.act_show_stats.triggered.connect(self.show_stats_dialog)
        self.act_start_pomodoro.triggered.connect(self.show_pomodoro_dialog)
        self.act_toggle_sidebar.triggered.connect(self.toggle_sidebar)
        self.act_focus_mode.triggered.connect(self.toggle_focus_mode)
        self.act_set_font.triggered.connect(self.configure_font)
        self.act_autosave_settings.triggered.connect(self.configure_autosave)
        self.act_set_daily_goal.triggered.connect(self.configure_daily_goal)
        self.act_open_demografico.triggered.connect(self.open_demografico_medieval)
        self.act_open_personagens.triggered.connect(self.open_personagens)
        self.act_open_economico.triggered.connect(self.open_economico)
        self.act_open_linha_tempo.triggered.connect(self.open_linha_do_tempo)
        self.act_open_religioes.triggered.connect(self.open_religioes_faccoes)
        self.act_open_cidades_planetas.triggered.connect(self.open_cidades_planetas)

        self.find_bar.btn_close.clicked.connect(lambda: self.find_bar.setVisible(False))
        self.find_bar.btn_next.clicked.connect(lambda: self.find_next(True))
        self.find_bar.btn_prev.clicked.connect(lambda: self.find_next(False))
        self.find_bar.input.returnPressed.connect(lambda: self.find_next(True))

    def set_line_spacing(self, spacing: float) -> None:
        fmt = QTextBlockFormat()
        fmt.setLineHeight(int(spacing * 100), QTextBlockFormat.ProportionalHeight)
        cursor = self.editor.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.mergeBlockFormat(fmt)
        cursor.clearSelection()
        self.editor.setTextCursor(cursor)
        self.line_spacing = spacing

    def configure_font(self):
        font, ok = QFontDialog.getFont(self.editor.font(), self, "Escolher Fonte")
        if not ok:
            return
        self.editor.setFont(font)
        cfg = load_config()
        cfg["font_family"] = font.family()
        cfg["font_size"] = font.pointSize()
        spacing, ok = QInputDialog.getDouble(
            self,
            "Espaçamento entre linhas",
            "Múltiplo de espaçamento:",
            float(cfg.get("line_spacing", 1.0)),
            0.5,
            3.0,
            1,
        )
        if ok:
            self.set_line_spacing(spacing)
            cfg["line_spacing"] = spacing
        save_config(cfg)

    def configure_autosave(self):
        interval, ok = QInputDialog.getInt(
            self,
            "Intervalo de Autosave",
            "Intervalo em segundos:",
            self.autosave_interval // 1000,
            5,
            3600,
        )
        if not ok:
            return
        dir_path = QFileDialog.getExistingDirectory(
            self, "Pasta para backups", str(self.autosave_dir)
        )
        if not dir_path:
            return
        self.autosave_interval = interval * 1000
        self.autosave_dir = Path(dir_path)
        ensure_dir(self.autosave_dir)
        self.autosave_timer.setInterval(self.autosave_interval)
        cfg = load_config()
        cfg["autosave_interval"] = self.autosave_interval
        cfg["autosave_dir"] = dir_path
        save_config(cfg)

    def configure_daily_goal(self):
        cfg = load_config()
        current = int(cfg.get("daily_word_goal", self.daily_word_goal))
        goal, ok = QInputDialog.getInt(
            self,
            "Meta diária de palavras",
            "Número de palavras por dia:",
            current,
            0,
            100000,
        )
        if ok:
            self.daily_word_goal = goal
            cfg["daily_word_goal"] = goal
            save_config(cfg)
            if hasattr(self, "progress"):
                self.progress.setRange(0, max(goal, 1))
            self._update_stats()

    def toggle_sidebar(self, checked=None):
        if checked is None:
            checked = not self.tree_container.isVisible()
        self.tree_container.setVisible(checked)
        self.act_toggle_sidebar.setChecked(checked)

    def toggle_focus_mode(self, checked=None):
        if checked is None:
            checked = not self.focus_mode
        self.focus_mode = checked
        if checked:
            self._sidebar_was_visible = self.tree_container.isVisible()
            self.toolbar.setVisible(False)
            self.menuBar().setVisible(False)
            self.tree_container.setVisible(False)
            self.showFullScreen()
        else:
            self.toolbar.setVisible(True)
            self.menuBar().setVisible(True)
            self.tree_container.setVisible(getattr(self, '_sidebar_was_visible', True))
            self.showNormal()
        self.act_focus_mode.setChecked(checked)
        self.act_toggle_sidebar.setChecked(self.tree_container.isVisible())

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
        self.project_model.update_favorite_icon(path)
        self.save_favorites()

    def remove_favorite(self, path: Path):
        path_str = str(path)
        if path_str not in self.favorites:
            return
        self.favorites.remove(path_str)
        self._refresh_favorites_view()
        self.project_model.update_favorite_icon(path)
        self.save_favorites()

    def save_favorites(self):
        cfg = load_config()
        cfg["favorites"] = list(self.favorites)
        save_config(cfg)

    # Tags ---------------------------------------------------------------
    def _refresh_tags_view(self):
        self.tag_list.clear()
        all_tags = sorted({tag for tags in self.tags.values() for tag in tags})
        for t in all_tags:
            self.tag_list.addItem(t)

    def save_tags(self):
        cfg = load_config()
        cfg["tags"] = self.tags
        save_config(cfg)

    def filter_tree_by_tag(self, tag: str):
        self.tag_filter_input.setText(tag)
        self.tag_proxy.set_filter_tag(tag)

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
            self.project_model.set_root_path(self.workspace)
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
            self.project_model.load_project()
        except Exception as e:
            QMessageBox.critical(self, APP_NAME, f"Erro ao criar arquivo:\n{e}")
            return
        idx = self.project_model.index_from_path(file_path)
        if idx.isValid():
            self.tree.setCurrentIndex(self.tag_proxy.mapFromSource(idx))
        self.open_file(file_path)

    def open_file_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir arquivo",
            str(self.workspace),
            "Textos (*.txt *.md *.markdown *.json *.yaml *.yml *.ini *.cfg *.csv);;Todos (*.*)",
        )
        if path:
            self.open_file(Path(path))

    def save_file(self):
        if not self.current_file:
            return self.save_file_as()
        try:
            text = self.editor.toPlainText()
            self.current_file.write_text(text, encoding="utf-8")
            self.save_snapshot()
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

    def open_global_search(self):
        dlg = GlobalSearchDialog(self)
        dlg.exec_()

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
        order = list(AVAILABLE_THEMES.keys())
        idx = order.index(self.theme)
        self.theme = order[(idx + 1) % len(order)]
        apply_theme(self.theme)
        cfg = load_config()
        cfg["theme"] = self.theme
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
        src_index = self.tag_proxy.mapToSource(index)
        node = self.project_model.node_from_index(src_index)
        if node and node.node_type == "scene":
            # Verifica mudanças não salvas antes de trocar
            if not self.maybe_save_changes():
                return
            self.open_file(node.path)

    def _on_tree_context_menu(self, pos):
        index = self.tree.indexAt(pos)
        menu = QMenu(self)
        act_new_book = menu.addAction("Novo Livro…")
        act_new_chapter = None
        act_new_scene = None
        act_favorite = None
        act_add_tag = None
        act_remove_tag = None
        act_rename = None
        act_delete = None
        node = None
        file_path = None
        if index.isValid():
            src_index = self.tag_proxy.mapToSource(index)
            node = self.project_model.node_from_index(src_index)
            if node:
                file_path = node.path
                if node.node_type == "book":
                    act_new_chapter = menu.addAction("Novo Capítulo…")
                elif node.node_type == "chapter":
                    act_new_scene = menu.addAction("Nova Cena…")
                if str(file_path) in self.favorites:
                    act_favorite = menu.addAction("Remover dos Favoritos")
                else:
                    act_favorite = menu.addAction("Adicionar aos Favoritos")
                act_add_tag = menu.addAction("Adicionar Tag…")
                if str(file_path) in self.tags and self.tags[str(file_path)]:
                    act_remove_tag = menu.addAction("Remover Tag…")
                if node.node_type == "scene":
                    menu.addSeparator()
                    act_rename = menu.addAction("Renomear…")
                    act_delete = menu.addAction("Excluir…")
        chosen = menu.exec_(self.tree.viewport().mapToGlobal(pos))

        if chosen == act_new_book:
            name, ok = QInputDialog.getText(self, "Novo Livro", "Nome do livro:")
            if ok and name.strip():
                self.project_model.create_book(name.strip())
        elif chosen == act_new_chapter and node:
            name, ok = QInputDialog.getText(self, "Novo Capítulo", "Nome do capítulo:")
            if ok and name.strip():
                self.project_model.create_chapter(node, name.strip())
        elif chosen == act_new_scene and node:
            name, ok = QInputDialog.getText(self, "Nova Cena", "Nome da cena:")
            if ok and name.strip():
                idx = self.project_model.create_scene(node, name.strip())
                self.tree.setCurrentIndex(self.tag_proxy.mapFromSource(idx))
                new_node = self.project_model.node_from_index(idx)
                if new_node:
                    self.open_file(new_node.path)
        elif chosen == act_favorite and file_path is not None:
            if str(file_path) in self.favorites:
                self.remove_favorite(file_path)
            else:
                self.add_favorite(file_path)
        elif chosen == act_add_tag and file_path is not None:
            tag, ok = QInputDialog.getText(self, "Adicionar Tag", "Tag:")
            if ok and tag.strip():
                path_str = str(file_path)
                tags = self.tags.setdefault(path_str, [])
                if tag not in tags:
                    tags.append(tag)
                    self.save_tags()
                    self._refresh_tags_view()
                    self.tag_proxy.invalidateFilter()
        elif chosen == act_remove_tag and file_path is not None:
            path_str = str(file_path)
            tags = self.tags.get(path_str, [])
            if tags:
                tag, ok = QInputDialog.getItem(self, "Remover Tag", "Tag:", tags, 0, False)
                if ok and tag:
                    tags.remove(tag)
                    if not tags:
                        del self.tags[path_str]
                    self.save_tags()
                    self._refresh_tags_view()
                    self.tag_proxy.invalidateFilter()
        elif chosen == act_rename and node:
            default = node.path.stem if node.node_type == "scene" else node.path.name
            new_name, ok = QInputDialog.getText(self, "Renomear", "Novo nome:", text=default)
            if ok and new_name.strip():
                if node.node_type == "scene":
                    new_path = node.path.with_name(new_name + ".txt")
                else:
                    new_path = node.path.with_name(new_name)
                if new_path.exists():
                    QMessageBox.warning(self, APP_NAME, "Já existe um item com esse nome.")
                else:
                    node.path.rename(new_path)
                    node.path = new_path
                    node.setText(new_name)
                    self.project_model.update_favorite_icon(new_path)
        elif chosen == act_delete and node:
            resp = QMessageBox.question(self, APP_NAME, f"Excluir {node.path.name}?", QMessageBox.Yes | QMessageBox.No)
            if resp == QMessageBox.Yes:
                try:
                    node.path.unlink()
                except Exception:
                    pass
                parent = node.parent() or self.project_model.invisibleRootItem()
                parent.removeRow(node.row())

    def open_file(self, file_path: Path):
        try:
            text = read_file_text(file_path)
        except Exception as e:
            QMessageBox.critical(self, APP_NAME, f"Erro ao abrir:\n{e}")
            return
        ext = file_path.suffix.lower()
        if ext in {".docx", ".odt", ".rtf"}:
            # Importa como novo documento
            self.current_file = None
            title = f"{APP_NAME} — {file_path.name} (importado)"
        else:
            self.current_file = file_path
            title = f"{APP_NAME} — {file_path.name}"
        stats = compute_stats(text)
        self.last_word_count = stats["words"]
        self.editor.setPlainText(text)
        self.set_line_spacing(getattr(self, "line_spacing", 1.0))
        self.editor.setFocus()
        self.dirty = False
        self.setWindowTitle(title)

    def maybe_save_changes(self) -> bool:
        if not self.dirty:
            return True
        resp = QMessageBox.question(self, APP_NAME, "O arquivo foi modificado. Salvar alterações?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        if resp == QMessageBox.Yes:
            self.save_file()
            return not self.dirty
        return resp != QMessageBox.Cancel

    def save_snapshot(self):
        if not self.current_file:
            return
        history_dir = self.workspace / HISTORY_DIRNAME / self.current_file.name
        ensure_dir(history_dir)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        snap_path = history_dir / f"{timestamp}.bak"
        text = self.editor.toPlainText()
        try:
            snap_path.write_text(text, encoding="utf-8")
        except Exception:
            return
        meta_file = history_dir / "meta.json"
        try:
            data = json.loads(meta_file.read_text(encoding="utf-8")) if meta_file.exists() else []
        except Exception:
            data = []
        data.append({"timestamp": timestamp, "size": len(text)})
        while len(data) > MAX_SNAPSHOTS:
            old = data.pop(0)
            old_path = history_dir / f"{old['timestamp']}.bak"
            if old_path.exists():
                try:
                    old_path.unlink()
                except Exception:
                    pass
        try:
            meta_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass

    def autosave(self):
        if not self.autosave_enabled or not self.dirty or not self.current_file:
            return
        ensure_dir(self.autosave_dir)
        backup_path = self.autosave_dir / f"{self.current_file.name}.bak"
        try:
            backup_path.write_text(self.editor.toPlainText(), encoding="utf-8")
            self.statusBar().showMessage("Autosave concluído.", 1500)
        except Exception:
            self.statusBar().showMessage("Falha no autosave.", 1500)

    def _populate_history_menu(self):
        self.menu_history.clear()
        if not self.current_file:
            act = self.menu_history.addAction("Nenhum arquivo aberto")
            act.setEnabled(False)
            return
        history_dir = self.workspace / HISTORY_DIRNAME / self.current_file.name
        meta_file = history_dir / "meta.json"
        if not meta_file.exists():
            act = self.menu_history.addAction("Sem versões")
            act.setEnabled(False)
            return
        try:
            data = json.loads(meta_file.read_text(encoding="utf-8"))
        except Exception:
            act = self.menu_history.addAction("Erro ao ler histórico")
            act.setEnabled(False)
            return
        for entry in reversed(data):
            ts = entry.get("timestamp")
            size = entry.get("size", 0)
            try:
                dt = datetime.strptime(ts, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                dt = ts
            act = self.menu_history.addAction(f"{dt} ({size} bytes)")
            act.triggered.connect(lambda _, t=ts: self.restore_snapshot(t))

    def restore_snapshot(self, timestamp: str):
        if not self.current_file:
            return
        history_dir = self.workspace / HISTORY_DIRNAME / self.current_file.name
        snap_path = history_dir / f"{timestamp}.bak"
        if not snap_path.exists():
            return
        try:
            text = snap_path.read_text(encoding="utf-8")
        except Exception:
            return
        self.editor.setPlainText(text)
        self.dirty = True
        self.statusBar().showMessage("Versão restaurada. Salve para manter.", 2000)

    # Eventos -------------------------------------------------------------
    def closeEvent(self, event: QCloseEvent):
        if not self.maybe_save_changes():
            event.ignore()
            return
        # salva config
        cfg = load_config()
        cfg["workspace"] = str(self.workspace)
        cfg["theme"] = self.theme
        cfg["favorites"] = list(self.favorites)
        cfg["shortcuts"] = self.shortcuts
        cfg["line_spacing"] = getattr(self, "line_spacing", 1.0)
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
