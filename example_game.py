# example_game.py

from project_httpclient import ProjectHttpClient

# Make sure API key and user ID are in memory
with open('token.txt') as f:
    for line in f:
        if not line.startswith("#"):
            values = line.split(',')
            my_id = values[0]
            my_key = values[1].strip()
            break

playing_real_server = False
phc = ProjectHttpClient(my_id,  my_key,  playing_real_server)
# Create a few new games
board_size = 3
target_size = 3
me_first = True
phc.create_new_game(board_size,  target_size,  9999,  me_first)

game_id = phc.get_my_games()[0]

# Now make moves using phc.make_move(game_id,row,col)
# ...
