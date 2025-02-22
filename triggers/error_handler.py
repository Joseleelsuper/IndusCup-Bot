import functools
from .check import check
import traceback
from discord import Interaction


def command_error_handler(func: callable) -> callable:
    """Maneja los errores de los comandos.

    Args:
        func (callable): Función a la que se le manejarán los errores.

    Returns:
        callable: Función que maneja los errores.
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        interaction: Interaction = args[0]
        try:
            await func(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            try:
                await interaction.response.send_message(
                    f"Error al ejecutar el comando.\n\n```{str(e)}```", ephemeral=True
                )
            except Exception:
                await interaction.followup.send(
                    f"Error al ejecutar el comando.\n\n```{str(e)}```", ephemeral=True
                )
        finally:
            await check(interaction)

    return wrapper
