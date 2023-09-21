import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

url = "https://xoyondo.com/dp/QaVa6chaXJIgsnh/hnLajFxaIS"
headers = {
    "User-Agent": "Mozilla/5.0"
}
response = requests.get(url, headers=headers)
response.raise_for_status()
soup = BeautifulSoup(response.content, 'html.parser')

def get_date_range(start_str, end_str):
    """Get a list of date strings between start_str and end_str, inclusive."""
    start_date = datetime.strptime(start_str, '%Y/%m/%d')
    end_date = datetime.strptime(end_str, '%Y/%m/%d')
    delta = end_date - start_date
    return [(start_date + timedelta(days=i)).strftime('%Y/%m/%d') for i in range(delta.days + 1)]

# Extract available date strings and their IDs
date_elements = soup.find_all('i', {'class': 'fa fa-edit js-date-edit-cal text-warning pointer mx-1'})
date_to_id = {el['data-date']: el['data-dateid'] for el in date_elements}

# Get user input for dates to add
input_dates = input("Enter dates to add: ")
dates_to_add = []

if "," in input_dates or ":" in input_dates:
    parts = input_dates.split(",")
    for part in parts:
        if ":" in part:
            start, end = [x.strip() for x in part.split(":")]
            dates_to_add.extend(get_date_range(start, end))
        else:
            dates_to_add.append(part.strip())
else:
    dates_to_add.append(input_dates.strip())

# Add the dates using the extracted date IDs
add_url = "https://xoyondo.com/pc/poll-change-poll"
for date in dates_to_add:
    form_data = {
        'newdates': date,
        'ID': 'QaVa6chaXJIgsnh',
        'product': 'd',
        'operation': 'date_add_cal',  # change operation to date_add
        'pass': 'hnLajFxaIS',
        'times_selected': 0
    }
    add_response = requests.post(add_url, headers=headers, data=form_data)
    if add_response.status_code == 200:
        print(f'Successfully added date {date}')
    else:
        print(f'Failed to add date {date}: HTTP {add_response.status_code}')
