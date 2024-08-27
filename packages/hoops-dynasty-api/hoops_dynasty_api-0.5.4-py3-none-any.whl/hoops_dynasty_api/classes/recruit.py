from bs4 import BeautifulSoup
from selenium import webdriver

class Recruit:
    from .common_funcs import _sim_check

    def __init__(self, browser: webdriver, recruit_id: int):
        self.browser = browser
        self.recruit_rating_base_url = 'https://www.whatifsports.com/hd/RecruitProfile/Ratings.aspx?rid='

        #self.login_to_wis()
        #self.season = "    153"    
        self.browser.open_url(self.recruit_rating_base_url + str(recruit_id))
        soup = BeautifulSoup(self.browser.page_source, 'html.parser')
        self.url = f'{self.recruit_rating_base_url}{recruit_id}'
        self.id = recruit_id
        self.position = ''
        self.name = ''
        self.year = ''
        self.height = ''
        self.weight = ''
        self.high_school = str(soup.find(
            'span', {'id': 'ctl00_ctl00_ctl00_MainContentPlaceHolder_MainContentPlaceHolder_PlayerHS'}).findAll(
            text=True)[0])
        town_temp = str(soup.find(
            'span', {'id': 'ctl00_ctl00_ctl00_MainContentPlaceHolder_MainContentPlaceHolder_PlayerTown'}).findAll(
            text=True)[0])
        self.town = town_temp.split(',')[0]
        try:
            self.state = town_temp.split(',')[1]
        except IndexError:
            self.state = None
        self.athleticism = ''
        self.speed = ''
        self.rebounding = ''
        self.defense = ''
        self.shot_blocking = ''
        self.low_post = ''
        self.perimeter = ''
        self.ball_handling = ''
        self.passing = ''
        self.work_ethic = ''
        self.stamina = ''
        self.durability = ''
        self.ft_shooting = ''
