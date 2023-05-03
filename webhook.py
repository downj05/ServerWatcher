import human_readable as hr
from discord_webhook import DiscordWebhook, DiscordEmbed
import a2s

def baseEmbed(server_info: a2s.SourceInfo, server_icon: str, uptime: int) -> DiscordEmbed:
    e = DiscordEmbed()
    e.add_embed_field(name="Server:", value=server_info.server_name, inline=True)
    e.add_embed_field(name="Players:", value=f"{server_info.player_count}/{server_info.max_players}", inline=True)
    e.set_footer(text=f"Bot Uptime: {hr.time_delta(uptime)}  |  Server Ping: {int(server_info.ping*1000)}ms")
    e.set_thumbnail(url=server_icon)
    return e

def get_role_from_username(player: a2s.Player):
	"""
	Take in a player, get its username, '[Civilian]Robert' for example,
	and return its role and seperated username. e.g Civilian, Robert 
	"""
	# Get the username of the player
	username = player.name
	# Split the username on the first occurence of ']'
	role, username = username.split(']', 1)
	# Remove the first character of the role, which is '['
	role = role[1:]
	# Remove any spaces from the role
	role = role.strip()
	# Return the role and username
	return username, role

def join(webhook_url: str, player: a2s.Player, server_info: a2s.SourceInfo, server_icon: str, uptime: int):
    username, role = get_role_from_username(player)
    webhook = DiscordWebhook(url=webhook_url)
    join_embed = baseEmbed(server_info=server_info, server_icon=server_icon, uptime=uptime)
    join_embed.set_title(title='Player Joined')
    join_embed.set_color(color=1498786)
    join_embed.set_description(f"**{username}** has joined the server\nRole: **{role}**")
    webhook.add_embed(join_embed)
    response = webhook.execute()

def leave(webhook_url: str, player: a2s.Player, server_info: a2s.SourceInfo, server_icon: str, uptime: int):
    username, role = get_role_from_username(player)
    webhook = DiscordWebhook(url=webhook_url)
    leave_embed = baseEmbed(server_info=server_info, server_icon=server_icon, uptime=uptime)
    leave_embed.set_title(title='Player Left')
    leave_embed.set_color(color=14560790)
    leave_embed.set_description(f"**{username}** has left the server\n*Total Playtime: {hr.time_delta(int(player.duration))}*\nRole: **{role}**")
    webhook.add_embed(leave_embed)
    response = webhook.execute()