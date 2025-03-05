import os
import json
import discord
from discord import Interaction, Member
from pathlib import Path
import uuid
import bcrypt


async def log_command(interaction: Interaction, message: str):
    try:
        root_path = Path(__file__).resolve().parent.parent.parent
        util_file = os.path.join(root_path, "db", "util", "log_channel.json")
        with open(util_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        log_channel_id = int(data["log_channel"])
        log_channel = interaction.guild.get_channel(log_channel_id)
        if log_channel:
            await log_channel.send(message)
    except Exception:
        pass


async def create_team(
    interaction: Interaction, team_name: str, members_array: list[Member]
):
    """Crea un equipo con el nombre y los miembros especificados.

    El equipo se guardará en un json dentro de `/db/teams/{team_name}.json`.
    Además, se creará una nueva categoría con el nombre del equipo,
    un canal de texto llamado `general` y un canal de voz llamado `Voz` dentro de esa categoría.

    Esos canales serán privados, por lo que se creará un rol cuyos permisos sea poder ver esos canales.
    A los miembros del equipo se les asigna el mismo rol.

    Args:
        interaction (Interaction): Interacción del usuario con el bot.
        team_name (str): Nombre del equipo.
        members_array (list[Member]): Lista de miembros del equipo. Default to None.
    """
    guild = interaction.guild

    role = None
    category = None
    text_channel = None
    voice_channel = None

    try:
        # Comprobar si ya existe un rol con el mismo nombre
        existing_role = discord.utils.get(guild.roles, name="Team_" + team_name)
        if existing_role:
            await interaction.followup.send(
                f"Ya existe un rol con el nombre {team_name}", ephemeral=True
            )
            await log_command(interaction, f"create_team command by {interaction.user} failed: role already exists for team {team_name}")
            raise Exception(f"Ya existe un rol con el nombre {team_name}")
        # Comprobar que el usuario no pertenece a un equipo
        for member in members_array:
            for rol in member.roles:
                if rol.name.startswith("Team_"):
                    await interaction.followup.send(
                        f"El usuario {member.name} ya pertenece a un equipo",
                        ephemeral=True,
                    )
                    await log_command(interaction, f"create_team command by {interaction.user} failed: {member.name} already in a team")
                    raise Exception(
                        f"El usuario {member.name} ya pertenece a un equipo"
                    )

        # Crear rol con permisos para ver canales
        role = await guild.create_role(
            name="Team_" + team_name, 
            colour=discord.Colour.random(),
            hoist=True  # Esto hace que el rol aparezca separado en la lista de miembros
        )
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            role: discord.PermissionOverwrite(view_channel=True),
        }

        # Crear categoría y canales
        category = await guild.create_category(
            "Team_" + team_name, overwrites=overwrites
        )
        text_channel = await guild.create_text_channel(
            "🗨️general", category=category, overwrites=overwrites
        )
        voice_channel = await guild.create_voice_channel(
            "🔊Voz", category=category, overwrites=overwrites, user_limit=6, bitrate=96000
        )

        # Asignar el rol a los miembros
        for member in members_array:
            await member.add_roles(role)

        # Crear una contraseña aleatoria de 8 caracteres mayúsculas, minúsculas, números y especiales.
        password_base = os.urandom(8).hex()
        password = bcrypt.hashpw(
            password_base.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        # Preparar datos del equipo en formato JSON
        team_data = {
            "id": str(uuid.uuid4()),
            "name": team_name,
            "members": [
                {"id": str(member.id), "name": member.name} for member in members_array
            ],
            "password": password,
        }

        # Guardar el JSON en /db/teams/{team_name}.json
        root_path = Path(__file__).resolve().parent.parent.parent
        file_dir = root_path / "db" / "teams"
        file_dir.mkdir(parents=True, exist_ok=True)
        file_path = os.path.join(file_dir, f"{team_name.replace(' ', '_')}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(team_data, f, ensure_ascii=False, indent=4)

        # Enviar al canal de texto creado la contraseña, mencionando al creaodr del equipo.
        await text_channel.send(
            f"Equipo creado por **{interaction.user.mention}**.\nUtiliza la contraseña **{password_base}** para invitar a más miembros."
        )
        for member in members_array:
            if member.id != interaction.user.id:
                await text_channel.send(f"{member.mention} se ha unido al equipo.")

        # Responder al usuario
        await interaction.followup.send(
            f"Equipo {team_name} creado con éxito.", ephemeral=True
        )
        await log_command(interaction, f"create_team command by {interaction.user} succeeded: created team {team_name}")
    except Exception:
        if role:
            print(role)
            await role.delete()
        if category:
            await category.delete()
        if text_channel:
            await text_channel.delete()
        if voice_channel:
            await voice_channel.delete()
        await log_command(interaction, f"create_team command by {interaction.user} failed: error occurred while creating team {team_name}")
    finally:
        del password_base
        del password
