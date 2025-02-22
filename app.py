# |---------------------------------------------------------------|#
# |   Nombre del programa: app.py                                 |#
# |   Descripción: ULE-Bot                                        |#
# |   @autor: José Gallardo Caballero                             |#
# |   @date: 21/02/2025                                           |#
# |   @version: v1.0.0                                            |#
# |   Versiones:                                                  |#
# |       v1.0.0 [07/03/2023]: Creación del programa.             |#
# |---------------------------------------------------------------|#

# Librerías
# Generales
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Discord
import discord
from discord import app_commands
from discord.ext import commands

# Comandos
from commands.events import member_join, member_update
from commands.functions import getDotenv, read_commands
from commands.other import help
from commands.specific import create_team, join_team, delete_team, leave_team
from commands.util import ping, uptime, clear

from triggers import command_error_handler

# Variables globales
load_dotenv(getDotenv())
# Generales
CREATOR_ID = int(os.getenv("CREATOR_ID"))
VERSION = str(os.getenv("VERSION"))
COMMAND = read_commands()

# Discord
INTENTS = discord.Intents.all()
Color = discord.Color.orange()

# Bot
TOKEN = str(os.getenv("TOKEN"))
bot = commands.Bot(
    command_prefix="", intents=INTENTS
)  # Prefijo de los comandos del bot, en desuso
PERMISO = int(os.getenv("PERMISO"))


class abot(discord.Client):
    def __init__(self):
        super().__init__(intents=INTENTS, chunk_guilds_at_startup=True)
        self.token = TOKEN
        self.bot = bot
        self.synced = True
        self.activity = discord.Activity(
            type=discord.ActivityType.listening, name="/help"
        )
        self.status = discord.Status.online

    # Mensaje de inicio
    async def on_ready(self):
        await tree.sync(guild=None)
        print("Bot conectado y listo para usar")
        print(
            f"Enlace de invitación: https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions={PERMISO}&scope=bot"
        )


# Definir el árbol de comandos
bot = abot()
tree = app_commands.CommandTree(bot)

###################################################################
###################################################################
###################################################################


# Eventos
@bot.event
async def on_member_join(member: discord.Member):
    await member_join(member)


@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    await member_update(before, after)


###################################################################
###################################################################
###################################################################


# Comandos
# Los comandos se ejecutan solamente en su servidor. Para que se ejecuten en cualquier servidor, quitar el parámetro 'guild = Guild'
@tree.command(
    name=COMMAND["help"]["name"],
    description=COMMAND["help"]["description"],
)
@command_error_handler
async def help_command(interaction: discord.Interaction):
    await help(interaction)


###################################################################


@tree.command(
    name=COMMAND["ping"]["name"],
    description=COMMAND["ping"]["description"],
)
@command_error_handler
async def ping_command(interaction: discord.Interaction):
    await ping(interaction, bot)


###################################################################


@tree.command(
    name=COMMAND["uptime"]["name"],
    description=COMMAND["uptime"]["description"],
)
@command_error_handler
async def uptime_command(interaction: discord.Interaction):
    await uptime(interaction, bot_start_time)


###################################################################


@tree.command(
    name=COMMAND["createTeam"]["name"],
    description=COMMAND["createTeam"]["description"],
)
@command_error_handler
async def createteam_command(
    interaction: discord.Interaction,
    team_name: str,
    member2: discord.Member = None,
    member3: discord.Member = None,
    member4: discord.Member = None,
    member5: discord.Member = None,
):
    members_array = list(
        set(
            [
                member
                for member in [interaction.user, member2, member3, member4, member5]
                if member is not None
            ]
        )
    )
    await interaction.response.defer(ephemeral=True)
    await create_team(interaction, team_name, members_array)


###################################################################


@tree.command(
    name=COMMAND["joinTeam"]["name"],
    description=COMMAND["joinTeam"]["description"],
)
@command_error_handler
async def join_team_command(interaction: discord.Interaction):
    await join_team(interaction)


###################################################################


@tree.command(
    name=COMMAND["deleteTeam"]["name"],
    description=COMMAND["deleteTeam"]["description"],
)
@command_error_handler
async def delete_team_command(interaction: discord.Interaction):
    await delete_team(interaction)


###################################################################


@tree.command(
    name=COMMAND["leaveTeam"]["name"],
    description=COMMAND["leaveTeam"]["description"],
)
@command_error_handler
async def leave_team_command(interaction: discord.Interaction):
    await leave_team(interaction)

###################################################################

@tree.command(
    name=COMMAND["clear"]["name"],
    description=COMMAND["clear"]["description"],
)
@command_error_handler
async def clear_command(interaction: discord.Interaction, amount: int = 5):
    await clear(interaction, amount)


###################################################################
###################################################################
###################################################################


def main():
    global bot_start_time
    bot_start_time = datetime.now()

    asyncio.run(bot.start(TOKEN))


if __name__ == "__main__":
    main()
