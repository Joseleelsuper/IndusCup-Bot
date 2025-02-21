import traceback
from discord import Interaction


def command_error_handler(func: callable) -> callable:
    """Maneja los errores de los comandos.

    Args:
        func (callable): Función a la que se le manejarán los errores.

    Returns:
        callable: Función que maneja los errores.
    """
    async def wrapper(interaction: Interaction):
        try:
            await func(interaction)
        except Exception as e:
            traceback.print_exc()
            await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)
    return wrapper