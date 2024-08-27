import importlib.metadata
import requests

def version():

    def get_installed_version():
        installed_version = importlib.metadata.version("sammhelper")
        return installed_version

    def check_for_updates():
        installed_version = get_installed_version()
    
        # Fetch the latest version from PyPI
        try:
            response = requests.get("https://pypi.org/pypi/sammhelper/json")
            response.raise_for_status()  # Raise an error for bad responses (e.g., 404, 500)
            latest_version = response.json()["info"]["version"]
        except requests.RequestException:
            return "Error: Unable to fetch the latest version of sammhelper from PyPI."
        
        if installed_version == latest_version:
            return f"The newest version of sammhelper ({installed_version}) is already installed."
        else:
            return (
                f"A new version of sammhelper is available ({latest_version}). "
                f"In order to update sammhelper, open your command window and enter: pip install --upgrade sammhelper"
            )