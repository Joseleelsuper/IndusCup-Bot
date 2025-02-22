from pathlib import Path
from discord import Interaction, Embed
from discord.ui import Select, View
import os
import discord
import bcrypt
import json


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


async def join_team(interaction: Interaction):
    """Comando para unirse a un equipo.

    Al ejecutarlo, el usuario recibirá de forma ephemeral un embed diciendo: "Elije un equipo al que unirte".
    Abajo aparecerá un botón desplegable con el nombre de todos los equipos existenes, sacados de la BD.

    Al elegir uno, aparecerá un pop-up diciendo: "Uniendose a <nombre_del_equipo>".
    Y abajo una celda de texto para ingresar la clave/contraseña de acceso.

    Si todo está correcto, se le otorgará el rol del equipo y se enviará un mensaje al canal de texto del equipo.

    Args:
        interaction (Interaction): Interacción del usuario con el bot.
    """
    # Si el usuario ya pertenece a un equipo, no puede unirse a otro
    for role in interaction.user.roles:
        if role.name.startswith("Team_"):
            await interaction.response.send_message(
                "Ya perteneces a un equipo. No puedes unirte a otro.",
                ephemeral=True,
            )
            await log_command(interaction, f"join_team command by {interaction.user} failed: already in a team")
            return

    embed = Embed(
        title="Unirse a un equipo",
        description="Elije un equipo al que unirte",
    )
    view = await create_select_menu(interaction)

    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    await log_command(interaction, f"join_team command by {interaction.user} initiated")


async def create_select_menu(interaction: Interaction):
    # Define the Select menu
    # Fetch team names from the directory
    root_path = Path(__file__).resolve().parent.parent.parent
    team_files = os.listdir(
        os.path.join(os.path.dirname(__file__), root_path, "db", "teams")
    )
    team_names = [os.path.splitext(team_file)[0] for team_file in team_files]

    if not team_names:
        interaction.followup.send("No hay equipos creados.", ephemeral=True)
        await log_command(interaction, f"join_team command by {interaction.user} failed: no teams created")
        raise ValueError("No hay equipos creados.")

    # Create Select options from team names
    options = [discord.SelectOption(label=team_name) for team_name in team_names]

    select = Select(
        placeholder="Selecciona un equipo...",
        min_values=1,
        max_values=1,
        options=options,
    )

    # Define the callback for when an option is selected
    async def select_callback(interaction: Interaction):
        selected_team = select.values[0]

        # Create a modal to ask for the team password
        class PasswordModal(discord.ui.Modal, title="Ingresar clave del equipo"):
            password = discord.ui.TextInput(
            label="Clave del equipo",
            style=discord.TextStyle.short,
            placeholder="Ingresa la clave del equipo aquí...",
            required=True,
            )

            async def on_submit(self, interaction: Interaction):
                # Here you can add the logic to verify the password
                # Fetch the encrypted password from the database
                team_password_file = os.path.join(root_path, "db", "teams", f"{selected_team}.json")
                with open(team_password_file, "r") as file:
                    team_data = json.load(file)
                    encrypted_password = team_data["password"]

                # Encrypt the provided password using bcrypt
                provided_password_hash = bcrypt.hashpw(self.password.value.encode('utf-8'), encrypted_password.encode('utf-8')).decode('utf-8')

                # Check if the provided password matches the encrypted password
                if provided_password_hash == encrypted_password:

                    # Assign the role to the user
                    guild = interaction.guild
                    role = discord.utils.get(guild.roles, name=f"Team_{selected_team}")
                    await interaction.user.add_roles(role)

                    await interaction.response.send_message(
                        f"Te has unido al equipo {selected_team}", ephemeral=True
                    )

                    team_data["members"].append({"id": str(interaction.user.id), "name": interaction.user.name})
                    with open(team_password_file, "w") as file:
                        json.dump(team_data, file, ensure_ascii=False, indent=4)

                    # Send a message to the team's text channel
                    team_category = discord.utils.get(guild.categories, name=f"Team_{selected_team}")
                    team_text_channel: discord.TextChannel = discord.utils.get(team_category.text_channels, name="general")
                    await team_text_channel.send(f"{interaction.user.mention} se ha unido al equipo.")

                    await log_command(interaction, f"join_team command by {interaction.user} succeeded: joined team {selected_team}")
                else:
                    await interaction.response.send_message(
                        "Clave incorrecta. Inténtalo de nuevo.", ephemeral=True
                    )
                    await log_command(interaction, f"join_team command by {interaction.user} failed: incorrect password for team {selected_team}")

        # Show the modal to the user
        await interaction.response.send_modal(PasswordModal())

    select.callback = select_callback

    # Create a view and add the select menu to it
    view = View()
    view.add_item(select)
    return view
