import os
import json
from pathlib import Path
from discord import Interaction

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

async def clear(interaction: Interaction, amount: int):
    """Elimina mensajes del canal actual.

    Args:
        interaction (Interaction): Interacción del usuario con el bot.
        amount (int): Cantidad de mensajes a eliminar.
    """
    if amount < 1 or amount > 100:
        await interaction.response.send_message(
            "La cantidad de mensajes a eliminar debe ser mayor a 0 y menor que 100.", ephemeral=True
        )
        await log_command(interaction, f"clear command by {interaction.user} failed: invalid amount {amount}")
        return

    await interaction.response.defer(ephemeral=True)
    deleted_messages = await interaction.channel.purge(limit=amount)
    deleted_messages_content = "\n".join([f"{msg.author}: {msg.content}" for msg in deleted_messages])
    await log_command(interaction, f"clear command by {interaction.user} succeeded: purged {amount} messages\nDeleted messages:\n```{deleted_messages_content}```")
    await interaction.followup.send(
        f"Se han eliminado {amount} mensajes.", ephemeral=True
    )