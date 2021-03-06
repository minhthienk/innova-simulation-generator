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

    if ("OBDII_Monitors" in temp_file_name) and ('~' not in temp_file_name):
        obd2_monitors_path = temp_file_name
    if ("Generic_J1979_LD" in temp_file_name) and ('~' not in temp_file_name):
        j1979_ld_path = temp_file_name

    if ("Ford_DTCDatabase_" in temp_file_name) and ('~' not in temp_file_name):
        ford_dtc_fp = temp_file_name
    if ("Ford_NwScan_" in temp_file_name) and ('~' not in temp_file_name):
        ford_nws_fp = temp_file_name
    if ("Mazda_DTCDatabase_" in temp_file_name) and ('~' not in temp_file_name):
        mazda_dtc_fp = temp_file_name
    if ("Mazda_NwScan_" in temp_file_name) and ('~' not in temp_file_name):
        mazda_nws_fp = temp_file_name




