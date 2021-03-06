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
        ymme_path['Ford'] = temp_file_name
        print('Getting YMME database path: ' + ymme_path['Ford'])
    if "DTCDatabase" in temp_file_name:
        dtc_path['Ford'] = temp_file_name
        print('Getting DTC database path: ' + dtc_path['Ford'])
    if "Ford_Battery Reset_Database" in temp_file_name:
        battery_reset_path['Ford'] = temp_file_name
        print('Getting Battery Reset database path: ' + battery_reset_path['Ford'])
    if "Ford_VinDecode" in temp_file_name:
        vin_path['Ford'] = temp_file_name
        print('Getting Vin Decode database path: ' + vin_path['Ford'])
    #if "Generic_J1979_LD" in temp_file_name:
    #    generic_j1979_ld_path = temp_file_name
    #    print('Getting generic_j1979_path path: ' + generic_j1979_path)











