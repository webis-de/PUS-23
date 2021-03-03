import difflib
import unicodedata
from datetime import datetime

class Bridge():

    def __init__(self, k, l, i, j, c):
        self.k = k
        self.l = l
        self.i = i
        self.j = j
        self.c = c

class Bridges:

    def __init__(self):
        self.bridges = []

    def add(self, k, l, i, j, c):
        self.bridges.append(Bridge(k, l, i, j, c))

    def find(self, i, j):
        for bridge in self.bridges:
            if bridge.i == i and bridge.j == j:
                return bridge.k, bridge.l, bridge.c

class Differ:

    def __init__(self):
        self.m = None
        self.n = None
        self.bridges = None
        self.matrix = None

    def lcs(self, s1, s2):
        pre = 0
        while s1 and s2 and s1[0] == s2[0]:
            s1 = s1[1:]
            s2 = s2[2:]
            pre += 1
        while s1 and s2 and s1[-1] == s2[-1]:
            s1 = s1[:-1]
            s2 = s2[:-1]
            pre += 1
            
        self.m = len(s2)
        self.n = len(s1)
        self.bridges = Bridges()
        self.matrix = [[0 for _ in range(self.m + 1)] for _ in range(self.n + 1)]
        for i in range(1, self.n + 1):
            for j in range(1, self.m + 1):
                if s2[j-1] == s1[i-1]:
                    self.bridges.add(j-1, i-1, j, i, s2[j-1])
                    self.matrix[i][j] = self.matrix[i-1][j-1] + 1
                else:
                    self.matrix[i][j] = max(self.matrix[i-1][j], self.matrix[i][j-1])
        return self.matrix[-1][-1] + pre

    def compare(self, s1, s2):
        diff = []
        while s1 and s2 and s1[0] == s2[0]:
            diff.append("  " + s1[0])
            s1 = s1[1:]
            s2 = s2[2:]
        while s1 and s2 and s1[-1] == s2[-1]:
            diff.append("  " + s1[-1])
            s1 = s1[:-1]
            s2 = s2[:-1]
                
        self.lcs(s1, s2)
        
        while self.m != 0 or self.n != 0:
            if self.matrix[self.n][self.m-1] == self.matrix[self.n][self.m] and self.m != 0:
                diff.append(("+ " + s2[self.m-1]))
                self.m = max(self.m-1, 0)
            elif self.matrix[self.n-1][self.m] == self.matrix[self.n][self.m] and self.n != 0:
                diff.append(("- " + s1[self.n-1]))
                self.n = max(self.n-1, 0)
            else:
                self.m, self.n, c = self.bridges.find(self.m, self.n)
                diff.append(("  " + c))
        return diff[::-1]
