import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from collections import OrderedDict
import re

class xoyondo:
    """_summary_
    
    Attributes:
        url (str): The provided URL.
        id (str): The user ID extracted from the URL.
        password (str): The password extracted from the URL.
        headers (dict): The headers to be used for HTTP requests.
    """
    
    def __init__(self, url, headers = {"User-Agent": "Mozilla/5.0"}, print_messages = True):
        """Initialize the object with a specified URL and headers.

        Args:
            url (str): The URL that might contain user ID and password information. Defaults to an empty string.
            headers (dict, optional): The headers to be used for HTTP requests. Defaults to {"User-Agent": "Mozilla/5.0"}.
            print_messages (bool, optional): Whether to print messages to the console. Defaults to True.
        """
        
        self.url = url
        self.id, self.password = self.__extract_from_url(self.url)
        self.headers = headers
        self.print_messages = print_messages
    
    def __extract_from_url(self, url):
        """Extract ID and password from a given Xoyondo URL.

        Args:
            url (str): The Xoyondo URL containing user ID and password information.

        Raises:
            ValueError: If the provided URL does not match the expected Xoyondo format.

        Returns:
            tuple: A tuple containing the extracted user ID and password from the URL.
        """
        
        pattern= r'^https://xoyondo\.com/dp/([^/]+)/([^/]+)$'
        match = re.match(pattern, url)
        
        ### Error handling (ValueError)
        if not match:
            raise ValueError("Invalid URL format.")
        ###
        
        return match.groups()
    
    def __get_date_range(self,start, end):
        """Generate a list of dates in the format '%Y/%m/%d' between two given dates (inclusive).

        Args:
            start (str): The starting date in the format '%Y/%m/%d'.
            end (str): The ending date in the format '%Y/%m/%d'.

        Returns:
            list: A list of dates as strings in the format '%Y/%m/%d' from the start date to the end date, inclusive.
        """
        
        start_date = datetime.strptime(start, '%Y/%m/%d')
        end_date = datetime.strptime(end, '%Y/%m/%d')
        delta = end_date - start_date
        return [(start_date + timedelta(days=i)).strftime('%Y/%m/%d') for i in range(delta.days + 1)]
    
    def __get_webpage(self, url, headers, features="html.parser"):
        """Fetches the content of a webpage using the provided URL and headers, and then parses it using BeautifulSoup.

        Args:
            url (str): The URL of the webpage to be fetched.
            headers (dict): The headers to be used for the HTTP request.
            features (str, optional): The parser to be used by BeautifulSoup. Defaults to "html.parser".

        Raises:
            HTTPError: If there's an issue with the HTTP request (e.g., a 404 Not Found error).

        Returns:
            BeautifulSoup: A BeautifulSoup object containing the parsed content of the webpage.
        """
        
        response = requests.get(url, headers=headers)
        
        ### Error handling (HTTPError)
        response.raise_for_status()
        ###
        
        return BeautifulSoup(response.content, features)
    
    def __output_message(self, new_message, list_of_messages):
        """Prints a message to the console and adds it to a list of messages.

        Args:
            new_message (str): The message to be printed.
            list_of_messages (list): The list of messages to which the new message should be added.
        """
        
        list_of_messages.append(new_message)
        if self.print_messages:
            print(new_message)
        
    def change_url(self, url):
        """Updates the object's URL and extracts the user ID and password from the new URL.

        Args:
            url (str): The new URL that might contain user ID and password information.
        """
        self.url = url
        self.id, self.password = self.__extract_from_url(self.url)
    
    def delete_date(self, dates:str):
        messages = []
        
        html = self.__get_webpage(self.url, self.headers)
        date_elements = html.find_all('i', {'class': 'fa fa-edit js-date-edit-cal text-warning pointer mx-1'})
        date_to_id = {el['data-date']: el['data-dateid'] for el in date_elements}
        
        dates_to_delete = []
        
        if len(date_to_id) <= 1:
            self.__output_message("Deletion not possible as there is only one date left.", messages)
            return messages
        elif dates is None:
            dates_to_delete = list(date_to_id.values())
            self.__output_message("Deletion not possible as there will be no date left.", messages)
        elif "," in dates or ":" in dates:
            parts = dates.split(",")
            for part in parts:
                if ":" in part:
                    start, end = [x.strip() for x in part.split(":")]
                    
                    # Check if the range is valid
                    if start.isdigit() and end.isdigit() and int(start) <= int(end):
                        # positive numbers
                        start, end = int(start), int(end)
                        if len(date_to_id) <= start:
                            self.__output_message(f"Index {start} out of range.", messages)
                        elif len(date_to_id) <= end:
                            self.__output_message(f"Index {end} out of range.", messages)
                        dates_to_delete.extend(date_to_id[date] for i, date in enumerate(date_to_id.keys()) if start <= i <= end)
                    elif start.replace('-', '').isdigit() and end.replace('-', '').isdigit():
                        # at least one negative number
                        start, end = int(start), int(end)
                        if start < 0:
                            start = len(date_to_id) + start
                            if len(date_to_id) <= start or start < 0:
                                self.__output_message(f"Index {start} out of range.", messages)
                        if end < 0:
                            end = len(date_to_id) + end
                            if len(date_to_id) <= end or end < 0:
                                self.__output_message(f"Index {end} out of range.", messages)
                            
                        if start <= end:
                            dates_to_delete.extend(date_to_id[date] for i, date in enumerate(date_to_id.keys()) if start <= i <= end)
                        else:
                            self.__output_message(f"Start must be located before end. In this case start is {start} and end is {end}.", messages)
                    else:
                        # dates
                        dates_to_delete.extend(date_id for date in self.__get_date_range(start, end) if date in date_to_id for date_id in [date_to_id[date]])
                else:
                    if part.replace('-', '').isdigit():
                        index = int(part)
                        if -len(date_to_id) <= index < len(date_to_id):
                            dates_to_delete.append(date_to_id[list(date_to_id.keys())[index if index > 0 else index]])
                        else:
                            self.__output_message(f"Index {index} out of range.", messages)
                    elif part.strip() in date_to_id:
                        dates_to_delete.append(date_to_id[part.strip()])
                    else:
                        self.__output_message(f"Invalid date: {part.strip()}", messages)
        else:
            if dates.replace('-', '').isdigit():
                index = int(dates)
                if -len(date_to_id) <= index < len(date_to_id):
                    dates_to_delete.append(date_to_id[list(date_to_id.keys())[index if index > 0 else index]])
                else:
                    self.__output_message(f"Index {index} out of range.", messages)
            elif dates.strip() in date_to_id:
                dates_to_delete.append(date_to_id[dates.strip()])
            else:
                self.__output_message(f"Invalid date: {dates.strip()}", messages)
        
        dates_to_delete = list(OrderedDict.fromkeys(dates_to_delete))  # Remove duplicates while maintaining order
        
        remaining_dates = set(date_to_id.values()) - set(dates_to_delete)
        if len(remaining_dates) < 1:
            self.__output_message("Deletion will result in only one date being left. It is thus not possible.", messages)
            dates_to_delete = dates_to_delete[:-1]
        
        delete_url = "https://xoyondo.com/pc/poll-change-poll"
        for date_id in dates_to_delete:
            form_data = {
                'ID': self.id,
                'product': 'd',
                'dateID': date_id,
                'operation': 'date_delete',
                'pass': self.password
            }
            delete_response = requests.post(delete_url, headers=self.headers, data=form_data)
            if delete_response.status_code == 200:
                self.__output_message(f'Successfully deleted date with ID {date_id}', messages)
            else:
                self.__output_message(f'Failed to delete date with ID {date_id}: HTTP {delete_response.status_code}', messages)
                
        return messages
        
        # check if right format (date and list of dates)
        # -> integers are fine as well -> 1 means delete the first date - 2 -> first two dates (negative integers are also allowed -> -1 means delete the last date). 0 means all dates
        # delete every date given in the list of dates
        # if user wanted to delete every date give hint, that the last date could not be deleted due to xoyondo restrictions

    def add_date(self, dates):
        messages = []
        dates_to_add = []

        if "," in dates or ":" in dates:
            parts = dates.split(",")
            for part in parts:
                if ":" in part:
                    start, end = [x.strip() for x in part.split(":")]
                    dates_to_add.extend(self.__get_date_range(start, end))
                else:
                    dates_to_add.append(part.strip())
        else:
            dates_to_add.append(dates.strip())
        
        # Add the dates using the extracted date IDs
        add_url = "https://xoyondo.com/pc/poll-change-poll"
        for date in dates_to_add:
            form_data = {
                'newdates': date,
                'ID': self.id,
                'product': 'd',
                'operation': 'date_add_cal',  
                'pass': self.password,
                'times_selected': 0
            }
            add_response = requests.post(add_url, headers=self.headers, data=form_data)
            if add_response.status_code == 200:
                self.__output_message(f'Successfully added date {date}', messages)
            else:
                self.__output_message(f'Failed to add date {date}: HTTP {add_response.status_code}', messages)
                
        return messages
        
        # check if right format (date and list of dates)
        # add every date given in the list of dates
        # if user wanted to add every date give hint, that the last date could not be added due to xoyondo restrictions
        
    def delete_users(self):
        messages = []
        
        html = self.__get_webpage(self.url, self.headers)
        user_elements = html.find_all('tr', {'class': 'js-user-rows'})
        user_ids_to_delete = [el['data-userid'] for el in user_elements]
        
        if len(user_ids_to_delete) < 1:
            self.__output_message("Deletion not possible as there is no user registered.", messages)
            return messages
        
        # Delete each user
        delete_url = "https://xoyondo.com/pc/poll-change-poll-ajax"
        for user_id in user_ids_to_delete:
            form_data = {
                'u': user_id,
                'ID': self.id,
                'product': 'd',
                'operation': 'delete-user',
                'pass': self.password
                }
            delete_response = requests.post(delete_url, headers=self.headers, data=form_data)
            if delete_response.status_code == 200:
                self.__output_message(f'Successfully deleted user with ID {user_id}', messages)
            else:
                self.__output_message(f'Failed to delete user with ID {user_id}: HTTP {delete_response.status_code}', messages)

        return messages
        # delete every user
        
    def get_vote(self, index=None):
        html = self.__get_webpage(self.url, self.headers)
        user_rows = html.find_all('tr', class_='js-user-rows')
        
        date_results = {}

        # Process each user row
        for user_row in user_rows:
            # Get all vote columns for the user (excluding name columns)
            vote_columns = user_row.find_all('td', {'class': ['table-danger-cell', 'table-success-cell', 'table-warning-cell']})
            
            for idx, column in enumerate(vote_columns):
                # Check which vote it is based on class
                if 'table-danger-cell' in column['class']:
                    vote = 'no'
                elif 'table-success-cell' in column['class']:
                    vote = 'yes'
                else:
                    vote = 'maybe'
                
                # Use the date index as a key for the result dictionary
                if idx not in date_results:
                    date_results[idx] = {'yes': 0, 'no': 0, 'maybe': 0}
                
                date_results[idx][vote] += 1

        # Determine which indices to filter on
        if index is not None:
            # Adjusting for negative indices
            if isinstance(index, int):
                index = [index]

            if any(i < 0 for i in index):
                total_dates = len(date_results)
                index = [(i + total_dates) if i < 0 else i for i in index]

            # Filter the results
            filtered_results = {idx: result for idx, result in date_results.items() if idx in index}
        else:
            filtered_results = date_results

        # Format the results
        formatted_results = []
        for idx, counts in filtered_results.items():
            formatted_results.append({
                'date_index': idx,
                'yes_count': counts['yes'],
                'no_count': counts['no'],
                'maybe_count': counts['maybe']
            })
        
        return formatted_results
        
        # if specific date or dates or range of dates given, give the count of yes, no and maybe of all users for this date
    
    def get_date_for_index(self, index:int|list):
        html = self.__get_webpage(self.url, self.headers)
        
        # Extracting date to its respective ID
        date_elements = html.find_all('i', {'class': 'fa fa-edit js-date-edit-cal text-warning pointer mx-1'})
        date_to_id = {el['data-date']: el['data-dateid'] for el in date_elements}
        
        # Handle single integer index
        if isinstance(index, int):
            index = [index]
        
        # Adjust for negative indices
        total_dates = len(date_to_id)
        index = [(i + total_dates) if i < 0 else i for i in index]
        
        # Fetch the dates for given indices
        dates_for_indices = [list(date_to_id.keys())[i] for i in index if 0 <= i < total_dates]
        
        return dates_for_indices
    
    def get_index_for_date(self, dates:str):
        messages = []
        
        html = self.__get_webpage(self.url, self.headers)
        date_elements = html.find_all('i', {'class': 'fa fa-edit js-date-edit-cal text-warning pointer mx-1'})
        date_to_id = {el['data-date']: el['data-dateid'] for el in date_elements}
        indices_to_return = []
        
        if not dates:
            return indices_to_return

        if "," in str(dates) or ":" in str(dates):
            parts = str(dates).split(",")
            for part in parts:
                if ":" in part:
                    start, end = [x.strip() for x in part.split(":")]
                    valid_dates = [date for date in self.__get_date_range(start, end) if date in date_to_id]
                    indices_to_return.extend(list(date_to_id.keys()).index(date) for date in valid_dates)
                else:
                    if str(part).strip() in date_to_id:
                        indices_to_return.append(list(date_to_id.keys()).index(str(part).strip()))
                    else:
                        self.__output_message(f"Invalid date: {str(part).strip()}", messages)
        else:
            if str(dates).strip() in date_to_id:
                indices_to_return.append(list(date_to_id.keys()).index(str(dates).strip()))
            else:
                self.__output_message(f"Invalid date: {str(dates).strip()}", messages)
        
        # Remove duplicates while maintaining order
        indices_to_return = list(dict.fromkeys(indices_to_return))
        
        return indices_to_return, messages