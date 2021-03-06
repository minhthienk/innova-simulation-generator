import pathlib
from common.path_management import script_dir_path
from datetime import datetime


enumlog_fp = script_dir_path / 'innova_missing_enum.txt'
log_fp = script_dir_path / 'innova_server_log.txt'



# write data to a file, Open file in append mode, create new file if the file does not exist
write_missing_enum_flag = False
def write_missing_enum(txt):
    print('writing missing enum: ' + txt)
    global write_missing_enum_flag
    fp = enumlog_fp
    if write_missing_enum_flag == False:
        temp = '\n\n==================================================='
        temp += '\n' + str(datetime.now())
        temp += '\n' + txt
        write_missing_enum_flag = True
    else:
        temp = '\n' + txt

    with open(fp, "a") as file_object:
        file_object.write(temp)






