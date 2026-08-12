import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import random
import os
import asyncio
from aiohttp import web

# ========== CONFIGURATION ==========
TOKEN = os.environ.get("DISCORD_TOKEN")
PORT = int(os.environ.get("PORT", 8080))

if not TOKEN:
    print("❌ ERROR: DISCORD_TOKEN not found! Please add it in Render Environment Variables.")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ========== HTTP SERVER (Required for Render Web Service) ==========
async def handle(request):
    return web.Response(text="🏆 Tournament Master Bot is online!", content_type="text/html")

app = web.Application()
app.router.add_get('/', handle)

async def start_web_server():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"✅ Web server running on port {PORT}")

# ========== DATABASE ==========
def init_db():
    conn = sqlite3.connect('tournaments.db')
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS tournaments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id TEXT,
        name TEXT,
        game TEXT,
        format TEXT,
        bracket_type TEXT,
        max_players INTEGER,
        start_time TEXT,
        entry_fee TEXT,
        status TEXT DEFAULT 'open',
        created_by TEXT,
        channel_id TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS registrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tournament_id INTEGER,
        user_id TEXT,
        username TEXT,
        in_game_name TEXT,
        rank TEXT,
        region TEXT,
        team_name TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tournament_id INTEGER,
        round_num INTEGER,
        player1_id TEXT,
        player2_id TEXT,
        winner_id TEXT,
        score TEXT,
        status TEXT DEFAULT 'pending',
        voice_channel_id TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS disputes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tournament_id INTEGER,
        reporter_id TEXT,
        opponent_id TEXT,
        reason TEXT,
        status TEXT DEFAULT 'open',
        channel_id TEXT
    )""")

    conn.commit()
    conn.close()

init_db()

def get_db():
    return sqlite3.connect('tournaments.db')

def create_bracket(players, bracket_type):
    random.shuffle(players)
    matches = []

    if bracket_type == "single elimination":
        for i in range(0, len(players), 2):
            if i + 1 < len(players):
                matches.append({
                    'round': 1,
                    'player1': players[i],
                    'player2': players[i + 1]
                })
            else:
                matches.append({
                    'round': 1,
                    'player1': players[i],
                    'player2': None
                })
    elif bracket_type == "round robin":
        for i in range(len(players)):
            for j in range(i + 1, len(players)):
                matches.append({
                    'round': 1,
                    'player1': players[i],
                    'player2': players[j]
                })

    return matches

@bot.event
async def on_ready():
    print(f'✅ Tournament Master is online as {bot.user}')
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, 
        name="tournaments | /help"
    ))
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} commands")
    except Exception as e:
        print(f"⚠️ Sync error: {e}")

# ========== SLASH COMMANDS ==========

@bot.tree.command(name="create_tournament", description="Create a new tournament")
@app_commands.describe(
    name="Tournament name",
    game="Game name (e.g., Valorant, CS2)",
    format="Format (1v1, 2v2, 5v5)",
    bracket_type="Bracket type (single elimination, double elimination, round robin)",
    max_players="Maximum number of players",
    start_time="Start date and time (e.g., 2026-08-15 18:00)",
    entry_fee="Entry fee (default: Free)"
)
async def create_tournament(
    interaction: discord.Interaction,
    name: str,
    game: str,
    format: str,
    bracket_type: str,
    max_players: int,
    start_time: str,
    entry_fee: str = "Free"
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Only admins can create tournaments!", ephemeral=True)
        return

    conn = get_db()
    c = conn.cursor()

    c.execute("""INSERT INTO tournaments 
        (guild_id, name, game, format, bracket_type, max_players, start_time, entry_fee, created_by, channel_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (str(interaction.guild_id), name, game, format, bracket_type, max_players, start_time, entry_fee, str(interaction.user.id), str(interaction.channel_id)))

    tournament_id = c.lastrowid
    conn.commit()
    conn.close()

    embed = discord.Embed(
        title="🏆 Tournament Created!",
        description=f"**{name}** has been created!",
        color=discord.Color.gold()
    )
    embed.add_field(name="🎮 Game", value=game, inline=True)
    embed.add_field(name="⚔️ Format", value=format, inline=True)
    embed.add_field(name="📊 Bracket", value=bracket_type, inline=True)
    embed.add_field(name="👥 Max Players", value=str(max_players), inline=True)
    embed.add_field(name="💰 Entry Fee", value=entry_fee, inline=True)
    embed.add_field(name="📅 Start Time", value=start_time, inline=True)
    embed.add_field(name="📝 Tournament ID", value=str(tournament_id), inline=False)
    embed.set_footer(text="Use /register to join!")

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="register", description="Register for a tournament")
@app_commands.describe(
    tournament_id="The tournament ID",
    in_game_name="Your in-game username",
    rank="Your rank/level",
    region="Your region",
    team_name="Your team name (default: Solo)"
)
async def register(
    interaction: discord.Interaction,
    tournament_id: int,
    in_game_name: str,
    rank: str,
    region: str,
    team_name: str = "Solo"
):
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM tournaments WHERE id = ? AND status = 'open'", (tournament_id,))
    tournament = c.fetchone()

    if not tournament:
        await interaction.response.send_message("❌ Tournament not found or registration closed!", ephemeral=True)
        conn.close()
        return

    c.execute("SELECT * FROM registrations WHERE tournament_id = ? AND user_id = ?", 
              (tournament_id, str(interaction.user.id)))
    if c.fetchone():
        await interaction.response.send_message("❌ You are already registered!", ephemeral=True)
        conn.close()
        return

    c.execute("SELECT COUNT(*) FROM registrations WHERE tournament_id = ?", (tournament_id,))
    count = c.fetchone()[0]
    if count >= tournament[6]:
        await interaction.response.send_message("❌ Tournament is full!", ephemeral=True)
        conn.close()
        return

    c.execute("""INSERT INTO registrations 
        (tournament_id, user_id, username, in_game_name, rank, region, team_name)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (tournament_id, str(interaction.user.id), interaction.user.name, in_game_name, rank, region, team_name))

    conn.commit()
    conn.close()

    embed = discord.Embed(
        title="✅ Registered!",
        description=f"You have registered for **{tournament[2]}**!",
        color=discord.Color.green()
    )
    embed.add_field(name="🎮 In-Game Name", value=in_game_name, inline=True)
    embed.add_field(name="⭐ Rank", value=rank, inline=True)
    embed.add_field(name="🌍 Region", value=region, inline=True)
    embed.add_field(name="👥 Team", value=team_name, inline=True)

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="start_tournament", description="Start the tournament and generate bracket")
@app_commands.describe(tournament_id="The tournament ID to start")
async def start_tournament(interaction: discord.Interaction, tournament_id: int):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Only admins can start tournaments!", ephemeral=True)
        return

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM tournaments WHERE id = ?", (tournament_id,))
    tournament = c.fetchone()

    if not tournament:
        await interaction.response.send_message("❌ Tournament not found!", ephemeral=True)
        conn.close()
        return

    c.execute("SELECT user_id, in_game_name FROM registrations WHERE tournament_id = ?", (tournament_id,))
    players = c.fetchall()

    if len(players) < 2:
        await interaction.response.send_message("❌ Need at least 2 players to start!", ephemeral=True)
        conn.close()
        return

    matches = create_bracket(players, tournament[5])

    for match in matches:
        p1 = match['player1'][0] if match['player1'] else None
        p2 = match['player2'][0] if match['player2'] else None
        c.execute("""INSERT INTO matches (tournament_id, round_num, player1_id, player2_id)
            VALUES (?, ?, ?, ?)""", (tournament_id, match['round'], p1, p2))

    c.execute("UPDATE tournaments SET status = 'active' WHERE id = ?", (tournament_id,))
    conn.commit()
    conn.close()

    embed = discord.Embed(
        title=f"🏆 {tournament[2]} - Bracket Generated!",
        description=f"Format: {tournament[5]} | Players: {len(players)}",
        color=discord.Color.blue()
    )

    for i, match in enumerate(matches[:10], 1):
        p1_name = match['player1'][1] if match['player1'] else "Bye"
        p2_name = match['player2'][1] if match['player2'] else "Bye"
        embed.add_field(name=f"Match {i}", value=f"{p1_name} vs {p2_name}", inline=False)

    if len(matches) > 10:
        embed.set_footer(text=f"...and {len(matches) - 10} more matches")

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="report_result", description="Report match result")
@app_commands.describe(
    match_id="The match ID",
    winner="The winner",
    score="Score (e.g., 2-1)"
)
async def report_result(
    interaction: discord.Interaction,
    match_id: int,
    winner: discord.Member,
    score: str
):
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM matches WHERE id = ?", (match_id,))
    match = c.fetchone()

    if not match:
        await interaction.response.send_message("❌ Match not found!", ephemeral=True)
        conn.close()
        return

    c.execute("UPDATE matches SET winner_id = ?, score = ?, status = 'completed' WHERE id = ?",
              (str(winner.id), score, match_id))
    conn.commit()
    conn.close()

    embed = discord.Embed(
        title="✅ Match Result Recorded!",
        description=f"Match {match_id} completed!",
        color=discord.Color.green()
    )
    embed.add_field(name="🏆 Winner", value=winner.mention, inline=True)
    embed.add_field(name="📊 Score", value=score, inline=True)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="dashboard", description="View tournament dashboard")
@app_commands.describe(tournament_id="The tournament ID")
async def dashboard(interaction: discord.Interaction, tournament_id: int):
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM tournaments WHERE id = ?", (tournament_id,))
    tournament = c.fetchone()

    if not tournament:
        await interaction.response.send_message("❌ Tournament not found!", ephemeral=True)
        conn.close()
        return

    c.execute("SELECT COUNT(*) FROM registrations WHERE tournament_id = ?", (tournament_id,))
    total_players = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM matches WHERE tournament_id = ? AND status = 'completed'", (tournament_id,))
    completed = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM matches WHERE tournament_id = ? AND status = 'pending'", (tournament_id,))
    pending = c.fetchone()[0]

    conn.close()

    embed = discord.Embed(
        title=f"📊 {tournament[2]} - Dashboard",
        color=discord.Color.purple()
    )
    embed.add_field(name="🎮 Game", value=tournament[3], inline=True)
    embed.add_field(name="📈 Status", value=tournament[10].title(), inline=True)
    embed.add_field(name="👥 Players", value=str(total_players), inline=True)
    embed.add_field(name="✅ Completed", value=str(completed), inline=True)
    embed.add_field(name="⏳ Pending", value=str(pending), inline=True)
    embed.add_field(name="📅 Start", value=tournament[8], inline=True)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="dispute", description="Report a dispute")
@app_commands.describe(
    tournament_id="The tournament ID",
    opponent="The opponent",
    reason="Reason for dispute"
)
async def dispute(
    interaction: discord.Interaction,
    tournament_id: int,
    opponent: discord.Member,
    reason: str
):
    conn = get_db()
    c = conn.cursor()

    c.execute("""INSERT INTO disputes (tournament_id, reporter_id, opponent_id, reason)
        VALUES (?, ?, ?, ?)""",
        (tournament_id, str(interaction.user.id), str(opponent.id), reason))

    dispute_id = c.lastrowid
    conn.commit()
    conn.close()

    overwrites = {
        interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        opponent: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }

    for member in interaction.guild.members:
        if member.guild_permissions.administrator:
            overwrites[member] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

    channel = await interaction.guild.create_text_channel(
        f"dispute-{dispute_id}",
        overwrites=overwrites,
        reason=f"Dispute #{dispute_id}"
    )

    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE disputes SET channel_id = ? WHERE id = ?", (str(channel.id), dispute_id))
    conn.commit()
    conn.close()

    embed = discord.Embed(
        title=f"⚠️ Dispute #{dispute_id}",
        description=f"Reporter: {interaction.user.mention}\nOpponent: {opponent.mention}\nReason: {reason}",
        color=discord.Color.red()
    )

    await channel.send(embed=embed)
    await interaction.response.send_message(f"✅ Dispute created: {channel.mention}", ephemeral=True)

@bot.tree.command(name="help", description="Show all commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🏆 Tournament Master - Commands",
        description="Manage tournaments easily!",
        color=discord.Color.gold()
    )

    embed.add_field(name="/create_tournament", value="Create a new tournament (Admin only)", inline=False)
    embed.add_field(name="/register", value="Register for a tournament", inline=False)
    embed.add_field(name="/start_tournament", value="Start tournament & generate bracket (Admin)", inline=False)
    embed.add_field(name="/report_result", value="Report match result", inline=False)
    embed.add_field(name="/dashboard", value="View tournament stats", inline=False)
    embed.add_field(name="/dispute", value="Report a dispute", inline=False)

    await interaction.response.send_message(embed=embed)

# ========== RUN BOTH BOT AND WEB SERVER ==========
async def main():
    await start_web_server()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
