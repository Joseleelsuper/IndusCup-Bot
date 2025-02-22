import os
import json
from pathlib import Path
import discord
from discord import Member

async def member_update(before: Member, after: Member):
    """Función que se ejecuta cuando un miembro es actualizado.

    Args:
        before (Member): Usuario antes de la actualización.
        after (Member): Usuario después de la actualización.
    """

    guild = after.guild
    # Comprobar en el registro de auditoría si el bot realizó la actualización
    try:
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.member_role_update):
            if entry.target.id == after.id and entry.user.id == guild.me.id:
                return
            break
    except Exception:
        pass

    # Detectar roles de equipo agregados y removidos
    added_roles = [r for r in after.roles if r not in before.roles and r.name.startswith("Team_")]
    removed_roles = [r for r in before.roles if r not in after.roles and r.name.startswith("Team_")]

    for role in added_roles:
        team_name = role.name[len("Team_"):]
        root_path = Path(__file__).resolve().parent.parent.parent
        team_file_path = os.path.join(root_path, "db", "teams", f"{team_name.replace(' ', '_')}.json")
        try:
            with open(team_file_path, "r", encoding="utf-8") as f:
                team_data = json.load(f)
        except Exception:
            continue
        if not any(str(m["id"]) == str(after.id) for m in team_data.get("members", [])):
            team_data.setdefault("members", []).append({"id": str(after.id), "name": after.name})
            try:
                with open(team_file_path, "w", encoding="utf-8") as f:
                    json.dump(team_data, f, ensure_ascii=False, indent=4)
            except Exception:
                pass
            category = discord.utils.get(guild.categories, name=f"Team_{team_name}")
            if category:
                text_channel = discord.utils.get(category.text_channels, name="general")
                if text_channel:
                    await text_channel.send(f"{after.mention} se ha unido al equipo.")

    for role in removed_roles:
        team_name = role.name[len("Team_"):]
        root_path = Path(__file__).resolve().parent.parent.parent
        team_file_path = os.path.join(root_path, "db", "teams", f"{team_name.replace(' ', '_')}.json")
        try:
            with open(team_file_path, "r", encoding="utf-8") as f:
                team_data = json.load(f)
        except Exception:
            continue
        members = team_data.get("members", [])
        new_members = [m for m in members if str(m["id"]) != str(after.id)]
        if len(new_members) != len(members):
            team_data["members"] = new_members
            try:
                with open(team_file_path, "w", encoding="utf-8") as f:
                    json.dump(team_data, f, ensure_ascii=False, indent=4)
            except Exception:
                pass
            category = discord.utils.get(guild.categories, name=f"Team_{team_name}")
            if category:
                text_channel = discord.utils.get(category.text_channels, name="general")
                if text_channel:
                    await text_channel.send(f"{after.mention} ha sido eliminado del equipo.")