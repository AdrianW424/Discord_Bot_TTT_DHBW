import requests
from bs4 import BeautifulSoup

class xoyondo:
    
    def delete_date(self, dates):
        pass
        # check if right format (date and list of dates)
        # -> integers are fine as well -> 1 means delete the first date - 2 -> first two dates (negative integers are also allowed -> -1 means delete the last date). 0 means all dates
        # delete every date given in the list of dates
        # if user wanted to delete every date give hint, that the last date could not be deleted due to xoyondo restrictions

    def add_date(self, dates):
        pass
        # check if right format (date and list of dates)
        # add every date given in the list of dates
        # if user wanted to add every date give hint, that the last date could not be added due to xoyondo restrictions