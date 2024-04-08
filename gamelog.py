import requests
from requests.exceptions import JSONDecodeError
import chess.pgn
import io
import sqlite3

def fetch_and_print_user_games(usernames, conn, cursor):
    # Define the headers to include in your requests (optional, but good practice)
    headers = {'User-Agent': 'YourApp/1.0'}

    # Create a set to keep track of processed usernames
    processed_usernames = set(usernames)
    
    for username in usernames:
        print(f"Fetching games for {username}...")
        # Fetch the user's game archives URL
        archives_url = f'https://api.chess.com/pub/player/{username}/games/archives'
        archives_response = requests.get(archives_url, headers=headers)
        
        if archives_response.status_code == 200:
            archives = archives_response.json()
            for archive_url in archives['archives']:
                # Fetch the games for each archive
                games_response = requests.get(archive_url, headers=headers)
                if games_response.status_code == 200:
                    games = games_response.json()['games']
                    for game in games:
                        # Extract opponent username
                        opponent_username = get_opponent_username(game, username)
                        # If opponent username is not in the list, add it for fetching
                        if opponent_username not in processed_usernames:
                            print(f"Fetching games for {opponent_username}...")
                            processed_usernames.add(opponent_username)
                        # Print and save game details
                        print_and_save_game_details(game, cursor)
                else:
                    print(f"Error fetching games from archive. Status Code: {games_response.status_code}")
        else:
            print(f"Error fetching archives list for {username}. Status Code: {archives_response.status_code}")

def get_opponent_username(game, username):
    if game['white'].get('username') == username:
        return game['black'].get('username', 'N/A')
    elif game['black'].get('username') == username:
        return game['white'].get('username', 'N/A')
    else:
        return 'N/A'

def print_and_save_game_details(game, cursor):
    white_username = game.get('white', {}).get('username', 'N/A')
    black_username = game.get('black', {}).get('username', 'N/A')

    print(f"[White \"{white_username}\"]")
    print(f"[Black \"{black_username}\"]")
    
    # Save player names to the database
    cursor.execute("INSERT INTO games (white_username, black_username) VALUES (?, ?)", (white_username, black_username))

    pgn = game.get('pgn', '')
    if pgn:
        moves = extract_moves_from_pgn(pgn)
        # Save moves to the database
        for move_number, move in enumerate(moves, start=1):
            cursor.execute("INSERT INTO moves (white_username, black_username, move_number, move) VALUES (?, ?, ?, ?)", 
                           (white_username, black_username, move_number, move))

def extract_moves_from_pgn(pgn):
    # Parse the PGN data
    pgn_game = chess.pgn.read_game(io.StringIO(pgn))
    moves = []
    if pgn_game is not None:
        # Iterate through the moves and add them to the list
        node = pgn_game
        while node.variations:
            move = str(node.variation(0).move)
            moves.append(move)
            node = node.variation(0)
    return moves

# Connect to the SQLite database
conn = sqlite3.connect('gameslog.db')
cursor = conn.cursor()

# Create tables for games and moves
cursor.execute('''CREATE TABLE IF NOT EXISTS games
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   white_username TEXT,
                   black_username TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS moves
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   white_username TEXT,
                   black_username TEXT,
                   move_number INTEGER,
                   move TEXT)''')

# List of usernames to fetch games for
usernames = ["ck14gt9","Jkingnificent","kapilnathan","Avanziii","Orbiform","Turboautist69","nihalsarin","HansOnTwitch",
"Polish_fighter3000","NikoTheodorou","Bigfish1995","viditchess","LyonBeast","Konavets","GMWSO","BogdanDeac"]

# Fetch and print games for each user in the list
fetch_and_print_user_games(usernames, conn, cursor)

# Commit changes and close connection to the database
conn.commit()
conn.close()
