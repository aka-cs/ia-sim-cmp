class ParsingError(Exception):
    pass


class UnexpectedToken(ParsingError):

    def __init__(self, index):
        super().__init__()
        self.index = index
