"""
This a scraper code made for the third check point of the scraping project of the 2021 June cohort
of the <itc> Fellows Data-Science Training Program, and used for scraping data using the 'free NBA
API' API.
Authors: Bazham Khanatayev, David Muenz and Eyal Ran.
"""

import sys
import json
import requests
import pandas as pd
import constants


def create_teams_request_arguments_dict(data, params_dict=None):
    """
    This function creates a request arguments dictionary for a data request to the free NBA API.
    :param data: str, The data to be requested from the API
    :param params_dict: dict, a dictionary for the parameters request.get() params argument.
    :return: dict, dictionary for a data request to the free NBA API.
    """
    req_dict = {}
    req_dict[constants.URL] = constants.BASE_URL_API + data
    req_dict[constants.HEADERS] = {constants.API_KEY_KEY: constants.API_KEY_VALUE,
                                   constants.API_HOST_KEY: constants.API_HOST_VALUE}
    req_dict[constants.PARAMS] = params_dict
    return req_dict


def get_teams_page_content(req_dict):
    """
    This function gets a response object from the requested API page.
    :param req_dict: dict, dictionary for a data request to the free NBA API
    :return: content of the response object from the requested API page or an error object if request failed.
    """
    url_api = req_dict[constants.URL]
    headers = req_dict[constants.HEADERS]
    params = req_dict[constants.PARAMS]
    try:
        page = requests.get(url=url_api, headers=headers, params=params)
        return page.content
    except Exception as error:
        display_error_and_terminate(error)


def get_json(page_content):
    """
    This function creates an json object file out of the content of the API page.
    :param page_content: content of the response object from the requested API page
    :return: json object file out of the content of the API page.
    """
    return json.loads(page_content)


def get_dataframe(json_obj):
    """
    This function creates a Pandas DataFrame object out of a json object.
    :param json_obj: json object file out of the content of the API page.
    :return: Pandas DataFrame object out of a json object.
    """
    return pd.DataFrame(json_obj['data'])


def get_api_teams_data(data):
    """
    This function is a wrapper function for getting the API data.
    :return: Pandas DataFrame object containing the API data.
    """
    request_dict = create_teams_request_arguments_dict(data)
    page = get_teams_page_content(request_dict)
    json_page = get_json(page)
    return get_dataframe(json_page)


def get_player_single_page_from_api(page, url, headers, querystring):
    """
    This function gets a single page of players data.
    """
    return requests.get(url, headers=headers, params=querystring).content


def get_teams_from_players_api(page_json):
    """
    This function gets the NBA teams list.
    """
    teams = []
    for player in page_json['data']:
        teams.append(player['team']['full_name'])
    return teams


def get_player_data_dict_from_api(start_page, end_page, url, headers):
    """
    This function creates the dictionary holding the NBA players and their teams data.
    """
    players_dict = {'first_name': [], 'last_name': [], 'teams': []}
    page_to_request = start_page
    while page_to_request <= end_page:
        querystring = {"per_page": "100", "page": page_to_request}
        try:
            page = get_player_single_page_from_api(page_to_request, url, headers, querystring)
        except Exception:
            page_to_request += 1
            continue
        page_json = json.loads(page)
        players_page = pd.DataFrame(page_json['data'])[['first_name', 'last_name']]
        players_dict['first_name'].extend(players_page.first_name.to_list())
        players_dict['last_name'].extend(players_page.last_name.to_list())
        players_dict['teams'].extend(get_teams_from_players_api(page_json))
        page_to_request += 1
    return players_dict


def get_players_teams_from_api(start_page, end_page, data):
    """
    This function is a wrapper function for for getting the pandas data-frame holding the players'
    names and and the NBA team each of them plays for.
    """
    request_dict = create_teams_request_arguments_dict(data)
    url = request_dict[constants.URL]
    headers = request_dict[constants.HEADERS]
    players_teams_dict = get_player_data_dict_from_api(start_page, end_page, url, headers)
    players_teams = pd.DataFrame(players_teams_dict)
    return players_teams


def display_error_and_terminate(error):
    """
    This function display error messages to the standard output and terminates the program.
    :param error: Exception object, holding the error.
    :return: None
    """
    print(constants.GENERAL_ERROR_MSG, error)
    print(constants.TERMINATION_MSG)
    sys.exit(0)


def display_df(df):
    """
    This function displays the DataFrame object to the standard output.
    :param df: Pandas DataFrame object containing the API data.
    :return: None.
    """
    print(df.head(30))


def main():
    """
    This is main function which returns pandas data-frames of all NBA teams, and of NBA players
    and the NBA team that each of them plays for.
    """
    teams_data = get_api_teams_data(constants.TEAMS_URL_EXT)
    from_page = constants.PLAYERS_START_PAGE
    to_page = constants.PLAYERS_LAST_PAGE
    players_teams_data = get_players_teams_from_api(from_page, to_page, constants.PLAYERS_URL_EXT)
    display_df(teams_data)
    display_df(players_teams_data)
    return teams_data, players_teams_data


if __name__ == '__main__':
    main()
