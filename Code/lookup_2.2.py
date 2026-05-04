import argparse
import pandas as pd
from flask_jsonpify import jsonify
import json
from tabulate import tabulate
import requests

def func() :
    print()
    print('#######################################################################################################################################################################################################################################################################################################################')
    print()


base_url = 'http://127.0.0.1:5000'

parser = argparse.ArgumentParser()

parser.add_argument("--name", type = str, help = "Enter a Player Name")
parser.add_argument("--club", type = str, help = "Enter a Club Name")

args = parser.parse_args()

name_file, club_file = '', ''

if args.name:
    print("PLAYER")
    url = base_url + '/players/' + args.name
    response = requests.get(url)
    data = response.json()

    name_file += args.name+ '.csv'

    # Option 1: Using Tabulate
    print(tabulate(data, headers = 'keys', tablefmt = 'fancy_grid'))

    df = pd.DataFrame(data)
    df.to_csv(name_file, index = False)

    # Option 2: Using Pandas
    # print(df.to_string())

    


if args.club:
    if (args.name): func()

    print('CLUB')
    url = base_url + '/clubs/' + args.club
    response = requests.get(url)
    data = response.json()

    club_file += args.club + '.csv'

    # Option 1: Using Tabulate
    print(tabulate(data, headers = 'keys', tablefmt = 'fancy_grid'))

    df = pd.DataFrame(data)
    df.to_csv(club_file, index = False)

    df = pd.DataFrame(data)
    df.to_csv(club_file, index = False)

    # Option 2: Using Pandas
    # print(df.to_string())

print()

if name_file:
    print(f'File Saved:  | {name_file} |')
if club_file:
    print(f'File Saved: | {club_file} |')


