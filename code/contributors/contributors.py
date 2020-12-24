from difflib import Differ

class Contributors:

    def __init__(self, revision_text):

        self.revision_text = revision_text
        #TUPLES OF (CHARACTER, EDITOR)
        self.revision_map = []
        self.differ = Differ()

    def align(self, editor, previous=None):
        if not previous:
            self.revision_map = [(character,editor) for character in self.revision_text]
        else:
            #TUPLES OF (CHANGE, CHARACTER)
            diffs = [(item[0], item[2]) for item in self.differ.compare(previous.revision_text, self.revision_text)]
            i = 0
            for diff in diffs:
                if diff[0] == " ":
                    previous_item = previous.revision_map[i]
                    self.revision_map.append(previous_item)
                    i += 1
                elif diff[0] == "-":
                    i += 1
                else:
                    self.revision_map.append((diff[1],editor))

    def __str__(self):
        return " ".join(map(str, self.revision_map))

    def parts(self):
        parts = []
        block = ""
        editor = self.revision_map[0][1]
        for item in self.revision_map:
            if item[1] == editor:
                block += item[0]
            else:
                if block:
                    parts.append((block, editor))
                    block = item[0]
                    editor = item[1]
        if block:
            parts.append((block, editor))
        return parts

    def contributions(self):
        parts = self.parts()
        contributions = {}
        for part in parts:
            text = part[0]
            editor = part[1]
            if editor not in contributions:
                contributions[editor] = 0
            contributions[editor] += len(text)
        for editor in contributions:
            contributions[editor] = (contributions[editor], round(contributions[editor]/len(self.revision_text) * 100, 5))
        return contributions
            
if __name__ == "__main__":              
    t1 = "This here is a sentence."
    t2 = "This is another sentence."

    c1 = Contributors(t1)
    c1.align("editor 1")
    print(c1.parts())
    print(c1.contributions())

    c2 = Contributors(t2)
    c2.align("editor 2", c1)
    print(c2.parts())
    print(c2.contributions())
