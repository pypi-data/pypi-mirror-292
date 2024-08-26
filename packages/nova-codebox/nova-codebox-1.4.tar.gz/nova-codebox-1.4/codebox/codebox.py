from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QPlainTextEdit, QPushButton, QLabel, 
                             QHBoxLayout, QWidget, QApplication, QSizePolicy)
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtCore import Qt, QTimer
from .python_syntax_highlighter import PythonSyntaxHighlighter


class CodeBoxWidget(QFrame):
    def __init__(self, code, parent=None):
        super().__init__(parent)
        self.setObjectName("codeBoxFrame")

        # Hauptlayout für die CodeBox als Attribut speichern
        self.container_layout = QVBoxLayout(self)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)

        # Titelleiste
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        title_bar.setStyleSheet("""
            #titleBar {
                background-color: #424242;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
                border: 2px solid #424242;
            }
        """)
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(20, 6, 20, 6)

        language_label = QLabel("python")
        language_label.setStyleSheet("""
            color: #a9b7c6;
            font-size: 12px;
            background-color:424242;
        """)
        title_bar_layout.addWidget(language_label)
        title_bar_layout.addStretch()

        self.copy_button = QPushButton("Code kopieren")
        self.copy_button.setObjectName("copyButton")
        self.copy_button.setStyleSheet("""
            #copyButton {
                background-color: transparent;
                color: #a9b7c6;
                border: none;
                font-size: 12px;
            }
            #copyButton:hover {
                color: white;
            }
            #copyButton[copied="true"] {
                color: white;
                font-weight: bold;
            }
        """)
        self.copy_button.clicked.connect(self.copy_code)
        title_bar_layout.addWidget(self.copy_button)

        # Code-Box
        self.code_box = QPlainTextEdit()
        self.code_box.setStyleSheet("""
            QPlainTextEdit {
                background-color: #000000;
                color: #d4d4d4;
                border: 2px solid #424242;
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 14px;
                padding: 10px;
            }
        """)
        self.code_box.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.code_box.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.code_box.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.code_box.setReadOnly(True)

        # Anwenden des Syntax-Highlighters
        self.highlighter = PythonSyntaxHighlighter(self.code_box.document())

        # Füge Titelleiste und Code-Box zum Layout hinzu
        self.container_layout.addWidget(title_bar)
        self.container_layout.addWidget(self.code_box)

        # Timer für Button-Text-Reset
        self.button_timer = QTimer(self)
        self.button_timer.setSingleShot(True)
        self.button_timer.timeout.connect(self.reset_button_text)

        # Verbinden Sie das textChanged-Signal mit der updateHeight-Methode
        self.code_box.textChanged.connect(self.updateHeight)

        # Setze den initialen Code
        self.setCode(code)

    def setCode(self, code):
        self.code_box.setPlainText(code)
        self.updateHeight()

    def updateHeight(self):
        # Berechnen Sie die Anzahl der Zeilen und die Höhe einer Zeile
        num_lines = self.code_box.document().blockCount()
        line_height = QFontMetrics(self.code_box.font()).height()

        # Berechnen Sie die erforderliche Höhe für alle Zeilen
        content_height = num_lines * line_height
        margins = self.code_box.contentsMargins()
        extra_space = 30  # 20 für Polsterung + 26 zusätzliche Pixel

        # Setzen Sie die berechnete Höhe
        self.code_box.setFixedHeight(int(content_height + margins.top() + margins.bottom() + extra_space))

        # Aktualisieren Sie die Gesamthöhe des Widgets
        title_bar_height = self.container_layout.itemAt(0).widget().sizeHint().height()
        total_height = content_height + margins.top() + margins.bottom() + extra_space + title_bar_height
        self.setFixedHeight(int(total_height))

    def copy_code(self):
        code = self.code_box.toPlainText()
        QApplication.clipboard().setText(code)
        self.copy_button.setText("Kopiert!")
        self.copy_button.setProperty("copied", "true")
        self.copy_button.setStyle(self.copy_button.style())  # Erzwingt Style-Update
        self.copy_button.setDisabled(True)
        self.button_timer.start(2000)  # 2000 Millisekunden = 2 Sekunden

    def reset_button_text(self):
        self.copy_button.setText("Code kopieren")
        self.copy_button.setProperty("copied", "false")
        self.copy_button.setStyle(self.copy_button.style())  # Erzwingt Style-Update
        self.copy_button.setDisabled(False)


# Factory-Funktion für einfache Integration in die Hauptanwendung
def create_code_box_widget(code, parent=None):
    widget = QWidget(parent)
    layout = QVBoxLayout(widget)
    
    code_box_widget = CodeBoxWidget(code)
    layout.addWidget(code_box_widget)
    
    return widget
