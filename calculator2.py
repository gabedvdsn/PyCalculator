import math


class Calculator:
    def __init__(self):
        self.priority_operations = ['*', '/', '**', '*/']
        self.escape_operations = ['+', '-']

        self.operations = {
            '*': lambda x, y: x * y,
            '/': lambda x, y: x / y,
            '+': lambda x, y: x + y,
            '-': lambda x, y: x - y,
            '**': lambda x, y: math.pow(x, y),
            '*/': lambda x, y: math.pow(x, 1 / y)
        }

        self.last_expr = None

    def evaluate(self, expression: str):
        self.last_expr = Token(self, 0, expression)
        return self.last_expr.evaluate()

    def last(self):
        return self.last_expr.evaluate()


class Token:
    def __init__(self, calc: Calculator, depth: int, expr: str):
        self.calc = calc
        self.depth = depth
        self.expr = expr.replace(' ', '')

        self.operation = ""
        self.left: Token = None
        self.right: Token = None

        self.start = 0

        # Clean unnecessary enclosing parentheses
        while self.expr.startswith('('):
            if len(self._get_parentheses_field(0)) == len(self.expr) - 2:
                self.expr = self._get_parentheses_field(0)
            else:
                break

        print(f"{'  ' * self.depth}[ {self.depth} ] {self.expr}")
        self._inner_breakdown()

    def evaluate(self):
        return self._inner_evaluate()

    def _inner_evaluate(self):
        if self._is_complete_expr():
            return float(self.expr)

        return self.calc.operations[self.operation](self.left._inner_evaluate(), self.right._inner_evaluate())

    def _inner_breakdown(self):
        if not self.expr or self._is_complete_expr():
            print(f"{'  ' * self.depth}[ Complete Expression ] {self.expr}")
            return

        # Check for open parentheses => make token
        if self.expr[self.start] == '(':
            left_expr = self._get_parentheses_field(self.start)
            if left_expr == self.expr:
                left_expr = self._get_fields_until(self.start, list(self.calc.operations.keys()))
            print(f"{'  ' * self.depth}[ Open Parentheses ] Created L token: {left_expr}")
            self.left = Token(self.calc, self.depth + 1, left_expr)

            self.start += len(self.left.expr) + 2
            self.operation = self._get_next_operation(self.start)
            print(f"{'  ' * self.depth}[ Operation ] {self.operation}")
            self.start += len(self.operation)

            right_expr = self.expr[self.start:]
            print(f"{'  ' * self.depth}[ Easy Assign ] Created R token: {right_expr}")
            self.right = Token(self.calc, self.depth + 1, right_expr)

            return

        # We have neither left nor right assigned yet

        # Must be a number next
        left_expr = self._get_fields_having(self.start, self.calc.priority_operations)
        if left_expr == self.expr:
            left_expr = self._get_fields_until(self.start, list(self.calc.operations.keys()))

        # Check edge case when expression ends with operation (before parentheses)
        if any([left_expr.endswith(oper) for oper in self.calc.operations.keys()]):
            if not self.expr[self.start + len(left_expr)] == '(':
                raise Exception("Unmatched parentheses")
            left_expr += self._get_parentheses_field(self.start + len(left_expr), True)

        print(f"{'  ' * self.depth}[ Sub-Expression ] Created L token: {left_expr}")
        self.left = Token(self.calc, self.depth + 1, left_expr)
        self.start += len(self.left.expr)

        # Must be operation next
        self.operation = self._get_next_operation(self.start)
        print(f"{'  ' * self.depth}[ Operation ] {self.operation}")
        self.start += len(self.operation)

        # Now we can assign right branch
        right_expr = self.expr[self.start:]
        print(f"{'  ' * self.depth}[ Easy Assign ] Created R token: {right_expr}")
        self.right = Token(self.calc, self.depth + 1, right_expr)

    def _is_complete_expr(self):
        for oper in self.calc.operations.keys():
            if oper in self.expr:
                return False
        return not ('(' in self.expr or ')' in self.expr)

    def _get_fields_until(self, start: int, stopon_symbols: list[str]):
        i = start
        while i < len(self.expr):
            if self.expr[i] in stopon_symbols:
                return self.expr[start:i]

            i += 1
        return self.expr[start:]

    def _get_fields_having(self, start: int, allow_symbols: list[str]):
        i = start - 1
        unaccompanied_decimal = False
        while i < len(self.expr) - 1:
            i += 1

            if self.expr[i] not in allow_symbols and not self.expr[i].isdigit():
                if self.expr[i] == '.':
                    if unaccompanied_decimal:
                        raise Exception(f"Could not resolve decimal point at {i}")
                    unaccompanied_decimal = True
                    continue
                elif self.expr[i].isdigit():
                    unaccompanied_decimal = False
                    continue
                elif self.expr[i] == ")":
                    outer_str = self._get_fields_having(i + 1, allow_symbols)
                    if len(outer_str) > 0:
                        return self.expr[start:i + len(outer_str)]

                return self.expr[start:i]

        return self.expr[start:]

    def _get_parentheses_field(self, start: int, include_out: bool = False):
        i = start
        count = 0
        while i < len(self.expr):
            if self.expr[start + i] == ')':
                if count == 1:
                    out = start + i if not include_out else start + i + 1
                    if self._get_fields_until(start + i + 1, self.calc.escape_operations):
                        out += len(self._get_fields_until(start + i + 1, self.calc.escape_operations))
                    return self.expr[start + 1:out]
                count -= 1
            if self.expr[start + i] == '(':
                count += 1

            i += 1
        raise Exception(f"Missing {count} closing parentheses at index {i}")

    def _get_next_operation(self, start: int):
        i = start
        while i < len(self.expr):
            if self.expr[i] not in self.calc.operations.keys():
                return self.expr[start:i]

            i += 1
        e_string = f"Operation is invalid at index {i - 1}"
        raise Exception(e_string)


c = Calculator()
# print(c.evaluate("5**2+5**(2*3)"))
print(c.evaluate("5**2+6**3"))
# print(c.evaluate("(((5**2 + (5 * 2) * 9 - 12 */ 3)))"))
