from os import read
import requests
import json
import sqlite3
from bs4 import BeautifulSoup
import regex as re
import matplotlib.pyplot as plt
from requests.api import get
import numpy as np
import altair as alt
import pandas as pd


def get_nba_data(): 

    dict_data = {}
    dict_list = []
    base_url = "https://www.balldontlie.io/api/v1/games?seasons[]=2018&per_page=100&page={}"

    for i in range(1,15):
        request_url = base_url.format(i)
        r = requests.get(request_url)
        data = r.text
        dict_data = json.loads(data)
        dict_list.append(dict_data)

    conn = sqlite3.connect('team_database.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS team_data (home_team text, home_team_score integer)")
    conn.commit()

    for i in dict_list:
        for j in i['data']:
            c.execute("INSERT INTO team_data VALUES (?, ?)", (j['home_team']['full_name'], j['home_team_score']))
    conn.commit()
    conn.close()
    
    return dict_list

def read_data_from_db():
    conn = sqlite3.connect('team_database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM team_data")
    data = c.fetchall()
    conn.close()
    team_dict = {}
    conn = sqlite3.connect('team_points.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS team_points (home_team text, home_team_points integer)")
    conn.commit()
    for i in data:
        if i[0] not in team_dict:
            team_dict[i[0]] = i[1]
        else:
            team_dict[i[0]] += i[1]
    for item in team_dict:
        # transfer the items in the dictionary to the database
        c.execute("INSERT INTO team_points (home_team,home_team_points) VALUES ('{}', '{}')".format(item, team_dict[item]))
        conn.commit()
    conn.close()
    return team_dict

def get_pop_data():
    # create a beautiful soup object to parse the data on the page https://hoop-social.com/nba-team-market-size-rankings/
    url = 'https://hoop-social.com/nba-team-market-size-rankings/'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    # find the table on the page
    tables = soup.find_all('table', {'class': 'teamtable'})
    # find the rows in each table
    team_list = []
    team_dict = {}
    for table in tables:
        rows = table.find_all('td')
        for row in rows:
            if rows.index(row) % 3 == 0:
                if '/' in row.text:
                    row_split = row.text.split('/')
                    switch1 = re.sub('([0-9]|[0-9][0-9])\.\s', '', row_split[0].strip())
                    switch2 = re.sub('([0-9]|[0-9][0-9])\.\s', '', row_split[1].strip())
                    team_list.append(switch1)
                    team_list.append(switch2)
                else:
                    switch = re.sub('([0-9]|[0-9][0-9])\.\s', '', row.contents[0].strip())
                    team_list.append(switch)

            else:
                team_list.append(row.contents[0])
    
    for i in range(0, 1):
        team_dict[team_list[i]] = team_list[i+3]
        team_dict[team_list[i+1]] = team_list[i+3]
        team_dict[team_list[i+4]] = team_list[i+7]
        team_dict[team_list[i+5]] = team_list[i+7]

    # iterate through the list and add the data to the dictionary
    for i in range(8, len(team_list), 3):
        team_dict[team_list[i]] = team_list[i+2]
    # write a regular expression to only get the team name without any numbers
    # write a regular expression to only get the team name without any numbers
    for key in team_dict:
        team_dict[key] = int(team_dict[key].replace(',', ''))
        # if there is a slash in the team name, split the team name at the slash and add the second half to the dictionary with the same key value
    
    return team_dict

def barchart_population_size(pop_data):
    points = read_data_from_db()
    sorted_points = dict(sorted(points.items(), key=lambda item: item[0]))
    points_list = []

    for key in sorted_points:
        points_list.append(sorted_points[key])

    # make the first bar blue and the second one yellow
    plt.bar(pop_data.keys(), pop_data.values(), color='blue')
    plt.bar(pop_data.keys(), points_list, color='yellow')


    plt.xticks(rotation=90)
    plt.xlabel("NBA Teams")
    # plt.yticks(range(1000000, 20000000, 1000000))

    plt.ylabel("Population Size (Millions)")
    plt.title("Population Size of NBA Teams compared to NBA Team Points")
    plt.show()

# use seaborn library to create a visualization of the population size of the NBA teams compared to the number of points they have scored
def barchart_points(pop_data):
    points = read_data_from_db()
    sorted_points = dict(sorted(points.items(), key=lambda item: item[0]))
    points_list = []

    for key in sorted_points:
        points_list.append(sorted_points[key])

    chart = alt.Chart(points_list).mark_bar().encode(
        x=alt.X('home_team:O', axis=alt.Axis(title='NBA Teams')),
        y=alt.Y('home_team_points:Q', axis=alt.Axis(title='Points Scored')),
        color=alt.Color('home_team:N', legend=alt.Legend(title='NBA Teams'))
    ).properties(
        width=500,
        height=500
    ).interactive()

    chart.show()

def main():
    # test = read_data_from_db()
    pops = get_pop_data()
    sorted_pops = dict(sorted(pops.items(), key=lambda item: item[0]))
    
    #barchart_population_size(sorted_pops)
    barchart_points(sorted_pops)

if __name__ == "__main__":
    main()