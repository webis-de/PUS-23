class Contribution:
    """
    Class to track editor contributions for a revision
    by diffing it against a previous revision.

    Attributes:
        differ: The Differ used to diff two texts.
        index: The index of the revision in the revision history.
        url: The url of the revision on Wikipedia
        size: The size of the revision.
        text: The text of the revision.
        user: The editor of this revision.
        userid: The ID of the editor of this revision
        character_editor_map: List of character and editor tuples.
    """
    def __init__(self, differ, index, url, size, text, user, userid):
        self.differ = differ
        self.index = index
        self.url = url
        self.size = size
        self.text = text
        self.user = user
        self.userid = userid
        self.character_editor_map = []

    def diff(self, previous_contribution=None):
        """
        Diff the text and this revision, comparing and mapping contributors.
        If there is no previsious revision, i.e. previous_contribution is None,
        then everything is mapped to the editor of this revision,
        otherwise the text of this and the previous revision are diffed.
        
        The Differ provides a list of result strings of the form "+ c", "- c" or "  c",
        with c comprising one or more characters:
        - '  c' means there was no change to .
        - '- c' means c was removed
        - '+ c' means c was added        
        For each result string in the diff the following respective actions are applied:
        - add previous mapping in case of no change
        - discard mapping in case of removal
        - add new mapping in case of addition        
        """
        if not previous_contribution:
            self.character_editor_map = [(unit, self.user + "|" + str(self.userid)) for unit in self.text]
        else:
            diffs = list(self.differ.compare(previous_contribution.text, self.text))
            previous_character_editor_map = self._previous_character_editor_map(previous_contribution)
            for diff in diffs:
                if diff[0] == " ": 
                    self.character_editor_map.append(next(previous_character_editor_map))
                elif diff[0] == "-":
                    continue
                elif diff[0] == "+":
                    self.character_editor_map.append((diff[2:], self.user + "|" + str(self.userid)))
                else:
                    raise Exception

    def _previous_character_editor_map(self, previous_contribution):
        """Iterator over previous contributors character-editor map."""
        for item in previous_contribution.character_editor_map:
            yield item

    def __str__(self):
        """Stringifier for character-editor map."""
        return " ".join(map(str, self.character_editor_map))

    def parts(self):
        """
        Map editor map on unit level to section level
        by merging consecutive unit contributed
        by the same editor to string sections.
        """
        parts = []
        if not self.character_editor_map:
            print("No text found - revision probably deleted.")
        else:
            part = ""
            old_editor = self.character_editor_map[0][1]
            for unit, new_editor in self.character_editor_map:
                if new_editor == old_editor:
                    part += unit
                else:
                    if part:
                        parts.append((part, old_editor))
                        part = unit
                        old_editor = new_editor
            if part:
                parts.append((part, old_editor))
        return parts

    def editors(self):
        parts = self.parts()
        editors = {}
        for part, editor in parts:
            if editor not in editors:
                editors[editor] = 0
            editors[editor] += len(part)
        for editor in editors:
            editors[editor] = {"absolute":editors[editor],
                               "relative":round(editors[editor]/len("".join(self.text)), 5)}
        return editors

    def table(self, editors):
        table = ""
        table += str(self.index) + " " + self.url + " " + "\n"
        table += "html length: " + str(len(self.text)) + " " + "wikimedia size: " + str(self.size) + "\n"
        header = "user|userid".rjust(60, " ") + "absolute".rjust(20, " ") + "relative".rjust(20, " ")
        table += "\n" + header + "\n"
        table += "-" * len(header) + "\n"
        for editor in sorted(editors.keys(), key=lambda editor: editors[editor]["absolute"], reverse=True):
            table += (str(editor).rjust(60, " ") +
                      str(str(editors[editor]["absolute"])).rjust(20, " ") +
                      str(str(editors[editor]["relative"])).rjust(20, " ") + "\n")
        table += "="*100 + "\n"
        return table

    def json(self, editors):
        return {key:editors[key] for key in sorted(editors.keys())}
