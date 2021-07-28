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


def create_request_arguments_dict(data, params_dict=None):
    """
    This function creates a request arguments dictionary for a data request to the free NBA API.
    :param data: str, The data to be requested from the API
    :param params_dict: dict, a dictionary for the parameters request.get() params argument.
    :return: dict, dictionary for a data request to the free NBA API.
    """
    req_dict = {}
    req_dict[constants.URL] = constants.BASE_URL + data
    req_dict[constants.HEADERS] = {constants.API_KEY_KEY: constants.API_KEY_VALUE,
                                   constants.API_HOST_KEY: constants.API_HOST_VALUE}
    req_dict[PARAMS] = params_dict
    return req_dict


def get_page_content(req_dict):
    """
    This function gets a response object from the requested API page.
    :param req_dict: dict, dictionary for a data request to the free NBA API
    :return: content of the response object from the requested API page or an error object if request failed.
    """
    url = req_dict[constants.URL]
    headers = req_dict[constants.HEADERS]
    params = req_dict[constants.PARAMS]
    try:
        page = requests.get(url=url, headers=headers, params=params)
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


def get_api_data(data, params=None):
    """
    This function is a wrapper function for getting the API data.
    :return: Pandas DataFrame object containing the API data.
    """
    request_dict = create_request_arguments_dict(data)
    page = get_page_content(request_dict)
    json_page = get_json(page)
    return get_dataframe(json_page)


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
    teams_data = get_api_data(constants.TEAMS_URL_EXT)
    display_df(teams_data)


if __name__ == '__main__':
    main()
