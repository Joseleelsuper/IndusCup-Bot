import traceback
from discord import Interaction


def check(interaction: Interaction):
    """Comprueba si el comando ha sido enviado correctamente. Si no, imprime un mensaje de error en la consola.

    Args:
        interaction (Interaction): Interacción del usuario con el bot.
    """
    try:
        if interaction.response.is_done():
            print("\n")
            print(
                f"El comando '{interaction.data['name']}' ha sido enviado a '{interaction.guild.name}' por '{interaction.user.name}' a la hora '{interaction.created_at}'"
            )
    except Exception:
        print("\n\n")
        traceback.print_exc()
        print("\n\n")
        print(
            f"Error al enviar el comando '{interaction.data['name']}' a '{interaction.guild.name}' por '{interaction.user.name}' a la hora '{interaction.created_at}'"
        )
