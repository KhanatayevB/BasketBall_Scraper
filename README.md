# DataMiningProject

This is a project to learn and apply web scraping to some website that 
contains a lot of data. 

#Website 
The website that we chose is: https://www.basketball-reference.com/ \


#Approach

The first step to creating this scraper is to learn the BeautifulSoup package and some\
basic html. \

### Approach for checkpoint 1
The website stores the players data on different pages, indexed by the first letter of 
the players sure names. Therefore, the scrpaers first collects from the site all of the
urls for all of the pages with players data, and then uses those urls for sequentially
scrape the actual players data, of all of the players, starting from the the players with
sure name starts with A, up to Z. \
The scraped data is then loaded into a pandas DataFrame, printed to the screen, and saved
as a .csv file.

### Approach for checkpoint 2
As of the second checkpoint the scraper supports command-line arguments, as follows:

NBA players basic data and stats scraper.

optional arguments:
  -h, --help            show this help message and exit
  -s SCOPE, --scope SCOPE
                        Scraper scope (Players to scrape): all (default), for
                        scraping all players data,[Letter (For all players
                        with last name starts with the Letter)],[Letters-
                        Inclusive- (LETTER-LETTER) (last name starts with a
                        Letter in range)],
  -p, --print           used for printing scraping results to standard output.
  -d, --dataframe       for creating a serialized pandas data-frame of the
                        scraping results.
  -c, --csv             for creating a csv file of the scraping results.
  -b, --database        for writing the scraping results to the players DB.
\

By default, the scraper will get all of the players data. For limiting the scraper, it is
possible to provied -s argument, with a value of an alphabetical letter or a range of letters. \

The other arguments: -p, -d, -c, and -b, as shown above, controls the usage which will be done
with the scraped data, printing it to the standard output (-p), load it to a pandas DataFrame
object and serialize it as a .pkl file (-d), save it as a .csv file (-c), save it to the data-base,
(-b), or do all of them, or some subset of them. \

For example: 

players_data_scraper.py -s all -pc , will scrape all players data, prints it and save
it as a .csv file. \

players_data_scraper.py -s b-e -dbc , will scrape the data of all of the players with sure name, starts
with 'b', 'c', 'd', or 'e', load it to a dataframe and serialized it a a .pkl file, save it to the data-base, 
and save it it as a .csv file. \

players_data_scraper.py -s m -p , will scrape the data of all of the players with sure name, starts
with 'm', and will print the data to the standard output. \

Notice that even when the scraper is run without a -d argument, the scraped data will still be loaded to a
pnadas DataFrame, for use of other tasks, but the created DataFrame will not be serialized and therefore will
not be available after the end of the scraper run.

All files created by the scraper, as well as the data-based created by the scraper, are sved to the directory
that contains the players_data_scraper.py file. This could be changed by an assignment of the requested path
to the USER_PATH variable found on the constants.py file. \

When trying to right scraped data to the data-base, the user should provide the user's sql's user name and password
by an assignment to the SQL_USER_NAME AND SQL_USER_PASSWORD variables found on the constants.py file. \


# Contributors

This project is owned by: \
Bazham Khanatayev \
David Muenz \
Eyal Ran   

# GitHub Link

This project is in a public repository: \
https://github.com/KhanatayevB/BasketBall_Scraper


# Project Status

Checkpoint 1 - basic webscrape working, project set up. \
Checkpoint 2 - Scraper supports command-line arguments for filtering scraped data and saving the scraped data in multiple formats and to a data-base.