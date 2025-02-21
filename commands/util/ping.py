from discord import BotIntegration, Interaction
from dotenv import load_dotenv

from commands.functions.getDBFiles import getDotenv

load_dotenv(getDotenv())


async def ping(
    interaction: Interaction,
    bot: BotIntegration,
):
    """Comando de ping.

    Args:
        interaction (Interaction): Interacción con el bot.
        bot (BotIntegration): Integración con el bot.
    """
    await interaction.response.send_message(
        f"Pong! {round(bot.latency * 1000)}ms",
        ephemeral=True,
    )
