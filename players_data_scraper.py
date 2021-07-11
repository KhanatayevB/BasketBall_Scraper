"""
This a scraper code made for the first check point of the scraping project of the 2021 June cohort
of the <itc> Fellows Data-Science Training Program, and used for scraping all of the NBA players
data from the https://www.basketball-reference.com/ website.

Authors: Bazham Khanatayev, David Muenz and Eyal Ran.
"""

import constants
import sys
import requests
from bs4 import BeautifulSoup
import argparse
import pandas as pd


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


def scrape_player_data(tr, players_dict):
    """
    This function receives a single row of a player  data, scraped from the players data tables,
    and extract the player's data from it, into the players_dict.
    :param tr: BeautifulSoup object, contains a single row of a player  data, scraped from the
               players data tables
    :param players_dict: dict, containing the players data.
    :return: players_dict: dict, containing the players data.
    """
    players_dict['player'].append(tr.a.text)
    players_dict['start_year'].append(tr.find('td', {'data-stat': 'year_min'}).text)
    players_dict['end_year'].append(tr.find('td', {'data-stat': 'year_max'}).text)
    players_dict['position'].append(tr.find('td', {'data-stat': 'pos'}).text)
    players_dict['height'].append(tr.find('td', {'data-stat': 'height'}).text)
    players_dict['weight'].append(tr.find('td', {'data-stat': 'weight'}).text)
    players_dict['birth_date'].append(tr.find('td', {'data-stat': 'birth_date'}).text)
    players_dict['colleges'].append(tr.find('td', {'data-stat': 'colleges'}).text)
    return players_dict


def scrape_letter_players_data(letter_page_soup_obj, players_dict):
    """
    This function receives a BeautifulSoup object containing the data table of all players
    with last name starts with same letter, and for each row of tge data table, calls to
    a helper function the writes the player's data into the players_dict.
    :param letter_page_soup_obj: BeautifulSoup object containing the data table of all players
                                 with last name starts with same letter
    :param players_dict: dict, containing the players data.
    :return: dict, containing the players data.
    """
    for tr in letter_page_soup_obj.find_all('tr'):
        if tr.find('a'):
            players_dict = scrape_player_data(tr, players_dict)
    return players_dict


def get_all_players_data(urls_list, players_dict):
    """
    This function receives a list of URL's to scrape data from, and the players_dict proto-type
    which will hold the players scraped data.
    :param urls_list: st, of  https://www.basketball-reference.com/ website URL's needed for scraping
    :param players_dict: dict, containing the players data.
    :return: dict, containing the players data.
    """
    print(constants.SCRAPING_MSG)
    for url in urls_list:
        letter_page_soup = get_letter_page_soup_obj(url)
        players_dict = scrape_letter_players_data(letter_page_soup, players_dict)
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
    if path:
        path = path + constants.CSV_FILE_NAME
    else:
        path = constants.CSV_FILE_NAME
    players_df.to_csv(path, index=False)
    return path


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


def main():
    """
    This is main(). The main function calls all necessary functions needed for scraping all of the
    players data from the https://www.basketball-reference.com/ website.
    :return: None.
    """
    args = operate_commandline_argument_parser()
    urls_list = create_urls_list()
    players_dict = create_players_dict()
    scope = check_scope_value(args.scope)
    if constants.USER_PATH:
        path = constants.USER_PATH + constants.FORWARD_SLASH
    else:
        path = constants.USER_PATH
    if scope == 'all':
        try:
            players_dict = get_all_players_data(urls_list, players_dict)
        except Exception as error:
            display_error_and_terminate(error)
    elif scope[0] == 'letter':
        try:
            players_dict = get_letter_players_data(urls_list, players_dict, scope[1])
        except Exception as error:
            display_error_and_terminate(error)
    elif scope[0] == 'letter_range':
        try:
            players_dict = get_letter_range_players_data(urls_list, players_dict, scope[1], scope[2])
        except Exception as error:
            display_error_and_terminate(error)
    elif not scope:
        print(constants.BAD_SCOPE_ARG_MSG)
        sys.exit(0)
    players_data_frame = create_players_data_frame(players_dict)
    if args.print:
        print(players_data_frame)
    if args.dataframe:
        path_pkl = path + constants.PKL_FILE_NAME
        players_data_frame.to_pickle(path=path_pkl)
        print(constants.DF_CREATED_SERIALIZED_MSG)
    if args.csv:
        path_csv = path + constants.CSV_FILE_NAME
        write_players_data_to_csv(players_data_frame, path=path_csv)
        print(constants.WRITTEN_TO_FILE_MSG.format(path_csv))
    if args.dataframe:
        # TODO: complete write to data base Code
        print(constants.WRITTEN_TO_DATA_BASE_MSG)


if __name__ == '__main__':
    main()
