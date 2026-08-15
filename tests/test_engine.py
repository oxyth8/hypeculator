from decimal import Decimal
import unittest

from calculator.engine import CalculatorEngine, DISPLAY_MAX_LENGTH, format_decimal


def enter(engine: CalculatorEngine, value: str) -> None:
    for character in value:
        if character == ".":
            engine.input_decimal()
        else:
            engine.input_digit(character)


class CalculatorEngineTests(unittest.TestCase):
    def test_four_basic_operations_use_decimal_values(self) -> None:
        cases = (("+", "0.3"), ("-", "-0.1"), ("×", "0.02"), ("÷", "0.5"))
        for operator, expected in cases:
            with self.subTest(operator=operator):
                engine = CalculatorEngine()
                enter(engine, "0.1")
                engine.select_operator(operator)
                enter(engine, "0.2")
                engine.equals()
                self.assertEqual(engine.display, expected)

    def test_decimal_input_allows_one_separator(self) -> None:
        engine = CalculatorEngine()
        engine.input_decimal()
        enter(engine, "25")
        engine.input_decimal()
        enter(engine, "5")
        self.assertEqual(engine.display, "0.255")

    def test_chained_operations_evaluate_in_entry_order(self) -> None:
        engine = CalculatorEngine()
        enter(engine, "2")
        engine.select_operator("+")
        enter(engine, "3")
        engine.select_operator("×")
        enter(engine, "4")
        engine.equals()
        self.assertEqual(engine.display, "20")

    def test_clear_resets_all_state(self) -> None:
        engine = CalculatorEngine()
        enter(engine, "5")
        engine.select_operator("+")
        enter(engine, "2")
        engine.clear()
        engine.equals()
        self.assertEqual(engine.display, "0")
        self.assertIsNone(engine.error_message)

    def test_sign_toggle_inverts_current_operand(self) -> None:
        engine = CalculatorEngine()
        enter(engine, "12.5")
        engine.toggle_sign()
        self.assertEqual(engine.display, "-12.5")
        engine.toggle_sign()
        self.assertEqual(engine.display, "12.5")

    def test_sign_toggle_starts_a_negative_second_operand(self) -> None:
        engine = CalculatorEngine()
        enter(engine, "5")
        engine.select_operator("+")
        engine.toggle_sign()
        self.assertEqual(engine.display, "-0")
        enter(engine, "2")
        engine.equals()
        self.assertEqual(engine.display, "3")

    def test_context_sensitive_percentage(self) -> None:
        cases = (("+", "220"), ("-", "180"), ("×", "20"), ("÷", "2000"))
        for operator, expected in cases:
            with self.subTest(operator=operator):
                engine = CalculatorEngine()
                enter(engine, "200")
                engine.select_operator(operator)
                enter(engine, "10")
                engine.percentage()
                engine.equals()
                self.assertEqual(engine.display, expected)

    def test_percentage_without_pending_operation_divides_by_one_hundred(self) -> None:
        engine = CalculatorEngine()
        enter(engine, "10")
        engine.percentage()
        self.assertEqual(engine.display, "0.1")

    def test_repeated_equals_reuses_last_operation_and_operand(self) -> None:
        engine = CalculatorEngine()
        enter(engine, "5")
        engine.select_operator("+")
        enter(engine, "2")
        engine.equals()
        engine.equals()
        engine.equals()
        self.assertEqual(engine.display, "11")

    def test_equals_without_second_operand_reuses_first_operand(self) -> None:
        engine = CalculatorEngine()
        enter(engine, "5")
        engine.select_operator("+")
        engine.equals()
        self.assertEqual(engine.display, "10")

    def test_last_operator_replaces_pending_operator(self) -> None:
        engine = CalculatorEngine()
        enter(engine, "5")
        engine.select_operator("+")
        engine.select_operator("-")
        enter(engine, "2")
        engine.equals()
        self.assertEqual(engine.display, "3")

    def test_division_by_zero_has_a_clear_error_and_recovers_on_number_input(self) -> None:
        engine = CalculatorEngine()
        enter(engine, "5")
        engine.select_operator("÷")
        enter(engine, "0")
        engine.equals()
        self.assertEqual(engine.display, "Error")
        self.assertEqual(engine.error_message, "Cannot divide by zero")
        engine.input_digit("7")
        self.assertEqual(engine.display, "7")
        self.assertIsNone(engine.error_message)

    def test_formatter_removes_trailing_artifacts_and_fits_the_display(self) -> None:
        self.assertEqual(format_decimal(Decimal("1.2300")), "1.23")
        long_value = format_decimal(Decimal("12345678901234567890"))
        self.assertLessEqual(len(long_value), DISPLAY_MAX_LENGTH)
        self.assertNotIn("Infinity", long_value)
        self.assertNotIn("NaN", long_value)

    def test_direct_number_input_is_limited_to_the_display_length(self) -> None:
        engine = CalculatorEngine()
        enter(engine, "12345678901234567890")
        self.assertEqual(engine.display, "1234567890123456")
        self.assertEqual(len(engine.display), DISPLAY_MAX_LENGTH)


if __name__ == "__main__":
    unittest.main()
