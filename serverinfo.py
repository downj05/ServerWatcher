import a2s
import re
import human_readable as hr
from datetime import datetime
import json
from time import sleep
from colorama import Fore, Style
import os
import argparse


parser = argparse.ArgumentParser(prog='cyrillic',
	description='Grab info about the server, log players and alert on certain player joins/leaves.',
	epilog='Have fun scheming!'
)

LOGS_DIR = 'logs'

parser.add_argument('-m', '--monitor', action='store_true', help='enable auto monitoring, also logs to directory)')
parser.add_argument('-a', '--address', type=str, default='145.239.131.158:27062',
					help='address of the Steam server for extracting player names, in format IP:port')
parser.add_argument('-d', '--delay', type=int, default='30',
			help='delay between doing new scans, in seconds, used for monitoring')
args = parser.parse_args()

# Extract server address and port from command line arguments
server_address, server_port = args.address.split(':')
server_port = int(server_port)
address = (server_address, server_port)

# get the absolute path of the directory containing the script
script_dir = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(script_dir, LOGS_DIR)
watchlist = []
if os.path.isfile(os.path.join(script_dir, 'usernames.txt')):
	# Open the usernames.txt file for reading
	with open(os.path.join(script_dir, 'usernames.txt'), 'r') as file:
		# Read all lines from the file, ignoring those starting with #
		watchlist = [line.strip() for line in file if not line.startswith('#')]

def write_log(players):
	# Create the 'logs' directory if it doesn't exist
	if not os.path.exists(LOGS_DIR):
		os.makedirs(LOGS_DIR)

	# Get the current date and time as a string
	date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

	# Set the filename to the current date and time
	filename = os.path.join(LOGS_DIR,f"{date_str}.json")
	
	json_players = []
	# Make new players array that can be serialized into JSON
	for p_old in players:
		json_players.append({'name': p_old.name, 'duration': p_old.duration})

	# Write the players array to the JSON file
	with open(filename, "w") as f:
		json.dump(json_players, f)

	print(f"{Style.DIM}{Fore.LIGHTBLACK_EX}Saved log to {Fore.WHITE}{filename}{Style.RESET_ALL}")

def match_terminal_color(text):
	# Extract the color code and text from the input text
	match = re.search(r'<color=(#[0-9a-fA-F]{6})>(.*?)</color>', text)
	if match:
		color_code = match.group(1)
		text_inside_tag = match.group(2)
		# Map the color code to a terminal color
		color_map = {
			'#000000': Fore.BLACK,
			'#0000FF': Fore.BLUE,
			'#00FFFF': Fore.CYAN,
			'#008000': Fore.GREEN,
			'#787878': Fore.LIGHTBLACK_EX,
			'#0000CD': Fore.LIGHTBLUE_EX,
			'#E0FFFF': Fore.LIGHTCYAN_EX,
			'#00FF00': Fore.LIGHTGREEN_EX,
			'#FF00FF': Fore.LIGHTMAGENTA_EX,
			'#FF0000': Fore.LIGHTRED_EX,
			'#F0F0F0': Fore.LIGHTWHITE_EX,
			'#FFFF00': Fore.LIGHTYELLOW_EX,
			'#FF00FF': Fore.MAGENTA,
			'#FF0000': Fore.RED,
			'#FFFFFF': Fore.WHITE,
			'#FFFF00': Fore.YELLOW,
		}
		if color_code in color_map:
			return color_map[color_code] + text_inside_tag + Fore.RESET
	return text

def _join_leave_message(player: a2s.Player, join: bool, print_message=False):
	join_color = Fore.YELLOW
	if player.name in watchlist:
		join_color = Fore.GREEN
	if join:
		action_string = "joined"
		s2 = ""
	else:
		action_string = "left"
		s2 = f"{Fore.LIGHTBLACK_EX} | Playtime: {Fore.YELLOW}{Style.BRIGHT}{hr.time_delta(int(player.duration))}{Style.NORMAL}.{Style.RESET_ALL}"
	s1 = f"{join_color}{Style.BRIGHT}{player.name}{Style.NORMAL} {action_string} the game{Style.RESET_ALL}"
	if print_message:
		print(s1+s2)
	return f"{s1}{s2}"

def join_message(player: a2s.Player):
	return _join_leave_message(player=player, join=True)

def leave_message(player: a2s.Player):
	return _join_leave_message(player=player, join=False)

def print_info(address=address):
	info = a2s.info(address)
	print(Fore.LIGHTCYAN_EX + info.server_name + Fore.LIGHTBLACK_EX + ' | ' + Fore.LIGHTBLUE_EX + match_terminal_color(info.game)
		+ Fore.LIGHTBLACK_EX + f" ({info.player_count}/{info.max_players})")

def get_players(address=address):
	players = a2s.players(address)
	return players

def player_in_list(player: a2s.Player, list: list):
	for lp in list:
		if lp.name == player.name:
			return True
	return False

# Have a list of players the first time we run
# Lets us see if a monitored username has joined
# Rather than printing their join message
# Also used for storing players we are aware of, for monitoring change
player_cache = []

while True:
	os.system('cls' if os.name == 'nt' else 'clear')
	print_info()
	players = get_players()
	action_messages = []
	for p in players:
		name_color = Fore.LIGHTMAGENTA_EX
		if p.name in watchlist:
			# Make player name red when printing list
			name_color = Fore.RED

		# If we are monitoring
		if args.monitor:
			# If player not in player_cache  
			if not player_in_list(p, player_cache):
				# If not in player_cache, print that the player joined
				action_messages.append(join_message(p))
				# Put player in player_cache
				player_cache.append(p)
		
		print(f"{name_color}{p.name.ljust(32)}{Fore.LIGHTBLACK_EX} | {Fore.CYAN}{hr.time_delta(int(p.duration))}{Fore.RESET}")

	if not args.monitor:
		break
	
	for p in player_cache:
		# If a watched player has left
		if not player_in_list(p, players):
			# Print leave message
			action_messages.append(leave_message(p))
			# Remove player from player_cache
			player_cache.remove(p)
	
	write_log(players)
	for m in action_messages:
		print(m)
	sleep(args.delay)