import sqlite3

__author__ = 'Eric'

'''This module serves as a utility module for accessing the database.'''

connection = sqlite3.connect("..\database\clueless.db")
curs = connection.cursor()

'''Return a map of suspects and their IDs'''
def get_suspects():
    suspect_map = {}
    for row in curs.execute("select * from suspects"):
        suspect_map[row[0]] = row[1]
    return suspect_map

'''Return a map of weapons and their IDs'''
def get_weapons():
    weapon_map = {}
    for row in curs.execute("select * from weapons"):
        weapon_map[row[0]] = row[1]
    return weapon_map

'''Return a map of locations and their IDs'''
def get_locations():
    location_map = {}
    for row in curs.execute("select * from locations"):
        location_map[row[0]] = row[1]
    return location_map

'''Return a list of all active games.'''
def get_running_games():
    games = []
    for row in curs.execute("select id from games"):
        games.append(int(row[0]))
    return games