import difflib
import unicodedata
from datetime import datetime

class Differ:

    def __init__(self):
        self.m = None
        self.n = None
        self.bridges = None
        self.matrix = None

    def _reset(self):
        self.m = None
        self.n = None
        self.bridges = None
        self.matrix = None

    def lcs(self, s1, s2):
        self._reset()
        start = 0
        end = 0
        while s1 and s2 and s1[0] == s2[0]:
            s1 = s1[1:]
            s2 = s2[1:]
            start += 1
        while s1 and s2 and s1[-1] == s2[-1]:
            s1 = s1[:-1]
            s2 = s2[:-1]
            end += 1
            
        self.m = len(s2)
        self.n = len(s1)
        self.matrix = [[0 for _ in range(self.m + 1)] for _ in range(self.n + 1)]
        for i in range(1, self.n + 1):
            for j in range(1, self.m + 1):
                if s2[j-1] == s1[i-1]:
                    self.matrix[i][j] = self.matrix[i-1][j-1] + 1
                else:
                    self.matrix[i][j] = max(self.matrix[i-1][j], self.matrix[i][j-1])
        return start + self.matrix[-1][-1] + end

    def _lcs(self, s1, s2):
        self.m = len(s2)
        self.n = len(s1)
        self.matrix = [[0 for _ in range(self.m + 1)] for _ in range(self.n + 1)]
        for i in range(1, self.n + 1):
            for j in range(1, self.m + 1):
                if s2[j-1] == s1[i-1]:
                    self.matrix[i][j] = self.matrix[i-1][j-1] + 1
                else:
                    self.matrix[i][j] = max(self.matrix[i-1][j], self.matrix[i][j-1])

    def compare(self, s1, s2):
        self._reset()
        diff_start = []
        diff_end = []
        while s1 and s2 and s1[0] == s2[0]:
            diff_start.append("  " + s1[0])
            s1 = s1[1:]
            s2 = s2[1:]
        while s1 and s2 and s1[-1] == s2[-1]:
            diff_end.append("  " + s1[-1])
            s1 = s1[:-1]
            s2 = s2[:-1]

        self._lcs(s1, s2)

        diff = []

        while self.m > 0 or self.n > 0:
            if self.matrix[self.n][self.m-1] == self.matrix[self.n][self.m] and self.m > 0:
                diff.append(("+ " + s2[self.m-1]))
                self.m = self.m-1
            elif self.matrix[self.n-1][self.m] == self.matrix[self.n][self.m] and self.n > 0:
                diff.append(("- " + s1[self.n-1]))
                self.n = self.n-1
            else:
                self.m = self.m-1
                self.n = self.n-1
                diff.append(("  " + s1[self.n]))
        return diff_start + diff[::-1] + diff_end[::-1]


if __name__ == "__main__":

    differ = Differ()

    for s1, s2 in [("This is the first sentence.","That is the second sentence.")]:#, ("XoooYooo","YoooXooo"), ("Wir stellen uns die Frage, ob wir den Fehler finden.", "Ich stelle mir die Frage, wie ich den Fehler finde.")]:

        print(s1, s2, "\n")

        for method in [differ.compare]:

            start = datetime.now()
            
            diff = [item for item in method(s1, s2)]
            print(len([item for item in diff if item.startswith(" ")]))
            print("".join([item[2] for item in diff]))
            print("".join([item[0] for item in diff]))

            end = datetime.now()

            print(end - start)

        print("\n" + "="*50 + "\n")
