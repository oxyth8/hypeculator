import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, Qt
from PySide6.QtTest import QTest

from calculator.ui import CalculatorWindow


class CalculatorWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = QApplication.instance() or QApplication([])

    def test_window_opens_and_screen_buttons_use_the_calculator_engine(self) -> None:
        window = CalculatorWindow()
        window.show()
        self.application.processEvents()

        self.assertTrue(window.isVisible())
        self.assertEqual(window.windowTitle(), "Hypeculator")
        self.assertFalse(window.windowIcon().isNull())
        self.assertTrue(window.windowFlags() & Qt.WindowType.WindowStaysOnTopHint)
        for label in ("5", "+", "2", "="):
            window._buttons[label].click()

        self.assertEqual(window._display.text(), "7")
        window.close()

    def test_keyboard_and_screen_buttons_produce_the_same_result(self) -> None:
        keyboard_window = CalculatorWindow()
        keyboard_window.show()
        self.application.processEvents()
        for key in (Qt.Key.Key_5, Qt.Key.Key_Plus, Qt.Key.Key_2, Qt.Key.Key_Equal):
            QTest.keyClick(keyboard_window, key)

        button_window = CalculatorWindow()
        button_window.show()
        self.application.processEvents()
        for label in ("5", "+", "2", "="):
            button_window._buttons[label].click()

        self.assertEqual(keyboard_window._display.text(), "7")
        self.assertEqual(keyboard_window._display.text(), button_window._display.text())
        keyboard_window.close()
        button_window.close()

    def test_keyboard_maps_numpad_style_operations_and_delete_clear(self) -> None:
        window = CalculatorWindow()
        window.show()
        self.application.processEvents()
        QTest.keyClick(window, Qt.Key.Key_8, Qt.KeyboardModifier.KeypadModifier)
        QTest.keyClick(window, Qt.Key.Key_Asterisk, Qt.KeyboardModifier.KeypadModifier)
        QTest.keyClick(window, Qt.Key.Key_2, Qt.KeyboardModifier.KeypadModifier)
        QTest.keyClick(window, Qt.Key.Key_Return)
        self.assertEqual(window._display.text(), "16")

        QTest.keyClick(window, Qt.Key.Key_Delete)
        self.assertEqual(window._display.text(), "0")
        self.assertTrue(window.isVisible())
        window.close()

    def test_escape_closes_the_window_and_quits_the_application_event_loop(self) -> None:
        window = CalculatorWindow()
        window.show()
        self.application.processEvents()
        previous_quit_behavior = self.application.quitOnLastWindowClosed()
        self.application.setQuitOnLastWindowClosed(False)
        try:
            QTimer.singleShot(0, lambda: QTest.keyClick(window, Qt.Key.Key_Escape))
            self.assertEqual(self.application.exec(), 0)
            self.assertFalse(window.isVisible())
        finally:
            self.application.setQuitOnLastWindowClosed(previous_quit_behavior)

    def test_keyboard_maps_decimal_subtraction_division_enter_and_delete(self) -> None:
        window = CalculatorWindow()
        window.show()
        self.application.processEvents()

        for key in (Qt.Key.Key_5, Qt.Key.Key_Period, Qt.Key.Key_5, Qt.Key.Key_Minus, Qt.Key.Key_2, Qt.Key.Key_Equal):
            QTest.keyClick(window, key)
        self.assertEqual(window._display.text(), "3.5")

        QTest.keyClick(window, Qt.Key.Key_Delete)
        self.assertEqual(window._display.text(), "0")

        for key in (Qt.Key.Key_8, Qt.Key.Key_Slash, Qt.Key.Key_2, Qt.Key.Key_Enter):
            QTest.keyClick(window, key)
        self.assertEqual(window._display.text(), "4")
        window.close()

    def test_keyboard_comma_maps_to_decimal_input(self) -> None:
        window = CalculatorWindow()
        window.show()
        self.application.processEvents()
        QTest.keyClick(window, Qt.Key.Key_1)
        QTest.keyClick(window, Qt.Key.Key_Comma)
        QTest.keyClick(window, Qt.Key.Key_5)
        self.assertEqual(window._display.text(), "1.5")
        window.close()

    def test_layout_keeps_a_wide_zero_button_when_resized(self) -> None:
        window = CalculatorWindow()
        window.resize(900, 1000)
        window.show()
        self.application.processEvents()

        self.assertGreater(window._buttons["0"].width(), window._buttons["."].width())
        self.assertGreaterEqual(window._buttons["7"].width(), 54)
        self.assertGreaterEqual(window._buttons["7"].height(), 54)
        window.close()

    def test_first_render_uses_geometry_matched_button_radii(self) -> None:
        window = CalculatorWindow()
        window.show()
        QTest.qWait(1)
        self.application.processEvents()

        for label in ("7", "+", "0"):
            button = window._buttons[label]
            expected_radius = button.height() // 2 if label == "0" else min(button.width(), button.height()) // 2
            self.assertIn(f"border-radius: {expected_radius}px", button.styleSheet())
        window.close()


if __name__ == "__main__":
    unittest.main()
