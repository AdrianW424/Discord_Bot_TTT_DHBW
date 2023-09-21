import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from collections import OrderedDict

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

# Step 1: Build a mapping from date strings to date IDs
date_elements = soup.find_all('i', {'class': 'fa fa-edit js-date-edit-cal text-warning pointer mx-1'})
date_to_id = {el['data-date']: el['data-dateid'] for el in date_elements}

# Step 2: Get user input for dates to delete
input_dates = input("Enter dates to delete: ")

# Step 3: Find the corresponding date IDs
dates_to_delete = []

if len(date_to_id) <= 1:
    print("Deletion not possible as there is only one date left.")
    exit()

elif input_dates == '0':
    dates_to_delete = list(date_to_id.values())
    print("Deletion not possible as there will be no date left.")
elif "," in input_dates or ":" in input_dates:
    parts = input_dates.split(",")
    for part in parts:
        if ":" in part:
            start, end = [x.strip() for x in part.split(":")]
            
            # Check if the range is valid
            if start.isdigit() and end.isdigit() and int(start) <= int(end):
                start, end = int(start) - 1, int(end) - 1
                dates_to_delete.extend(date_to_id[date] for i, date in enumerate(date_to_id.keys()) if start <= i <= end)
            elif start.replace('-', '').isdigit() and end.replace('-', '').isdigit() and int(start) <= int(end):
                start, end = int(start), int(end)
                dates_to_delete.extend(date_to_id[date] for i, date in enumerate(date_to_id.keys()) if len(date_to_id) + start <= i <= len(date_to_id) + end)
            else:
                dates_to_delete.extend(date_id for date in get_date_range(start, end) if date in date_to_id for date_id in [date_to_id[date]])
        else:
            if part.replace('-', '').isdigit():
                index = int(part)
                if -len(date_to_id) <= index - 1 < len(date_to_id):
                    dates_to_delete.append(date_to_id[list(date_to_id.keys())[index - 1 if index > 0 else index]])
                else:
                    print(f"Index {index} out of range.")
            elif part.strip() in date_to_id:
                dates_to_delete.append(date_to_id[part.strip()])
            else:
                print(f"Invalid date: {part.strip()}")
else:
    if input_dates.replace('-', '').isdigit():
        index = int(input_dates)
        if -len(date_to_id) <= index - 1 < len(date_to_id):
            dates_to_delete.append(date_to_id[list(date_to_id.keys())[index - 1 if index > 0 else index]])
        else:
            print(f"Index {index} out of range.")
    elif input_dates.strip() in date_to_id:
        dates_to_delete.append(date_to_id[input_dates.strip()])
    else:
        print(f"Invalid date: {input_dates.strip()}")

dates_to_delete = list(OrderedDict.fromkeys(dates_to_delete))  # Remove duplicates while maintaining order
print(date_to_id)
print(dates_to_delete)

remaining_dates = set(date_to_id.values()) - set(dates_to_delete)
if len(remaining_dates) < 1:
    print("Deletion will result in only one date being left. It is thus not possible.")
    dates_to_delete = dates_to_delete[:-1]


# Step 4: Delete the dates using the extracted date IDs
delete_url = "https://xoyondo.com/pc/poll-change-poll"
for date_id in dates_to_delete:
    form_data = {
        'ID': 'QaVa6chaXJIgsnh',
        'product': 'd',
        'dateID': date_id,
        'operation': 'date_delete',
        'pass': 'hnLajFxaIS'
    }
    delete_response = requests.post(delete_url, headers=headers, data=form_data)
    if delete_response.status_code == 200:
        print(f'Successfully deleted date with ID {date_id}')
    else:
        print(f'Failed to delete date with ID {date_id}: HTTP {delete_response.status_code}')
