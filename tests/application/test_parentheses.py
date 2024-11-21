import time
import unittest

from application.parentheses import HolodequeSolution, Parentheses, StackSolution


class TestParenthesesSolutions(unittest.TestCase):

    def setUp(self) -> None:
        self.stack_solution = StackSolution()
        self.holodeque_solution = HolodequeSolution()

    def test_isValid(self) -> None:
        # Test with fixed cases
        fixed_cases = [
            "",        # valid
            "()[]{}",  # valid
            "([{}])",  # valid
            "{[()]}",  # valid
            "{[()]]",  # invalid
            "([)]",    # invalid
            "({[])(})"  # invalid
        ]

        for case in fixed_cases:
            parens = Parentheses(case)
            self.assertEqual(
                self.stack_solution.isValid(parens),
                self.holodeque_solution.isValid(parens),
                f"Mismatch for case: {case}"
            )

    def test_random_isValid(self) -> None:

        stack_total_time = 0.
        holodeque_total_time = 0.

        for _ in range(1_000_000):
            random_case = Parentheses.randomstring(90)
            parens = Parentheses(random_case)

            # Time StackSolution
            start_time = time.time()
            stack_result = self.stack_solution.isValid(parens)
            stack_total_time += time.time() - start_time

            # Time HolodequeSolution
            start_time = time.time()
            holodeque_result = self.holodeque_solution.isValid(parens)
            holodeque_total_time += time.time() - start_time

            self.assertEqual(
                stack_result,
                holodeque_result,
                f"Mismatch for random case: {random_case}"
            )

        print(f"Total time for StackSolution: {stack_total_time:.4f} seconds")
        print(f"Total time for HolodequeSolution: {
              holodeque_total_time:.4f} seconds")


if __name__ == '__main__':
    unittest.main()
