class Error(Exception):
    """Base class for exceptions"""


class NotXlsxError(Error):

    def __init__(self, ext, loc):
        self.file_ext = ext
        self.file_loc = loc
        self.message = f'file ext of {ext} is not xlsx'

    def __str__(self):
        return f'{self.file_loc} -> {self.message}'

