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


def get_nba_data(page): 

    dict_data = {}
    dict_list = []
    base_url = "https://www.balldontlie.io/api/v1/games?seasons[]=2018&per_page=25&page={}"

    request_url = base_url.format(page)
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
    for i in data:
        if i[0] not in team_dict:
            team_dict[i[0]] = i[1]
        else:
            team_dict[i[0]] += i[1]
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
    
    #create a second table in the team_database.db file called Populations to store the population data of each team
    conn = sqlite3.connect('team_database.db')
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS Populations")
    c.execute("CREATE TABLE IF NOT EXISTS Populations (team text, population integer)")
    conn.commit()
    for key in team_dict:
        c.execute("INSERT INTO Populations VALUES (?, ?)", (key, team_dict[key]))
    conn.commit()
    conn.close()
    

    return team_dict

#barchart of the population size of each team and the number of points they have scored
def barchart_population_size(pop_data):
    points = read_data_from_db()
    sorted_points = dict(sorted(points.items(), key=lambda item: item[0]))
    points_list = []

    for key in sorted_points:
        points_list.append(sorted_points[key] * 1000)
    points_mean = sum(points_list)/len(points_list)

    # make the first bar blue and the second one yellow
    plt.bar(pop_data.keys(), pop_data.values(), color='blue')
    plt.bar(pop_data.keys(), points_list, color='yellow')
    # make the bars side by side
    plt.legend(['Population', 'Points'])
    

    plt.xticks(rotation=90)
    plt.xlabel("NBA Teams")
    # plt.yticks(range(1000000, 20000000, 1000000))

    plt.ylabel("Population Size (Millions)")
    plt.title("Population Size of NBA Teams compared to NBA Team Points")
    plt.show()

#scatter plot of the population size of each team and the number of points they have scored
def scatter_points(pop_data):
    points = read_data_from_db()
    sorted_points = dict(sorted(points.items(), key=lambda item: item[0]))
    points_list = []

    for key in sorted_points:
        points_list.append(sorted_points[key])

    plt.scatter(pop_data.values(), points_list, color='blue')
    plt.xlabel("Population Size (Millions)")
    plt.ylabel("NBA Team Points")
    plt.title("Population Size of NBA Teams compared to NBA Team Points")
    plt.show()

#pie chart of what percentage of the points are scored by each team
def pie_chart(pop_data):
    points = read_data_from_db()
    sorted_points = dict(sorted(points.items(), key=lambda item: item[0]))
    points_list = []

    for key in sorted_points:
        points_list.append(sorted_points[key])

    plt.pie(points_list, labels=pop_data.keys(), autopct='%1.1f%%')
    plt.title("NBA Team Points make up")
    plt.show()

def line_graph(pop_data):
    points = read_data_from_db()
    sorted_points = dict(sorted(points.items(), key=lambda item: item[0]))
    points_list = []

    for key in sorted_points:
        points_list.append(sorted_points[key])

    plt.plot(pop_data.values(), points_list, color='blue')
    plt.xlabel("Population Size (Millions)")
    plt.ylabel("NBA Team Points")
    plt.title("Population Size of NBA Teams compared to NBA Team Points")
    plt.show()

# find the mean of the points scored by each team and calculate how far from the mean each team is and store that data in a dictionary
def find_mean_difference(pop_data):
    points = read_data_from_db()
    sorted_points = dict(sorted(points.items(), key=lambda item: item[0]))
    points_list = []

    for key in sorted_points:
        points_list.append(sorted_points[key])

    points_mean = sum(points_list)/len(points_list)
    mean_difference = {}
    for key in pop_data:
        mean_difference[key] = abs(points_mean - pop_data[key])

    return mean_difference
# create a barchart for the mean differences between the points and the population size
def barchart_mean_difference(mean_difference):
    sorted_mean_difference = dict(sorted(mean_difference.items(), key=lambda item: item[1]))
    mean_difference_list = []

    for key in sorted_mean_difference:
        mean_difference_list.append(sorted_mean_difference[key])

    plt.bar(mean_difference.keys(), mean_difference.values(), color='blue')
    plt.xticks(rotation=90)
    plt.xlabel("NBA Teams")
    plt.ylabel("Mean Difference")
    plt.title("Mean Difference between NBA Team Points and Population Size")
    plt.show()

def main():
    # db = get_nba_data(8)
    # once you get up to 4 runs, calculate team totals (usually needs more to render graphs)
    test = read_data_from_db()
    # get population sizes from web
    pops = get_pop_data()
    sorted_pops = dict(sorted(pops.items(), key=lambda item: item[0]))

    # barchart_population_size(sorted_pops)
    # scatter_points(sorted_pops)
    # pie_chart(sorted_pops)
    # line_graph(sorted_pops)
    mean = find_mean_difference(get_pop_data())
    barchart_mean_difference(mean)
if __name__ == "__main__":
    main()