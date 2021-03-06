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

    if "OBDII_Monitors" in temp_file_name:
        obd2_monitors_path = temp_file_name











