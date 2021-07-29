"""
This is a constants python file, made to serve players_data_scraper.py.
Authors: Bazham Khanatayev, David Muenz and Eyal Ran.
"""

A_TO_Z = 'abcdefghijklmnopqrstuvwxyz'
BASE_URL = 'https://www.basketball-reference.com/players/'
FORWARD_SLASH = '/'
RETRIEVING_DATA_MSG = 'Retrieving players data...'
SCRAPING_MSG = 'Starts scraping all players data...'
CSV_FILE_NAME = 'players_data.csv'
PKL_FILE_NAME = 'players_df.pkl'
USER_PATH = ''
GENERAL_ERROR_MSG = 'Error!:'
NOT_WRITTEN_TO_FILE_MSG = 'The data was not written to a file!'
DATA_FRAME_NOT_SERIALIZED_MSG = 'The data-frame was not serialized!'
DATA_WAS_NOT_WRITTEN_TO_DB_MSG = 'The data was not written to the data-base!'
TERMINATION_MSG = 'The scraper will now be terminated.'
BAD_SCOPE_ARG_MSG = 'Bad value for scope argument was provided. Please refer to the help menu!'
DF_CREATED_SERIALIZED_MSG = 'Players DataFrame was created and serialized as: players_df.pkl'
WRITTEN_TO_FILE_MSG = '\nThe players data was written to the file: {}'
WRITTEN_TO_DATA_BASE_MSG = '\nThe players data was written to the Data Base.'
SQL_USER_NAME = ''  # your username
SQL_USER_PASSWORD = ''  # your password
BASE_URL_API = 'https://free-nba.p.rapidapi.com/'
TEAMS_URL_EXT = 'teams'
PLAYERS_URL_EXT = 'players'
GAMES_URL_EXT = 'games'
STATS_URL_EXT = 'stats'
API_KEY_KEY = 'x-rapidapi-key'
API_KEY_VALUE = 'c0b6c75352mshaec7fab79e21b2dp10a159jsncc125cbb081c'
API_HOST_KEY = 'x-rapidapi-host'
API_HOST_VALUE = 'free-nba.p.rapidapi.com'
URL = 'url'
HEADERS = 'headers'
PARAMS = 'params'