import sys
import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

import pandas as pd

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QLabel,
    QFileDialog, QMessageBox, QDialog, QFrame,
    QHeaderView, QSizePolicy, QLineEdit, QFormLayout, QDialogButtonBox, QScrollArea,
)
from PyQt6.QtGui import QFont, QColor, QBrush
from PyQt6.QtCore import Qt

# ── Import user modules ──
from dataset_analyzing import (
    get_summary_column, get_summary_table, column_mode,
    count_NaN, filterby_value, groupby_mode
)
from dataset_refactoring import (
    delete_by_column, row_deleteby_value, column_deleteby_value,
    fill_na, delete_by_value, delete_column, rename_column, drop_duplicate_column
)
from dataset_visualizing import (
    categorical_sum, categorical_mean, categorical_std,
    distribution, scatter_plot, pie
)


# ──────────────────────── STYLE ────────────────────────
BG_DARK     = "#0d0d0d"
BG_PANEL    = "#111111"
BG_TABLE    = "#0a0a0a"
ACCENT_BLUE = "#00aaff"
ACCENT_RED  = "#ff3333"
TEXT_WHITE  = "#e8e8e8"
TEXT_GREY   = "#888888"
BORDER      = "#1e1e1e"

GLOBAL_STYLE = f"""
QMainWindow, QWidget {{
    background-color: {BG_DARK};
    color: {TEXT_WHITE};
    font-family: 'Segoe UI', sans-serif;
}}
QTableWidget {{
    background-color: {BG_TABLE};
    color: {TEXT_WHITE};
    gridline-color: {BORDER};
    border: 1px solid {BORDER};
    border-radius: 6px;
    selection-background-color: #1a3a55;
    font-size: 12px;
}}
QTableWidget::item {{ padding: 4px 8px; }}
QHeaderView::section {{
    background-color: #141414;
    color: {ACCENT_BLUE};
    border: none;
    border-bottom: 1px solid {BORDER};
    border-right: 1px solid {BORDER};
    padding: 6px 8px;
    font-size: 12px;
    font-weight: bold;
}}
QComboBox {{
    background-color: #1a1a1a;
    color: {TEXT_WHITE};
    border: 1px solid #2a2a2a;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 13px;
    min-width: 220px;
}}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox QAbstractItemView {{
    background-color: #1a1a1a;
    color: {TEXT_WHITE};
    border: 1px solid #2a2a2a;
    selection-background-color: #1a3a55;
}}
QPushButton {{
    background-color: #1a1a1a;
    color: {TEXT_WHITE};
    border: 1px solid #2a2a2a;
    border-radius: 6px;
    padding: 7px 18px;
    font-size: 13px;
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: #252525;
    border-color: {ACCENT_BLUE};
}}
QPushButton:pressed {{ background-color: #0d1a26; }}
QLabel {{ color: {TEXT_WHITE}; background: transparent; }}
QLineEdit {{
    background-color: #1a1a1a;
    color: {TEXT_WHITE};
    border: 1px solid #2a2a2a;
    border-radius: 5px;
    padding: 5px 10px;
    font-size: 13px;
}}
QScrollBar:vertical {{
    background: {BG_DARK}; width: 8px; border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: #2a2a2a; border-radius: 4px; min-height: 20px;
}}
QScrollBar:horizontal {{
    background: {BG_DARK}; height: 8px; border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: #2a2a2a; border-radius: 4px;
}}
"""


# ──────────────────────── CLICKABLE LABEL ────────────────────────
from PyQt6.QtCore import pyqtSignal

class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


# ──────────────────────── FUNCTION REGISTRY ────────────────────────
FUNCTIONS = {
    "── Data Analyzing ──":    None,
    "Column Summary":          "analyzing",
    "Table Summary":           "analyzing",
    "Column Mode":             "analyzing",
    "Count NaN":               "analyzing",
    "Filter by Value":         "analyzing",
    "Group by Mode":           "analyzing",
    "── Data Refactoring ──":  None,
    "Delete by Column":        "refactoring",
    "Delete Row by Value":     "refactoring",
    "Delete Column by Value":  "refactoring",
    "Fill NaN":                "refactoring",
    "Delete by Value":         "refactoring",
    "Delete Column":           "refactoring",
    "Rename Column":           "refactoring",
    "Drop Duplicates":         "refactoring",
    "── Data Visualizing ──":  None,
    "Categorical Sum":         "visualizing",
    "Categorical Mean":        "visualizing",
    "Categorical Std":         "visualizing",
    "Distribution":            "visualizing",
    "Scatter Plot":            "visualizing",
    "Pie Chart":               "visualizing",
}


# ──────────────────────── PARAM DIALOG ────────────────────────
class ParamDialog(QDialog):
    def __init__(self, title, fields, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setStyleSheet(GLOBAL_STYLE)
        self.setMinimumWidth(340)
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        lbl = QLabel(title)
        lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {ACCENT_BLUE};")
        layout.addWidget(lbl)

        form = QFormLayout()
        form.setSpacing(10)
        self.inputs = {}
        for field_name, placeholder in fields:
            le = QLineEdit()
            le.setPlaceholderText(str(placeholder))
            form.addRow(QLabel(field_name + ":"), le)
            self.inputs[field_name] = le
        layout.addLayout(form)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def get_values(self):
        return {k: v.text() for k, v in self.inputs.items()}


# ──────────────────────── HELP CONTENT ────────────────────────
HELP_DATA = {
    "Data Analyzing": [
        (
            "Column Summary",
            "Generates statistical summary for the selected numerical column.",
            [
                "• Column must be numerical (int/float).",
                "• Output: mean, std, max, min, sum values.",
            ]
        ),
        (
            "Table Summary",
            "Groups by one column and displays statistics of another numerical column.",
            [
                "• 'Value Column' must be numerical.",
                "• Output: count, mean, std, min, max — for each group.",
            ]
        ),
        (
            "Column Mode",
            "Returns the most frequently occurring value (mode) of the selected column.",
            [
                "• Applicable to both numerical and categorical columns.",
                "• If there are multiple modes, all are listed.",
            ]
        ),
        (
            "Count NaN",
            "Returns the number of missing (NaN) values in the selected column.",
            [
                "• Applicable to any numerical or categorical column.",
                "• Result is a single integer.",
            ]
        ),
        (
            "Filter by Value",
            "Filters rows where the selected column equals the entered value.",
            [
                "• Value is case-sensitive (for string columns).",
                "• Numbers must be entered for numerical columns.",
            ]
        ),
        (
            "Group by Mode",
            "Groups by one column and shows the mode of the other column for each group.",
            [
                "• Two columns must be selected.",
                "• If a group is empty, it is skipped.",
            ]
        ),
    ],
    "Data Refactoring": [
        (
            "Delete by Column",
            "Deletes all rows containing NaN in the specified column.",
            [
                "• Irreversible — Use Undo to revert to the previous state.",
                "• Column name must be written exactly and correctly.",
            ]
        ),
        (
            "Delete Row by Value",
            "Deletes rows that have fewer non-null cells than the entered threshold.",
            [
                "• Parameter: minimum number of non-null cells (integer).",
                "• Example: If 5 is entered, rows with fewer than 5 non-null cells are deleted.",
            ]
        ),
        (
            "Delete Column by Value",
            "Deletes columns that have fewer non-null cells than the entered threshold.",
            [
                "• Parameter: minimum number of non-null cells (integer).",
                "• Used for column-based missing data cleaning.",
            ]
        ),
        (
            "Fill NaN",
            "Fills NaN values in the selected column with a specified constant value.",
            [
                "• Numbers for numerical columns, strings for text columns can be entered.",
                "• Irreversible — Undo can be used.",
            ]
        ),
        (
            "Delete by Value",
            "Completely deletes rows that are equal to the specified value in the selected column.",
            [
                "• Numbers for numerical columns, strings for text columns must be entered.",
                "• Case-sensitive.",
            ]
        ),
        (
            "Delete Column",
            "Completely removes the selected column from the dataset.",
            [
                "• Column name must be written exactly and correctly.",
                "• Irreversible — Undo can be used.",
            ]
        ),
        (
            "Rename Column",
            "Renames the selected column with a new name.",
            [
                "• New name must not conflict with another column.",
                "• Leaving it blank may produce incorrect results.",
            ]
        ),
        (
            "Drop Duplicates",
            "Drops duplicate rows based on the selected column, keeping the first instance.",
            [
                "• Duplication check is performed only on the specified column.",
                "• Differences in other columns are ignored.",
            ]
        ),
    ],
    "Data Visualizing": [
        (
            "Categorical Sum",
            "Groups by a categorical column and displays the sum of a numerical column as a bar chart.",
            [
                "• 'Value Column' must be numerical.",
                "• Vertical chart if categories < 10, horizontal if < 30.",
                "• Chart is not created if there are more than 30 unique values.",
            ]
        ),
        (
            "Categorical Mean",
            "Groups by a categorical column and displays the mean of a numerical column as a bar chart.",
            [
                "• 'Value Column' must be numerical.",
                "• Vertical chart if categories < 10, horizontal if < 30.",
                "• Chart is not created if there are more than 30 unique values.",
            ]
        ),
        (
            "Categorical Std",
            "Groups by a categorical column and displays the standard deviation of a numerical column as a bar chart.",
            [
                "• 'Value Column' must be numerical.",
                "• Vertical chart if categories < 10, horizontal if < 30.",
                "• Chart is not created if there are more than 30 unique values.",
            ]
        ),
        (
            "Distribution",
            "Displays the distribution of a numerical column as a histogram.",
            [
                "• Column must be numerical (int/float).",
                "• 35 bins are used; KDE curve is not shown.",
            ]
        ),
        (
            "Scatter Plot",
            "Displays the relationship between two numerical columns with a scatter plot.",
            [
                "• X and Y columns must be numerical.",
                "• Hue column is optional; can contain at most 8 unique values.",
                "• Hue columns with more than 8 unique values are rejected.",
            ]
        ),
        (
            "Pie Chart",
            "Displays the value distribution of a categorical column as a pie chart.",
            [
                "• A maximum of 15 unique values is supported.",
                "• Chart is not created if there are more than 15 unique values.",
            ]
        ),
    ],
}


# ──────────────────────── HELP WINDOW ────────────────────────
class HelpWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Get Help")
        self.setStyleSheet(GLOBAL_STYLE)
        self.resize(680, 620)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header bar
        header_bar = QWidget()
        header_bar.setFixedHeight(56)
        header_bar.setStyleSheet(f"background:#0d1f33; border-bottom:1px solid {BORDER};")
        hbl = QHBoxLayout(header_bar)
        hbl.setContentsMargins(20, 0, 20, 0)
        title_lbl = QLabel("? Get Help")
        title_lbl.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        title_lbl.setStyleSheet(f"color:{ACCENT_BLUE};")
        hbl.addWidget(title_lbl)
        hbl.addStretch()
        sub = QLabel("Descriptions and limitations of all functions.")
        sub.setStyleSheet(f"color:{TEXT_GREY}; font-size:12px;")
        hbl.addWidget(sub)
        root.addWidget(header_bar)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;}")
        content = QWidget()
        content.setStyleSheet(f"background:{BG_DARK};")
        vbox = QVBoxLayout(content)
        vbox.setContentsMargins(20, 16, 20, 20)
        vbox.setSpacing(4)

        for section_name, funcs in HELP_DATA.items():
            # Section title
            sec_lbl = QLabel(section_name)
            sec_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            sec_lbl.setStyleSheet(
                f"color:{ACCENT_RED}; background:#140000;"
                f" border-radius:4px; padding:5px 10px; margin-top:12px;"
            )
            vbox.addWidget(sec_lbl)

            for func_name, desc, rules in funcs:
                card = QFrame()
                card.setStyleSheet(
                    f"background:#111; border:1px solid {BORDER};"
                    f" border-radius:6px; margin-top:4px;"
                )
                card_layout = QVBoxLayout(card)
                card_layout.setContentsMargins(14, 10, 14, 10)
                card_layout.setSpacing(4)

                name_lbl = QLabel(func_name)
                name_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
                name_lbl.setStyleSheet(f"color:{ACCENT_BLUE}; border:none;")
                card_layout.addWidget(name_lbl)

                desc_lbl = QLabel(desc)
                desc_lbl.setWordWrap(True)
                desc_lbl.setStyleSheet(f"color:{TEXT_WHITE}; font-size:12px; border:none;")
                card_layout.addWidget(desc_lbl)

                for rule in rules:
                    r_lbl = QLabel(rule)
                    r_lbl.setWordWrap(True)
                    r_lbl.setStyleSheet(f"color:{TEXT_GREY}; font-size:11px; border:none;")
                    card_layout.addWidget(r_lbl)

                vbox.addWidget(card)

        vbox.addStretch()
        scroll.setWidget(content)
        root.addWidget(scroll)

        # Footer close
        footer = QWidget()
        footer.setFixedHeight(52)
        footer.setStyleSheet(f"background:{BG_PANEL}; border-top:1px solid {BORDER};")
        fbl = QHBoxLayout(footer)
        fbl.setContentsMargins(20, 0, 20, 0)
        fbl.addStretch()
        close_btn = QPushButton("Kapat")
        close_btn.setFixedWidth(100)
        close_btn.setStyleSheet(f"border-color:{ACCENT_RED}; color:{ACCENT_RED};")
        close_btn.clicked.connect(self.close)
        fbl.addWidget(close_btn)
        root.addWidget(footer)


# ──────────────────────── RESULT WINDOW ────────────────────────
class ResultWindow(QDialog):
    def __init__(self, result, title="Result", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setStyleSheet(GLOBAL_STYLE)
        self.resize(840, 600)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        header = QLabel(title)
        header.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {ACCENT_BLUE};")
        layout.addWidget(header)

        if isinstance(result, plt.Figure):
            canvas = FigureCanvas(result)
            canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            layout.addWidget(canvas)
        elif isinstance(result, pd.DataFrame):
            self._add_dataframe(layout, result)
        elif isinstance(result, pd.Series):
            self._add_dataframe(layout, result.reset_index())
        else:
            lbl = QLabel(str(result))
            lbl.setWordWrap(True)
            lbl.setStyleSheet(f"color: {TEXT_WHITE}; font-size: 14px; padding: 10px;")
            layout.addWidget(lbl)

        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(100)
        close_btn.setStyleSheet(f"border-color: {ACCENT_RED}; color: {ACCENT_RED};")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)

    def _add_dataframe(self, layout, df):
        table = QTableWidget(len(df), len(df.columns))
        table.setHorizontalHeaderLabels([str(c) for c in df.columns])
        for r in range(len(df)):
            for c in range(len(df.columns)):
                item = QTableWidgetItem(str(df.iloc[r, c]))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(r, c, item)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(table)


# ──────────────────────── MAIN WINDOW ────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.df = None
        self.df_history = []
        self.setWindowTitle("MYDataS")
        self.setMinimumSize(1050, 660)
        self.setStyleSheet(GLOBAL_STYLE)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # LEFT
        left = QWidget()
        left.setStyleSheet(f"background: {BG_DARK};")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(16, 16, 8, 16)
        left_layout.setSpacing(10)

        topbar = QHBoxLayout()
        logo = QLabel("MYDataS")
        logo.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        logo.setStyleSheet(f"color: {ACCENT_BLUE};")
        topbar.addWidget(logo)
        topbar.addStretch()

        self.combo = QComboBox()
        self.combo.setFixedHeight(36)
        for name in FUNCTIONS:
            self.combo.addItem(name)
            if FUNCTIONS[name] is None:
                idx = self.combo.count() - 1
                self.combo.model().item(idx).setEnabled(False)
                self.combo.model().item(idx).setForeground(QBrush(QColor(TEXT_GREY)))
        topbar.addWidget(self.combo)

        self.initiate_btn = QPushButton("Initiate")
        self.initiate_btn.setFixedHeight(36)
        self.initiate_btn.setStyleSheet(
            f"background:#0d1f33; color:{ACCENT_BLUE}; border:1px solid {ACCENT_BLUE};"
            f" border-radius:6px; font-weight:bold; padding:0 18px;"
        )
        self.initiate_btn.clicked.connect(self.initiate)
        topbar.addWidget(self.initiate_btn)
        left_layout.addLayout(topbar)

        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(
            self.table.styleSheet() + "QTableWidget{alternate-background-color:#0e0e0e;}"
        )
        left_layout.addWidget(self.table)

        bottombar = QHBoxLayout()
        self.upload_btn = QPushButton("📂  Upload Data")
        self.upload_btn.setFixedHeight(36)
        self.upload_btn.setStyleSheet(
            f"background:#0d1f33; color:{ACCENT_BLUE}; border:1px solid {ACCENT_BLUE}; border-radius:6px;"
        )
        self.upload_btn.clicked.connect(self.load_csv)
        bottombar.addWidget(self.upload_btn)

        self.undo_btn = QPushButton("↩  Undo")
        self.undo_btn.setFixedHeight(36)
        self.undo_btn.setEnabled(False)
        self.undo_btn.setStyleSheet(
            f"background:#1a1200; color:#ffcc00; border:1px solid #ffcc00; border-radius:6px;"
        )
        self.undo_btn.clicked.connect(self.undo)
        bottombar.addWidget(self.undo_btn)
        bottombar.addStretch()

        self.row_count_lbl = QLabel("")
        self.row_count_lbl.setStyleSheet(f"color:{TEXT_GREY}; font-size:12px;")
        bottombar.addWidget(self.row_count_lbl)

        help_btn = QPushButton("? Get Help")
        help_btn.setStyleSheet(
            f"background:transparent; border:none; color:{ACCENT_BLUE};"
            f" font-size:12px; text-decoration:underline; padding:0 4px;"
        )
        help_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        help_btn.clicked.connect(lambda: HelpWindow(self).exec())
        bottombar.addWidget(help_btn)

        left_layout.addLayout(bottombar)
        root.addWidget(left, stretch=1)

        # RIGHT panel
        right = QWidget()
        right.setFixedWidth(210)
        right.setStyleSheet(f"background:{BG_PANEL}; border-left:1px solid {BORDER};")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(14, 16, 14, 16)
        right_layout.setSpacing(6)

        panel_title = QLabel("Functions")
        panel_title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        panel_title.setStyleSheet(f"color:{ACCENT_RED};")
        right_layout.addWidget(panel_title)

        def section(text):
            lbl = QLabel(text)
            lbl.setStyleSheet(f"color:{TEXT_GREY}; font-size:11px; margin-top:8px;")
            right_layout.addWidget(lbl)
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setStyleSheet(f"color:{BORDER};")
            right_layout.addWidget(sep)

        def fn_btn(text):
            btn = QPushButton(text)
            btn.setStyleSheet(
                f"background:transparent; border:none; color:{TEXT_WHITE};"
                f" text-align:left; padding:4px 2px; font-size:12px; border-radius:4px;"
            )
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, t=text: self._select_function(t))
            right_layout.addWidget(btn)

        section("Data Analyzing :")
        for name, cat in FUNCTIONS.items():
            if cat == "analyzing":
                fn_btn(name)
        section("Data Refactoring :")
        for name, cat in FUNCTIONS.items():
            if cat == "refactoring":
                fn_btn(name)
        section("Data Visualizing :")
        for name, cat in FUNCTIONS.items():
            if cat == "visualizing":
                fn_btn(name)

        right_layout.addStretch()
        root.addWidget(right)

    def _select_function(self, name):
        idx = self.combo.findText(name)
        if idx >= 0:
            self.combo.setCurrentIndex(idx)

    # ── CSV LOAD ──
    def load_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if not path:
            return
        try:
            self.df = pd.read_csv(path)
            self.df_history.clear()
            self.undo_btn.setEnabled(False)
            self._populate_table(self.df)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"File could not be loaded:\n{e}")

    def _populate_table(self, df):
        self.table.clear()
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels(list(df.columns))
        for r in range(len(df)):
            for c, col in enumerate(df.columns):
                val = df.iloc[r, c]
                item = QTableWidgetItem("" if pd.isna(val) else str(val))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(r, c, item)
        self.row_count_lbl.setText(f"{len(df)} rows  ·  {len(df.columns)} columns")

    # ── UNDO ──
    def undo(self):
        if self.df_history:
            self.df = self.df_history.pop()
            self._populate_table(self.df)
            self.undo_btn.setEnabled(bool(self.df_history))

    def _save_state(self):
        self.df_history.append(self.df.copy())
        self.undo_btn.setEnabled(True)

    # ── RESULT / WARNING ──
    def _handle_result(self, result, title):
        """If result is an error string → QMessageBox.warning. Otherwise open ResultWindow."""
        if isinstance(result, str) and result.startswith("Error:") or (
            isinstance(result, str) and result.startswith("Too many")
        ):
            QMessageBox.warning(self, "Warning", result)
            return
        win = ResultWindow(result, title, self)
        win.exec()

    # ── INITIATE ──
    def initiate(self):
        if self.df is None:
            QMessageBox.warning(self, "Warning", "First, upload a CSV file.")
            return
        func = self.combo.currentText()
        if FUNCTIONS.get(func) is None:
            QMessageBox.warning(self, "Warning", "Please select a valid function.")
            return

        if FUNCTIONS[func] == "refactoring":
            reply = QMessageBox.question(
                self, "Are you sure?",
                f"'{func}' operation will permanently modify the dataset.\n"
                f"Do you want to continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        cols = list(self.df.columns)

        try:
            # ── ANALYZING ──────────────────────────────────────────
            if func == "Column Summary":
                d = ParamDialog("Column Summary", [("Column", cols[0])], self)
                if d.exec() != QDialog.DialogCode.Accepted: return
                v = d.get_values()
                self._handle_result(get_summary_column(self.df, v["Column"]), func)

            elif func == "Table Summary":
                d = ParamDialog("Table Summary", [
                    ("Grouping Column", cols[0]),
                    ("Value Column", cols[1] if len(cols) > 1 else cols[0])
                ], self)
                if d.exec() != QDialog.DialogCode.Accepted: return
                v = d.get_values()
                self._handle_result(
                    get_summary_table(self.df, v["Grouping Column"], v["Value Column"]), func
                )


            elif func == "Column Mode":
                d = ParamDialog("Column Mode", [("Column", cols[0])], self)
                if d.exec() != QDialog.DialogCode.Accepted: return
                v = d.get_values()
                self._handle_result(column_mode(self.df, v["Column"]), func)

            elif func == "Count NaN":
                d = ParamDialog("Count NaN", [("Column", cols[0])], self)
                if d.exec() != QDialog.DialogCode.Accepted: return
                v = d.get_values()
                n = count_NaN(self.df, v["Column"])
                self._handle_result(f"'{v['Column']}' column number of NaN: {n}", func)

            elif func == "Filter by Value":
                d = ParamDialog("Filter by Value", [("Column", cols[0]), ("Value", "")], self)
                if d.exec() != QDialog.DialogCode.Accepted: return
                v = d.get_values()
                self._handle_result(filterby_value(self.df, v["Column"], v["Value"]), func)

            elif func == "Group by Mode":
                d = ParamDialog("Group by Mode", [
                    ("Grouping Column", cols[0]),
                    ("Value Column", cols[1] if len(cols) > 1 else cols[0])
                ], self)
                if d.exec() != QDialog.DialogCode.Accepted: return
                v = d.get_values()
                self._handle_result(
                    groupby_mode(self.df, v["Grouping Column"], v["Value Column"]), func
                )

            # ── REFACTORING ────────────────────────────────────────
            # Note: refactoring functions mutate inplace, so we copy first and pass the copy.
            elif func == "Delete by Column":
                d = ParamDialog("Delete by Column", [("Column", cols[0])], self)
                if d.exec() != QDialog.DialogCode.Accepted: return
                v = d.get_values()
                self._save_state()
                self.df = self.df.copy()
                delete_by_column(self.df, v["Column"])
                self._populate_table(self.df)

            elif func == "Delete Row by Value":
                d = ParamDialog("Delete Row by Value", [("Minimum Number of Occupied Cells", "5")], self)
                if d.exec() != QDialog.DialogCode.Accepted: return
                v = d.get_values()
                self._save_state()
                self.df = self.df.copy()
                row_deleteby_value(self.df, int(v["Minimum Number of Occupied Cells"]))
                self._populate_table(self.df)

            elif func == "Delete Column by Value":
                d = ParamDialog("Delete Column by Value", [("Minimum Number of Occupied Cells", "5")], self)
                if d.exec() != QDialog.DialogCode.Accepted: return
                v = d.get_values()
                self._save_state()
                self.df = self.df.copy()
                column_deleteby_value(self.df, int(v["Minimum Number of Occupied Cells"]))
                self._populate_table(self.df)

            elif func == "Fill NaN":
                d = ParamDialog("Fill NaN", [("Column", cols[0]), ("Value to Fill", "0")], self)
                if d.exec() != QDialog.DialogCode.Accepted: return
                v = d.get_values()
                val = v["Value to Fill"]
                try: val = float(val)
                except: pass
                self._save_state()
                self.df = self.df.copy()
                fill_na(self.df, v["Column"], val)
                self._populate_table(self.df)

            elif func == "Delete by Value":
                d = ParamDialog("Delete by Value", [("Column", cols[0]), ("Value", "")], self)
                if d.exec() != QDialog.DialogCode.Accepted: return
                v = d.get_values()
                val = v["Value"]
                try: val = float(val)
                except: pass
                self._save_state()
                self.df = self.df.copy()
                delete_by_value(self.df, v["Column"], val)
                self._populate_table(self.df)

            elif func == "Delete Column":
                d = ParamDialog("Delete Column", [("Column", cols[0])], self)
                if d.exec() != QDialog.DialogCode.Accepted: return
                v = d.get_values()
                self._save_state()
                self.df = self.df.copy()
                delete_column(self.df, v["Column"])
                self._populate_table(self.df)

            elif func == "Rename Column":
                d = ParamDialog("Rename Column", [("Column", cols[0]), ("New name", "")], self)
                if d.exec() != QDialog.DialogCode.Accepted: return
                v = d.get_values()
                self._save_state()
                self.df = self.df.copy()
                rename_column(self.df, v["Column"], v["New name"])
                self._populate_table(self.df)

            elif func == "Drop Duplicates":
                d = ParamDialog("Drop Duplicates", [("Column", cols[0])], self)
                if d.exec() != QDialog.DialogCode.Accepted: return
                v = d.get_values()
                self._save_state()
                self.df = self.df.copy()
                drop_duplicate_column(self.df, v["Column"])
                self._populate_table(self.df)

            # ── VISUALIZING ────────────────────────────────────────
            elif func == "Categorical Sum":
                d = ParamDialog("Categorical Sum", [
                    ("Category Column", cols[0]),
                    ("Value Column", cols[1] if len(cols) > 1 else cols[0])
                ], self)
                if d.exec() != QDialog.DialogCode.Accepted: return
                v = d.get_values()
                self._handle_result(
                    categorical_sum(self.df, v["Category Column"], v["Value Column"]), func
                )

            elif func == "Categorical Mean":
                d = ParamDialog("Categorical Mean", [
                    ("Category Column", cols[0]),
                    ("Value Column", cols[1] if len(cols) > 1 else cols[0])
                ], self)
                if d.exec() != QDialog.DialogCode.Accepted: return
                v = d.get_values()
                self._handle_result(
                    categorical_mean(self.df, v["Category Column"], v["Value Column"]), func
                )

            elif func == "Categorical Std":
                d = ParamDialog("Categorical Std", [
                    ("Category Column", cols[0]),
                    ("Value Column", cols[1] if len(cols) > 1 else cols[0])
                ], self)
                if d.exec() != QDialog.DialogCode.Accepted: return
                v = d.get_values()
                self._handle_result(
                    categorical_std(self.df, v["Category Column"], v["Value Column"]), func
                )

            elif func == "Distribution":
                d = ParamDialog("Distribution", [("Column", cols[0])], self)
                if d.exec() != QDialog.DialogCode.Accepted: return
                v = d.get_values()
                self._handle_result(distribution(self.df, v["Column"]), func)

            elif func == "Scatter Plot":
                d = ParamDialog("Scatter Plot", [
                    ("X Column", cols[0]),
                    ("Y Column", cols[1] if len(cols) > 1 else cols[0]),
                    ("Hue Column (optional)", "")
                ], self)
                if d.exec() != QDialog.DialogCode.Accepted: return
                v = d.get_values()
                hue = v["Hue Column (optional)"].strip() or None
                self._handle_result(scatter_plot(self.df, v["X Column"], v["Y Column"], hue), func)

            elif func == "Pie Chart":
                d = ParamDialog("Pie Chart", [("Column", cols[0])], self)
                if d.exec() != QDialog.DialogCode.Accepted: return
                v = d.get_values()
                self._handle_result(pie(self.df, v["Column"]), func)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during the operation:\n{e}")


# ──────────────────────── ENTRY POINT ────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
