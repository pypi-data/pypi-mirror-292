""" Player class that handles the data for a player

"""
from selenium import webdriver
from hoops_dynasty_api.exceptions import WebBrowserCreationError
from pandas_gbq import to_gbq
import pandas as pd


class Player:
    from .common_funcs import _sim_check, _html_check

    def __init__(self, browser: webdriver, player_id: int, team_id: int):
        #self.build_web_browser(url)
        self.browser = browser
        self.team_id = team_id
        self.height_inches = 0
        self.height_feet = 0
        self.graduated = False
        self.retired = False
        self.player_ratings_base_url = 'https://www.whatifsports.com/hd/PlayerProfile/Ratings.aspx?tid=0&pid='
        self.player_game_log_base_url = 'https://www.whatifsports.com/hd/PlayerProfile/GameLog.aspx?tid=0&pid='
        self.player_id = player_id
        self.pull_ratings()
        # todo add game stats
        #self.pull_game_stats()

    def pull_game_stats(self):
        url_to_open = self.player_game_log_base_url + str(self.player_id)
        soup = self.browser.open_and_soup(url_to_open)
        game_log = soup.find('table', {'id': 'GameLogTable'})
        if not game_log:
            game_log = soup.find('table', {'id': 'GameLogTable_copy'})
        games = []
        game_data = game_log.find_all('tr')
        if len(game_data) > 1:
            for i in range(0, 19):
                one_game = game_data[i].text.split('\n')
                if i == 0:
                    game_log_headers_temp = one_game
                    game_log_headers = [x for x in game_log_headers_temp if x != '']

                    #del game_log_headers[19]
                    #del game_log_headers[0]
                else:
                    games.append(one_game)
            # todo need to add to this to a dict
            self.games_log_list = []
            for x in range(1, len(games)):
                games_dict = {}
                game_data = [item for item in games[x] if item != '']

                for y in range(1, 18):

                    games_dict.setdefault(game_log_headers[y].lower(), game_data[y])
                self.games_log_list.append(games_dict)
                # todo here i need to make the stats
                # {'date': '6/22', 'opponent': '', 'result': '@American U.', 'min': '', 'fgm': 'L 80-83', 'fga': '20', '3pm': '3', '3pa': '3', 'ftm': '0', 'fta': '0', 'off': '0', 'reb': '0', 'ast': '0', 'to': '0', 'stl': '4', 'blk': '2', 'pf': '3', 'pts': '0'}

    def pull_ratings(self):    
        url_to_open = self.player_ratings_base_url + str(self.player_id)
        self.url = url_to_open
        soup = self.browser.open_and_soup(url_to_open)

        if not self._html_check(soup=soup):
            raise WebBrowserCreationError()

        else:
            soup = self.browser.open_and_soup(url_to_open)

            self.team_name = str(soup.find('a', {'class': 'teamlink'}).findAll(text=True)[0])
            self.position = str(soup.find(
                'span', {'id': 'ctl00_ctl00_ctl00_MainContentPlaceHolder_MainContentPlaceHolder_PlayerRating_Pos'}).findAll(
                text=True)[0])
            self.player_name = str(soup.find(
                'span', {'id': 'ctl00_ctl00_ctl00_MainContentPlaceHolder_MainContentPlaceHolder_PlayerName'}).findAll(
                text=True)[0])

            #print(f'getting info for player -> {self.name}')

            self.year = str(soup.find(
                'span', {'id': 'ctl00_ctl00_ctl00_MainContentPlaceHolder_MainContentPlaceHolder_PlayerYear'}).findAll(
                text=True)[0])
            self.height = str(soup.find(
                'span', {'id': 'ctl00_ctl00_ctl00_MainContentPlaceHolder_MainContentPlaceHolder_PlayerHeight'}).findAll(
                text=True)[0]).replace('"', '')
            self.weight = str(soup.find(
                'span', {'id': 'ctl00_ctl00_ctl00_MainContentPlaceHolder_MainContentPlaceHolder_PlayerWeight'}).findAll(
                text=True)[0])
            if self._sim_check(str(soup.find('div', {'id': 'PlayerProfile_PlayerInfo'}))):
                self.recruited_by = 'Sim AI'
            else:
                self.recruited_by = str(soup.find(
                    'a', {'id': 'ctl00_ctl00_ctl00_MainContentPlaceHolder_MainContentPlaceHolder_CPL'}).findAll(
                    text=True)[0])
            if '(#' in str(soup.find('div', {'id': 'PlayerProfile_PlayerInfo'})):
                self.recruit_ranking = str(soup.find(
                    'span',
                    {'id': 'ctl00_ctl00_ctl00_MainContentPlaceHolder_MainContentPlaceHolder_lblRecruitRanking'}).findAll(
                    text=True)[0]).strip(' ()')
            else:
                self.recruit_ranking = ''
            self.high_school = str(soup.find(
                'span', {'id': 'ctl00_ctl00_ctl00_MainContentPlaceHolder_MainContentPlaceHolder_PlayerHS'}).findAll(
                text=True)[0])
            town_temp = str(soup.find(
                        'span', {'id': 'ctl00_ctl00_ctl00_MainContentPlaceHolder_MainContentPlaceHolder_PlayerTown'}).findAll(
                        text=True)[0])
            self.city = town_temp.split(',')[0]
            try:
                self.state = town_temp.split(',')[1]
            except IndexError:
                self.state = None
            self.athleticism = int(soup.find(
                'td', {'id': 'ctl00_ctl00_ctl00_MainContentPlaceHolder_MainContentPlaceHolder_MainContentPlaceHolder_PlayerRatingsControl_tdAthleticism'}).findAll(
                text=True)[0])
            self.speed = int(soup.find(
                'td', {'id': 'ctl00_ctl00_ctl00_MainContentPlaceHolder_MainContentPlaceHolder_MainContentPlaceHolder_PlayerRatingsControl_tdSpeed'}).findAll(
                text=True)[0])
            self.rebounding = int(soup.find(
                'td', {'id': 'ctl00_ctl00_ctl00_MainContentPlaceHolder_MainContentPlaceHolder_MainContentPlaceHolder_PlayerRatingsControl_tdRebounding'}).findAll(
                text=True)[0])
            self.defense = int(soup.find(
                'td', {'id': 'ctl00_ctl00_ctl00_MainContentPlaceHolder_MainContentPlaceHolder_MainContentPlaceHolder_PlayerRatingsControl_tdDefense'}).findAll(
                text=True)[0])
            self.shot_blocking = int(soup.find(
                'td', {'id': 'ctl00_ctl00_ctl00_MainContentPlaceHolder_MainContentPlaceHolder_MainContentPlaceHolder_PlayerRatingsControl_tdShotBlocking'}).findAll(
                text=True)[0])
            self.low_post = int(soup.find(
                'td', {'id': 'ctl00_ctl00_ctl00_MainContentPlaceHolder_MainContentPlaceHolder_MainContentPlaceHolder_PlayerRatingsControl_tdLowPost'}).findAll(
                text=True)[0])
            self.perimeter = int(soup.find(
                'td', {'id': 'ctl00_ctl00_ctl00_MainContentPlaceHolder_MainContentPlaceHolder_MainContentPlaceHolder_PlayerRatingsControl_tdPerimeter'}).findAll(
                text=True)[0])
            self.ball_handling = int(soup.find(
                'td', {'id': 'ctl00_ctl00_ctl00_MainContentPlaceHolder_MainContentPlaceHolder_MainContentPlaceHolder_PlayerRatingsControl_tdBallhandling'}).findAll(
                text=True)[0])
            self.passing = int(soup.find(
                'td', {'id': 'ctl00_ctl00_ctl00_MainContentPlaceHolder_MainContentPlaceHolder_MainContentPlaceHolder_PlayerRatingsControl_tdPassing'}).findAll(
                text=True)[0])
            self.work_ethic = int(soup.find('table', {'id': 'playerratings_table'}).find_all(
                'td', {'class': 'rating'})[9].findAll(text=True)[0])
            self.stamina = int(soup.find(
                'td', {'id': 'ctl00_ctl00_ctl00_MainContentPlaceHolder_MainContentPlaceHolder_MainContentPlaceHolder_PlayerRatingsControl_tdStamina'}).findAll(
                text=True)[0])
            self.durability = int(soup.find(
                'td', {'id': 'ctl00_ctl00_ctl00_MainContentPlaceHolder_MainContentPlaceHolder_MainContentPlaceHolder_PlayerRatingsControl_tdDurability'}).findAll(
                text=True)[0])
            self.ft_shooting = str(soup.find(
                'td', {'id': 'ctl00_ctl00_ctl00_MainContentPlaceHolder_MainContentPlaceHolder_MainContentPlaceHolder_PlayerRatingsControl_tdFT'}).findAll(
                text=True)[0]).strip()
            self.flex_iq = str(soup.find(
                'span', {'id': 'ctl00_ctl00_ctl00_MainContentPlaceHolder_MainContentPlaceHolder_MainContentPlaceHolder_IQ_Flex'}).findAll(
                text=True)[0])
            self.motion_iq = str(soup.find(
                'span', {'id': 'ctl00_ctl00_ctl00_MainContentPlaceHolder_MainContentPlaceHolder_MainContentPlaceHolder_IQ_Motion'}).findAll(
                text=True)[0])
            self.triangle_iq = str(soup.find(
                'span', {'id': 'ctl00_ctl00_ctl00_MainContentPlaceHolder_MainContentPlaceHolder_MainContentPlaceHolder_IQ_Triangle'}).findAll(
                text=True)[0])
            self.fastbreak_iq = str(soup.find(
                'span', {'id': 'ctl00_ctl00_ctl00_MainContentPlaceHolder_MainContentPlaceHolder_MainContentPlaceHolder_IQ_Fastbreak'}).findAll(
                text=True)[0])
            self.man_to_man_iq = str(soup.find(
                'span', {'id': 'ctl00_ctl00_ctl00_MainContentPlaceHolder_MainContentPlaceHolder_MainContentPlaceHolder_IQ_ManMan'}).findAll(
                text=True)[0])
            self.zone_iq = str(soup.find(
                'span', {'id': 'ctl00_ctl00_ctl00_MainContentPlaceHolder_MainContentPlaceHolder_MainContentPlaceHolder_IQ_Zone'}).findAll(
                text=True)[0])
            self.press_iq = str(soup.find(
                'span', {'id': 'ctl00_ctl00_ctl00_MainContentPlaceHolder_MainContentPlaceHolder_MainContentPlaceHolder_IQ_Press'}).findAll(
                text=True)[0])

    def total_rating(self) -> int:
        return self.athleticism + self.speed + self.rebounding + \
               self.defense + self.shot_blocking + self.low_post + \
               self.perimeter + self.ball_handling + self.passing + \
               self.work_ethic + self.stamina + self.durability

    def player_details(self) -> dict:
        """ this function builds player details and returns a dictionary that can
            be fed into a pd df

        :return: dict of objects values
        """
        return {'player_name': self.name, 'team_name': self.team_name, 'position': self.position,
                'class': self.year, 'height': self.height, 'weight': self.weight,
                'high_school': self.high_school, 'city': self.city,
                'recruited_by': self.recruited_by,
                'recruit_ranking': self.recruit_ranking, 'athleticism': self.athleticism,
                'speed': self.speed, 'rebounding': self.rebounding,
                'defense': self.defense, 'shot_blocking': self.shot_blocking, 'low_post': self.low_post,
                'perimeter': self.perimeter, 'ball_handling': self.ball_handling, 'passing': self.passing,
                'work_ethic': self.work_ethic, 'stamina': self.stamina, 'durability': self.durability,
                'free_throw_shooting': self.ft_shooting, 'total_rating': self.total_rating(), 'flex_iq': self.flex_iq,
                'motion_iq': self.motion_iq, 'triangle_iq': self.triangle_iq, 'fastbreak_iq': self.fastbreak_iq,
                'man_to_man_iq': self.man_to_man_iq, 'zone_iq': self.zone_iq, 'press_iq': self.press_iq,
                'url': self.url, 'id': self.player_id, 'game_log': self.games_log_list}

    def to_dict(self):
        return {key: value for key, value in self.__dict__.items() if key not in
                ['browser', 'player_ratings_base_url', 'player_game_log_base_url', 'team_name']}

    def to_bq(self, project, table):
        df = pd.DataFrame([self.to_dict()])
        df['player_id'] = df['player_id'].apply(lambda x: int(x))
        df.rename(columns={'player_id': 'id'}, inplace=True)
        df['weight'] = df['weight'].apply(lambda x: int(x.split(' ')[0]))
        # todo set height_feet, height_inches
        df['height_feet'] = df['height'].apply(lambda x: int(x.split("'")[0]))
        df['height_inches'] = df['height'].apply(lambda x: int(x.split("'")[1]))
        df['create_ts'] = pd.Timestamp.now()
        df['update_ts'] = pd.Timestamp.now()
        to_gbq(df, table, project_id=project, if_exists='append')

    def game_stats(self) -> list[dict]:
        game_log_list = []
        game_log_dict = {}

        return game_log_list
