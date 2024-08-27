import click
from hoops_dynasty_api.extract_data import extract_player_data_v2, extract_team_data_v2, extract_players_from_team_id_v2, extract_world_data


WORLD_NAMES = ['iba', 'knight', 'naismith', 'wooden', 'rupp',
               'tarkanian', 'phelan', 'allen', 'smith', 'crum']


@click.command()
@click.argument('world_names',
                nargs=-1)
@click.option('--save-excel-file', '-sef', is_flag=True, default=True,
              help='flag to save the output to current path')
@click.option('--save-path', '-sp', type=click.Path(), default='.',
              help='Path to save the output file')
def pull_hd_world_data(world_names, save_excel_file: bool, save_path):
    """ cli function for pulling world data from site

    :param world_names: the list of ids to pull data for
    :param save_excel_file: flag for saving file to local
    :return:
    """

    # todo check world names and error if one is wrong

    all_world_names = list(world_names)
    if all_world_names:
        # validate world names
        invalid_worlds = [world.lower() for world in all_world_names if world not in WORLD_NAMES]
        if invalid_worlds:
            raise click.BadParameter(
                f"Invalid world name(s): {', '.join(invalid_worlds)}. "
                f"Valid options are: {', '.join(WORLD_NAMES)}"
            )

        extract_world_data(all_world_names, save_excel_file, save_path)
    else:
        raise click.BadParameter(
            "must enter at least one worlds name as a parameter"
            f"Valid options are: {', '.join(WORLD_NAMES)}"
        )


@click.command()
@click.argument('team_ids', 
                nargs=-1)
@click.option('--save-excel-file', '-sef', is_flag=True, default=True,
              help='flag to save the output to current path')
@click.option('--save-path', '-sp', type=click.Path(), default='.',
              help='Path to save the output file')
def pull_hd_team_data(team_ids, save_excel_file: bool, save_path):
    """ cli function for pulling team data from site

    :param team_ids: the list of ids to pull data for
    :param save_excel_file: flag for saving file to local
    :return:
    """
    all_team_ids = list(team_ids)
    extract_team_data_v2(all_team_ids, save_excel_file, save_path)


@click.command()
@click.argument('player_ids', 
                nargs=-1)
@click.option('--save-excel-file', '-sef', is_flag=True, default=True,
              help='flag to save the output to current path')
@click.option('--save-path', '-sp', type=click.Path(), default='.',
              help='Path to save the output file')
def pull_hd_player_data(player_ids, save_excel_file: bool, save_path):
    """ cli function for pulling player data from site

    :param player_ids: the list of ids to pull data for
    :param save_excel_file: flag for saving file to local
    :return:
    """
    all_player_ids = list(player_ids)
    extract_player_data_v2(all_player_ids, save_excel_file, save_path)


@click.command()
@click.argument('team_ids', 
                nargs=-1)
@click.option('--save-excel-file', '-sef', is_flag=True, default=True,
              help='flag to save the output to current path')
@click.option('--save-path', '-sp', type=click.Path(), default='.',
              help='Path to save the output file')
def pull_team_player_data(team_ids, save_excel_file: bool, save_path):
    """ cli function for pulling player data from site

    :param player_ids: the list of ids to pull data for
    :param save_excel_file: flag for saving file to local
    :return:
    """
    all_team_ids = list(team_ids)
    extract_players_from_team_id_v2(all_team_ids, save_excel_file, save_path)

