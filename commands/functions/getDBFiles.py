import os
from pathlib import Path

def getCommands() -> str:
    """Obtiene la ruta del archivo commands.json

    Returns:
        str: Ruta del archivo commands.json
    """
    app_path = os.getcwd()
    file_path = os.path.join(app_path, "db/util/commands.json")

    return file_path

def getDotenv() -> str:
    """Obtiene la ruta del archivo .env

    Returns:
        str: Ruta del archivo .env
    """
    project_dir = Path(__file__).resolve().parents[2]
    file_path = project_dir / ".env"
    
    return str(file_path)