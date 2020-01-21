#!/usr/bin/python3
# achen 2020/1/11 1:29 AM
# cell_programming

import math


class BaseCell(object):
    def run(self):
        pass

    def main(self):
        pass


class SubtractCell(BaseCell):
    def __init__(self, a, b):
        self.a = a
        self.b = b
        self.next_cell = SqrtCell
        self.error_cell = ErrorCell

    def run(self):
        return self.a - self.b

    def main(self):
        try:
            result = self.run()
            self.next_cell(result).main()
        except Exception as e:
            print(e.__repr__())
            self.error_cell(self.a, self.b).main()


class SqrtCell(BaseCell):
    def __init__(self, n):
        self.n = n
        self.next_cell = None
        self.error_cell = SqrtErrorCell

    def run(self):
        return math.sqrt(self.n)

    def main(self):
        try:
            result = self.run()
            if self.next_cell is None:
                print(result)
        except Exception as e:
            print(e.__repr__())
            self.error_cell(self.n).main()


class ErrorCell(BaseCell):
    def __init__(self, a, b):
        self.a, self.b = float(a), float(b)
        self.next_cell = SubtractCell

    def main(self):
        self.next_cell(self.a, self.b).main()


class SqrtErrorCell(BaseCell):
    def __init__(self, n):
        self.n = -n
        self.next_cell = SqrtCell

    def main(self):
        self.next_cell(self.n).main()


if __name__ == '__main__':
    SubtractCell('45', 9).main()
