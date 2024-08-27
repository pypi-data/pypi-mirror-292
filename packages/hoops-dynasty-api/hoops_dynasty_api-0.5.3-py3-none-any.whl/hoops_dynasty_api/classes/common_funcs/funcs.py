import time


def _sim_check(self, data: str):
    """ This function checks if an input string has Sim AI as the coach
        this is needed as there are some differences in the html when its a
        user vs simmy

    :param self:
    :param data: this is a row of data from bs4 where we need to check if Sim AI is the user
    :return: bool if Sim AI is in the string or not
    """
    return 'Sim AI' in data


def _html_check(self, soup, retries: int = 5, delay: int = 5) -> bool:
    for _ in range(retries):
        if soup.find():  # Check if any HTML content is present
           return True
        else:
            time.sleep(delay)  # Wait if no HTML content is found

    return False
