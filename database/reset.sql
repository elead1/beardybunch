delete from games;
delete from player_assignments;
delete from cardholders;
delete from suspect_locations;
delete from sqlite_sequence where name='games' or name='player_assignments' or name='cardholders' or name = 'suspect_locations';