# importing everything necessary

import requests
import time
import json
import pandas as pd
from hashlib import md5
from glom import glom
import csv
import re
import sys
import fuzzywuzzy
from fuzzywuzzy import process


def get_characters():
    
    """
    Function to Request the Marvel API to get Characters and store it in a characters.csv file
    
    variables:
        limit: Marvel API does not return more than 100 Characters in one request. So this is set to 100
        offset: This will help us keep track of the index with which we make next request to fetch data from API
        count: This is the total number of characters returned by the API
    """
    
    PRIVATE_KEY = 'Enter your key here'
    PUBLIC_KEY = 'Enter your key here'
    limit = 100
    offset = 0
    count = 0
    
    
    # setting up the needed values required to make the get request
    t = int(time.time())
    input_string = str(t) + PRIVATE_KEY + PUBLIC_KEY
    hash = md5(input_string.encode("utf-8")).hexdigest()
    
    # Since the API only returns 100 values at max in a single reuest
    # We will keep recieving data until we recieve all of it
    # We accomplish this by using a while loop to kee making new requests until we reach the very end
    print("Getting data from API...")
    while True:
        response = requests.get('https://gateway.marvel.com:443/v1/public/characters?limit={}&offset={}&ts={}&apikey={}&hash={}'.format(limit,offset,t,PUBLIC_KEY,hash))        
        
        body = response.json()['data']  # keeping only the reuired part from the response
        
        df = pd.DataFrame.from_dict(body['results'])  # only results column is required for our mission
        
        columns = set(df.columns)
        col_to_keep = set(['id', 'name', 'comics'])
        col_to_remove = columns - col_to_keep
        df = df.drop(list(col_to_remove), axis =1)
        
        # retrieving the value of 'count' from the nested dictionary
        # 'count' is the number of 'comics' a character has featured in
        df['comics'] = df['comics'].apply(lambda count: glom(count, 'available'))
        
        
        # let's write down all the data in our file
        df.to_csv('characters.csv',index=False, mode='a')
        
        # setting offset to retrieve from this point from the API
        offset = offset + limit
        
        # Condition to break the loop in case we reach the end
        if body['count'] < limit:
            break  
            
            
def clean_csv():
    """
    Function to clean up the characters.csv file 
    This function removes rows which contain redundant headers (column names: 'id', 'name', 'count')
    which get inserted in our csv file after every request. 
    """
    print("Cleaning the file...")
    df = pd.read_csv('characters.csv')
    df = df[df['id']!='id']
    
    df.to_csv('characters.csv', index=False)
    
    
def print_comic_count(names):
    
    """
    Function to search character by name and print number of comics the character has featured in
    """
    for name in names:
        # cleaing the name for any extra white space, special characters and capitalizing words (data is case sensitive)
        name = re.sub('[\[\]\'\"$%^&*@!;?<>,\+-=~`:]', "", name)
        name = " ".join(name.split()).title()
        df = pd.read_csv('characters3.csv')
    
        if name in set(df['name']):
            count = int(df['comics'].loc[df['name']==name])
            print("{} has featured in {} comics".format(name,count))
        else:
            best_match = list(process.extract(name, df['name'], limit=3))
            print("{} not found. \nTry the following top 3 matches found.".format(name))
            print(list(zip(*best_match))[0])
 

def main():
    get_characters()
    clean_csv()
    print("Which characters would you like to search?\n")
    x = list(map(str, input("You can enter multiple character names at once (comma seperated):\n").split(',')))
    print_comic_count(x)
    
if __name__ == '__main__':
    main()