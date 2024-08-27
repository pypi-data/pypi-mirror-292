class Error(Exception):
    """Base class for exceptions"""


class WebBrowserCreationError(Error):

    def __init__(self,):
        self.message = f'browser creation error, please run again'

    def __str__(self):
        return f'{self.message}'


class NoBrowserAvailableError(Error):

    def __init__(self):
        self.message = ''

