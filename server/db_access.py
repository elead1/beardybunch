import sqlite3
import logging
import itertools
import server.DuplicateTokenError

__author__ = 'Eric'

'''This module serves as a utility module for accessing the database.'''


#Return a tuple with db connection and cursor
def get_db_access():
    connection = sqlite3.connect("..\database\clueless.db")
    curs = connection.cursor()
    return connection, curs


#Return a map of suspects and their IDs
def get_suspects(connection, curs):
    suspect_map = {}
    for row in curs.execute("select id, name from suspects"):
        suspect_map[row[0]] = row[1]
    return suspect_map


#Returns a map of suspect id->name pairs that are not assigned to players for a game.
def get_unassigned_suspects(connection, curs, game_id):
    suspect_map = {}
    curs.execute("select id, name from suspects where id in (select id from suspects except select suspect from player_assignments where game_id=?)", (game_id,))
    avail = curs.fetchall()
    for row in avail:
        suspect_map[row[0]] = row[1]
    return suspect_map


#Returns a map of suspect IDs->client IDs
def get_suspect_client_assignments(connection, curs, game_id):
    suspect_map = {}
    curs.execute("select s.id, p.client_id from suspects s, player_assignments p where p.game_id=? and s.id=p.suspect", (game_id,))
    results = curs.fetchall()
    for row in results:
        suspect_map[row[0]] = row[1]
    return suspect_map


#Returns a map of suspect IDs -> list of all assigned card names.
def get_assigned_cards(connection, curs, game_id):
    suspect_map = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
    sql_select = "select c.suspect, s.name from cardholders c, {0}s s where c.{0}_card_id=s.id and c.{0}_card_id is not null and c.game_id=?"
    curs.execute(sql_select.format("suspect"), (game_id,))
    results = curs.fetchall()
    for row in results:
        suspect_map[row[0]].append(row[1])
    curs.execute(sql_select.format("weapon"), (game_id,))
    results = curs.fetchall()
    for row in results:
        suspect_map[row[0]].append(row[1])
    curs.execute(sql_select.format("location"), (game_id,))
    results = curs.fetchall()
    for row in results:
        suspect_map[row[0]].append(row[1])
    return suspect_map


#Return a map of suspects->locations for the given game.
def get_suspect_locations(connection, curs, game_id):
    suspect_map = {}
    for row in curs.execute("select suspect, location from suspect_locations where game_id=?", (game_id,)):
        suspect_map[row[0]] = row[1]
    return suspect_map


#Get current turn for given game.
def get_turn(connection, curs, game_id):
    curs.execute("select turn from games where id=?", (game_id,))
    return curs.fetchall()[0][0]


#Returns a suspect's ID by name.
def get_suspect_id_by_name(connection, curs, name):
    result = curs.execute('select id from suspects where name = ?', (name,)).fetchone()
    return result[0]


#Return a map of weapons and their IDs
def get_weapons(connection, curs):
    weapon_map = {}
    for row in curs.execute("select * from weapons"):
        weapon_map[row[0]] = row[1]
    return weapon_map


#Return a map of locations and their IDs
def get_locations(connection, curs):
    location_map = {}
    for row in curs.execute("select * from locations"):
        location_map[row[0]] = row[1]
    return location_map


#Return a map of rooms and their IDs
def get_rooms(connection, curs):
    room_map = {}
    for row in curs.execute("select l.id, l.name from rooms r, locations l where l.id=r.location_id"):
        room_map[row[0]] = row[1]
    return room_map


#Return a list of all active games.
def get_running_games(connection, curs):
    games = []
    for row in curs.execute("select id from games"):
        games.append(int(row[0]))
    return games


#Returns the game ID for a given game token.
#Raises DuplicateTokenError if the given token is not unique to the databse.
def get_game_id_by_token(connection, curs, token):
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


#Return a list of active game tokens.
def get_game_tokens(connection, curs):
    tokens = []
    for row in curs.execute("select self_token from games"):
        tokens.append(int(row[0]))
    return tokens


#Creates a new game in the database using the given generated token. This token is of
#temporary use, just to allow a Game to identify its database equivalent.
def insert_new_game(connection, curs, token):
    try:
        insert_params = (int(token), get_suspect_id_by_name(connection, curs, "Scarlet"))
    except ValueError:
        print("Invalid token!")
        logging.warning("Invalid token!")
        return
    curs.execute("insert into games (self_token, turn) values (?, ?)", insert_params)
    connection.commit()


#Deletes an entry from the games table (i.e. a game that has ended.) Does not validate that the
#game_id provided is (a) a finished game, or (b) a game that exists. Because of (a) this function is
#potentially dangerous. CHECK YOUR GAME_ID!
def delete_game(connection, curs, game_id):
    curs.execute('delete from games where id = ?', (game_id,))
    connection.commit()


#Moves a given suspect to a given location for a given game_id.
def set_suspect_location(connection, curs, game_id, suspect, location):
    try:
        update_params = (int(location), int(game_id), int(suspect))
    except ValueError as e:
        print(e.value)
        logging.warning(e.value)
        return
    curs.execute('update suspect_locations set location=? where game_id=? and suspect=?', update_params)
    connection.commit()


#Moves all suspects to designated starting points for a given game_id.
def initialize_suspect_locations(connection, curs, game_id):
    orig_locs = [4, 8, 20, 18, 14, 6]
    suspects = get_suspects(connection, curs)
    for loc, sus in itertools.izip_longest(orig_locs, suspects.keys()):
        curs.execute('insert into suspect_locations (game_id, suspect, location) values (?, ?, ?)', (game_id, sus, loc))
    connection.commit()


#Update turn tracker, setting the turn value to the given suspect (denoting its that suspect's turn)
def change_turn(connection, curs, game_id, new_sus_turn):
    curs.execute("update games set turn=? where id=?", (new_sus_turn, game_id))
    connection.commit()


#Assign suspect to client for a game.
#suspect is a suspect id.
#client is a md5 hash of an (ip, port) tuple
def assign_suspect(connection, curs, game_id, client, suspect):
    params = (game_id, str(client), suspect)
    curs.execute('insert into player_assignments (game_id, client_id, suspect) values (?, ?, ?)', params)
    connection.commit()


#Assigns cards to suspects.
# card_type should be either suspect, weapon, or room
# card_id is the numerical identifier of the card to assign
# suspect_id is the numerical identifier of the suspect to assign the card to
def assign_card(connection, curs, game_id, card_type, suspect_id, card_id):
    query = "insert into cardholders (game_id, suspect, {0}_card_id) values (?, ?, ?)".format(card_type)
    params = (game_id, suspect_id, card_id)
    curs.execute(query, params)
    connection.commit()


def add_loser(connection, curs, game_id, suspect):
    query = "insert into losing_players (game_id, suspect) values (?, ?)"
    curs.execute(query, (game_id, suspect))
    connection.commit()

#Close database connection. SHOULD ONLY BE CALLED ON EXIT OF MAIN CLASS.
def close_db(connection, curs):
    curs.close()
    connection.close()