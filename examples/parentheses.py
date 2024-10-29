import random
from src.holodeque import holodeque


class Parentheses:

    def __init__(self, string: str) -> None:
        parens_list: list[str] = []
        for ch in string:
            if ch not in "()[]{}":
                raise ValueError(f"Incorrect character: {ch}.")
            parens_list.append(ch)
        self._string: str = "".join(parens_list)

    @property
    def string(self) -> str:
        return self._string

    @staticmethod
    def randomstring(n: int) -> str:
        parens_list: list[str] = []
        for _ in range(n):
            parens_list.append(random.choice("()[]{}"))
        return "".join(parens_list)


class StackSolution:

    def __init__(self) -> None:
        self.pairs: dict[str, str] = {"(": ")", "[": "]", "{": "}"}
        self.stack: list[str] = []

    def isValid(self, parentheses: Parentheses) -> bool:
        for ch in parentheses.string:
            if ch in self.pairs:
                self.stack.append(ch)
            elif self.stack and ch == self.pairs[self.stack[-1]]:
                self.stack.pop()
            else:
                self.stack.clear()
                return False
        ans: bool = not self.stack
        self.stack.clear()
        return ans


class HolodequeSolution:

    def __init__(self) -> None:
        self.pairs: dict[str, str] = {"(": ")", "[": "]", "{": "}"}
        self.holodeque: holodeque = holodeque(alphabet=set("()[]{}"))

    def isValid(self, parentheses: Parentheses) -> bool:
        for ch in parentheses.string:
            if ch in self.pairs:
                self.holodeque.pushright(ch)
            elif self.holodeque and ch == self.pairs[self.holodeque.peekright()]:
                self.holodeque.popright()
            else:
                self.holodeque.clear()
                return False
        ans: bool = not self.holodeque
        self.holodeque.clear()
        return ans
