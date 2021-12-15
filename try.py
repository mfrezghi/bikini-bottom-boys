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
    base_url = "https://www.balldontlie.io/api/v1/games?seasons[]=2018&per_page=25"
    # You must limit how much data you store from an API into the database each time you 
    # execute your code to 25 or fewer items (60 points). The data must be stored in a SQLite 
    # database. This means that you must run the code that stores the data multiple times to 
    # gather at least 100 items total without duplicating existing data or changing it. 
    


