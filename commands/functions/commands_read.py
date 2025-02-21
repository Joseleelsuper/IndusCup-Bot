import json
from commands.functions.getDBFiles import getCommands


def read_commands() -> dict:
    """Lee los comandos del archivo commands.json

    Returns:
        dict: Comandos del archivo commands.json
    """
    with open(getCommands(), "r") as f:
        commands = json.load(f)
    return commands
