import os
import json
import discord
from discord import Interaction, Member
from pathlib import Path
import uuid


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
    print("Creating team")
    guild = interaction.guild

    role = None
    category = None
    text_channel = None
    voice_channel = None

    try:
        print("Checking if team exists")
        # Comprobar si ya existe un rol con el mismo nombre
        existing_role = discord.utils.get(guild.roles, name="Team_" + team_name)
        if existing_role:
            await interaction.followup.send(
                f"Ya existe un rol con el nombre {team_name}", ephemeral=True
            )
            raise Exception(f"Ya existe un rol con el nombre {team_name}")

        print("Checking if member is in a team")
        # Comprobar que el usuario no pertenece a un equipo
        for member in members_array:
            for role in member.roles:
                if role.name.startswith("Team_"):
                    await interaction.followup.send(
                        f"El usuario {member.name} ya pertenece a un equipo", ephemeral=True
                    )
                    raise Exception(
                        f"El usuario {member.name} ya pertenece a un equipo"
                    )

        print("Creating role")
        # Crear rol con permisos para ver canales
        role = await guild.create_role(name="Team_" + team_name)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            role: discord.PermissionOverwrite(view_channel=True),
        }

        print("Creating category and channels")
        # Crear categoría y canales
        category = await guild.create_category(
            "Team_" + team_name, overwrites=overwrites
        )
        text_channel = await guild.create_text_channel(
            "general", category=category, overwrites=overwrites
        )
        voice_channel = await guild.create_voice_channel(
            "Voz", category=category, overwrites=overwrites, user_limit=6, bitrate=96000
        )

        print("Assigning role to members")
        # Asignar el rol a los miembros
        for member in members_array:
            await member.add_roles(role)

        print("Saving team data")
        # Preparar datos del equipo en formato JSON
        team_data = {
            "id": str(uuid.uuid4()),
            "name": team_name,
            "members": [
                {"id": str(member.id), "name": member.name} for member in members_array
            ],
        }

        print("Saving JSON")
        # Guardar el JSON en /db/teams/{team_name}.json
        root_path = Path(__file__).resolve().parent.parent.parent
        file_dir = root_path / "db" / "teams"
        file_dir.mkdir(parents=True, exist_ok=True)
        file_path = os.path.join(file_dir, f"{team_name.replace(' ', '_')}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(team_data, f, ensure_ascii=False, indent=4)

        # Responder al usuario
        await interaction.followup.send(
            f"Equipo {team_name} creado con éxito.", ephemeral=True
        )
    except Exception:
        if role:
            await role.delete()
        if category:
            await category.delete()
        if text_channel:
            await text_channel.delete()
        if voice_channel:
            await voice_channel.delete()
