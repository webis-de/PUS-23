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
    def __init__(self, fullname):
        """
        Initialises author.

        Args:
            fullname: Full name as extracted from bibentry.
        """
        self.fullname = fullname
        self.names = fullname.split(",")
        self.surname = self.names[0][0].upper() + self.names[0][1:].lower()
        self.firstname = self.names[1]

    def __str__(self):
        return pformat(self.__dict__)

if __name__ == "__main__":

    author = Author("MOJICA,F")
    print(author)
