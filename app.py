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
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import os

# Discord
import discord
from discord import app_commands
from discord.ext import commands

# Comandos
from commands.events import member_join
from commands.functions import getDotenv, read_commands
from commands.other import help
from commands.util import ping, uptime

from triggers import check, command_error_handler

# Variables globales
load_dotenv(getDotenv())
# Generales
GUILD_ID = int(os.getenv("GUILD_ID"))
CREATOR_ID = int(os.getenv("CREATOR_ID"))
VERSION = str(os.getenv("VERSION"))
COMMAND = read_commands()

# Discord
GUILD = discord.Object(id=GUILD_ID)
INTENTS = discord.Intents.all()
Color = discord.Color.orange()

# Bot
TOKEN = str(os.getenv("TOKEN"))
commands_bot = commands.Bot(
    command_prefix="", intents=INTENTS
)  # Prefijo de los comandos del bot, en desuso
PERMISO = int(os.getenv("PERMISO"))


class abot(discord.Client):
    def __init__(self):
        super().__init__(intents=INTENTS, chunk_guilds_at_startup=True)
        self.token = TOKEN
        self.bot = commands_bot
        self.synced = True
        self.activity = discord.Activity(
            type=discord.ActivityType.listening, name="/help"
        )
        self.status = discord.Status.online

    # Mensaje de inicio
    async def on_ready(self):
        await tree.sync(guild=GUILD)
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
async def on_member_join(member):
    await member_join(member)


###################################################################
###################################################################
###################################################################


# Comandos
# Los comandos se ejecutan solamente en su servidor. Para que se ejecuten en cualquier servidor, quitar el parámetro 'guild = Guild'
@tree.command(
    name=COMMAND["help"]["name"],
    description=COMMAND["help"]["description"],
    guild=GUILD,
)
@command_error_handler
async def help_command(interaction):
    await help(interaction)
    check(interaction)


###################################################################
# Comando de ping
@tree.command(
    name=COMMAND["ping"]["name"],
    description=COMMAND["ping"]["description"],
    guild=GUILD,
)
@command_error_handler
async def ping_command(interaction):
    await ping(interaction, bot)
    check(interaction)


###################################################################
# Comando de uptime
@tree.command(
    name=COMMAND["uptime"]["name"],
    description=COMMAND["uptime"]["description"],
    guild=GUILD,
)
@command_error_handler
async def uptime_command(interaction):
    await uptime(interaction, bot_start_time)
    check(interaction)


###################################################################
###################################################################
###################################################################
def main():
    global bot_start_time
    bot_start_time = datetime.now()

    asyncio.run(bot.start(TOKEN))


if __name__ == "__main__":
    main()
