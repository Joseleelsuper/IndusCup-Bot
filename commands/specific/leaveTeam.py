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

async def leave_team(interaction: discord.Interaction):
    """Abandonar un equipo.

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
        await log_command(interaction, f"leave_team command by {interaction.user} failed: not in any team")
        return

    team_name = team_role.name[len("Team_") :]
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
        await log_command(interaction, f"leave_team command by {interaction.user} failed: team file for {team_name} not found")
        return

    # Eliminar al usuario de la lista de miembros
    members = team_data.get("members", [])
    new_members = [m for m in members if str(m["id"]) != str(interaction.user.id)]
    if len(new_members) == len(members):
        await interaction.response.send_message(
            "No formas parte de este equipo.", ephemeral=True
        )
        await log_command(interaction, f"leave_team command by {interaction.user} failed: user not in members for team {team_name}")
        return

    guild = interaction.guild
    # Quitar el rol del equipo al usuario
    try:
        await interaction.user.remove_roles(team_role)
    except Exception:
        pass

    # Si la lista de miembros queda vacía, proceder a eliminar el equipo (como delete_team)
    if not new_members:
        category = discord.utils.get(guild.categories, name=f"Team_{team_name}")
        if category:
            for channel in category.channels:
                await channel.delete()
            await category.delete()
        role = discord.utils.get(guild.roles, name=f"Team_{team_name}")
        if role:
            await role.delete()
        try:
            os.remove(team_file_path)
        except Exception:
            pass
        await interaction.response.send_message(
            f"Has abandonado el equipo {team_name}. Al no quedar miembros, el equipo ha sido eliminado.",
            ephemeral=True,
        )
        await log_command(interaction, f"leave_team command by {interaction.user} succeeded: left and deleted team {team_name}")
    else:
        team_data["members"] = new_members

        # Enviar un mensaje al canal del equipo informando que el usuario ha abandonado el equipo
        team_channel = discord.utils.get(
            guild.text_channels, name=f"team_{team_name.lower()}"
        )
        if team_channel:
            await team_channel.send(
                f"{interaction.user.display_name} ha abandonado el equipo."
            )

        # Verificar si el usuario era el líder del equipo
        if str(team_data["members"][0]["id"]) == str(interaction.user.id):
            new_leader = new_members[0] if new_members else None
            if new_leader:
                await team_channel.send(
                    f"{new_leader['name']} es el nuevo líder del equipo."
                )

        # Actualizar el archivo JSON
        try:
            with open(team_file_path, "w", encoding="utf-8") as f:
                json.dump(team_data, f, ensure_ascii=False, indent=4)
        except Exception:
            pass
        await interaction.response.send_message(
            f"Has abandonado el equipo {team_name}.", ephemeral=True
        )
        await log_command(interaction, f"leave_team command by {interaction.user} succeeded: left team {team_name}")
