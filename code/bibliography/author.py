from pprint import pformat

class Author:
    """
    Wrapper class for author.

    Attributes:
        fullname: Full name as extracted from bibentry.
        names: List of surname and first name as per split bibentry.
        surname: First element in names. First character converted to
                 upper case, rest to lower case.
        firstname: Second element in names.
    """
    def __init__(self, name):
        """
        Initialises author.

        Args:
            fullname: Full name as extracted from bibentry.
        """
        nameparts = [part.strip() for part in name.split(",")]
        self.surname = nameparts[0][0].upper() + nameparts[0][1:].lower()
        self.firstname = nameparts[1][0].upper() + nameparts[1][1:].lower()
        self.fullname = self.surname + "," + self.firstname
        
    def __str__(self):
        return pformat(self.__dict__)

if __name__ == "__main__":

    author = Author("MOJICA, F.")
    print(author)
