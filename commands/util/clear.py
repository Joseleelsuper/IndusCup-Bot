from discord import Interaction


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
        return

    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(
        f"Se han eliminado {amount} mensajes.", ephemeral=True
    )