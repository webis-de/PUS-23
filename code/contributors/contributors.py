from difflib import Differ

class Contributors:

    def __init__(self, text):

        self.text = text
        self.character_editor_map = []
        self.differ = Differ()

    def align(self, editor, previous_contributors=None):
        if not previous_contributors:
            self.character_editor_map = [(character,editor) for character in self.text]
        else:
            #TUPLES OF (CHANGE, CHARACTER)
            diffs = list(self.differ.compare(previous_contributors.text, self.text))
            previous_character_editor_map = self._previous_character_editor_map(previous_contributors)
            for diff in diffs:
                if diff[0] == " ": 
                    self.character_editor_map.append(next(previous_character_editor_map))
                elif diff[0] == "-":
                    continue
                elif diff[0] == "+":
                    self.character_editor_map.append((diff[2],editor))
                else:
                    raise Exception

    def _previous_character_editor_map(self, previous_contributors):
        for item in previous_contributors.character_editor_map:
            yield item

    def __str__(self):
        return " ".join(map(str, self.character_editor_map))

    def parts(self):
        parts = []
        block = ""
        editor = self.character_editor_map[0][1]
        for item in self.character_editor_map:
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
            string = part[0]
            editor = part[1]
            if editor not in contributions:
                contributions[editor] = 0
            contributions[editor] += len(string)
        for editor in contributions:
            contributions[editor] = (contributions[editor], round(contributions[editor]/len(self.text) * 100, 5))
        return contributions

    def contributions_table(self, contributions):
        table = ""
        contributions = sorted([(k,v) for k,v in contributions.items()], key=lambda item:item[1][0], reverse=True)
        header = "user".rjust(60, " ") + "absolute".rjust(20, " ") + "relative".rjust(20, " ")
        table += "\n" + header + "\n"
        table += "-" * len(header) + "\n"
        for contribution in contributions:
            table += (str(contribution[0]).rjust(60, " ") +
                      str(str(contribution[1][0])).rjust(20, " ") +
                      str(str(contribution[1][1])).rjust(20, " ") + "\n")
        return table

    def contributions_json(self, contributions):
        return {key:contributions[key] for key in sorted(contributions.keys())}
            
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
