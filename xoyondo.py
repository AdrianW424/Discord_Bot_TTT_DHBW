import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from collections import OrderedDict
import re
import threading
import queue
from multipledispatch import dispatch

class Xoyondo:
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
        
        self.print_messages = print_messages
        self.url = url
        self.id, self.password, _ = self.__extract_from_url(self.url)
        self.headers = headers
    
    def __extract_from_url(self, url):  # throws ValueError
        """Extract ID and password from a given Xoyondo URL.

        Args:
            url (str): The Xoyondo URL containing user ID and password information.

        Raises:
            ValueError: If the provided URL does not match the expected Xoyondo format.

        Returns:
            tuple: A tuple containing the extracted user ID and password from the URL.
        """
        messages = []
        
        pattern= r'^https://xoyondo\.com/dp/([^/]+)/([^/]+)$'
        match = re.match(pattern, url)
        
        ### Error handling (ValueError)
        if not match:
            raise ValueError(f"Invalid URL format: {url}")
        ###
        
        id, password = match.groups()
        
        self.log_message(f"URL has correct format. Consisting of ID: {id} and password: {password}", messages)
        
        return id, password, messages
    
    def set_url(self, url):
        """Updates the object's URL and extracts the user ID and password from the new URL.

        Args:
            url (str): The new URL that might contain user ID and password information.
        """
        messages = []
        
        self.url = url
        self.id, self.password, _messages = self.__extract_from_url(self.url)
        messages.extend(_messages)
        
        self.log_message(f"Changed URL to: {url}", messages)
        
        return messages
    
    def get_url(self, full=False):
        """Returns the object's URL.

        Args:
            full (bool, optional): Whether to return the full URL containing the ID and password or just the base URL containing the ID. Defaults to False.
            
        Returns:
            str: The object's URL.
        """
        if full:
            return self.url
        else:
            return re.sub(r'/[^/]+$', '', self.url)
    
    @dispatch(str, str)
    def get_date_list(self, start, end):    # throws ValueError
        """Generate a list of dates in the format '%Y/%m/%d' between two given dates (inclusive).

        Args:
            start (str): The starting date in the format '%Y/%m/%d'.
            end (str): The ending date in the format '%Y/%m/%d'.

        Returns:
            list: A list of dates as strings in the format '%Y/%m/%d' from the start date to the end date, inclusive.
        """
        messages = []
        
        start = str(start)
        end = str(end)
        
        try:
            start_date = datetime.strptime(start, '%Y/%m/%d')
        except ValueError:
            raise ValueError(f"Invalid start date: {start}")
        try:
            end_date = datetime.strptime(end, '%Y/%m/%d')
        except ValueError:
            raise ValueError(f"Invalid end date: {end}")
        
        delta = end_date - start_date
        date_list = [(start_date + timedelta(days=i)).strftime('%Y/%m/%d') for i in range(delta.days + 1)]
        self.log_message(f"Generated date list from {start} to {end}", messages)
        
        return date_list, messages
        
    @dispatch(str)
    def get_date_list(self, dates):
        
        messages = []
        
        dates = str(dates)
        if "," in dates or ":" in dates:
            parts = dates.split(",")
            dates = []
            for part in parts:
                if ":" in part:
                    start, end = [x.strip() for x in part.split(":")]
                    dates_buf, _messages = self.get_date_list(start, end)
                    dates.extend(dates_buf)
                    messages.extend(_messages)
                    self.log_message(f"Added date list from {start} to {end} to date list", messages)
                else:
                    try:
                        _ = datetime.strptime(part.strip(), '%Y/%m/%d')
                        dates.append(part.strip())
                        self.log_message(f"Added date {part.strip()} to date list", messages)
                    except ValueError:
                        raise ValueError(f"Invalid date: {part.strip()}")
        else:
            try:
                _ = datetime.strptime(dates.strip(), '%Y/%m/%d')
                dates = [dates.strip()]
                self.log_message(f"Added date {dates.strip()} to date list", messages)
            except ValueError:
                raise ValueError(f"Invalid date: {dates.strip()}")
            
        return dates, messages
    
    def __get_webpage(self, url, headers, features="html.parser"):  # throws HTTPError
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
        
        messages = []
        
        response = requests.get(url, headers=headers)
        
        ### Error handling (HTTPError)
        response.raise_for_status()
        ###
        
        self.log_message(f"Successfully fetched webpage: {url}", messages)
        
        return BeautifulSoup(response.content, features), messages
    
    def log_message(self, new_message, list_of_messages):
        """Prints a message to the console and adds it to a list of messages.

        Args:
            new_message (str): The message to be printed.
            list_of_messages (list): The list of messages to which the new message should be added.
        """
        
        list_of_messages.append(new_message)
        if self.print_messages:
            print(new_message)
    
    def delete_dates(self, dates:str=None):
        messages = []
        dates_to_delete = []
        
        html, _messages = self.__get_webpage(self.url, self.headers)
        messages.extend(_messages)
        date_elements = html.find_all('i', {'class': 'fa fa-edit js-date-edit-cal text-warning pointer mx-1'})
        date_to_id = {el['data-date']: el['data-dateid'] for el in date_elements}
        
        if len(date_to_id) <= 1:
            self.log_message("Deletion not possible as there is only one date left.", messages)
            return messages
        elif dates is None:
            dates_to_delete = list(date_to_id.values())
            self.log_message(f"Full deletion not possible as there will be '{list(date_to_id.keys())[-1]}' left.", messages)
        else:
            dates = str(dates)
            if "," in dates or ":" in dates:
                parts = dates.split(",")
                for part in parts:
                    if ":" in part:
                        start, end = [x.strip() for x in part.split(":")]
                        
                        # Check if the range is valid
                        if start.replace('-', '').isdigit() and end.replace('-', '').isdigit():
                            # at least one negative number

                            try:
                                start = int(start)
                            except ValueError:
                                raise ValueError(f"Invalid index: {start.strip()}")   
                             
                            try:
                                end = int(end)
                            except ValueError:
                                raise ValueError(f"Invalid index: {end.strip()}")    
                                
                            if start < 0:
                                start = len(date_to_id) + start
                            if len(date_to_id) <= start or start < 0:
                                raise ValueError(f"Index {start} out of range.")
                            if end < 0:
                                end = len(date_to_id) + end
                            if len(date_to_id) <= end or end < 0:
                                raise ValueError(f"Index {end} out of range.")

                            if start <= end:
                                dates_to_delete.extend(date_to_id[date] for i, date in enumerate(date_to_id.keys()) if start <= i <= end)
                                self.log_message(f"Added dates from {list(date_to_id.keys())[start]} to {list(date_to_id.keys())[end]} to deletion list", messages)
                            else:
                                raise ValueError(f"Start index must be less than or equal to end index. Given: {start}:{end}")
                                
                        else:
                            # dates
                            dates, _messages = self.get_date_list(start, end)
                            messages.extend(_messages)
                            for date in dates:
                                if date.strip() in date_to_id:
                                    dates_to_delete.append(date_to_id[date.strip()])
                                    self.log_message(f"Added date {date.strip()} to deletion list", messages)
                                else:
                                    raise ValueError(f"No such date to delete: {date.strip()}")
                    else:
                        if part.replace('-', '').isdigit():
                            try:
                                index = int(part)
                                
                                if -len(date_to_id) <= index < len(date_to_id):
                                    dates_to_delete.append(date_to_id[list(date_to_id.keys())[index if index > 0 else index]])
                                    self.log_message(f"Added date {list(date_to_id.keys())[index if index > 0 else index]} to deletion list", messages)
                                else:
                                    raise ValueError(f"Index {index} out of range.")
                            except ValueError:
                                raise ValueError(f"Invalid index: {part.strip()}")
                        elif part.strip() in date_to_id:
                            dates_to_delete.append(date_to_id[part.strip()])
                            self.log_message(f"Added date {part.strip()} to deletion list", messages)
                        else:
                            raise ValueError(f"No such date to delete: {part.strip()}")
            else:
                if dates.replace('-', '').isdigit():    
                    try:
                        index = int(dates)
                        
                        if -len(date_to_id) <= index < len(date_to_id):
                            dates_to_delete.append(date_to_id[list(date_to_id.keys())[index if index > 0 else index]])
                            self.log_message(f"Added date {list(date_to_id.keys())[index if index > 0 else index]} to deletion list", messages)
                        else:
                            raise ValueError(f"Index {index} out of range.")
                    except ValueError:
                        raise ValueError(f"Invalid index: {dates.strip()}")
                elif dates.strip() in date_to_id:
                    dates_to_delete.append(date_to_id[dates.strip()])
                    self.log_message(f"Added date {dates.strip()} to deletion list", messages)
                else:
                    raise ValueError(f"No such date to delete: {dates.strip()}")
        
        dates_to_delete = list(OrderedDict.fromkeys(dates_to_delete))  # Remove duplicates while maintaining order
        
        remaining_dates = set(date_to_id.values()) - set(dates_to_delete)
        if len(remaining_dates) < 1:
            self.log_message("Deletion will result in only one date being left. It is thus not possible.", messages)
            dates_to_delete = dates_to_delete[:-1]
            
        threads = []
        message_queue = queue.Queue()
        for date_id in dates_to_delete:
            thread = threading.Thread(target=self.__delete_date, args=("https://xoyondo.com/pc/poll-change-poll", date_id, message_queue))
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join()
            
        while not message_queue.empty():
            messages.extend(message_queue.get())
        
        return messages
        
        # check if right format (date and list of dates)
        # -> integers are fine as well -> 1 means delete the first date - 2 -> first two dates (negative integers are also allowed -> -1 means delete the last date). 0 means all dates
        # delete every date given in the list of dates
        # if user wanted to delete every date give hint, that the last date could not be deleted due to xoyondo restrictions

    def __delete_date(self, delete_url, date_id, message_queue):
        messages = []
        
        form_data = {
            'ID': self.id,
            'product': 'd',
            'dateID': date_id,
            'operation': 'date_delete',
            'pass': self.password
        }
        delete_response = requests.post(delete_url, headers=self.headers, data=form_data)
        if delete_response.status_code == 200:
            self.log_message(f'Successfully deleted date with ID {date_id}', messages)
        else:
            self.log_message(f'Failed to delete date with ID {date_id}: HTTP {delete_response.status_code}', messages)
                
        message_queue.put(messages)

    def add_dates(self, dates):
        messages = []
        dates_to_add = []
        
        try:
            dates = str(dates)
        except ValueError:
            raise ValueError(f"Invalid input: {dates}")
        
        if "," in dates or ":" in dates:
            parts = dates.split(",")
            for part in parts:
                if ":" in part:
                    start, end = [x.strip() for x in part.split(":")]
                    dates, _messages = self.get_date_list(start, end)
                    messages.extend(_messages)
                    dates_to_add.extend(dates)
                    self.log_message(f"Added date list from {start} to {end} to add list", messages)
                else:
                    # check for valid date format
                    try:
                        datetime.strptime(part.strip(), '%Y/%m/%d')
                        dates_to_add.append(part.strip())
                        self.log_message(f"Added date {part.strip()} to add list", messages)
                    except ValueError:
                        raise ValueError(f"Invalid date: {part.strip()}")
        else:
            # check for valid date format
            try:
                datetime.strptime(dates.strip(), '%Y/%m/%d')
                dates_to_add.append(dates.strip())
                self.log_message(f"Added date {dates.strip()} to add list", messages)
            except ValueError:
                raise ValueError(f"Invalid date: {dates.strip()}")
            
        
            
        threads = []
        message_queue = queue.Queue()
        
        for date in dates_to_add:
            thread = threading.Thread(target=self.__add_date, args=("https://xoyondo.com/pc/poll-change-poll", date, message_queue))
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join()
            
        while not message_queue.empty():
            messages.extend(message_queue.get())

        return messages
        
        # check if right format (date and list of dates)
        # add every date given in the list of dates
        # if user wanted to add every date give hint, that the last date could not be added due to xoyondo restrictions
        
    def __add_date(self, add_url, date, message_queue):
        messages = []
        
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
            self.log_message(f'Successfully added date {date}', messages)
        else:
            self.log_message(f'Failed to add date {date}: HTTP {add_response.status_code}', messages)
                
        message_queue.put(messages)
        
    def get_dates(self):
        messages = []
        dates = []
        
        html, _messages = self.__get_webpage(self.url, self.headers)
        messages.extend(_messages)
        date_elements = html.find_all('i', {'class': 'fa fa-edit js-date-edit-cal text-warning pointer mx-1'})
        date_to_id = {el['data-date']: el['data-dateid'] for el in date_elements}
        
        dates = list(date_to_id.keys())
        self.log_message(f"Found dates: {dates}", messages)
        
        return dates, messages
        
        # get all dates
        
    def delete_users(self, users: str = None):
        messages = []
        user_ids_to_delete = []
    
        html, _messages = self.__get_webpage(self.url, self.headers)
        messages.extend(_messages)
        user_elements = html.find_all('tr', {'class': 'js-user-rows'})
        
        if users:  # If usernames are provided
            user_names_to_delete = [username.strip() for username in users.split(',')]  # Split the usernames string into a list

            # Find the corresponding user ids for the usernames provided
            for user_element in user_elements:
                user_name_element = user_element.find('td', {'class': 'table-user-cell'})
                if user_name_element:
                    user_elems = list(user_name_element.stripped_strings)
                    user_name = user_elems[-1]
                    if user_name in user_names_to_delete:
                        user_ids_to_delete.append(user_element['data-userid'])
                        self.log_message(f"Added user with name {user_name} to deletion list", messages)
        else:  # If no username is provided, delete all users
            user_ids_to_delete = [el['data-userid'] for el in user_elements]
            self.log_message(f"Added all users to deletion list", messages)
        
        if len(user_ids_to_delete) < 1:
            self.log_message("Deletion not possible as there is no user registered.", messages)
        
        # Delete each user
        threads = []
        message_queue = queue.Queue()
        for user_id in user_ids_to_delete:
            thread = threading.Thread(target=self.__delete_user, args=("https://xoyondo.com/pc/poll-change-poll-ajax", user_id, message_queue))
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join()
            
        while not message_queue.empty():
            messages.extend(message_queue.get())
        
        return messages
    
        # delete every user
        
    def __delete_user(self, delete_url, user_id, message_queue):
        messages = []
        
        form_data = {
            'u': user_id,
            'ID': self.id,
            'product': 'd',
            'operation': 'delete-user',
            'pass': self.password
        }
        delete_response = requests.post(delete_url, headers=self.headers, data=form_data)
        if delete_response.status_code == 200:
            self.log_message(f'Successfully deleted user with ID {user_id}', messages)
        else:
            self.log_message(f'Failed to delete user with ID {user_id}: HTTP {delete_response.status_code}', messages)
        
        message_queue.put(messages)
    
    def get_users(self):
        messages = []
        users = []
        
        html, _messages = self.__get_webpage(self.url, self.headers)
        messages.extend(_messages)
        user_elements = html.find_all('tr', {'class': 'js-user-rows'})
        
        for user_element in user_elements:
            user_name_element = user_element.find('td', {'class': 'table-user-cell'})
            if user_name_element:
                user_elems = list(user_name_element.stripped_strings)
                user_name = user_elems[-1]
                users.append(user_name)
                self.log_message(f"Found user with name {user_name}", messages)
        
        return users, messages
        
        # get all users
    
    def get_votes_by_index(self, index=None):
        messages = []
        date_results = {}
        filtered_results = {}
        
        html, _messages = self.__get_webpage(self.url, self.headers)
        messages.extend(_messages)
        user_rows = html.find_all('tr', class_='js-user-rows')
        
        for user_row in user_rows:
            vote_columns = user_row.find_all('td', {'class': ['table-danger-cell', 'table-success-cell', 'table-warning-cell', 'table-question-cell']})
            
            for idx, column in enumerate(vote_columns):
                if 'table-danger-cell' in column['class']:
                    vote = 'no'
                elif 'table-success-cell' in column['class']:
                    vote = 'yes'
                elif 'table-warning-cell' in column['class']:
                    vote = 'maybe'
                else: 
                    vote = 'question'
                    
                if idx not in date_results:
                    date_results[idx] = {'yes': 0, 'no': 0, 'maybe': 0, 'question': 0}
                    
                date_results[idx][vote] += 1
                
        if index is not None:
            index = str(index)
            indices = []
            parts = index.split(",")
            for part in parts:
                if ":" in part:
                    start, end = [x.strip() for x in part.split(":")]
                    
                    try:
                        start = int(start)
                    except ValueError:
                        raise ValueError(f"Invalid index: {start}")    
                    try:
                        end = int(end)
                    except ValueError:
                        raise ValueError(f"Invalid index: {end}")

                    if start < 0:
                        start = len(date_results) + start
                    if len(date_results) <= start or start < 0:
                        raise ValueError(f"Index {start} out of range.")
                    if end < 0:
                        end = len(date_results) + end
                    if len(date_results) <= end or end < 0:
                        raise ValueError(f"Index {end} out of range.")
                    
                    if start <= end:
                        indices.extend(range(start, end + 1))
                        self.log_message(f"Added indices from {start} to {end} to index list", messages)
                    else:
                        raise ValueError(f"Start index must be less than or equal to end index: {start}:{end}")
                            
                        
                        
                    

                else:
                    try:
                        indices.append(int(part))
                        self.log_message(f"A: Added index {part} to index list", messages)
                    except ValueError:
                        raise ValueError(f"Invalid index: {part}")
            indices = [(i + len(date_results)) if i < 0 else i for i in indices]
            filtered_results = {idx: result for idx, result in date_results.items() if idx in indices}

        else:
            filtered_results = date_results
            
        self.log_message(f"Found votes: {filtered_results}", messages)
            
        
        formatted_results = []
        for idx, counts in filtered_results.items():
            formatted_results.append({
                'date_index': idx,
                'yes_count': counts['yes'],
                'no_count': counts['no'],
                'maybe_count': counts['maybe'],
                'question_count': counts['question']
            })
            
        return formatted_results, messages
        
        # if specific date or dates or range of dates given, give the count of yes, no and maybe of all users for this date
    
    def get_votes_by_date(self, dates = None):
        messages = []
        votes = []
        
        if dates:
            indices, _messages = self.get_index_for_date(dates)
            messages.extend(_messages)
            votes, _messages = self.get_votes_by_index(",".join(str(index) for index in indices))
            messages.extend(_messages)
            
            dates = self.get_date_list(dates)
        else:
            dates = []
            
            votes, _messages = self.get_votes_by_index()
            messages.extend(_messages)
            for vote in votes:
                date, _message = self.get_date_for_index(vote['date_index'])
                dates.append(date[0])
                messages.extend(_message)
                
        formatted_results = []

        for idx, vote in enumerate(votes):
            # Replace the date_index with the corresponding date
            formatted_results.append({
                'date': dates[idx],
                'yes_count': vote['yes_count'],
                'no_count': vote['no_count'],
                'maybe_count': vote['maybe_count'],
                'question_count': vote['question_count']
            })
            
        return formatted_results, messages
    
    def get_user_votes(self, user:str = None):
        messages = []
        user_votes = {}
        
        html, _messages = self.__get_webpage(self.url, self.headers)
        messages.extend(_messages)
        user_rows = html.find_all('tr', class_='js-user-rows')
        
        for user_row in user_rows:
            user_name_element = user_row.find('td', {'class': 'table-user-cell'})
            if user_name_element:
                user_elems = list(user_name_element.stripped_strings)
                user_name = user_elems[-1]
                
                if user is not None and user_name != user:
                    continue
                
                vote_columns = user_row.find_all('td', {'class': ['table-danger-cell', 'table-success-cell', 'table-warning-cell', 'table-question-cell']})
                
                for idx, column in enumerate(vote_columns):
                    if 'table-danger-cell' in column['class']:
                        vote = 'no'
                    elif 'table-success-cell' in column['class']:
                        vote = 'yes'
                    elif 'table-warning-cell' in column['class']:
                        vote = 'maybe'
                    else: 
                        vote = 'question'
                        
                    if user_name not in user_votes:
                        user_votes[user_name] = {}
                        
                    user_votes[user_name][idx] = vote
                
        if len(user_votes) < 1:
            self.log_message(f"No user found for given name {user}", messages)
            
        self.log_message(f"Found votes: {user_votes}", messages)
        
        return user_votes, messages
        
        # if specific user or users or range of users given, give the vote of this user for all dates
    
    def get_date_for_index(self, index:str = None):
        messages = []
        dates_for_indices = []
        html, _messages = self.__get_webpage(self.url, self.headers)
        messages.extend(_messages)
        
        date_elements = html.find_all('i', {'class': 'fa fa-edit js-date-edit-cal text-warning pointer mx-1'})
        date_to_id = {el['data-date']: el['data-dateid'] for el in date_elements}
        
        if index is not None:
            indices = []
            index = str(index)
            parts = index.split(",")
            for part in parts:
                if ":" in part:
                    start, end = [x.strip() for x in part.split(":")]
                    
                    try:
                        start = int(start)
                    except ValueError:
                        raise ValueError(f"Invalid index: {start}")
                    
                    try:
                        end = int(end)
                    except ValueError:
                        raise ValueError(f"Invalid index: {end}")    
                    
                    if start < 0:
                        start = len(date_to_id) + start
                    if len(date_to_id) <= start or start < 0:
                        raise ValueError(f"Index {start} out of range.")
                    if end < 0:
                        end = len(date_to_id) + end
                    if len(date_to_id) <= end or end < 0:
                        raise ValueError(f"Index {end} out of range.")
                    
                    if start <= end:
                        indices.extend(range(start, end + 1))
                        self.log_message(f"Added indices from {start} to {end} to index list", messages)
                    else:
                        raise ValueError(f"Start index must be less than or equal to end index. Given: {start}:{end}")
                    
                else:
                    try:
                        idx = int(part)
                        if idx < 0:
                            idx = len(date_to_id) + idx
                        
                        if 0 <= idx < len(date_to_id):
                            indices.append(idx)
                            self.log_message(f"B: Added index {idx} to index list", messages)
                        else:
                            raise ValueError(f"Index {idx} out of range.")
                    
                    except ValueError:
                        raise ValueError(f"Invalid index: {part}")
            
            dates_for_indices = [list(date_to_id.keys())[i] for i in indices]
        else:
            dates_for_indices = list(date_to_id.keys())
        
        return dates_for_indices, messages
    
    def get_index_for_date(self, dates:str):
        messages = []
        indices_to_return = []
        
        html, _messages = self.__get_webpage(self.url, self.headers)
        messages.extend(_messages)
        date_elements = html.find_all('i', {'class': 'fa fa-edit js-date-edit-cal text-warning pointer mx-1'})
        date_to_id = {el['data-date']: el['data-dateid'] for el in date_elements}

        dates = str(dates)
        if "," in dates or ":" in dates:
            parts = dates.split(",")
            for part in parts:
                if ":" in part:
                    start, end = [x.strip() for x in part.split(":")]
                    dates, _messages = self.get_date_list(start, end)
                    messages.extend(_messages)
                    valid_dates = [date for date in dates if date in date_to_id]
                    indices_to_return.extend(list(date_to_id.keys()).index(date) for date in valid_dates)
                    self.log_message(f"Added indices from {start} to {end} to index list", messages)
                else:
                    if part.strip() in date_to_id:
                        indices_to_return.append(list(date_to_id.keys()).index(part.strip()))
                        self.log_message(f"C: Added index {part.strip()} to index list", messages)
                    else:
                        raise ValueError(f"Invalid date: {part.strip()}")
        else:
            if dates.strip() in date_to_id:
                indices_to_return.append(list(date_to_id.keys()).index(dates.strip()))
                self.log_message(f"C: Added index {dates.strip()} to index list", messages)
            else:
                raise ValueError(f"Invalid date: {dates.strip()}")
        
        # Remove duplicates while maintaining order
        indices_to_return = list(dict.fromkeys(indices_to_return))
        
        return indices_to_return, messages