import sqlite3
import os
import matplotlib.pyplot as plt
import numpy as np

# Don't change anything in this function
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

# Create a function called most_pop_movie
# This function counts the number of votes each movie has and returns the count and movie title as a list of tuples
# Hint: Use COUNT(*) 
# Hint2: this function requires a JOIN
# It should return: [(2, 'Avatar'), (2, 'Jurassic Park'), (1, 'Star Wars'), (3, 'The Fast and the Furious: Tokyo Drift'), (4, 'Titanic')]

def most_pop_movie(cur, conn): 
    cur.execute("""
    SELECT COUNT(*), title
    FROM Movies
    JOIN People
    ON Movies.id = People.fave_movie_id
    GROUP BY Movies.title
    """
    )
    data = cur.fetchall()
    #print(data)
    return data


# Create a bar plot vizualization using matplotlib with the data returned from most_pop_movie
def viz_one(data):
    names = []
    votes = []
    for i in data:
        names.append(i[1])
        votes.append(i[0])
    plt.bar(names, votes, align='center', alpha=0.5)
    plt.xticks(names, rotation = 45)
    plt.ylabel('number_of_votes')
    plt.xlabel('name')
    plt.title('Number of Votes for Movies')
    plt.show()

# Create a pie chart vizualization using matplotlib with the data returned from most_pop_movie
def viz_two(data):
    names = []
    votes = []
    for i in data:
        names.append(i[1])
        votes.append(i[0])
    plt.pie(votes, labels = names)
    plt.axis('equal')
    plt.title('Number of Votes for Movies')
    plt.show()

# # Uncomment this to make sure your function works
cur, conn = setUpDatabase('Movies.db')
data = most_pop_movie(cur, conn)
# # uncomment these one at a time to see the visualizations
viz_one(data)
viz_two(data)
