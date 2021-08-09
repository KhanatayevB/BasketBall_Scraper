"""
This a scraper code made for the first check point of the scraping project of the 2021 June cohort
of the <itc> Fellows Data-Science Training Program, and used for scraping all of the NBA players
data from the https://www.basketball-reference.com/ website.

Authors: Bazham Khanatayev, David Muenz and Eyal Ran.
"""
import logging

import constants
import sys
import requests
from bs4 import BeautifulSoup
import argparse
import pandas as pd
import pymysql.cursors
import numpy as np
import api_integration

# The following code is used to set up the logger. It is mostly from the logging cookbook provided in the python
# documentation

logger = logging.getLogger('basketBall_scraper')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s')

file_handler = logging.FileHandler('basketball_scraper.log')
file_handler.setLevel(logging.DEBUG)  # This level is used to make sure the logger captures everything to the file
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.WARNING)  # This level is used so that only warnings are printed out
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)



def get_tables_from_api():
    """
    Load Tables teams and player_in_team from API
    """
    logging.debug(f'Getting tables from API')
    try:
        df_teams, df_play_team = api_integration.main()
        return df_teams, df_play_team
    except Exception:
        logging.error(f'Failed to get tables from API')

def get_players_team_ids(df_play_team):
    """
    Extracts and return IDs from players and team tables based on df_play_team
    """
    try:
        play_and_team_ids = []
        for index, row in df_play_team.iterrows():
            play_name = f'{row.first_name} {row.last_name}'
            cur.execute(f'SELECT id FROM players where player = "{play_name}" order by start_year desc')
            play_id = cur.fetchall()
            cur.execute(f"SELECT id FROM teams where full_name = '{row.teams}'")
            team_id = cur.fetchall()
            if play_id != ():
                play_and_team_ids.append((play_id[0][0], team_id[0][0]))
            return play_and_team_ids
    except Exception:
        logging.debug(f'Failed to get player ID')



def insert_players_to_team_in_db(play_and_team_ids):
    """
    Insert list of play and teams ids to db
    """
    logging.debug(f'Inserting players into Database')
    try:
        cur.execute(
            "CREATE TABLE IF NOT EXISTS players_to_team (player_id int, team_id int)")
        cur.execute(
            " ALTER TABLE players_to_team ADD UNIQUE INDEX ( player_id, team_id);")
        sql = (f"INSERT IGNORE INTO players_to_team ( player_id, team_id)"
               f"VALUES(%s,%s) ;")

        cur.executemany(sql, play_and_team_ids)
        con.commit()
    except Exception:
        logging.debug(f'Failed to insert players into DataBase')


def get_team_tables_from_api(df_teams):
    """
    Loads Teams Table to databse
    """
    logging.debug(f'Getting team tables from API')
    df_teams_lists = df_teams.values.tolist()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS teams (id int AUTO_INCREMENT PRIMARY KEY, abbreviation VARCHAR(100), "
        "city VARCHAR(100), conference VARCHAR(100), "
        " division VARCHAR(100), full_name VARCHAR(100), name VARCHAR(100))")
    cur.execute(
        " ALTER TABLE teams ADD UNIQUE INDEX (abbreviation, city, conference, division, full_name, name);")
    sql = (f"INSERT IGNORE INTO teams (id, abbreviation, city, conference, division, full_name, name)"
           f"VALUES(%s,%s,%s,%s,%s,%s,%s) ;")
    cur.executemany(sql, df_teams_lists)

    con.commit()


def connect_to_db():
    """
    Connecting to MySql database
    """
    logging.debug(f'Connecting to DataBase')
    try:
        username = constants.SQL_USER_NAME
        password = constants.SQL_USER_PASSWORD
        con = pymysql.connect(user=username, password=password)
        cur = con.cursor()
        cur.execute("CREATE DATABASE IF NOT EXISTS bask_play;")
        cur.execute("use bask_play;")

        return con, cur
    except Exception:
        logging.warning(f'Could not connect to DataBase')

def insert_position_in_db(new_positions):
    """
    Insert list of new_positions in database
    """
    sql = (f"INSERT INTO positions ( position)"
           f"VALUES(%s);")
    cur.executemany(sql, new_positions)
    con.commit()


def insert_college_in_db(new_colleges):
    """
    Insert list of new_colleges in database
    """
    sql = (f"INSERT INTO colleges ( college)"
           f"VALUES(%s);")
    cur.executemany(sql, new_colleges)
    con.commit()


def insert_players_to_position_in_db(players_data_frame):
    """
    Creates/Inserts ID References between players and positions
    """
    cur.execute("SELECT id, position FROM positions")
    id_positions = cur.fetchall()
    conv_pos = dict((y, x) for x, y in id_positions)
    players_data_frame = players_data_frame.assign(players_pos_id=[[conv_pos[k] for k in row if conv_pos.get(k)]
                                                                   for row in players_data_frame.position])
    df_id_play = get_players_id()
    play_and_pos_ids = players_data_frame.merge(df_id_play, on='player')[['players_pos_id', 'id']]
    play_and_pos_ids = play_and_pos_ids[play_and_pos_ids.players_pos_id.str.len() != 0]
    cur.execute(
        "CREATE TABLE IF NOT EXISTS players_to_pos (player_id int, pos_id int)")
    cur.execute(
        " ALTER TABLE players_to_pos ADD UNIQUE INDEX ( player_id, pos_id);")
    sql = (f"INSERT IGNORE INTO players_to_pos ( pos_id, player_id)"
           f"VALUES(%s,%s) ;")
    cur.executemany(sql, play_and_pos_ids.explode('players_pos_id').values.tolist())
    con.commit()


def insert_players_to_college_in_db(players_data_frame):
    """
    Creates/Inserts ID References between players and colleges
    """
    cur.execute("SELECT id, college FROM colleges")
    id_colleges = cur.fetchall()
    conv_col = dict((y, x) for x, y in id_colleges)
    players_data_frame = players_data_frame.assign(players_col_id=[[conv_col[k] for k in row if conv_col.get(k)]
                                                                   for row in players_data_frame.colleges])
    df_id_play = get_players_id()
    play_and_col_ids = players_data_frame.merge(df_id_play, on='player')[['players_col_id', 'id']]
    play_and_col_ids = play_and_col_ids[play_and_col_ids.players_col_id.str.len() != 0]
    cur.execute(
        "CREATE TABLE IF NOT EXISTS players_to_college (player_id int, col_id int)")
    cur.execute(
        " ALTER TABLE players_to_college ADD UNIQUE INDEX ( player_id, col_id);")
    sql = (f"INSERT IGNORE INTO players_to_college ( col_id, player_id)"
           f"VALUES(%s,%s) ;")
    cur.executemany(sql, play_and_col_ids.explode('players_col_id').values.tolist())
    con.commit()


def get_players_id():
    """
    Returns database id's from players
    """
    cur.execute("SELECT id, player  FROM players where id >= id ")
    id_player = cur.fetchall()
    df_id_play = pd.DataFrame(
        id_player, columns=['id', 'player'])
    return df_id_play


def insert_player_in_db(players_data_frame):
    """
        Creates from the dataframe 'players_data_frame' the database
    """

    play_data_list = players_data_frame.drop(['position', 'colleges'], axis=1).values.tolist()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS players (id int AUTO_INCREMENT PRIMARY KEY, player VARCHAR(100), start_year INT"
        ",end_year INT, height VARCHAR(100), weight INT, birth_date VARCHAR(100))")
    cur.execute(
        " ALTER TABLE players ADD UNIQUE INDEX ( player,start_year,end_year,height,weight,birth_date);")
    sql = (f"INSERT IGNORE INTO players ( player,start_year,end_year,height,weight,birth_date)"
           f"VALUES(%s,%s,%s,%s,%s,%s) ;")
    cur.executemany(sql, play_data_list)

    con.commit()


def create_urls_list():
    """
    This function creates the URL's list from which the data will be scraped. The list includes all
    the pages in https://www.basketball-reference.com/, website which contains the data for every
    player that ever played in the NBA league.
    :return: lst, of  https://www.basketball-reference.com/ website URL's needed for scraping.
    """
    base_url = constants.BASE_URL
    for_slash = constants.FORWARD_SLASH
    a_z_urls = []
    for char in constants.A_TO_Z:
        a_z_urls.append(base_url + char + for_slash)
    return a_z_urls


def create_players_dict():
    """
    This function creates a proto-type of the dictionary to which the scraped players data
    will be written.
    :return: dict.
    """
    players_dict = {'player': [], 'start_year': [], 'end_year': [], 'position': [],
                    'height': [], 'weight': [], 'birth_date': [], 'colleges': []}
    return players_dict


def get_letter_page_soup_obj(url):
    """
    This function create a single web request to a website, by the website's URL, and creates
    a BeautifulSoup object out of its HTML code.
    :param url: str, represents a website's URL to form a web request from.
    :return: BeautifulSoup object of the website's URL HTML code.
    """
    page = requests.get(url)
    letter_page_soup = BeautifulSoup(page.content, 'html.parser')
    print(constants.RETRIEVING_DATA_MSG)
    return letter_page_soup


def check_scope_value(scope):
    """
    This function identifies which value was provided for the program's --scope argument. The
    function returns either the value provided, or a flag and the value provided, or None, in
    the event that an unsupported value was provided.
    :param scope: str, the value provided as the program's --scope argument.
    :return: str/tuple/None
    """
    if '-' in scope:
        scope_list = scope.split('-')
        if len(scope_list) == 2:
            for part in scope_list:
                if not ((part.isalpha()) & (len(part) == 1)):
                    return None
            return 'letter_range', scope_list[0].lower(), scope_list[1].lower()
    elif (len(scope) == 1) & (scope.isalpha()):
        return 'letter', scope.lower()
    elif scope == 'all':
        return 'all'
    else:
        return None


def get_url_idx(letter):
    """
    This is a helper function which returns the index of the url which leads to the web page
    of the players that their name starts with the letter provided to the function.
    :param letter: str, one alphabetical letter.
    :return: int, representing the index of the letter web page url.
    """
    return constants.A_TO_Z.index(letter)


def get_letter_players_data(urls_list, players_dict, letter):
    """
    This function extracts the url that leads to the web page of the players that their name
    starts with the letter provided to the function, and calls to the get_all_players_data()
    with the said url.
    :param urls_list: list, webpage urls list.
    :param players_dict: dict, meant to hold the players data.
    :param letter: str, one alphabetical letter.
    :return: dict, containing the players data.
    """
    url_idx = get_url_idx(letter)
    url = urls_list[url_idx]
    return get_all_players_data([url], players_dict)


def get_letter_range_players_data(urls_list, players_dict, letter1, letter2):
    """
    This function extracts the urls that leads to the web pages of the players that their name
    starts with the letters provided, or any of the letters found between them, and calls to
    the get_all_players_data() with the appropriate urls.
    :param urls_list: list, webpage urls list.
    :param players_dict: dict, meant to hold the players data.
    :param letter1: str, one alphabetical letter, represent the first letter in the letters range.
    :param letter2: str, one alphabetical letter, represent the last letter in the letters range.
    :return: dict, containing the players data.
    """
    url1_idx = get_url_idx(letter1)
    url2_idx = get_url_idx(letter2)
    range_urls_list = urls_list[url1_idx:url2_idx + 1]
    return get_all_players_data(range_urls_list, players_dict)


def scrape_player_data(tr, players_dict, positions, colleges):
    """
    This function receives a single row of a player  data, scraped from the players data tables,
    and extract the player's data from it, into the players_dict.
    :param tr: BeautifulSoup object, contains a single row of a player  data, scraped from the
               players data tables
    :param players_dict: dict, containing the players data.
    :param positions: list of positions in db.
    :param colleges: list of colleges in db.
    :return: players_dict: dict, containing the players data.
    """

    logging.debug(f'Starting to scrape player data')
    try:
        players_dict['player'].append(tr.a.text)
        players_dict['start_year'].append(tr.find('td', {'data-stat': 'year_min'}).text)
        players_dict['end_year'].append(tr.find('td', {'data-stat': 'year_max'}).text)
        players_dict['position'].append(tr.find('td', {'data-stat': 'pos'}).text.split('-'))
        pos = tr.find('td', {'data-stat': 'pos'}).text.split('-')
        new_positions = list(np.setdiff1d(pos, positions))
        if new_positions not in [[''], []]:
            insert_position_in_db(new_positions)
            positions += new_positions
        # print()
        players_dict['height'].append(tr.find('td', {'data-stat': 'height'}).text)
        players_dict['weight'].append(tr.find('td', {'data-stat': 'weight'}).text)
        players_dict['birth_date'].append(tr.find('td', {'data-stat': 'birth_date'}).text)
        players_dict['colleges'].append(tr.find('td', {'data-stat': 'colleges'}).text.split(', '))
        col = tr.find('td', {'data-stat': 'colleges'}).text.split(', ')
        new_col = list(np.setdiff1d(col, colleges))
        if new_col not in [[''], []]:
            insert_college_in_db(new_col)
            colleges += new_col
        return players_dict
    except ValueError():
        logging.debug(f'Failed to scrape player data')


def scrape_letter_players_data(letter_page_soup_obj, players_dict, positions, colleges):
    """
    This function receives a BeautifulSoup object containing the data table of all players
    with last name starts with same letter, and for each row of tge data table, calls to
    a helper function the writes the player's data into the players_dict.
    :param letter_page_soup_obj: BeautifulSoup object containing the data table of all players
                                 with last name starts with same letter
    :param players_dict: dict, containing the players data.
    :param positions: list of positions in db.
    :param colleges: list of colleges in db.
    :return: dict, containing the players data.
    """
    for tr in letter_page_soup_obj.find_all('tr'):
        if tr.find('a'):
            players_dict = scrape_player_data(tr, players_dict, positions, colleges)
    return players_dict


def get_all_players_data(urls_list, players_dict, positions, colleges):
    """
    This function receives a list of URL's to scrape data from, and the players_dict proto-type
    which will hold the players scraped data.
    :param urls_list: st, of  https://www.basketball-reference.com/ website URL's needed for scraping
    :param players_dict: dict, containing the players data.
    :param positions: list of positions in db.
    :param colleges: list of colleges in db.
    :return: dict, containing the players data.
    """
    print(constants.SCRAPING_MSG)
    for url in urls_list:
        letter_page_soup = get_letter_page_soup_obj(url)
        players_dict = scrape_letter_players_data(letter_page_soup, players_dict, positions, colleges)
    return players_dict


def create_players_data_frame(players_dict):
    """
    This function receives a dictionary holding all of the players' data which was scraped, and feed
    it to a pandas DataFrame object.
    :param players_dict: dict, containing the players data.
    :return: pandas DataFrame object.
    """
    return pd.DataFrame(players_dict)


def write_players_data_to_csv(players_df, path=None):
    """
    This function receives a pandas DataFrame holding all of the scraped players data, and writes
    its contained data to a .csv file. If the function was provided with a path, the .csv file will
    be written to that path, otherwise, the .csv file will be written to the directory from which
    the script was ran.
    :param players_df: pandas DataFrame object.
    :param path: str, representing a file absolute file.
    :return: str, representing the path to which the .csv file was written.
    """
    logging.debug(f'Writing players to csv')
    try:
        if path:
            path = path + constants.CSV_FILE_NAME
        else:
            path = constants.CSV_FILE_NAME
        players_df.to_csv(path, index=False)
        return path
    except Exception:
        logging.debug(f'Failed to write players to csv')


def operate_commandline_argument_parser():
    """
    This function defines commandline arguments to be used with the program.
    :return: argparse.parseargs object storing the commandline arguments.
    """
    line_parser = argparse.ArgumentParser(prog='NBA Players Scraper.',
                                          description='NBA players basic data and stats scraper.',
                                          add_help=True)
    line_parser.add_argument('-s', '--scope', action='store',
                             help='Scraper scope (Players to scrape): all (default), for scraping all players data,'
                                  '[Letter (For all players with last name starts with the Letter)],'
                                  '[Letters-Inclusive- (LETTER-LETTER) (last name starts with a Letter in range)],',
                             type=str, required=False, default='all')
    line_parser.add_argument('-p', '--print', action='store_true',
                             help='used for printing scraping results to standard output.',
                             required=False)
    line_parser.add_argument('-d', '--dataframe', action='store_true',
                             help='for creating a serialized pandas data-frame of the scraping results.',
                             required=False)
    line_parser.add_argument('-c', '--csv', action='store_true',
                             help='for creating a csv file of the scraping results.',
                             required=False)
    line_parser.add_argument('-b', '--database', action='store_true',
                             help='for writing the scraping results to the players DB.',
                             required=False)
    return line_parser.parse_args()


def display_error_and_terminate(error):
    print(constants.GENERAL_ERROR_MSG, error)
    print(constants.NOT_WRITTEN_TO_FILE_MSG)
    print(constants.DATA_FRAME_NOT_SERIALIZED_MSG)
    print(constants.DATA_WAS_NOT_WRITTEN_TO_DB_MSG)
    print(constants.TERMINATION_MSG)
    sys.exit(0)


def get_positions():
    """
    Returns all positions from mysql table to a python list
    """
    cur.execute(
        "CREATE TABLE IF NOT EXISTS positions (id int AUTO_INCREMENT PRIMARY KEY, position VARCHAR(100))")
    cur.execute("SELECT position FROM positions")
    positions = cur.fetchall()
    return list(positions)


def get_colleges():
    """
    Returns all colleges from mysql table to a python list
    """
    cur.execute(
        "CREATE TABLE IF NOT EXISTS colleges (id int AUTO_INCREMENT PRIMARY KEY, college VARCHAR(100))")
    cur.execute("SELECT college FROM colleges")
    colleges = cur.fetchall()
    return list(colleges)



def get_path():
    """
    This function determines the path according to the user path defined on constants.
    """
    if constants.USER_PATH:
        path = constants.USER_PATH + constants.FORWARD_SLASH
    else:
        path = constants.USER_PATH
    return path


def get_scope(scope, urls_list, players_dict, positions, colleges):
    """
    This function checks the value of scope and calls for the appropriate function.
    """
    if scope == 'all':
        players_dict = get_all(urls_list, players_dict, positions, colleges)
    elif scope[0] == 'letter':
        players_dict = get_letter(urls_list, players_dict, scope[1])
    elif scope[0] == 'letter_range':
        players_dict = get_letter_rang(urls_list, players_dict, scope[1], scope[2])
    return players_dict


def get_all(urls_list, players_dict, positions, colleges):
    """
    This function gets all players data in case scope value is 'all'.
    """
    try:
        players_dict = get_all_players_data(urls_list, players_dict, positions, colleges)
        return players_dict
    except Exception as error:
        display_error_and_terminate(error)


def get_letter(urls_list, players_dict, letter):
    """
    This function gets all players with a name starts at ath the chosen letter, data, in case
    scope value is a letter.
    """
    try:
        players_dict = get_letter_players_data(urls_list, players_dict, letter)
        return players_dict
    except Exception as error:
        display_error_and_terminate(error)


def get_letter_rang(urls_list, players_dict, letter1, letter2):
    """
    This function gets all players with a name starts at ath the chosen letter, data, in case
    scope value holds a range of letters.
    """
    try:
        players_dict = get_letter_range_players_data(urls_list, players_dict, letter1, letter2)
        return players_dict
    except Exception as error:
        display_error_and_terminate(error)


def pickle_dataframe(path,players_data_frame):
    """
    This function pickles the data dataframe.
    """
    path_pkl = path + constants.PKL_FILE_NAME
    players_data_frame.to_pickle(path=path_pkl)
    print(constants.DF_CREATED_SERIALIZED_MSG)


def handle_csv(path, players_data_frame):
    """
    This function handles the creation of a .csv file out of players_data_frame.
    """
    path_csv = path + constants.CSV_FILE_NAME
    write_players_data_to_csv(players_data_frame, path=path_csv)
    print(constants.WRITTEN_TO_FILE_MSG.format(path_csv))


def handle_database(players_data_frame):
    """
    This function handles the creation of a data-base, if was not created before,
    and the writing the data to it.
    """
    players_data_frame.loc[players_data_frame.weight == '', :] = 0  # replaces empty string values in weight with 0
    players_data_frame = players_data_frame[(players_data_frame.T != 0).any()]  # deletes empty rows
    insert_player_in_db(players_data_frame)
    insert_players_to_position_in_db(players_data_frame)
    insert_players_to_college_in_db(players_data_frame)
    df_teams, df_play_team = get_tables_from_api()
    get_team_tables_from_api(df_teams)
    play_and_team_ids = get_players_team_ids(df_play_team)
    insert_players_to_team_in_db(play_and_team_ids)
    print(constants.WRITTEN_TO_DATA_BASE_MSG)



def main():
    """
    This is main(). The main function calls all necessary functions needed for scraping all of the
    players data from the https://www.basketball-reference.com/ website.
    :return: None.
    """
    args = operate_commandline_argument_parser()
    urls_list = create_urls_list()
    players_dict = create_players_dict()
    positions = get_positions()
    colleges = get_colleges()
    scope = check_scope_value(args.scope)
    path = get_path()
    if (scope == 'all') | (scope[0] == 'letter') | (scope[0] == 'letter_range'):
        players_dict = get_scope(scope, urls_list, players_dict, positions, colleges)
    elif not scope:
        print(constants.BAD_SCOPE_ARG_MSG)
        sys.exit(0)
    players_data_frame = create_players_data_frame(players_dict)
    if args.print:
        print(players_data_frame)
    if args.dataframe:
        pickle_dataframe(path, players_data_frame)
    if args.csv:
        handle_csv(path, players_data_frame)
    if args.database:
        handle_database(players_data_frame)

if __name__ == '__main__':
    con, cur = connect_to_db()
    main()
