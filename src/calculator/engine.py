"""UI-independent calculator state and Decimal arithmetic."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, DivisionByZero, InvalidOperation, localcontext


DISPLAY_MAX_LENGTH = 16
OPERATORS = {"+", "-", "×", "÷"}


def format_decimal(value: Decimal, max_length: int = DISPLAY_MAX_LENGTH) -> str:
    """Return a compact, readable Decimal representation for the result display."""
    if value.is_zero():
        return "0"

    fixed = format(value, "f")
    if "." in fixed:
        fixed = fixed.rstrip("0").rstrip(".")
    if len(fixed) <= max_length:
        return fixed

    for precision in range(max_length, 0, -1):
        candidate = format(value, f".{precision}g").replace("E", "e")
        if len(candidate) <= max_length:
            return candidate

    return "Overflow"


@dataclass
class CalculatorEngine:
    """A stateful four-function calculator with no UI dependency."""

    _entry: str = "0"
    _accumulator: Decimal | None = None
    _pending_operator: str | None = None
    _waiting_for_operand: bool = False
    _last_operator: str | None = None
    _last_operand: Decimal | None = None
    _just_evaluated: bool = False
    _error_message: str | None = None

    @property
    def display(self) -> str:
        """Return the current user-facing display value."""
        return "Error" if self._error_message else self._entry

    @property
    def error_message(self) -> str | None:
        """Return the error detail for a future UI to present accessibly."""
        return self._error_message

    def clear(self) -> None:
        """Reset all calculator state."""
        self._entry = "0"
        self._accumulator = None
        self._pending_operator = None
        self._waiting_for_operand = False
        self._last_operator = None
        self._last_operand = None
        self._just_evaluated = False
        self._error_message = None

    def input_digit(self, digit: str) -> None:
        """Append one decimal digit to the current operand."""
        if len(digit) != 1 or not digit.isdigit():
            raise ValueError("digit must be a single decimal digit")

        self._prepare_for_number_input()
        if self._entry == "0":
            self._entry = digit
        elif self._entry == "-0":
            self._entry = f"-{digit}"
        elif len(self._entry) < DISPLAY_MAX_LENGTH:
            self._entry += digit

    def input_decimal(self) -> None:
        """Add a decimal separator when the current operand has none."""
        self._prepare_for_number_input()
        if "." not in self._entry and len(self._entry) < DISPLAY_MAX_LENGTH:
            self._entry += "."

    def select_operator(self, operator: str) -> None:
        """Select an arithmetic operator, evaluating a prior complete operation."""
        if operator not in OPERATORS:
            raise ValueError(f"unsupported operator: {operator}")
        if self._error_message:
            return

        if self._pending_operator and not self._waiting_for_operand:
            result = self._apply(self._accumulator, self._current_value(), self._pending_operator)
            if result is None:
                return
            self._accumulator = result
            self._entry = format_decimal(result)
        elif self._accumulator is None:
            self._accumulator = self._current_value()

        self._pending_operator = operator
        self._waiting_for_operand = True
        self._just_evaluated = False
        self._last_operator = None
        self._last_operand = None

    def equals(self) -> None:
        """Evaluate the pending operation or repeat the most recent operation."""
        if self._error_message:
            return

        if self._pending_operator:
            operand = self._accumulator if self._waiting_for_operand else self._current_value()
            result = self._apply(self._accumulator, operand, self._pending_operator)
            if result is None:
                return
            self._last_operator = self._pending_operator
            self._last_operand = operand
            self._entry = format_decimal(result)
            self._accumulator = None
            self._pending_operator = None
            self._waiting_for_operand = False
            self._just_evaluated = True
            return

        if self._last_operator and self._last_operand is not None:
            result = self._apply(self._current_value(), self._last_operand, self._last_operator)
            if result is None:
                return
            self._entry = format_decimal(result)
            self._just_evaluated = True

    def toggle_sign(self) -> None:
        """Invert the sign of the current operand."""
        if self._error_message:
            return
        if self._waiting_for_operand:
            self._entry = "0"
            self._waiting_for_operand = False
        if self._entry.startswith("-"):
            self._entry = self._entry[1:]
        else:
            self._entry = f"-{self._entry}"

    def percentage(self) -> None:
        """Apply context-sensitive percentage behavior."""
        if self._error_message:
            return

        value = self._current_value()
        if self._pending_operator in {"+", "-"} and self._accumulator is not None:
            value = self._accumulator * value / Decimal("100")
        else:
            value /= Decimal("100")

        self._entry = format_decimal(value)
        self._waiting_for_operand = False
        self._just_evaluated = False

    def _prepare_for_number_input(self) -> None:
        if self._error_message or self._just_evaluated:
            self.clear()
        if self._waiting_for_operand:
            self._entry = "0"
            self._waiting_for_operand = False

    def _current_value(self) -> Decimal:
        return Decimal(self._entry)

    def _apply(
        self, left: Decimal | None, right: Decimal | None, operator: str
    ) -> Decimal | None:
        if left is None or right is None:
            raise RuntimeError("an operation requires two operands")

        try:
            with localcontext() as context:
                context.prec = 50
                if operator == "+":
                    return left + right
                if operator == "-":
                    return left - right
                if operator == "×":
                    return left * right
                return left / right
        except (DivisionByZero, InvalidOperation):
            self._set_error("Cannot divide by zero")
            return None

    def _set_error(self, message: str) -> None:
        self._error_message = message
        self._accumulator = None
        self._pending_operator = None
        self._waiting_for_operand = False
        self._last_operator = None
        self._last_operand = None
        self._just_evaluated = False
