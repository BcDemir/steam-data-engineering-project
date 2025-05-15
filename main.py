import os
import json
import requests
from datetime import datetime


url = "http://api.steampowered.com/ISteamApps/GetAppList/v0002/?format=json"
response = requests.get(url)


save_state_env = os.getenv("SAVE_STATE")
if save_state_env:
    save_state = save_state_env
else:
    save_state = 'w'


while(True):
    temp_list = ['w','x']
    if save_state not in temp_list:
        print('The parameter set to the default w value')
        save_state = 'w'
        break
    else:
        break


if response.status_code == 200:
    try:
        with open('/json/applist.json', f'{save_state}') as file:
            data = response.json()
            json.dump(data, file, indent=4, ensure_ascii=True)
    except Exception as e:
        print(f"Error writing file: {str(e)}")
else:
    print(f"Failed to retrieve data: {response.status_code}")
    print(f"Response content: {response.text}")    
    
    
# Load the data from the file here
f = open('/json/applist.json', 'r')
data = json.load(f) 

# Get all appids in a new json    
# Extract nested data
id_list_data = {
    'appid': [app['appid'] for app in data['applist']['apps'] if app['name'] != '']
}

empty_data = {
    'appid': [app['appid'] for app in data['applist']['apps'] if app['name'] == '']
}

id_list_data = id_list_data['appid']

# Use a set to remove duplicates
id_list_data = set(id_list_data)
id_list_data = list(id_list_data)

# sort the new data in ascending order
id_list_data.sort()


# Save with proper formatting
try:
    with open('/json/appids.json', f'{save_state}') as file:
        json.dump(id_list_data, file, indent=4, ensure_ascii=False)
except FileExistsError:
    print("File already exists!")
    
    
def clean_data(data, i):
    """
    Cleans and structures the raw JSON data from the Steam app details API.

    Extracts specific fields from the API response for a given app ID,
    handles missing data by assigning 'NA', and formats some values
    (e.g., price).

    Args:
        data (dict): The raw JSON response from the Steam API for one or more apps,
                     where app data is nested under the app ID as a key.
        app_id (str): The string representation of the Steam AppID for which
                      to clean data (used as a key in the `data` dictionary).

    Returns:
        dict: A dictionary containing structured information for the app,
              including 'steam_appid', 'type', 'name', 'is_free', 'currency',
              'final_price', 'categories', 'genres', 'recommendations',
              'release_date', and 'coming_soon'.
    """
    def_value = 'NA'
    f_data = data[f'{i}']['data']
    
    steam_appid = f_data.get('steam_appid', 'NA')
    type = f_data.get('type', 'NA')
    name = f_data.get('name', 'NA')
    is_free = f_data.get('is_free', 'NA')
    # price_overview = data.get('price_overview', 'NA')
    # print('debug 4')
    try:        
        currency = f_data.get('price_overview', 'NA').get('currency', 'NA')
    except:
        currency = def_value
        
    try:        
        final_price = f_data.get('price_overview', 'NA').get('final', 'NA')
        final_price = final_price / 100
    except:
        final_price = def_value
        
    try:        
        rec_total = f_data.get('recommendations', 'NA').get('total', def_value)
    except:
        rec_total = def_value
        
    # release_date = data.get('release_date', 'NA')
    try:        
        coming_soon = f_data.get('release_date', def_value).get('coming_soon', 'NA')
    except:
        coming_soon = def_value
    try:
        date_published = f_data.get('release_date').get('date', 'NA')
    except:
        date_published = def_value
    
    structured_data = {
        'steam_appid': steam_appid,
        'type': type,
        'name': name,
        'is_free': is_free,
        'currency': currency,
        'final_price': final_price,
        'categories': f_data.get('categories', 'NA'),
        'genres': f_data.get('genres', 'NA'),
        'recommendations': rec_total,
        'release_date': date_published,
        'coming_soon': coming_soon
    }
    
    return structured_data


# Initiate lists here
data_append = []
error_logs = []


# File path to save gathered data
file_path = '/json/raw_data.json'


def load_previous_raw_data():
    """
    Loads previously gathered and structured app data from '/json/raw_data.json'.

    This function attempts to open and read 'raw_data.json'. If successful,
    it extends the global `data_append` list with the loaded data. This allows
    the script to resume fetching and append new data to existing data.
    If the file doesn't exist or an error occurs during loading, it passes silently.
    """
    try:
        f = open('/json/raw_data.json', 'r')
        raw_data = json.load(f)
        
        for i in raw_data:
            data_append.append(raw_data[i])
        
    except:
        pass
    

def get_data(list: list, start_close, end_close, file=file_path):
    """
    Fetches detailed data for a slice of app IDs from the Steam API,
    cleans it, and saves it along with any errors and progress logs.

    It first loads any previously fetched data using `load_previous_raw_data`.
    Then, it iterates through the specified slice of `app_ids_list`,
    makes API requests, cleans the response using `clean_data`, and appends
    to a global list. Finally, it writes the accumulated data, error logs,
    and interval logs to their respective files.

    Args:
        app_ids_list (list): The complete list of Steam AppIDs (integers or strings)
                             from which to fetch data.
        start_index (int): The starting index (inclusive, typically negative to count
                           from the end) of the slice in `app_ids_list` to process.
        end_index (int): The ending index (exclusive, typically negative) of the slice
                         in `app_ids_list` to process.
        output_file (str, optional): The path to the file where the structured
                                     app data will be saved.
                                     Defaults to the global `file_path`.
    """   
    # Start by loading the existing data
    load_previous_raw_data()
    
    
    for i in list[start_close:end_close]:
        try:
            url = f'https://store.steampowered.com/api/appdetails?appids={i}'
            response = requests.get(url)
            print(f'Response\'s status code: {response.status_code} and retrieving item no: {i}')
            
            data = response.json()
            
            new_data = clean_data(data, i)
            
            data_append.append(new_data)
        except Exception as e:
            error_logs.append({'id':i, 'error': str(e)})
            print(e)
    
    
    # Write the filtered data on a json file
    with open(file, 'w') as file, open('/json/errorLogs.json', 'w') as error_file, open('/json/intervalLogs.txt','a') as interval:
        json.dump(data_append, file, indent=4)
        json.dump(error_logs, error_file, indent=4)
        interval.write(f'\nData requested between last {end_close} and {start_close}!\nThe data until {start_close} is gathered!\n')
        
        
    print(f'Data gathered until {start_close} completed and saved in {file}!')
    
    
if __name__ == '__main__':
    last_no = os.getenv("LAST_NO")
    rangeLast = os.getenv("RANGE_LAST")
    intervals = os.getenv("INTERVALS")
    
    try:
        last_no = int(last_no)
        rangeLast = int(rangeLast)
        intervals = int(intervals)
    except (TypeError, ValueError):
        last_no = -1
        rangeLast = -1000
        intervals = 100
        
    # Ensure intervals is positive
    if intervals <= 0:
        print("Intervals must be a positive number. Defaulting to 100.")
        intervals = 100

    while last_no > rangeLast:
        start_time = datetime.now()
        
        print(f'Fetching data between {last_no-intervals} and {last_no}!')
        get_data(id_list_data, last_no-intervals, last_no)
        last_no -= intervals
        
        # Calculate elapsed time for this batch
        elapsed_time = (datetime.now() - start_time).total_seconds()
        print(f"The batch took {elapsed_time:.2f} seconds!")