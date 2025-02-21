from datetime import datetime
from discord import Interaction

async def uptime(
    interaction: Interaction,
    bot_start_time: datetime,
):
    """Comando de uptime.

    Args:
        interaction (Interaction): Interacción con el bot.
        bot_start_time (datetime): Tiempo de inicio del bot.
    """
    # Mostrar tiempo de actividad
    now = datetime.now()
    uptime = now - bot_start_time
    await interaction.response.send_message(f"Bot uptime: {uptime}", ephemeral=True)