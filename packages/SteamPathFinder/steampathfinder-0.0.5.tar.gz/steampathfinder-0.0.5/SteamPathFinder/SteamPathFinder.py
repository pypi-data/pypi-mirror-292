import os
import vdf
import winreg

def get_steam_path():
    """Get the installation path of Steam from the Windows registry."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\\Valve\\Steam") as key:
            steam_path, _ = winreg.QueryValueEx(key, "SteamPath")
    except FileNotFoundError:
        raise FileNotFoundError("ERROR: Steam is not installed.")
    
    if not os.path.exists(steam_path):
        raise FileNotFoundError("ERROR: The Steam path does not exist or is not accessible.")
    
    return steam_path

def load_library_folders(steam_path):
    """Load and parse the libraryfolders.vdf file to get Steam library folders."""
    vdf_file_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
    
    if not os.path.exists(vdf_file_path):
        raise FileNotFoundError("ERROR: libraryfolders.vdf file does not exist.")
    
    try:
        with open(vdf_file_path, 'r') as file:
            vdf_data = file.read()
        parsed_vdf = vdf.loads(vdf_data)
    except IOError as e:
        raise IOError(f"ERROR: Unable to read the libraryfolders.vdf file. {e}")
    except ValueError as e:
        raise ValueError(f"ERROR: Error parsing the VDF file. {e}")
    
    return parsed_vdf.get('libraryfolders', {})

def get_app_path(steam_path, app_id):
    """Get the installation path of the specified app by its app ID."""
    libraryfolders = load_library_folders(steam_path)
    app_path = None
    
    for folder in libraryfolders.values():
        if isinstance(folder, dict) and 'apps' in folder and str(app_id) in folder['apps']:
            app_path = folder.get('path')
            if app_path and os.path.exists(app_path):
                break
    
    if app_path is None:
        raise FileNotFoundError(f"ERROR: Could not find the installation path for app {app_id}.")
    
    return os.path.join(app_path, 'steamapps')

def get_game_path(steam_path, app_id, game_name):
    """Get the installation path of the specified game by its app ID and name."""
    app_path = get_app_path(steam_path, app_id)
    game_path = os.path.join(app_path, 'common', game_name)
    
    if not os.path.exists(game_path):
        raise FileNotFoundError(f"ERROR: The game path does not exist. Check if the game name '{game_name}' is correct and the game is properly installed.")
    
    return game_path

# Example usage:
# steam_path = get_steam_path()
# game_path = get_game_path(steam_path, 440, "Team Fortress 2")