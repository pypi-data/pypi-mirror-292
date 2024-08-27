import click
from hoops_dynasty_api.classes import Player, Team
from hoops_dynasty_api.web import WebBrowser
import logging


def process_single_team(team_id: int, all_worlds_team_data, all_worlds_players_data, save_files_flag: bool = False):
    browser = WebBrowser()
    browser2 = WebBrowser() #show_browser=True)

    try:
        team = Team(browser=browser, team_id=team_id)
        logging.info(f'*******************************************************')
        logging.info(f'team data: adding data for {team.team_name} | {team_id}')
        logging.info(f'*******************************************************')
        all_worlds_team_data.append(team.to_dict())

        logging.info(f'       logging {team.team_name} to big query           ')
        logging.info(f'*******************************************************')
        #team.to_bq(table='hoops_dynasty.schools', project='wis-data-preprod')

        with click.progressbar(team.player_ids, label=f"Processing players for {team.team_name}") as players_bar:
            for player_id in players_bar:
                player = Player(browser=browser2, player_id=player_id, team_id=team_id)
                all_worlds_players_data.append(player.to_dict())
                logging.info(f'         logging {player.player_name} to big query            ')
                logging.info(f'*******************************************************')
                #player.to_bq(table='hoops_dynasty.players', project='wis-data-preprod')

    except Exception as e:
        logging.error(f"Error processing team {team_id}: {e}")
        print(e)
