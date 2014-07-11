import sqlite3
import logging
import server.DuplicateTokenError

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

'''Returns a suspect's ID by name.'''
def get_suspect_id_by_name(name):
    result = curs.execute('select id from suspects where name = ?', (name,)).fetchone()
    return result[0]

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

'''Returns the game ID for a given game token.
Raises DuplicateTokenError if the given token is not unique to the databse.'''
def get_game_id_by_token(token):
    try:
        token = (int(token),)
    except ValueError:
        print("Invalid token!")
        logging.warning("Invalid token!")
        return
    result = curs.execute("select id from games where self_token=?", token).fetchall()
    if len(result) > 1:
        raise server.DuplicateTokenError.DuplicateTokenError('The token provided was not unique.')
    return result[0][0]

'''Return a list of active game tokens.'''
def get_game_tokens():
    tokens = []
    for row in curs.execute("select self_token from games"):
        tokens.append(int(row[0]))
    return tokens

'''Creates a new game in the database using the given generated token. This token is of
temporary use, just to allow a Game to identify its database equivalent.'''
def insert_new_game(token):
    try:
        insert_params = (int(token), get_suspect_id_by_name("Scarlet"))
    except ValueError:
        print("Invalid token!")
        logging.warning("Invalid token!")
        return
    curs.execute("insert into games (self_token, turn) values (?, ?)", insert_params)
    connection.commit()

'''Deletes an entry from the games table (i.e. a game that has ended.) Does not validate that the
game_id provided is (a) a finished game, or (b) a game that exists. Because of (a) this function is
potentially dangerous. CHECK YOUR GAME_ID!'''
def delete_game(game_id):
    curs.execute('delete from games where id = ?', (game_id,))
    connection.commit()

'''Moves a given suspect to a given location for a given game_id.'''
def set_suspect_location(game_id, suspect, location):
    try:
        update_params = (int(location), int(game_id), int(suspect))
    except ValueError as e:
        print(e.value)
        logging.warning(e.value)
        return
    curs.execute('update suspect_locations set location=? where game_id=? and suspect=?', update_params)
    connection.close()

'''Close database connection. SHOULD ONLY BE CALLED ON EXIT OF MAIN CLASS.'''
def close_db():
    curs.close()
    connection.close()