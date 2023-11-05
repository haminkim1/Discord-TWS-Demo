import os

def get_project_dir_name():
    # Get the directory path where this script is located
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Split the path into components
    path_components = script_directory.split(os.path.sep)

    # Get the second-to-last folder name
    if len(path_components) >= 2:
        second_to_last_folder = path_components[-2]
    else:
        second_to_last_folder = None

    return second_to_last_folder




project_dir = get_project_dir_name()


def ibapi_port_no():
    if project_dir == "discord-TWS":
        return 7497
    else:
        return 7496

    
# ATM chrome extension's and under app.py some of the URL Is hard coded to 127.0.0.1:5000. I will need to work around this later. 
def flask_port_no():
    if project_dir == "discord-TWS":
        return 5000
    else:
        return 8080
    

def is_production_env():
    if project_dir == "discord-TWS":
        return False
    else:
        return True