"""PySide6 desktop user interface for Calculator."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import sys

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QCloseEvent, QIcon, QKeyEvent, QShowEvent
from PySide6.QtWidgets import QApplication, QGridLayout, QHBoxLayout, QLabel, QSizePolicy, QToolButton, QVBoxLayout, QWidget

from .engine import CalculatorEngine


WINDOW_MINIMUM_SIZE = (320, 500)
WINDOW_INITIAL_SIZE = (360, 560)
CONTENT_MAXIMUM_SIZE = (520, 820)
OUTER_MARGIN = 16
CONTENT_MARGIN = 16
GRID_SPACING = 12
APP_NAME = "Hypeculator"


def _find_icon_path() -> Path:
    """Locate the source or installed Hypeculator icon."""
    source_icon = Path(__file__).resolve().parents[2] / "assets" / "logo" / "hypeculator.png"
    installed_icons = (
        Path(sys.prefix) / "share" / "icons" / "hicolor" / "512x512" / "apps" / "hypeculator.png",
        Path("/usr/share/icons/hicolor/512x512/apps/hypeculator.png"),
    )
    return next((icon for icon in (source_icon, *installed_icons) if icon.is_file()), source_icon)


APP_ICON_PATH = _find_icon_path()

_BUTTON_COLORS = {
    "number": ("#111b2a", "#182b42", "#244364", "#edf7ff"),
    "function": ("#263850", "#345274", "#476b91", "#eaf6ff"),
    "operator": ("#0877d1", "#159cff", "#05549b", "#ffffff"),
}


class CalculatorWindow(QWidget):
    """A compact calculator window backed by a CalculatorEngine instance."""

    def __init__(self, engine: CalculatorEngine | None = None) -> None:
        super().__init__()
        self._engine = engine or CalculatorEngine()
        self._buttons: dict[str, QToolButton] = {}

        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(str(APP_ICON_PATH)))
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setMinimumSize(*WINDOW_MINIMUM_SIZE)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setStyleSheet(
            "CalculatorWindow { background: #02050b; }"
            "QWidget#calculatorContent {"
            "background: #060d18; border: 1px solid #15588f; border-radius: 28px; }"
        )

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(OUTER_MARGIN, OUTER_MARGIN, OUTER_MARGIN, OUTER_MARGIN)
        root_layout.addStretch()

        centered_layout = QHBoxLayout()
        centered_layout.addStretch()
        self._content = QWidget()
        self._content.setObjectName("calculatorContent")
        self._content.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        centered_layout.addWidget(self._content)
        centered_layout.addStretch()
        root_layout.addLayout(centered_layout)
        root_layout.addStretch()

        layout = QVBoxLayout(self._content)
        layout.setContentsMargins(CONTENT_MARGIN, CONTENT_MARGIN, CONTENT_MARGIN, CONTENT_MARGIN)
        layout.setSpacing(GRID_SPACING)

        self._display = QLabel()
        self._display.setObjectName("display")
        self._display.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        self._display.setMinimumHeight(110)
        self._display.setWordWrap(False)
        layout.addWidget(self._display, 28)

        keypad = QGridLayout()
        keypad.setHorizontalSpacing(GRID_SPACING)
        keypad.setVerticalSpacing(GRID_SPACING)
        for index in range(4):
            keypad.setColumnStretch(index, 1)
        for index in range(5):
            keypad.setRowStretch(index, 1)

        self._add_button(keypad, "AC", "function", 0, 0, self._engine.clear)
        self._add_button(keypad, "+/-", "function", 0, 1, self._engine.toggle_sign)
        self._add_button(keypad, "%", "function", 0, 2, self._engine.percentage)
        self._add_button(keypad, "÷", "operator", 0, 3, lambda: self._engine.select_operator("÷"))

        for row, labels in enumerate((("7", "8", "9", "×"), ("4", "5", "6", "-"), ("1", "2", "3", "+")), start=1):
            for column, label in enumerate(labels):
                role = "operator" if label in {"×", "-", "+"} else "number"
                action = self._action_for_label(label)
                self._add_button(keypad, label, role, row, column, action)

        self._add_button(keypad, "0", "number", 4, 0, lambda: self._engine.input_digit("0"), column_span=2)
        self._add_button(keypad, ".", "number", 4, 2, self._engine.input_decimal)
        self._add_button(keypad, "=", "operator", 4, 3, self._engine.equals)

        layout.addLayout(keypad, 72)
        self.resize(*WINDOW_INITIAL_SIZE)
        self._resize_content()
        self._refresh_display()

    def _add_button(
        self,
        layout: QGridLayout,
        label: str,
        role: str,
        row: int,
        column: int,
        action: Callable[[], None],
        column_span: int = 1,
    ) -> None:
        button = QToolButton()
        button.setText(label)
        button.setAccessibleName(label)
        button.setProperty("role", role)
        button.setMinimumSize(54, 54)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        button.clicked.connect(lambda: self._run_action(action))
        layout.addWidget(button, row, column, 1, column_span)
        self._buttons[label] = button

    def _action_for_label(self, label: str) -> Callable[[], None]:
        if label.isdigit():
            return lambda: self._engine.input_digit(label)
        return lambda: self._engine.select_operator(label)

    def _run_action(self, action: Callable[[], None]) -> None:
        action()
        self._refresh_display()

    def _refresh_display(self) -> None:
        value = self._engine.display
        self._display.setText(value)
        self._update_visual_scale()

    def resizeEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        super().resizeEvent(event)
        if not hasattr(self, "_content"):
            return
        self._resize_content()
        self._update_visual_scale()

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        QTimer.singleShot(0, self._update_visual_scale)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Close the application when its only calculator window closes."""
        event.accept()
        application = QApplication.instance()
        if application is not None:
            application.quit()

    def _resize_content(self) -> None:
        content_width = min(self.width() - 2 * OUTER_MARGIN, CONTENT_MAXIMUM_SIZE[0])
        content_height = min(self.height() - 2 * OUTER_MARGIN, CONTENT_MAXIMUM_SIZE[1])
        self._content.setFixedSize(content_width, content_height)

    def _update_visual_scale(self) -> None:
        display_font_size = min(64, max(48, self._content.width() // 6))
        if len(self._engine.display) > 10:
            display_font_size = max(30, display_font_size - 18)
        self._display.setStyleSheet(
            "background: #071323; border: 1px solid #1684cf; border-radius: 18px; "
            f"color: #8eeaff; font-family: Sans Serif; font-size: {display_font_size}px; "
            "font-weight: 600; padding: 8px 12px;"
        )

        for label, button in self._buttons.items():
            diameter = min(button.width(), button.height())
            radius = button.height() // 2 if label == "0" else diameter // 2
            font_size = min(30, max(24, int(diameter * 0.42)))
            button.setStyleSheet(_button_style(button.property("role"), radius, font_size))

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Route supported keyboard input through the same engine actions as buttons."""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            event.accept()
            return

        action = self._keyboard_action(event)
        if action is None:
            event.ignore()
            return

        self._run_action(action)
        event.accept()

    def _keyboard_action(self, event: QKeyEvent) -> Callable[[], None] | None:
        key = event.key()
        text = event.text()

        if len(text) == 1 and text in "0123456789":
            return lambda: self._engine.input_digit(text)
        if text in {".", ","} or key in {Qt.Key.Key_Period, Qt.Key.Key_Comma}:
            return self._engine.input_decimal
        if text in {"+", "-"}:
            return lambda: self._engine.select_operator(text)
        if text == "*":
            return lambda: self._engine.select_operator("×")
        if text == "/":
            return lambda: self._engine.select_operator("÷")
        if text == "=" or key in {Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Equal}:
            return self._engine.equals
        if key == Qt.Key.Key_Delete:
            return self._engine.clear
        return None


def _button_style(role: str, radius: int, font_size: int) -> str:
    background, hover, pressed, text_color = _BUTTON_COLORS[role]
    return f"""
        QToolButton {{
            background: {background};
            border: 1px solid #1a4b76;
            border-radius: {radius}px;
            color: {text_color};
            font-family: Sans Serif;
            font-size: {font_size}px;
            font-weight: 500;
            padding: 6px;
        }}
        QToolButton:hover {{ background: {hover}; border-color: #45bfff; }}
        QToolButton:pressed {{ background: {pressed}; border-color: #8eeaff; }}
    """
