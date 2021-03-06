import pathlib


script_dir_path = pathlib.Path.cwd()
master_dir_path = pathlib.Path.cwd().parent
databases_dir_path = master_dir_path / 'databases'
pickled_dir_path = master_dir_path / 'pickled' 
simulation_dir_path = master_dir_path / 'simulation' 
ymme_path = {}
dtc_path = {}
battery_reset_path = {}
vin_path = {}

# get the path(s) of excel file(s)
for currentFile in databases_dir_path.iterdir():  
    temp_file_name = str(currentFile)
    if "Ford_YMME" in temp_file_name:
        ymme_path['ford'] = temp_file_name
        print('Getting YMME database path: ' + ymme_path['ford'])
    if "DTCDatabase" in temp_file_name:
        dtc_path['ford'] = temp_file_name
        print('Getting DTC database path: ' + dtc_path['ford'])
    if "Ford_Battery Reset_Database" in temp_file_name:
        battery_reset_path['ford'] = temp_file_name
        print('Getting Battery Reset database path: ' + battery_reset_path['ford'])
    if "Ford_VinDecode" in temp_file_name:
        vin_path['ford'] = temp_file_name
        print('Getting Vin Decode database path: ' + vin_path['ford'])












