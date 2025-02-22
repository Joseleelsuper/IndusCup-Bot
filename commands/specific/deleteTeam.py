import os
import json
import discord
from pathlib import Path

async def log_command(interaction, message: str):
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

async def delete_team(interaction: discord.Interaction):
    """Eliminar un equipo.

    Args:
        interaction (discord.Interaction): Interacción del usuario.
    """
    # Verificar si el usuario pertenece a un equipo
    team_role = next(
        (r for r in interaction.user.roles if r.name.startswith("Team_")), None
    )
    if team_role is None:
        await interaction.response.send_message(
            "No perteneces a ningún equipo.", ephemeral=True
        )
        await log_command(interaction, f"delete_team command by {interaction.user} failed: not in any team")
        return

    team_name = team_role.name[len("Team_") :]
    # Construir la ruta al archivo JSON del equipo
    root_path = Path(__file__).resolve().parent.parent.parent
    team_file_path = os.path.join(
        root_path, "db", "teams", f"{team_name.replace(' ', '_')}.json"
    )

    try:
        with open(team_file_path, "r", encoding="utf-8") as f:
            team_data = json.load(f)
    except Exception:
        await interaction.response.send_message(
            "El equipo no existe en la base de datos.", ephemeral=True
        )
        await log_command(interaction, f"delete_team command by {interaction.user} failed: team file for {team_name} not found")
        return

    # Comprobar si el usuario es el líder (primer miembro de la lista)
    if not team_data.get("members") or str(team_data["members"][0]["id"]) != str(
        interaction.user.id
    ):
        await interaction.response.send_message(
            "Solo el líder del equipo puede eliminarlo.", ephemeral=True
        )
        await log_command(interaction, f"delete_team command by {interaction.user} failed: user is not team leader for {team_name}")
        return

    guild = interaction.guild

    # Eliminar canales, categoría y rol del equipo
    category = discord.utils.get(guild.categories, name=f"Team_{team_name}")
    if category:
        for channel in category.channels:
            await channel.delete()
        await category.delete()

    role = discord.utils.get(guild.roles, name=f"Team_{team_name}")
    if role:
        await role.delete()

    # Borrar el archivo JSON del equipo
    try:
        os.remove(team_file_path)
    except Exception:
        pass

    try:
        await interaction.response.send_message(
            f"Equipo {team_name} eliminado con éxito.", ephemeral=True
        )
        await log_command(interaction, f"delete_team command by {interaction.user} succeeded: deleted team {team_name}")
    except discord.Forbidden:
        await interaction.user.send(f"Equipo {team_name} eliminado con éxito.")
        await log_command(interaction, f"delete_team command by {interaction.user} succeeded (forbidden response): deleted team {team_name}")
