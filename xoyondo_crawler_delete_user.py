import requests
from bs4 import BeautifulSoup

# Fetch the page
url = "https://xoyondo.com/dp/QaVa6chaXJIgsnh/hnLajFxaIS"
headers = {
    "User-Agent": "Mozilla/5.0"
}
response = requests.get(url, headers=headers)
response.raise_for_status()
soup = BeautifulSoup(response.content, 'html.parser')

# Extract user IDs
user_elements = soup.find_all('tr', {'class': 'js-user-rows'})
user_ids_to_delete = [el['data-userid'] for el in user_elements]

# Delete each user
delete_url = "https://xoyondo.com/pc/poll-change-poll-ajax"
for user_id in user_ids_to_delete:
    form_data = {
        'u': user_id,
        'ID': 'QaVa6chaXJIgsnh',
        'product': 'd',
        'operation': 'delete-user',
        'pass': 'hnLajFxaIS'
        }
    delete_response = requests.post(delete_url, headers=headers, data=form_data)
    if delete_response.status_code == 200:
        print(f'Successfully deleted user with ID {user_id}')
    else:
        print(f'Failed to delete user with ID {user_id}: HTTP {delete_response.status_code}')
