import requests
import json
import unittest

def get_nba_data(id): 
    base_url = "https://www.balldontlie.io/api/v1/teams/{}"
    request_url = base_url.format(id)
    r = requests.get(request_url)
    data = r.text
    dict_list = json.loads(data)
    return dict_list

def get_pop_data():
    base_url = "https://api.census.gov/data/2019/pep/population"
    request_url = base_url.format()
    r = requests.get(request_url)
    data = r.text
    dict_list = json.loads(data)
    return dict_list


def main():
    test = get_nba_data(14)
    print(test)

if __name__ == "__main__":
    main()