# python_syntax_highlighter.py
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt5.QtCore import QRegExp

class PythonSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []

        # Keyword format (e.g., def, class, etc.)
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            "\\bdef\\b", "\\bclass\\b", "\\breturn\\b", "\\bif\\b", "\\belse\\b",
            "\\belif\\b", "\\bfor\\b", "\\bwhile\\b", "\\bbreak\\b", "\\bcontinue\\b",
            "\\bimport\\b", "\\bfrom\\b", "\\bpass\\b", "\\bNone\\b", "\\bTrue\\b", "\\bFalse\\b"
        ]
        for keyword in keywords:
            self.highlighting_rules.append((QRegExp(keyword), keyword_format))

        # Class name format
        class_format = QTextCharFormat()
        class_format.setForeground(QColor("#4EC9B0"))
        self.highlighting_rules.append((QRegExp("\\b[A-Z][a-zA-Z0-9_]+\\b"), class_format))

        # Function name format
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#DCDCAA"))
        self.highlighting_rules.append((QRegExp("\\b[A-Za-z0-9_]+(?=\\()"), function_format))

        # String format
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))
        self.highlighting_rules.append((QRegExp("\".*\""), string_format))
        self.highlighting_rules.append((QRegExp("\'.*\'"), string_format))

        # Comment format
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        self.highlighting_rules.append((QRegExp("#[^\n]*"), comment_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)
