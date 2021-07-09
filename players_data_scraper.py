"""
This a scraper code made for the first check point of the scraping project of the 2021 June cohort
of the <itc> Fellows Data-Science Training Program, and used for scraping all of the NBA players
data from the https://www.basketball-reference.com/ website.

Authors: Bazham Khanatayev, David Muenz and Eyal Ran.
"""

import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd
# import os
# import argparse
import pymysql

cnx = pymysql.connect(
        user= "new",
        password= "Ahoibrause#97",
        db= "aalwines",
    )
cursor = cnx.cursor()
def create_db(urls_list, tr):

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS players (id INT AUTO_INCREMENT PRIMARY KEY, player VARCHAR(100),  start_year INT,"
        "end_year INT, position INT, height float, weight INT, birth_date DATE, colleges VARCHAR(100))")
    print('Starts scraping all players data...')
    for url in urls_list:
        letter_page_soup = get_letter_page_soup_obj(url)
        for tr in letter_page_soup.find_all('tr'):
            if tr.find('a'):
                letter_page_soup = get_letter_page_soup_obj(url)
                players_dict = scrape_letter_players_data(letter_page_soup, players_dict, url)
                players_dict = {'player': [], 'start_year': [], 'end_year': [], 'position': [],
                                'height': [], 'weight': [], 'birth_date': [], 'colleges': []}

                player = tr.a.text
                start_year = tr.find('td', {'data-stat': 'year_min'}).text
                end_year = tr.find('td', {'data-stat': 'year_max'}).text
                position = tr.find('td', {'data-stat': 'pos'}).text
                height = tr.find('td', {'data-stat': 'height'}).text
                weight = tr.find('td', {'data-stat': 'weight'}).text
                birth_date = tr.find('td', {'data-stat': 'birth_date'}).text
                colleges = tr.find('td', {'data-stat': 'colleges'}).text
                player_url = tr.find('a').get('href')


        add_node_list = ("INSERT INTO node_list ( player, start_year, end_year, position , height, weight, birth_date, colleges)"
                     "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                     )


def create_urls_list():
    """
    This function creates the URL's list from which the data will be scraped. The list includes all
    the pages in https://www.basketball-reference.com/, website which contains the data for every
    player that ever played in the NBA league.
    :return: lst, of  https://www.basketball-reference.com/ website URL's needed for scraping.
    """
    base_url = 'https://www.basketball-reference.com/players/'
    a_z = 'abcdefghijklmnopqrstuvwxyz'
    for_slash = '/'
    a_z_urls = []
    for char in a_z:
        a_z_urls.append(base_url + char + for_slash)
    return a_z_urls


def get_letter_page_soup_obj(url):
    """
    This function create a single web request to a website, by the website's URL, and creates
    a BeautifulSoup object out of its HTML code.
    :param url: str, represents a website's URL to form a web request from.
    :return: BeautifulSoup object of the website's URL HTML code.
    """
    page = requests.get(url)
    letter_page_soup = BeautifulSoup(page.content, 'html.parser')
    print('Retrieving players data...')
    return letter_page_soup


def create_players_dict():
    """
    This function creates a proto-type of the dictionary to which the scraped players data
    will be written.
    :return: dict.
    """
    players_dict = {'player': [], 'start_year': [], 'end_year': [], 'position': [],
                    'height': [], 'weight': [], 'birth_date': [], 'colleges': []}
    return players_dict

def create_players_dict():
    """
    This function creates a proto-type of the dictionary to which the scraped players data
    will be written.
    :return: dict.
    """
    players_career_sum_dict = {'player': [], 'G': [], 'PTS': [], 'TRB': [], 'AST': []}
    return players_career_sum_dict

def scrap_payer_data(tr, players_dict ,url):
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
    player_url = tr.find('a').get('href')
    page_pl = requests.get(url + player_url)
    letter_page_soup_pl = BeautifulSoup(page_pl.content, 'html.parser')
    return players_dict


def scrape_letter_players_data(letter_page_soup_obj, players_dict, url):
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
            players_dict = scrap_payer_data(tr, players_dict, url)
    return players_dict


def get_all_players_data(urls_list, players_dict):
    """
    This function receives a list of URL's to scrape data from, and the players_dict proto-type
    which will hold the players scraped data.
    :param urls_list: st, of  https://www.basketball-reference.com/ website URL's needed for scraping
    :param players_dict: dict, containing the players data.
    :return: dict, containing the players data.
    """
    print('Starts scraping all players data...')
    for url in urls_list:
        letter_page_soup = get_letter_page_soup_obj(url)
        players_dict = scrape_letter_players_data(letter_page_soup, players_dict,url)
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
        path = path + 'players_data.csv'
    else:
        path = 'players_data.csv'
    players_df.to_csv(path, index=False)
    return path


def main():
    """
    This is main(). The main function calls all necessary functions needed for scraping all of the
    players data from the https://www.basketball-reference.com/ website.
    :return: None.
    """
    urls_list = create_urls_list()
    players_dict = create_players_dict()
    try:
        players_dict = get_all_players_data(urls_list, players_dict)
        players_data_frame = create_players_data_frame(players_dict)
        print("\nThe first 10 players' data: ", players_data_frame.head(10))
        print(f'\nData of {players_data_frame.shape[0]} players was scraped.\n')
        path = write_players_data_to_csv(players_data_frame, path='/Users/bazhamkhanatayev/Documents/ITC/Scraper Project/')
        print(f'\nThe players data was written to the file: {path}')
    except Exception as error:
        print('Error!:', error)
        print('The data was not written to a file!')
        print('The scraper will now be terminated.')
        sys.exit(0)


if __name__ == '__main__':
    main()
