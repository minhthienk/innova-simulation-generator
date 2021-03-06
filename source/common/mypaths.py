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
        obd2_monitors_fp = temp_file_name
    if ("Generic_J1979_LD" in temp_file_name) and ('~' not in temp_file_name):
        obd2_ld_fp = temp_file_name

    if ("Ford_DTCDatabase_" in temp_file_name) and ('~' not in temp_file_name):
        ford_dtc_fp = temp_file_name
    if ("Ford_NwScan_" in temp_file_name) and ('~' not in temp_file_name):
        ford_nws_fp = temp_file_name
    if ("Ford_Chasis_LD" in temp_file_name) and ('~' not in temp_file_name):
        ford_chassis_ld_fp = temp_file_name
    if ("Ford_Body_LD" in temp_file_name) and ('~' not in temp_file_name):
        ford_body_ld_fp = temp_file_name
    if ("Ford_TelematicDongle" in temp_file_name) and ('~' not in temp_file_name):
        ford_telematics_fp = temp_file_name
    


    if ("Ford_ABS_LD" in temp_file_name) and ('~' not in temp_file_name):
        ford_abs_ld_fp = temp_file_name
    
    if ("Ford_SRS_LD" in temp_file_name) and ('~' not in temp_file_name):
        ford_srs_ld_fp = temp_file_name

    if ("Ford_PCM_LD" in temp_file_name) and ('~' not in temp_file_name):
        ford_pcm_ld_fp = temp_file_name

    if ("Ford_PCM(Only TCM PID)_LD" in temp_file_name) and ('~' not in temp_file_name):
        ford_pcm_tcm_ld_fp = temp_file_name


    if ("Ford_TCM_LD" in temp_file_name) and ('~' not in temp_file_name):
        ford_tcm_ld_fp = temp_file_name


    if ("Ford_BECM_LD" in temp_file_name) and ('~' not in temp_file_name):
        ford_becm_ld_fp = temp_file_name

    if ("Ford_DCDC" in temp_file_name) and ('~' not in temp_file_name):
        ford_DCDC_ld_fp = temp_file_name


    if ("Ford_US_TPMS" in temp_file_name) and ('~' not in temp_file_name):
        ford_tpms_ld_fp = temp_file_name





    if ("Mazda_NwScan_" in temp_file_name) and ('~' not in temp_file_name):
        mazda_nws_fp = temp_file_name


    if ("Mazda_DTCDatabase_" in temp_file_name) and ('~' not in temp_file_name):
        mazda_dtc_fp = temp_file_name


    if ("Mazda_US_TPMS" in temp_file_name) and ('~' not in temp_file_name):
        mazda_tpms_ld_fp = temp_file_name

    if ("Mazda_ABS_LD" in temp_file_name) and ('~' not in temp_file_name):
        mazda_abs_ld_fp = temp_file_name
    
    if ("Mazda_SRS_LD" in temp_file_name) and ('~' not in temp_file_name):
        mazda_srs_ld_fp = temp_file_name

    if ("Mazda_Chassis_LD_" in temp_file_name) and ('~' not in temp_file_name):
        mazda_chassis_ld_fp = temp_file_name
    if ("Mazda_Body_LD_" in temp_file_name) and ('~' not in temp_file_name):
        mazda_body_ld_fp = temp_file_name


