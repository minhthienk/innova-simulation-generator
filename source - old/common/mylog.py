import pathlib
from datetime import datetime
import traceback
import sys

script_dp = pathlib.Path.cwd()
debuglog_fp = script_dp / 'debuglog.txt'

# write data to a file, Open file in append mode, create new file if the file does not exist
first_log_flag = False
def log(*infors):
    global first_log_flag
    fp = debuglog_fp
    if first_log_flag == False:
        temp = '\n\n\n\n==================================================='
        temp += '\n' + str(datetime.now())
        for infor in infors:
            temp += '\n\n' + str(infor)

        first_log_flag = True

    else:
        temp = ''
        for infor in infors:
            temp += '\n\n' + str(infor)

    with open(fp, "a") as file_object:
        file_object.write(temp)



